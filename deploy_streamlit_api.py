import os
import shutil
import tempfile
import zipfile
import subprocess
import socket
import uuid
import logging
from typing import Optional, Dict
from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager
import signal
import atexit
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global state to track active deployments
active_deployments: Dict[str, dict] = {}

class DeploymentManager:
    def __init__(self):
        self.lock = threading.Lock()
    
    def find_free_port(self) -> int:
        """Find a free TCP port on localhost."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', 0))
            s.listen(1)
            port = s.getsockname()[1]
        return port
    
    def install_dependencies(self, project_dir: str) -> bool:
        """Install Python dependencies from requirements.txt if it exists."""
        requirements_path = os.path.join(project_dir, 'requirements.txt')
        if os.path.exists(requirements_path):
            try:
                subprocess.run(
                    ['pip', 'install', '-r', requirements_path],
                    check=True,
                    capture_output=True,
                    text=True
                )
                logger.info(f"Dependencies installed from {requirements_path}")
                return True
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to install dependencies: {e.stderr}")
                return False
        return True
    
    def run_streamlit_app(self, project_dir: str, port: int, deployment_id: str) -> Optional[subprocess.Popen]:
        """Run Streamlit app as a subprocess on the specified port."""
        # Find the main Python file (prioritize app.py, main.py, then any .py file)
        main_file = None
        for filename in ['app.py', 'main.py']:
            if os.path.exists(os.path.join(project_dir, filename)):
                main_file = filename
                break
        
        if not main_file:
            # Find any Python file in the root directory
            py_files = [f for f in os.listdir(project_dir) if f.endswith('.py')]
            if py_files:
                main_file = py_files[0]
        
        if not main_file:
            logger.error(f"No Python file found in {project_dir}")
            return None
        
        try:
            # Run Streamlit in headless mode with no browser
            proc = subprocess.Popen(
                [
                    'streamlit', 'run',
                    os.path.join(project_dir, main_file),
                    '--server.port', str(port),
                    '--server.headless', 'true',
                    '--browser.serverAddress', '0.0.0.0',
                    '--browser.gatherUsageStats', 'false'
                ],
                cwd=project_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            
            # Give it a moment to start
            threading.Timer(2.0, self.check_streamlit_status, args=[proc, port, deployment_id]).start()
            
            return proc
        except Exception as e:
            logger.error(f"Failed to start Streamlit: {str(e)}")
            return None
    
    def check_streamlit_status(self, proc: subprocess.Popen, port: int, deployment_id: str):
        """Check if Streamlit started successfully."""
        if proc.poll() is not None:
            # Process has already exited
            stdout, stderr = proc.communicate()
            logger.error(f"Streamlit failed to start on port {port}. Error: {stderr.decode()}")
            
            with self.lock:
                if deployment_id in active_deployments:
                    self.cleanup_deployment(deployment_id)
            
            raise HTTPException(
                status_code=500,
                detail=f"Streamlit failed to start: {stderr.decode()}"
            )
    
    def start_ngrok_tunnel(self, port: int, deployment_id: str) -> Optional[str]:
        """Start ngrok tunnel and return public URL."""
        try:
            from pyngrok import ngrok
        except ImportError:
            logger.error("pyngrok not installed. Please install with 'pip install pyngrok'")
            return None
        
        try:
            # Set ngrok auth token if specified in environment
            if 'NGROK_AUTH_TOKEN' in os.environ:
                ngrok.set_auth_token(os.environ['NGROK_AUTH_TOKEN'])
            
            # Create HTTP tunnel
            tunnel = ngrok.connect(port, bind_tls=True)
            public_url = tunnel.public_url
            
            logger.info(f"Ngrok tunnel created: {public_url} -> localhost:{port}")
            
            return public_url
        except Exception as e:
            logger.error(f"Failed to create ngrok tunnel: {str(e)}")
            return None
    
    def cleanup_deployment(self, deployment_id: str):
        """Clean up a deployment by killing processes and removing temp files."""
        with self.lock:
            if deployment_id in active_deployments:
                deployment = active_deployments.pop(deployment_id)
                
                # Terminate Streamlit process
                if 'streamlit_process' in deployment and deployment['streamlit_process'].poll() is None:
                    try:
                        deployment['streamlit_process'].terminate()
                        deployment['streamlit_process'].wait(timeout=5)
                        logger.info(f"Terminated Streamlit process for deployment {deployment_id}")
                    except Exception as e:
                        logger.warning(f"Failed to terminate Streamlit process: {str(e)}")
                
                # Terminate ngrok tunnel
                if 'ngrok_public_url' in deployment:
                    try:
                        from pyngrok import ngrok
                        tunnels = ngrok.get_tunnels()
                        for tunnel in tunnels:
                            if tunnel.public_url == deployment['ngrok_public_url']:
                                ngrok.disconnect(tunnel.public_url)
                                logger.info(f"Closed ngrok tunnel for deployment {deployment_id}")
                                break
                    except Exception as e:
                        logger.warning(f"Failed to close ngrok tunnel: {str(e)}")
                
                # Remove temp directory
                if 'temp_dir' in deployment and os.path.exists(deployment['temp_dir']):
                    try:
                        shutil.rmtree(deployment['temp_dir'])
                        logger.info(f"Removed temp directory for deployment {deployment_id}")
                    except Exception as e:
                        logger.warning(f"Failed to remove temp directory: {str(e)}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Initialize deployment manager
    app.state.deployment_manager = DeploymentManager()
    logger.info("Server started")
    
    yield
    
    # Clean up all active deployments on shutdown
    logger.info("Server shutting down - cleaning up deployments")
    for deployment_id in list(active_deployments.keys()):
        app.state.deployment_manager.cleanup_deployment(deployment_id)

app = FastAPI(lifespan=lifespan)

@app.post("/deploy_streamlit")
async def deploy_streamlit(file: UploadFile):
    """Endpoint to deploy a zipped Streamlit project."""
    deployment_id = str(uuid.uuid4())
    deployment_manager: DeploymentManager = app.state.deployment_manager
    
    try:
        # Create temp directory for this deployment
        temp_dir = tempfile.mkdtemp(prefix=f"streamlit_deploy_{deployment_id}_")
        logger.info(f"Created temp directory: {temp_dir}")
        
        # Save uploaded zip file
        zip_path = os.path.join(temp_dir, "uploaded.zip")
        with open(zip_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        # Unzip the file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        os.remove(zip_path)
        logger.info(f"Unzipped project to {temp_dir}")
        
        # Install dependencies
        if not deployment_manager.install_dependencies(temp_dir):
            raise HTTPException(
                status_code=400,
                detail="Failed to install dependencies from requirements.txt"
            )
        
        # Find free port and start Streamlit
        port = deployment_manager.find_free_port()
        streamlit_proc = deployment_manager.run_streamlit_app(temp_dir, port, deployment_id)
        if not streamlit_proc:
            raise HTTPException(
                status_code=400,
                detail="Failed to start Streamlit app - no valid Python file found"
            )
        
        # Start ngrok tunnel
        public_url = deployment_manager.start_ngrok_tunnel(port, deployment_id)
        if not public_url:
            raise HTTPException(
                status_code=500,
                detail="Failed to create ngrok tunnel"
            )
        
        # Store deployment info
        with deployment_manager.lock:
            active_deployments[deployment_id] = {
                'temp_dir': temp_dir,
                'port': port,
                'streamlit_process': streamlit_proc,
                'ngrok_public_url': public_url,
                'deployment_id': deployment_id
            }
        
        return JSONResponse(
            status_code=200,
            content={
                "deployment_id": deployment_id,
                "public_url": public_url,
                "local_port": port,
                "status": "deployed"
            }
        )
    
    except Exception as e:
        # Clean up if anything went wrong
        deployment_manager.cleanup_deployment(deployment_id)
        logger.error(f"Deployment failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Deployment failed: {str(e)}"
        )

@app.delete("/undeploy/{deployment_id}")
async def undeploy(deployment_id: str):
    """Endpoint to undeploy a running Streamlit app."""
    deployment_manager: DeploymentManager = app.state.deployment_manager
    
    if deployment_id not in active_deployments:
        raise HTTPException(
            status_code=404,
            detail="Deployment not found"
        )
    
    deployment_manager.cleanup_deployment(deployment_id)
    return {"status": "undeployed", "deployment_id": deployment_id}

@app.get("/deployments")
async def list_deployments():
    """List all active deployments."""
    return {
        "deployments": [
            {
                "deployment_id": dep_id,
                "public_url": dep['ngrok_public_url'],
                "local_port": dep['port']
            }
            for dep_id, dep in active_deployments.items()
        ]
    }

if __name__ == "__main__":
    # Get port from environment variable or use default 8000
    port = int(os.getenv("API_PORT", "8001"))
    # Run the FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=port)
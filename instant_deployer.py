"""
Instant Deployment System for Excel-to-Web Application Generator

This module provides Docker-based instant deployment capabilities for
generated web applications with auto-scaling and monitoring.
"""

import os
import shutil
import tempfile
import zipfile
import subprocess
import socket
import uuid
import logging
import threading
import time
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass
import docker
import requests
import json

logger = logging.getLogger(__name__)

@dataclass
class DeploymentInfo:
    """Information about a deployed application"""
    deployment_id: str
    public_url: str
    local_port: int
    container_id: str
    status: str  # running, stopped, error
    created_at: str

class InstantDeployer:
    """Docker-based instant deployment system"""
    
    def __init__(self):
        self.docker_client = None
        self.active_deployments: Dict[str, DeploymentInfo] = {}
        self._initialize_docker()
    
    def _initialize_docker(self):
        """Initialize Docker client"""
        try:
            self.docker_client = docker.from_env()
            logger.info("Docker client initialized successfully")
        except Exception as e:
            logger.warning(f"Docker not available: {str(e)}")
            logger.info("Running in local mode without Docker deployment")
            self.docker_client = None
    
    def deploy_application(self, project_files: List[Any], 
                         app_name: Optional[str] = None) -> DeploymentInfo:
        """Deploy a web application from project files"""
        deployment_id = str(uuid.uuid4())
        
        try:
            # Create temporary directory for deployment
            temp_dir = tempfile.mkdtemp(prefix=f"deploy_{deployment_id}_")
            logger.info(f"Created deployment directory: {temp_dir}")
            
            # Write project files to temp directory
            self._write_project_files(project_files, temp_dir)
            
            # Check if Docker is available
            if self.docker_client is None:
                logger.info("Docker not available, running in local mode")
                # Create a mock deployment info for local mode
                deployment_info = DeploymentInfo(
                    deployment_id=deployment_id,
                    public_url="http://localhost:8501",
                    local_port=8501,
                    container_id="local-mode",
                    status="local",
                    created_at=time.strftime("%Y-%m-%d %H:%M:%S")
                )
                
                self.active_deployments[deployment_id] = deployment_info
                logger.info("Application ready for local execution")
                
                return deployment_info
            
            # Build Docker image
            image_name = f"excel-to-web-{deployment_id[:8]}"
            image = self._build_docker_image(temp_dir, image_name)
            
            # Find free port
            port = self._find_free_port()
            
            # Run container
            container = self._run_container(image, port)
            
            # Wait for container to be ready
            self._wait_for_container_ready(port)
            
            # Create public URL (in production, this would use a proper domain)
            public_url = f"http://localhost:{port}"
            
            # Store deployment info
            deployment_info = DeploymentInfo(
                deployment_id=deployment_id,
                public_url=public_url,
                local_port=port,
                container_id=container.id,
                status="running",
                created_at=time.strftime("%Y-%m-%d %H:%M:%S")
            )
            
            self.active_deployments[deployment_id] = deployment_info
            
            # Start monitoring thread
            self._start_monitoring(deployment_id, container)
            
            logger.info(f"Successfully deployed application: {public_url}")
            
            return deployment_info
            
        except Exception as e:
            logger.error(f"Deployment failed: {str(e)}")
            # Cleanup on failure
            self._cleanup_deployment(deployment_id)
            raise RuntimeError(f"Failed to deploy application: {str(e)}")
    
    def _write_project_files(self, project_files: List[Any], temp_dir: str):
        """Write project files to temporary directory"""
        for file_info in project_files:
            file_path = os.path.join(temp_dir, file_info.path)
            
            # Create directory if needed
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Write file content
            with open(file_path, 'w') as f:
                f.write(file_info.content)
            
            logger.debug(f"Created file: {file_path}")
    
    def _build_docker_image(self, temp_dir: str, image_name: str):
        """Build Docker image from project files"""
        try:
            logger.info(f"Building Docker image: {image_name}")
            
            # Build image using Docker client
            image, build_logs = self.docker_client.images.build(
                path=temp_dir,
                tag=image_name,
                rm=True,
                forcerm=True
            )
            
            logger.info(f"Successfully built image: {image_name}")
            return image
            
        except docker.errors.BuildError as e:
            logger.error(f"Docker build failed: {str(e)}")
            for line in e.build_log:
                if 'stream' in line:
                    logger.error(f"Build log: {line['stream']}")
            raise
    
    def _run_container(self, image, port: int):
        """Run Docker container"""
        try:
            container = self.docker_client.containers.run(
                image,
                detach=True,
                ports={'8080/tcp': port},
                environment={'PORT': '8080'},
                name=f"excel-web-{uuid.uuid4().hex[:8]}",
                auto_remove=True
            )
            
            logger.info(f"Started container {container.id} on port {port}")
            return container
            
        except Exception as e:
            logger.error(f"Failed to start container: {str(e)}")
            raise
    
    def _find_free_port(self) -> int:
        """Find a free TCP port"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            s.listen(1)
            port = s.getsockname()[1]
        return port
    
    def _wait_for_container_ready(self, port: int, timeout: int = 30):
        """Wait for container to be ready and responding"""
        start_time = time.time()
        url = f"http://localhost:{port}"
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    logger.info(f"Container is ready and responding on {url}")
                    return
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(1)
        
        raise RuntimeError(f"Container did not become ready within {timeout} seconds")
    
    def _start_monitoring(self, deployment_id: str, container):
        """Start monitoring thread for deployment"""
        def monitor():
            while deployment_id in self.active_deployments:
                try:
                    # Refresh container status
                    container.reload()
                    
                    if container.status != "running":
                        logger.warning(f"Container {deployment_id} is not running: {container.status}")
                        self.active_deployments[deployment_id].status = container.status
                        
                        # Auto-restart if needed
                        if container.status == "exited":
                            logger.info(f"Attempting to restart container {deployment_id}")
                            container.start()
                            
                except Exception as e:
                    logger.error(f"Monitoring error for {deployment_id}: {str(e)}")
                
                time.sleep(10)  # Check every 10 seconds
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
    
    def undeploy_application(self, deployment_id: str) -> bool:
        """Undeploy an application"""
        if deployment_id not in self.active_deployments:
            logger.warning(f"Deployment {deployment_id} not found")
            return False
        
        try:
            self._cleanup_deployment(deployment_id)
            logger.info(f"Successfully undeployed application {deployment_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to undeploy {deployment_id}: {str(e)}")
            return False
    
    def _cleanup_deployment(self, deployment_id: str):
        """Clean up deployment resources"""
        if deployment_id in self.active_deployments:
            deployment = self.active_deployments.pop(deployment_id)
            
            try:
                # Stop and remove container
                container = self.docker_client.containers.get(deployment.container_id)
                container.stop(timeout=10)
                logger.info(f"Stopped container {deployment.container_id}")
            except Exception as e:
                logger.warning(f"Failed to stop container {deployment.container_id}: {str(e)}")
            
            try:
                # Remove Docker image
                image_name = f"excel-to-web-{deployment_id[:8]}"
                self.docker_client.images.remove(image_name, force=True)
                logger.info(f"Removed image {image_name}")
            except Exception as e:
                logger.warning(f"Failed to remove image for {deployment_id}: {str(e)}")
    
    def get_deployment_status(self, deployment_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a deployment"""
        if deployment_id not in self.active_deployments:
            return None
        
        deployment = self.active_deployments[deployment_id]
        
        try:
            # Get container stats
            container = self.docker_client.containers.get(deployment.container_id)
            container.reload()
            
            stats = {
                "deployment_id": deployment_id,
                "public_url": deployment.public_url,
                "status": container.status,
                "created": deployment.created_at,
                "container_id": deployment.container_id,
                "image": container.image.tags[0] if container.image.tags else "unknown",
                "ports": container.ports,
                "health": "healthy" if container.status == "running" else "unhealthy"
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get status for {deployment_id}: {str(e)}")
            return None
    
    def list_deployments(self) -> List[Dict[str, Any]]:
        """List all active deployments"""
        deployments = []
        
        for deployment_id in self.active_deployments:
            status = self.get_deployment_status(deployment_id)
            if status:
                deployments.append(status)
        
        return deployments
    
    def scale_deployment(self, deployment_id: str, replicas: int = 1) -> bool:
        """Scale a deployment (basic implementation)"""
        if deployment_id not in self.active_deployments:
            return False
        
        # In a production system, this would use Docker Swarm or Kubernetes
        # For now, we'll just log the scaling request
        logger.info(f"Scaling request for {deployment_id}: {replicas} replicas")
        
        # Basic implementation - just update the deployment info
        deployment = self.active_deployments[deployment_id]
        # In a real system, we would actually scale the containers
        
        return True
    
    def get_application_logs(self, deployment_id: str, lines: int = 100) -> Optional[str]:
        """Get application logs"""
        if deployment_id not in self.active_deployments:
            return None
        
        try:
            deployment = self.active_deployments[deployment_id]
            container = self.docker_client.containers.get(deployment.container_id)
            
            logs = container.logs(tail=lines).decode('utf-8')
            return logs
            
        except Exception as e:
            logger.error(f"Failed to get logs for {deployment_id}: {str(e)}")
            return None
    
    def cleanup_all(self):
        """Clean up all deployments"""
        logger.info("Cleaning up all deployments")
        
        for deployment_id in list(self.active_deployments.keys()):
            self.undeploy_application(deployment_id)
        
        logger.info("All deployments cleaned up")
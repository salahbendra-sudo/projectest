import requests
import logging
from pathlib import Path

class DeployAPIClient:
    def __init__(self, base_url="http://127.0.0.1:8001"):
        self.base_url = base_url
        self.logger = logging.getLogger(__name__)
    
    def deploy_project(self, project_zip_path: str):
        """Client for /deploy_streamlit endpoint"""
        try:
            with open(project_zip_path, 'rb') as f:
                response = requests.post(
                    f"{self.base_url}/deploy_streamlit",
                    files={'file': (Path(project_zip_path).name, f)},
                    timeout=300
                )
                response.raise_for_status()
                
                result = response.json()
                self.logger.info(f"Deployment successful! URL: {result['public_url']}")
                return result
                
        except Exception as e:
            self.logger.error(f"Deployment failed: {str(e)}")
            raise

# Test Client            
if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    
    if len(sys.argv) != 2:
        print("Usage: python deploy_api_client.py <project_zip_path>")
        sys.exit(1)
    
    client = DeployAPIClient()
    try:
        result = client.deploy_project(sys.argv[1])
        print(f"Test successful! Deployment: {result}")
    except Exception as e:
        print(f"Test failed: {str(e)}")

import logging
from unified_api_client import UnifiedAPIClient
from deploy_api_client import DeployAPIClient

def test_full_flow():
    logging.basicConfig(level=logging.INFO)
    
    # 1. Process Excel and generate project
    unified_client = UnifiedAPIClient()
    project_zip = unified_client.analyze_and_generate(
        excel_path="test.xlsx",
        instructions_path="instructions.md",
        prompt="Create a sales dashboard"
    )
    
    # 2. Deploy the generated project
    deploy_client = DeployAPIClient()
    deployment = deploy_client.deploy_project(project_zip)
    
    print(f"\n🎉 Successfully deployed to: {deployment['public_url']}")
    print(f"Local port: {deployment['local_port']}")
    print(f"Deployment ID: {deployment['deployment_id']}")

if __name__ == "__main__":
    test_full_flow()

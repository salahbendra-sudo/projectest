import requests
from pathlib import Path
import tempfile
import logging

class UnifiedAPIClient:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.logger = logging.getLogger(__name__)
        
    def analyze_and_generate(self, excel_path: str, instructions_path: str, prompt: str):
        """Client for /analyze-and-generate endpoint"""
        try:
            with open(excel_path, 'rb') as excel_file, \
                 open(instructions_path, 'r') as instructions_file:
                
                files = {
                    'excel_file': (Path(excel_path).name, excel_file),
                    'analysis_instructions': ('instructions.md', instructions_file)
                }
                data = {
                    'project_prompt': prompt,
                    'analysis_model': 'deepseek/deepseek-chat-v3-0324:free',
                    'generation_model': 'deepseek/deepseek-chat-v3-0324:free'
                }
                
                response = requests.post(
                    f"{self.base_url}/analyze-and-generate",
                    files=files,
                    data=data,
                    timeout=300
                )
                response.raise_for_status()
                
                # Save the zip result
                output_path = Path(excel_path).with_suffix('.zip')
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                self.logger.info(f"Success! Project saved to {output_path}")
                return output_path
                
        except Exception as e:
            self.logger.error(f"API call failed: {str(e)}")
            raise

# Test Client
if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    
    if len(sys.argv) != 4:
        print("Usage: python unified_api_client.py <excel_path> <instructions_path> <prompt>")
        sys.exit(1)
    
    client = UnifiedAPIClient()
    try:
        result = client.analyze_and_generate(sys.argv[1], sys.argv[2], sys.argv[3])
        print(f"Test successful! Output: {result}")
    except Exception as e:
        print(f"Test failed: {str(e)}")

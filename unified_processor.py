"""
Unified Processor for Excel-to-Web Application Generator

This module provides a unified interface that combines Excel analysis,
code generation, and instant deployment into a single pipeline.
"""

import os
import tempfile
import zipfile
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass

from enhanced_excel_analyzer import EnhancedExcelAnalyzer
from modular_code_generator import ModularCodeGenerator, GeneratedFile
from instant_deployer import InstantDeployer, DeploymentInfo

logger = logging.getLogger(__name__)

@dataclass
class ProcessingResult:
    """Result of the unified processing pipeline"""
    success: bool
    deployment_info: Optional[DeploymentInfo]
    analysis_result: Optional[Dict[str, Any]]
    generated_files: List[GeneratedFile]
    error_message: Optional[str]
    processing_time: float

class UnifiedProcessor:
    """Unified processor that handles the complete Excel-to-web pipeline"""
    
    def __init__(self):
        self.excel_analyzer = EnhancedExcelAnalyzer()
        self.code_generator = ModularCodeGenerator()
        self.deployer = InstantDeployer()
        
    def process_excel_to_web(self, excel_file_path: Path, 
                           template_type: str = "streamlit",
                           app_name: Optional[str] = None) -> ProcessingResult:
        """
        Complete pipeline: Excel analysis -> Code generation -> Instant deployment
        """
        import time
        start_time = time.time()
        
        try:
            # Step 1: Analyze Excel file
            logger.info("Step 1: Analyzing Excel file")
            analysis_result = self.excel_analyzer.analyze_excel_file(excel_file_path)
            
            # Step 2: Generate web application code
            logger.info("Step 2: Generating web application code")
            generated_files = self.code_generator.generate_application(
                analysis_result, template_type
            )
            
            # Step 3: Deploy application
            logger.info("Step 3: Deploying application")
            deployment_info = self.deployer.deploy_application(
                generated_files, app_name
            )
            
            processing_time = time.time() - start_time
            
            return ProcessingResult(
                success=True,
                deployment_info=deployment_info,
                analysis_result=analysis_result,
                generated_files=generated_files,
                error_message=None,
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Processing pipeline failed: {str(e)}")
            
            return ProcessingResult(
                success=False,
                deployment_info=None,
                analysis_result=None,
                generated_files=[],
                error_message=str(e),
                processing_time=processing_time
            )
    
    def generate_project_only(self, excel_file_path: Path,
                            template_type: str = "streamlit") -> Dict[str, Any]:
        """
        Generate project files without deployment
        Returns analysis result and generated files
        """
        try:
            # Analyze Excel file
            analysis_result = self.excel_analyzer.analyze_excel_file(excel_file_path)
            
            # Generate web application code
            generated_files = self.code_generator.generate_application(
                analysis_result, template_type
            )
            
            return {
                "success": True,
                "analysis_result": analysis_result,
                "generated_files": [
                    {"path": f.path, "content_preview": f.content[:200] + "..." if len(f.content) > 200 else f.content}
                    for f in generated_files
                ],
                "file_count": len(generated_files),
                "template_type": template_type
            }
            
        except Exception as e:
            logger.error(f"Project generation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def deploy_existing_project(self, project_zip_path: Path,
                              app_name: Optional[str] = None) -> DeploymentInfo:
        """
        Deploy an existing project from a ZIP file
        """
        try:
            # Extract project files from ZIP
            project_files = self._extract_project_files(project_zip_path)
            
            # Deploy application
            deployment_info = self.deployer.deploy_application(project_files, app_name)
            
            return deployment_info
            
        except Exception as e:
            logger.error(f"Deployment from ZIP failed: {str(e)}")
            raise RuntimeError(f"Failed to deploy project: {str(e)}")
    
    def _extract_project_files(self, zip_path: Path) -> List[GeneratedFile]:
        """Extract project files from ZIP"""
        project_files = []
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract ZIP
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Walk through extracted files
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # Calculate relative path
                    rel_path = os.path.relpath(file_path, temp_dir)
                    
                    # Read file content
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    project_files.append(GeneratedFile(rel_path, content))
        
        return project_files
    
    def get_deployment_status(self, deployment_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a deployment"""
        return self.deployer.get_deployment_status(deployment_id)
    
    def list_deployments(self) -> List[Dict[str, Any]]:
        """List all active deployments"""
        return self.deployer.list_deployments()
    
    def undeploy_application(self, deployment_id: str) -> bool:
        """Undeploy an application"""
        return self.deployer.undeploy_application(deployment_id)
    
    def get_application_logs(self, deployment_id: str, lines: int = 100) -> Optional[str]:
        """Get application logs"""
        return self.deployer.get_application_logs(deployment_id, lines)
    
    def cleanup_all_deployments(self):
        """Clean up all deployments"""
        self.deployer.cleanup_all()
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information and health"""
        return {
            "system": "Excel-to-Web Unified Processor",
            "status": "operational",
            "active_deployments": len(self.deployer.active_deployments),
            "components": {
                "excel_analyzer": "ready",
                "code_generator": "ready",
                "deployer": "ready" if self.deployer.docker_client else "unavailable"
            },
            "supported_templates": ["streamlit", "fastapi"],
            "max_file_size": "10MB",
            "supported_formats": [".xlsx", ".xls", ".xlsm"]
        }
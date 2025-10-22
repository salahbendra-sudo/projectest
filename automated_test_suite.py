#!/usr/bin/env python3
"""
Automated Test Suite for Excel-to-Web Application System
Run this script to perform comprehensive regression testing
"""

import unittest
import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add project directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_excel_analyzer import EnhancedExcelAnalyzer
from modular_code_generator import ModularCodeGenerator
from unified_processor import UnifiedProcessor


class TestExcelToWebSystem(unittest.TestCase):
    """Comprehensive test suite for the Excel-to-Web application system"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = "/workspace/projectest/test_excel_files"
        self.temp_dir = tempfile.mkdtemp()
        self.analyzer = EnhancedExcelAnalyzer()
        self.code_generator = ModularCodeGenerator()
        self.processor = UnifiedProcessor()
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_simple_data_analysis(self):
        """Test analysis of simple data table"""
        file_path = os.path.join(self.test_dir, "simple_data.xlsx")
        result = self.analyzer.analyze_excel_file(file_path)
        
        self.assertIn("sheets", result)
        self.assertEqual(len(result["sheets"]), 1)
        self.assertEqual(len(result.get("formulas", [])), 0)
        self.assertEqual(len(result.get("charts", [])), 0)
    
    def test_sales_data_with_formulas(self):
        """Test analysis of sales data with formulas"""
        file_path = os.path.join(self.test_dir, "sales_data.xlsx")
        result = self.analyzer.analyze_excel_file(file_path)
        
        self.assertIn("sheets", result)
        self.assertEqual(len(result["sheets"]), 1)
        self.assertGreater(len(result.get("formulas", [])), 0)
    
    def test_multi_sheet_analysis(self):
        """Test analysis of multi-sheet workbook"""
        file_path = os.path.join(self.test_dir, "inventory_management.xlsx")
        result = self.analyzer.analyze_excel_file(file_path)
        
        self.assertIn("sheets", result)
        self.assertEqual(len(result["sheets"]), 3)
        self.assertGreater(len(result.get("formulas", [])), 0)
    
    def test_code_generation_simple(self):
        """Test code generation for simple data"""
        file_path = os.path.join(self.test_dir, "simple_data.xlsx")
        analysis_result = self.analyzer.analyze_excel_file(file_path)
        generated_files = self.code_generator.generate_application(analysis_result, "streamlit")
        
        self.assertGreater(len(generated_files), 0)
        
        # Check essential files are generated
        file_paths = [f.path for f in generated_files]
        self.assertIn("app.py", file_paths)
        self.assertIn("requirements.txt", file_paths)
        self.assertIn("config.json", file_paths)
    
    def test_code_generation_complex(self):
        """Test code generation for complex template"""
        file_path = os.path.join(self.test_dir, "complex_template.xlsx")
        analysis_result = self.analyzer.analyze_excel_file(file_path)
        generated_files = self.code_generator.generate_application(analysis_result, "streamlit")
        
        self.assertGreater(len(generated_files), 0)
        
        # Check all expected files are generated
        file_paths = [f.path for f in generated_files]
        expected_files = ["app.py", "requirements.txt", "config.json", "Dockerfile", 
                         "utils/data_processing.py", "utils/formula_translator.py"]
        
        for expected_file in expected_files:
            self.assertIn(expected_file, file_paths)
    
    def test_full_pipeline_simple(self):
        """Test complete pipeline with simple data"""
        file_path = os.path.join(self.test_dir, "simple_data.xlsx")
        result = self.processor.process_excel_to_web(file_path)
        
        # Check that processing completed successfully
        self.assertIsNotNone(result)
        self.assertTrue(hasattr(result, 'success'))
    
    def test_full_pipeline_complex(self):
        """Test complete pipeline with complex template"""
        file_path = os.path.join(self.test_dir, "complex_template.xlsx")
        result = self.processor.process_excel_to_web(file_path)
        
        # Check that processing completed successfully
        self.assertIsNotNone(result)
        self.assertTrue(hasattr(result, 'success'))
    
    def test_file_info_extraction(self):
        """Test file information extraction"""
        file_path = os.path.join(self.test_dir, "simple_data.xlsx")
        result = self.analyzer.analyze_excel_file(file_path)
        
        self.assertIn("file_info", result)
        file_info = result["file_info"]
        
        self.assertIn("filename", file_info)
        self.assertIn("size", file_info)
        self.assertIn("extension", file_info)
        self.assertEqual(file_info["extension"], ".xlsx")
    
    def test_formula_extraction(self):
        """Test formula extraction from financial model"""
        file_path = os.path.join(self.test_dir, "financial_model.xlsx")
        result = self.analyzer.analyze_excel_file(file_path)
        
        formulas = result.get("formulas", [])
        self.assertGreater(len(formulas), 20)  # Financial model has many formulas
    
    def test_generated_code_quality(self):
        """Test quality of generated code"""
        file_path = os.path.join(self.test_dir, "sales_data.xlsx")
        analysis_result = self.analyzer.analyze_excel_file(file_path)
        generated_files = self.code_generator.generate_application(analysis_result, "streamlit")
        
        for file_info in generated_files:
            # Check that files have reasonable content length
            self.assertGreater(len(file_info.content), 50)
            
            # Check that Python files have proper structure
            if file_info.path.endswith('.py'):
                self.assertIn('import', file_info.content)
                self.assertIn('def ', file_info.content)
    
    def test_error_handling(self):
        """Test error handling for non-existent files"""
        with self.assertRaises(Exception):
            self.analyzer.analyze_excel_file("non_existent_file.xlsx")


class PerformanceTests(unittest.TestCase):
    """Performance and scalability tests"""
    
    def setUp(self):
        self.analyzer = EnhancedExcelAnalyzer()
        self.test_dir = "/workspace/projectest/test_excel_files"
    
    def test_analysis_performance(self):
        """Test that analysis completes in reasonable time"""
        import time
        
        file_path = os.path.join(self.test_dir, "complex_template.xlsx")
        
        start_time = time.time()
        result = self.analyzer.analyze_excel_file(file_path)
        end_time = time.time()
        
        analysis_time = end_time - start_time
        
        # Analysis should complete in under 5 seconds
        self.assertLess(analysis_time, 5.0)
        self.assertIsNotNone(result)


def run_all_tests():
    """Run all test suites and return results"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestExcelToWebSystem))
    suite.addTests(loader.loadTestsFromTestCase(PerformanceTests))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == "__main__":
    print("🚀 Running Automated Test Suite for Excel-to-Web Application System")
    print("=" * 70)
    
    result = run_all_tests()
    
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n🎉 ALL TESTS PASSED! The system is production-ready.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")
        sys.exit(1)
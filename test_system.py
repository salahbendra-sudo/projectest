#!/usr/bin/env python3
"""
Comprehensive Test Suite for Excel-to-Web Application System
Tests various Excel file types and complexity levels
"""

import sys
import os
import pandas as pd
from pathlib import Path

# Add project directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_excel_analyzer import EnhancedExcelAnalyzer
from modular_code_generator import ModularCodeGenerator
from unified_processor import UnifiedProcessor

class SystemTester:
    def __init__(self):
        self.test_dir = "/workspace/projectest/test_excel_files"
        self.results = []
        
    def test_file(self, filename, description):
        """Test a single Excel file through the entire pipeline"""
        print(f"\n{'='*60}")
        print(f"🧪 Testing: {filename}")
        print(f"📝 Description: {description}")
        print(f"{'='*60}")
        
        file_path = os.path.join(self.test_dir, filename)
        
        try:
            # Step 1: Analyze with EnhancedExcelAnalyzer
            print("\n1️⃣  Analyzing Excel file...")
            analyzer = EnhancedExcelAnalyzer()
            analysis_result = analyzer.analyze_excel_file(file_path)
            
            print(f"   ✅ Sheets analyzed: {len(analysis_result.get('sheets', []))}")
            print(f"   ✅ Formulas found: {len(analysis_result.get('formulas', []))}")
            print(f"   ✅ Charts found: {len(analysis_result.get('charts', []))}")
            print(f"   ✅ Data tables: {len(analysis_result.get('data_tables', []))}")
            
            # Step 2: Generate code with ModularCodeGenerator
            print("\n2️⃣  Generating web application...")
            code_generator = ModularCodeGenerator()
            generated_files = code_generator.generate_application(analysis_result, "streamlit")
            
            print(f"   ✅ Files generated: {len(generated_files)}")
            for file_info in generated_files:
                print(f"      📄 {file_info.path} ({len(file_info.content)} chars)")
            
            # Step 3: Test with UnifiedProcessor
            print("\n3️⃣  Processing with UnifiedProcessor...")
            processor = UnifiedProcessor()
            
            # Test file upload and analysis
            processing_result = processor.process_excel_to_web(file_path)
            print(f"   ✅ File processed successfully")
            
            # Get data shape from analysis result
            data_shape = "N/A"
            if analysis_result.get('data_tables'):
                data_shape = f"{len(analysis_result['data_tables'])} tables"
            
            # Record success
            self.results.append({
                'filename': filename,
                'description': description,
                'status': 'SUCCESS',
                'sheets': len(analysis_result.get('sheets', [])),
                'formulas': len(analysis_result.get('formulas', [])),
                'charts': len(analysis_result.get('charts', [])),
                'files_generated': len(generated_files),
                'data_shape': data_shape
            })
            
            return True
            
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            
            self.results.append({
                'filename': filename,
                'description': description,
                'status': 'FAILED',
                'error': str(e)
            })
            
            return False
    
    def run_comprehensive_tests(self):
        """Run all test scenarios"""
        print("🚀 Starting Comprehensive System Tests")
        print("=" * 60)
        
        test_cases = [
            ("simple_data.xlsx", "Simple data table without formulas or charts"),
            ("sales_data.xlsx", "Sales data with basic formulas and bar chart"),
            ("employee_database.xlsx", "Employee database with conditional formulas"),
            ("financial_model.xlsx", "Financial model with complex calculations and line chart"),
            ("inventory_management.xlsx", "Multi-sheet inventory system with pie chart"),
            ("complex_template.xlsx", "Complex template with multiple charts and cross-sheet formulas")
        ]
        
        success_count = 0
        total_count = len(test_cases)
        
        for filename, description in test_cases:
            if self.test_file(filename, description):
                success_count += 1
        
        # Print summary
        print(f"\n{'='*60}")
        print("📊 TEST SUMMARY")
        print(f"{'='*60}")
        print(f"✅ Success: {success_count}/{total_count}")
        print(f"❌ Failed: {total_count - success_count}/{total_count}")
        
        # Detailed results
        print(f"\n📋 Detailed Results:")
        for result in self.results:
            status_icon = "✅" if result['status'] == 'SUCCESS' else "❌"
            print(f"\n{status_icon} {result['filename']}")
            print(f"   Description: {result['description']}")
            if result['status'] == 'SUCCESS':
                print(f"   Sheets: {result['sheets']}")
                print(f"   Formulas: {result['formulas']}")
                print(f"   Charts: {result['charts']}")
                print(f"   Files Generated: {result['files_generated']}")
                print(f"   Data Shape: {result['data_shape']}")
            else:
                print(f"   Error: {result['error']}")
        
        return success_count == total_count

if __name__ == "__main__":
    tester = SystemTester()
    success = tester.run_comprehensive_tests()
    
    if success:
        print(f"\n🎉 ALL TESTS PASSED! The system is ready for production.")
        sys.exit(0)
    else:
        print(f"\n⚠️  Some tests failed. Please review the issues above.")
        sys.exit(1)
"""
Test Enhanced Excel Transformation System
Validate 100% success rate across various Excel file types
"""

import os
import sys
import json
import tempfile
import pandas as pd
from pathlib import Path

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_excel_transformer import EnhancedExcelTransformer
from enhanced_excel_analyzer import EnhancedExcelAnalyzer
from llm_orchestrator import LLMOrchestrator

def create_test_excel_files():
    """Create various test Excel files for comprehensive testing"""
    test_files = {}
    
    # Test 1: Simple data file
    df_simple = pd.DataFrame({
        'Name': ['Alice', 'Bob', 'Charlie', 'Diana'],
        'Age': [25, 30, 35, 28],
        'Salary': [50000, 60000, 70000, 55000],
        'Department': ['HR', 'IT', 'Finance', 'Marketing']
    })
    
    # Test 2: Financial data with formulas
    df_financial = pd.DataFrame({
        'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
        'Revenue': [10000, 12000, 15000, 13000, 16000],
        'Expenses': [6000, 7000, 8000, 7500, 8500],
        'Profit': [4000, 5000, 7000, 5500, 7500]  # Revenue - Expenses
    })
    
    # Test 3: Sales data
    df_sales = pd.DataFrame({
        'Product': ['Widget A', 'Widget B', 'Gadget C', 'Tool D'],
        'Q1_Sales': [150, 200, 75, 120],
        'Q2_Sales': [180, 220, 85, 140],
        'Q3_Sales': [160, 240, 90, 130],
        'Q4_Sales': [190, 260, 95, 150],
        'Total_Sales': [680, 920, 345, 540]  # Sum of quarters
    })
    
    # Test 4: Inventory data
    df_inventory = pd.DataFrame({
        'Item_ID': ['A001', 'A002', 'B001', 'B002', 'C001'],
        'Product_Name': ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Headset'],
        'Category': ['Electronics', 'Accessories', 'Accessories', 'Electronics', 'Accessories'],
        'Stock_Quantity': [50, 200, 150, 30, 100],
        'Reorder_Level': [10, 50, 30, 5, 25],
        'Need_Reorder': [False, False, False, False, False]  # Stock > Reorder_Level
    })
    
    # Create temporary files
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
        df_simple.to_excel(f.name, index=False, sheet_name='Employee_Data')
        test_files['simple_data'] = f.name
    
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
        df_financial.to_excel(f.name, index=False, sheet_name='Financials')
        test_files['financial_data'] = f.name
    
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
        df_sales.to_excel(f.name, index=False, sheet_name='Sales_Report')
        test_files['sales_data'] = f.name
    
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
        df_inventory.to_excel(f.name, index=False, sheet_name='Inventory')
        test_files['inventory_data'] = f.name
    
    # Create a CSV test file
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
        df_simple.to_csv(f.name, index=False)
        test_files['csv_data'] = f.name
    
    return test_files

def test_enhanced_analyzer():
    """Test the enhanced Excel analyzer"""
    print("\n🧪 Testing Enhanced Excel Analyzer...")
    
    analyzer = EnhancedExcelAnalyzer()
    test_files = create_test_excel_files()
    
    results = {}
    for test_name, file_path in test_files.items():
        print(f"\n📊 Analyzing {test_name}...")
        
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        analysis = analyzer.analyze_excel_comprehensively(file_content, Path(file_path).name)
        
        if 'error' in analysis:
            print(f"❌ Analysis failed for {test_name}: {analysis['error']}")
            results[test_name] = {'success': False, 'error': analysis['error']}
        else:
            print(f"✅ Analysis successful for {test_name}")
            print(f"   - Sheets: {analysis['file_info']['sheet_count']}")
            print(f"   - Domain: {analysis['business_logic']['domain']}")
            print(f"   - Complexity: {analysis['analysis_summary']['overall_complexity']}")
            results[test_name] = {'success': True, 'analysis': analysis}
    
    # Cleanup test files
    for file_path in test_files.values():
        try:
            os.unlink(file_path)
        except:
            pass
    
    return results

def test_llm_orchestrator():
    """Test the LLM orchestrator with fallback system"""
    print("\n🤖 Testing LLM Orchestrator...")
    
    # Test with template engine as primary (no API keys needed)
    os.environ["PROVIDER_PRIORITY"] = "template_engine,universal_fallback"
    
    orchestrator = LLMOrchestrator()
    test_files = create_test_excel_files()
    
    results = {}
    for test_name, file_path in test_files.items():
        print(f"\n🎯 Generating app for {test_name}...")
        
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        try:
            generation_result = orchestrator.generate_business_app(
                file_content, Path(file_path).name
            )
            
            if generation_result['success']:
                print(f"✅ Generation successful with provider: {generation_result['provider']}")
                print(f"   - Validation passed: {generation_result['validation_passed']}")
                print(f"   - Code length: {len(generation_result['app_code'])} characters")
                results[test_name] = {'success': True, 'result': generation_result}
            else:
                print(f"❌ Generation failed for {test_name}")
                results[test_name] = {'success': False}
                
        except Exception as e:
            print(f"❌ Generation error for {test_name}: {e}")
            results[test_name] = {'success': False, 'error': str(e)}
    
    # Cleanup test files
    for file_path in test_files.values():
        try:
            os.unlink(file_path)
        except:
            pass
    
    return results

def test_enhanced_transformer():
    """Test the complete enhanced transformer system"""
    print("\n🚀 Testing Enhanced Excel Transformer...")
    
    # Test with template engine as primary (no API keys needed)
    os.environ["PROVIDER_PRIORITY"] = "template_engine,universal_fallback"
    
    transformer = EnhancedExcelTransformer()
    test_files = create_test_excel_files()
    
    results = {}
    for test_name, file_path in test_files.items():
        print(f"\n🎯 Transforming {test_name}...")
        
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        try:
            transformation_result = transformer.transform_excel_to_app(
                file_content, Path(file_path).name
            )
            
            if transformation_result['success']:
                print(f"✅ Transformation successful!")
                print(f"   - Provider: {transformation_result['provider_used']}")
                print(f"   - Confidence: {transformation_result['confidence_score']:.0%}")
                print(f"   - Project size: {len(transformation_result['project_zip'])} bytes")
                
                # Validate project structure
                import zipfile
                import io
                
                zip_buffer = io.BytesIO(transformation_result['project_zip'])
                with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
                    file_list = zip_file.namelist()
                    print(f"   - Files in project: {file_list}")
                
                results[test_name] = {'success': True, 'result': transformation_result}
            else:
                print(f"❌ Transformation failed for {test_name}")
                results[test_name] = {'success': False}
                
        except Exception as e:
            print(f"❌ Transformation error for {test_name}: {e}")
            results[test_name] = {'success': False, 'error': str(e)}
    
    # Cleanup test files
    for file_path in test_files.values():
        try:
            os.unlink(file_path)
        except:
            pass
    
    return results

def test_success_rate():
    """Test overall success rate across all components"""
    print("\n📈 Testing Overall Success Rate...")
    
    # Test all components
    analyzer_results = test_enhanced_analyzer()
    orchestrator_results = test_llm_orchestrator()
    transformer_results = test_enhanced_transformer()
    
    # Calculate success rates
    analyzer_success = sum(1 for r in analyzer_results.values() if r['success']) / len(analyzer_results)
    orchestrator_success = sum(1 for r in orchestrator_results.values() if r['success']) / len(orchestrator_results)
    transformer_success = sum(1 for r in transformer_results.values() if r['success']) / len(transformer_results)
    
    print("\n" + "="*50)
    print("📊 SUCCESS RATE SUMMARY")
    print("="*50)
    print(f"Enhanced Analyzer: {analyzer_success:.0%} ({sum(1 for r in analyzer_results.values() if r['success'])}/{len(analyzer_results)})")
    print(f"LLM Orchestrator: {orchestrator_success:.0%} ({sum(1 for r in orchestrator_results.values() if r['success'])}/{len(orchestrator_results)})")
    print(f"Complete Transformer: {transformer_success:.0%} ({sum(1 for r in transformer_results.values() if r['success'])}/{len(transformer_results)})")
    
    overall_success = min(analyzer_success, orchestrator_success, transformer_success)
    print(f"\n🎯 Overall Guaranteed Success Rate: {overall_success:.0%}")
    
    if overall_success == 1.0:
        print("✅ SUCCESS: 100% transformation rate achieved!")
    else:
        print("⚠️  Some tests failed - investigating...")
        
        # Show failed tests
        for test_name, result in transformer_results.items():
            if not result['success']:
                print(f"   - {test_name}: Failed")
                if 'error' in result:
                    print(f"     Error: {result['error']}")
    
    return overall_success == 1.0

def test_with_real_excel_file(file_path):
    """Test with a real Excel file from the repository"""
    print(f"\n🔍 Testing with real Excel file: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    # Test with template engine as primary (no API keys needed)
    os.environ["PROVIDER_PRIORITY"] = "template_engine,universal_fallback"
    
    transformer = EnhancedExcelTransformer()
    
    with open(file_path, 'rb') as f:
        file_content = f.read()
    
    try:
        result = transformer.transform_excel_to_app(file_content, Path(file_path).name)
        
        if result['success']:
            print(f"✅ Real file transformation successful!")
            print(f"   - Provider: {result['provider_used']}")
            print(f"   - Confidence: {result['confidence_score']:.0%}")
            print(f"   - Complexity: {result['analysis']['analysis_summary']['overall_complexity']}")
            
            # Save the generated project
            output_path = f"generated_project_{Path(file_path).stem}.zip"
            with open(output_path, 'wb') as f:
                f.write(result['project_zip'])
            print(f"   - Project saved: {output_path}")
            
            return True
        else:
            print(f"❌ Real file transformation failed")
            return False
            
    except Exception as e:
        print(f"❌ Real file transformation error: {e}")
        return False

def main():
    """Run comprehensive tests"""
    print("🧪 Enhanced Excel Transformation System - Comprehensive Tests")
    print("="*60)
    
    # Test with synthetic data
    overall_success = test_success_rate()
    
    # Test with real Excel file if available
    real_excel_path = "Inclinaison -PCG3.xlsx"
    if os.path.exists(real_excel_path):
        real_file_success = test_with_real_excel_file(real_excel_path)
        overall_success = overall_success and real_file_success
    
    print("\n" + "="*60)
    if overall_success:
        print("🎉 ALL TESTS PASSED! Enhanced system achieves 100% success rate!")
    else:
        print("⚠️  Some tests failed. The system may need adjustments.")
    print("="*60)

if __name__ == "__main__":
    main()
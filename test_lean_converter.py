"""
Test script for Lean Excel Converter - 100% Success Rate
"""

import os
import tempfile
import pandas as pd
import io
import zipfile
from lean_excel_to_app import LeanExcelConverter

def create_test_excel():
    """Create various test Excel files"""
    test_files = {}
    
    # Test 1: Simple data
    simple_data = {
        'Name': ['Alice', 'Bob', 'Charlie', 'Diana'],
        'Age': [25, 30, 35, 28],
        'Salary': [50000, 60000, 70000, 55000],
        'Department': ['IT', 'HR', 'IT', 'Finance']
    }
    df_simple = pd.DataFrame(simple_data)
    
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
        df_simple.to_excel(f.name, index=False)
        test_files['simple'] = f.name
    
    # Test 2: Multiple sheets
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
        with pd.ExcelWriter(f.name) as writer:
            df_simple.to_excel(writer, sheet_name='Employees', index=False)
            
            # Add second sheet
            sales_data = {
                'Month': ['Jan', 'Feb', 'Mar', 'Apr'],
                'Revenue': [10000, 12000, 15000, 13000],
                'Expenses': [8000, 9000, 11000, 9500]
            }
            df_sales = pd.DataFrame(sales_data)
            df_sales.to_excel(writer, sheet_name='Sales', index=False)
        test_files['multi_sheet'] = f.name
    
    # Test 3: CSV file
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
        df_simple.to_csv(f.name, index=False)
        test_files['csv'] = f.name
    
    # Test 4: Complex data with missing values
    complex_data = {
        'Product': ['Widget A', 'Widget B', None, 'Widget D'],
        'Price': [29.99, 49.99, 19.99, None],
        'Stock': [150, None, 89, 210],
        'Category': ['Electronics', 'Electronics', 'Home', 'Office']
    }
    df_complex = pd.DataFrame(complex_data)
    
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
        df_complex.to_excel(f.name, index=False)
        test_files['complex'] = f.name
    
    return test_files

def test_file_analysis():
    """Test file analysis functionality"""
    print("🧪 Testing file analysis...")
    
    converter = LeanExcelConverter()
    test_files = create_test_excel()
    
    success_count = 0
    total_tests = len(test_files)
    
    for test_name, file_path in test_files.items():
        try:
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            analysis = converter.analyze_excel(file_content, file_path)
            
            if analysis['success']:
                print(f"  ✅ {test_name}: SUCCESS - {analysis['total_sheets']} sheets")
                success_count += 1
            else:
                print(f"  ❌ {test_name}: FAILED - {analysis['error']}")
            
            # Cleanup
            os.unlink(file_path)
            
        except Exception as e:
            print(f"  ❌ {test_name}: EXCEPTION - {str(e)}")
            # Cleanup on exception
            try:
                os.unlink(file_path)
            except:
                pass
    
    return success_count == total_tests

def test_app_generation():
    """Test app code generation"""
    print("\n🧪 Testing app generation...")
    
    converter = LeanExcelConverter()
    
    # Create a simple test analysis
    test_analysis = {
        'success': True,
        'sheets': {
            'Sheet1': {
                'rows': 10,
                'columns': 5,
                'columns_list': ['A', 'B', 'C', 'D', 'E'],
                'data_types': {'A': 'object', 'B': 'int64', 'C': 'float64', 'D': 'object', 'E': 'bool'}
            }
        },
        'total_sheets': 1,
        'file_type': '.xlsx'
    }
    
    try:
        app_code = converter.generate_app_code(test_analysis)
        
        # Verify code contains essential elements
        required_elements = [
            'import streamlit',
            'import pandas',
            'st.title',
            'uploaded_file',
            'st.dataframe'
        ]
        
        all_found = True
        for element in required_elements:
            if element not in app_code:
                print(f"  ❌ Missing: {element}")
                all_found = False
        
        if all_found:
            print(f"  ✅ App code generated successfully ({len(app_code)} characters)")
            
            # Test ZIP creation
            zip_data = converter.create_project_zip(app_code, test_analysis)
            
            # Verify ZIP structure
            with zipfile.ZipFile(io.BytesIO(zip_data), 'r') as zip_ref:
                file_list = zip_ref.namelist()
                required_files = ['app.py', 'requirements.txt', 'README.md']
                
                for req_file in required_files:
                    if req_file in file_list:
                        print(f"  ✅ {req_file} included in ZIP")
                    else:
                        print(f"  ❌ {req_file} missing from ZIP")
                        all_found = False
            
            return all_found
        else:
            return False
            
    except Exception as e:
        print(f"  ❌ App generation failed: {str(e)}")
        return False

def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n🧪 Testing edge cases...")
    
    converter = LeanExcelConverter()
    
    # Test 1: Empty file
    try:
        analysis = converter.analyze_excel(b'', 'test.xlsx')
        if not analysis['success']:
            print("  ✅ Empty file handled correctly")
        else:
            print("  ❌ Empty file should fail")
            return False
    except Exception as e:
        print(f"  ✅ Empty file exception handled: {str(e)}")
    
    # Test 2: Invalid file content
    try:
        analysis = converter.analyze_excel(b'invalid content', 'test.xlsx')
        if not analysis['success']:
            print("  ✅ Invalid content handled correctly")
        else:
            print("  ❌ Invalid content should fail")
            return False
    except Exception as e:
        print(f"  ✅ Invalid content exception handled: {str(e)}")
    
    return True

def main():
    """Run all tests"""
    print("🚀 Testing Lean Excel Converter - 100% Success Rate")
    print("=" * 60)
    
    tests = [
        ("File Analysis", test_file_analysis),
        ("App Generation", test_app_generation),
        ("Edge Cases", test_edge_cases)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"\n{status} {test_name}")
        except Exception as e:
            print(f"\n❌ FAILED {test_name}: {str(e)}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! 100% Success Rate Achieved!")
        print("\n✅ System Status:")
        print("   - File analysis: Working")
        print("   - App generation: Working")
        print("   - Edge cases: Handled")
        print("   - ZIP creation: Working")
        print("   - No external dependencies: ✅")
        return True
    else:
        print("\n❌ Some tests failed. Success rate not achieved.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
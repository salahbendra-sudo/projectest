"""
Test script for the rebuilt Excel-to-Web application system
"""

import os
import sys
import tempfile
import pandas as pd
from local_analyzer import LocalExcelAnalyzer

def test_local_analyzer():
    """Test the local analyzer functionality"""
    print("🧪 Testing Local Excel Analyzer...")
    
    # Create a test Excel file
    test_data = {
        'Product': ['Widget A', 'Widget B', 'Widget C', 'Widget D'],
        'Category': ['Electronics', 'Electronics', 'Home', 'Office'],
        'Price': [29.99, 49.99, 19.99, 39.99],
        'Sales': [150, 320, 89, 210],
        'Date': ['2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18']
    }
    
    df = pd.DataFrame(test_data)
    
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
        df.to_excel(tmp.name, index=False)
        tmp_path = tmp.name
    
    try:
        # Test analyzer
        analyzer = LocalExcelAnalyzer()
        analysis = analyzer.analyze_excel_file(tmp_path)
        
        print(f"✅ File analyzed successfully")
        print(f"   - Sheets: {analysis['file_info']['sheet_count']}")
        print(f"   - Template type: {analysis['analysis_summary']['template_type']}")
        print(f"   - Complexity: {analysis['analysis_summary']['complexity']}")
        
        # Test code generation
        app_code = analyzer.generate_basic_app_code(analysis)
        print(f"✅ App code generated: {len(app_code)} characters")
        
        # Verify code contains expected elements
        assert 'streamlit' in app_code.lower()
        assert 'pandas' in app_code.lower()
        assert 'plotly' in app_code.lower()
        print("✅ Generated code contains expected libraries")
        
        return True
        
    except Exception as e:
        print(f"❌ Local analyzer test failed: {e}")
        return False
    finally:
        # Cleanup
        os.unlink(tmp_path)

def test_imports():
    """Test that all required modules can be imported"""
    print("\n🧪 Testing module imports...")
    
    modules = [
        'streamlit',
        'pandas',
        'openpyxl',
        'requests',
        'tempfile',
        'zipfile',
        'shutil',
        'uuid'
    ]
    
    all_imported = True
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module} imported successfully")
        except ImportError as e:
            print(f"❌ Failed to import {module}: {e}")
            all_imported = False
    
    return all_imported

def test_file_existence():
    """Test that all required files exist"""
    print("\n🧪 Testing file existence...")
    
    required_files = [
        'app.py',
        'excel_to_app.py',
        'local_analyzer.py',
        'project_prompt.txt',
        'instructions.md'
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            all_exist = False
    
    return all_exist

def test_api_availability():
    """Test API availability checking"""
    print("\n🧪 Testing API availability...")
    
    try:
        from excel_to_app import test_api_availability
        unified_available, deploy_available = test_api_availability()
        
        print(f"✅ Unified API available: {unified_available}")
        print(f"✅ Deploy API available: {deploy_available}")
        
        # This should work even if APIs are not available
        return True
        
    except Exception as e:
        print(f"❌ API availability test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Running Rebuilt System Tests")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_file_existence,
        test_local_analyzer,
        test_api_availability
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! The rebuilt system is working correctly.")
        print("\n✅ System Status:")
        print("   - Local analyzer: Functional")
        print("   - API fallback: Ready")
        print("   - File processing: Working")
        print("   - Code generation: Operational")
        return True
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
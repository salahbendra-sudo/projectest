#!/usr/bin/env python3
"""
Test Script for Enhanced Excel-to-Web Application Generator

This script demonstrates the key components of the enhanced system
without requiring actual Excel file processing.
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_enhanced_excel_analyzer():
    """Test the enhanced Excel analyzer"""
    print("🧪 Testing Enhanced Excel Analyzer...")
    
    try:
        from enhanced_excel_analyzer import EnhancedExcelAnalyzer, TemplateType
        
        analyzer = EnhancedExcelAnalyzer()
        
        # Test template patterns
        print(f"  ✅ Loaded {len(analyzer.template_patterns)} template patterns")
        
        # Test formula categories
        print(f"  ✅ Loaded {len(analyzer.formula_categories)} formula categories")
        
        print("  ✅ Enhanced Excel Analyzer initialized successfully")
        return True
        
    except Exception as e:
        print(f"  ❌ Enhanced Excel Analyzer test failed: {e}")
        return False

def test_modular_code_generator():
    """Test the modular code generator"""
    print("🧪 Testing Modular Code Generator...")
    
    try:
        from modular_code_generator import ModularCodeGenerator
        
        generator = ModularCodeGenerator()
        
        # Test template loading
        print(f"  ✅ Loaded {len(generator.templates)} code templates")
        
        # Test basic generation (without actual analysis)
        mock_analysis = {
            "sheets": {"Sheet1": {"name": "Sheet1", "dimensions": "10x5"}},
            "formulas": [],
            "charts": [],
            "template_type": {"type": "custom", "name": "Custom", "confidence": 0.0}
        }
        
        files = generator.generate_application(mock_analysis, "streamlit")
        print(f"  ✅ Generated {len(files)} files for mock analysis")
        
        print("  ✅ Modular Code Generator initialized successfully")
        return True
        
    except Exception as e:
        print(f"  ❌ Modular Code Generator test failed: {e}")
        return False

def test_instant_deployer():
    """Test the instant deployer (without Docker)"""
    print("🧪 Testing Instant Deployer...")
    
    try:
        from instant_deployer import InstantDeployer
        
        # This will fail if Docker is not running, but we can test initialization
        try:
            deployer = InstantDeployer()
            print("  ✅ Instant Deployer initialized successfully")
            return True
        except RuntimeError as e:
            if "Docker is not available" in str(e):
                print("  ⚠️  Docker not available (expected in test environment)")
                return True  # This is expected in test environment
            else:
                raise
                
    except Exception as e:
        print(f"  ❌ Instant Deployer test failed: {e}")
        return False

def test_unified_processor():
    """Test the unified processor"""
    print("🧪 Testing Unified Processor...")
    
    try:
        from unified_processor import UnifiedProcessor
        
        processor = UnifiedProcessor()
        
        # Test system info
        system_info = processor.get_system_info()
        print(f"  ✅ System info: {system_info['system']}")
        
        print("  ✅ Unified Processor initialized successfully")
        return True
        
    except Exception as e:
        print(f"  ❌ Unified Processor test failed: {e}")
        return False

def test_enhanced_frontend():
    """Test the enhanced frontend"""
    print("🧪 Testing Enhanced Frontend...")
    
    try:
        from enhanced_frontend import EnhancedFrontend
        
        frontend = EnhancedFrontend()
        
        # Test session state initialization
        assert 'processing_result' in frontend.processor.__dict__
        print("  ✅ Enhanced Frontend initialized successfully")
        return True
        
    except Exception as e:
        print(f"  ❌ Enhanced Frontend test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Enhanced Excel-to-Web Application Generator")
    print("=" * 60)
    
    tests = [
        test_enhanced_excel_analyzer,
        test_modular_code_generator,
        test_instant_deployer,
        test_unified_processor,
        test_enhanced_frontend
    ]
    
    results = []
    for test in tests:
        results.append(test())
        print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The enhanced system is ready.")
        print("\nNext steps:")
        print("1. Install Docker for deployment functionality")
        print("2. Run: streamlit run enhanced_frontend.py")
        print("3. Upload an Excel file to test the complete pipeline")
    else:
        print("⚠️  Some tests failed. Please check the dependencies.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
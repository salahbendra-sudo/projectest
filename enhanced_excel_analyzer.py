"""
Enhanced Excel Analyzer for Excel-to-Web Application Generator

This module provides advanced Excel file analysis capabilities including:
- Formula extraction with dependency mapping
- VBA code analysis with security validation
- Template pattern recognition
- Chart and graph configuration extraction
- Business logic preservation
"""

import pandas as pd
import openpyxl
import xlrd
import re
import json
from typing import Dict, List, Set, Tuple, Optional, Any, Union
from pathlib import Path
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class TemplateType(Enum):
    FINANCIAL_MODEL = "financial_model"
    DASHBOARD = "dashboard"
    DATA_ANALYSIS = "data_analysis"
    INVENTORY_MANAGEMENT = "inventory_management"
    PROJECT_PLANNING = "project_planning"
    CUSTOM = "custom"

@dataclass
class FormulaInfo:
    """Enhanced formula information with dependencies"""
    sheet: str
    cell: str
    formula: str
    dependencies: List[str]
    category: str  # financial, statistical, logical, etc.
    complexity: int  # 1-10 scale

@dataclass
class ChartInfo:
    """Chart configuration and data"""
    sheet: str
    name: str
    chart_type: str
    data_range: str
    title: str
    axis_labels: Dict[str, str]

@dataclass
class TemplatePattern:
    """Template detection patterns"""
    name: str
    template_type: TemplateType
    sheet_patterns: List[str]
    column_patterns: Dict[str, List[str]]
    formula_patterns: List[str]

class EnhancedExcelAnalyzer:
    """Advanced Excel file analyzer with template detection and business logic extraction"""
    
    def __init__(self):
        self.template_patterns = self._load_template_patterns()
        self.formula_categories = self._load_formula_categories()
    
    def _load_template_patterns(self) -> List[TemplatePattern]:
        """Load predefined template patterns for detection"""
        return [
            TemplatePattern(
                name="Financial Model",
                template_type=TemplateType.FINANCIAL_MODEL,
                sheet_patterns=["Income Statement", "Balance Sheet", "Cash Flow", "Assumptions"],
                column_patterns={
                    "financial": ["Revenue", "Cost", "Profit", "EBITDA", "Net Income"],
                    "time_periods": ["Q1", "Q2", "Q3", "Q4", "Year"]
                },
                formula_patterns=["SUMIF", "VLOOKUP", "IFERROR", "NPV", "IRR"]
            ),
            TemplatePattern(
                name="Dashboard",
                template_type=TemplateType.DASHBOARD,
                sheet_patterns=["Dashboard", "Summary", "KPIs", "Charts"],
                column_patterns={
                    "metrics": ["KPI", "Metric", "Value", "Target", "Actual"],
                    "time": ["Date", "Month", "Quarter", "Year"]
                },
                formula_patterns=["AVERAGE", "COUNT", "MAX", "MIN", "SUM"]
            ),
            TemplatePattern(
                name="Data Analysis",
                template_type=TemplateType.DATA_ANALYSIS,
                sheet_patterns=["Data", "Analysis", "Results", "Statistics"],
                column_patterns={
                    "analysis": ["Mean", "Median", "Std Dev", "Correlation", "P-Value"],
                    "data": ["Variable", "Value", "Category", "Group"]
                },
                formula_patterns=["CORREL", "STDEV", "AVERAGE", "MEDIAN", "FORECAST"]
            )
        ]
    
    def _load_formula_categories(self) -> Dict[str, List[str]]:
        """Load formula categories for classification"""
        return {
            "financial": ["NPV", "IRR", "PMT", "FV", "PV", "RATE", "DB", "DDB", "SLN", "SYD"],
            "statistical": ["AVERAGE", "MEDIAN", "MODE", "STDEV", "VAR", "CORREL", "FORECAST", "TREND"],
            "logical": ["IF", "AND", "OR", "NOT", "XOR", "IFERROR", "IFNA"],
            "lookup": ["VLOOKUP", "HLOOKUP", "INDEX", "MATCH", "XLOOKUP", "CHOOSE"],
            "text": ["CONCATENATE", "LEFT", "RIGHT", "MID", "LEN", "FIND", "SUBSTITUTE"],
            "date": ["DATE", "NOW", "TODAY", "YEAR", "MONTH", "DAY", "DATEDIF", "NETWORKDAYS"],
            "math": ["SUM", "PRODUCT", "POWER", "SQRT", "LOG", "EXP", "ROUND", "CEILING", "FLOOR"]
        }
    
    def analyze_excel_file(self, file_path: Path) -> Dict[str, Any]:
        """Comprehensive Excel file analysis"""
        try:
            analysis_result = {
                "file_info": {},
                "sheets": {},
                "formulas": [],
                "charts": [],
                "template_type": None,
                "business_logic": {},
                "data_validation": {},
                "security_analysis": {}
            }
            
            # Basic file information
            analysis_result["file_info"] = self._get_file_info(file_path)
            
            # Load workbook
            wb = openpyxl.load_workbook(file_path, data_only=False, read_only=True)
            
            # Analyze each sheet
            for sheet_name in wb.sheetnames:
                ws = wb[sheet_name]
                sheet_analysis = self._analyze_sheet(ws, sheet_name)
                analysis_result["sheets"][sheet_name] = sheet_analysis
                
                # Extract formulas
                sheet_formulas = self._extract_formulas_from_sheet(ws, sheet_name)
                analysis_result["formulas"].extend(sheet_formulas)
                
                # Extract charts
                sheet_charts = self._extract_charts_from_sheet(ws, sheet_name)
                analysis_result["charts"].extend(sheet_charts)
            
            # Template detection
            analysis_result["template_type"] = self._detect_template(analysis_result)
            
            # Business logic extraction
            analysis_result["business_logic"] = self._extract_business_logic(analysis_result)
            
            # Security analysis
            analysis_result["security_analysis"] = self._analyze_security(file_path)
            
            wb.close()
            return analysis_result
            
        except Exception as e:
            logger.error(f"Excel analysis failed: {str(e)}")
            raise
    
    def _get_file_info(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Get basic file information"""
        path = Path(file_path)
        return {
            "filename": path.name,
            "size": path.stat().st_size,
            "extension": path.suffix.lower(),
            "modified_time": path.stat().st_mtime
        }
    
    def _analyze_sheet(self, worksheet, sheet_name: str) -> Dict[str, Any]:
        """Analyze individual worksheet"""
        sheet_data = {
            "name": sheet_name,
            "dimensions": f"{worksheet.max_row}x{worksheet.max_column}",
            "data_types": {},
            "formula_count": 0,
            "chart_count": 0,
            "data_validation_rules": []
        }
        
        # Analyze data types and content
        data_sample = {}
        for row in worksheet.iter_rows(min_row=1, max_row=min(10, worksheet.max_row)):
            for cell in row:
                if cell.value is not None:
                    cell_type = type(cell.value).__name__
                    data_sample[cell.coordinate] = {
                        "value": str(cell.value)[:100],  # Truncate long values
                        "type": cell_type
                    }
        
        sheet_data["data_sample"] = data_sample
        
        # Count formulas
        formula_count = 0
        for row in worksheet.iter_rows():
            for cell in row:
                if cell.data_type == 'f':
                    formula_count += 1
        
        sheet_data["formula_count"] = formula_count
        
        return sheet_data
    
    def _extract_formulas_from_sheet(self, worksheet, sheet_name: str) -> List[FormulaInfo]:
        """Extract formulas with enhanced analysis"""
        formulas = []
        
        for row in worksheet.iter_rows():
            for cell in row:
                if cell.data_type == 'f':
                    formula_text = str(cell.value)
                    if not formula_text.startswith('='):
                        formula_text = f"={formula_text}"
                    
                    # Extract dependencies
                    dependencies = self._extract_formula_dependencies(formula_text)
                    
                    # Categorize formula
                    category = self._categorize_formula(formula_text)
                    
                    # Calculate complexity
                    complexity = self._calculate_formula_complexity(formula_text)
                    
                    formula_info = FormulaInfo(
                        sheet=sheet_name,
                        cell=cell.coordinate,
                        formula=formula_text,
                        dependencies=dependencies,
                        category=category,
                        complexity=complexity
                    )
                    formulas.append(formula_info)
        
        return formulas
    
    def _extract_formula_dependencies(self, formula: str) -> List[str]:
        """Extract cell references from formula"""
        # Pattern for cell references (A1, B2, etc.)
        cell_pattern = re.compile(r'[A-Z]{1,3}\d{1,7}')
        return cell_pattern.findall(formula)
    
    def _categorize_formula(self, formula: str) -> str:
        """Categorize formula based on function types"""
        formula_upper = formula.upper()
        
        for category, functions in self.formula_categories.items():
            for func in functions:
                if func in formula_upper:
                    return category
        
        return "unknown"
    
    def _calculate_formula_complexity(self, formula: str) -> int:
        """Calculate formula complexity on 1-10 scale"""
        complexity = 1
        
        # Count functions
        function_count = len(re.findall(r'[A-Z]+\s*\(', formula))
        complexity += min(function_count, 3)
        
        # Count operators
        operator_count = len(re.findall(r'[+\-*/^&]', formula))
        complexity += min(operator_count // 2, 2)
        
        # Count parentheses depth
        max_depth = 0
        current_depth = 0
        for char in formula:
            if char == '(':
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char == ')':
                current_depth -= 1
        complexity += min(max_depth, 2)
        
        # Length factor
        length_factor = len(formula) // 20
        complexity += min(length_factor, 2)
        
        return min(complexity, 10)
    
    def _extract_charts_from_sheet(self, worksheet, sheet_name: str) -> List[ChartInfo]:
        """Extract chart information from worksheet"""
        charts = []
        
        try:
            # Check if worksheet has charts attribute
            if hasattr(worksheet, '_charts'):
                for chart in worksheet._charts:
                    chart_info = ChartInfo(
                        sheet=sheet_name,
                        name=getattr(chart, 'title', 'Untitled Chart'),
                        chart_type=type(chart).__name__,
                        data_range="",  # Would need more complex extraction
                        title=getattr(chart.title, 'text', 'No Title') if hasattr(chart, 'title') else 'No Title',
                        axis_labels={}
                    )
                    charts.append(chart_info)
            else:
                # For ReadOnlyWorksheet or worksheets without direct chart access
                logger.debug(f"No direct chart access for sheet {sheet_name}")
        except Exception as e:
            logger.warning(f"Chart extraction failed for sheet {sheet_name}: {str(e)}")
        
        return charts
    
    def _detect_template(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Detect Excel template type based on patterns"""
        best_match = None
        best_score = 0
        
        for pattern in self.template_patterns:
            score = self._calculate_template_score(analysis_result, pattern)
            if score > best_score:
                best_score = score
                best_match = pattern
        
        if best_match and best_score > 0.5:  # Threshold for confident match
            return {
                "type": best_match.template_type.value,
                "name": best_match.name,
                "confidence": best_score
            }
        
        return {"type": "custom", "name": "Custom Template", "confidence": 0.0}
    
    def _calculate_template_score(self, analysis_result: Dict[str, Any], pattern: TemplatePattern) -> float:
        """Calculate template matching score"""
        score = 0.0
        total_possible = 0.0
        
        # Sheet name matching
        sheet_names = list(analysis_result["sheets"].keys())
        for pattern_sheet in pattern.sheet_patterns:
            total_possible += 1
            if any(pattern_sheet.lower() in sheet.lower() for sheet in sheet_names):
                score += 1
        
        # Formula pattern matching
        all_formulas = [f.formula.upper() for f in analysis_result["formulas"]]
        for pattern_formula in pattern.formula_patterns:
            total_possible += 0.5
            if any(pattern_formula in formula for formula in all_formulas):
                score += 0.5
        
        # Avoid division by zero
        if total_possible == 0:
            return 0.0
        
        return score / total_possible
    
    def _extract_business_logic(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract business logic from formulas and structure"""
        business_logic = {
            "calculation_chains": [],
            "data_flows": [],
            "key_metrics": [],
            "validation_rules": []
        }
        
        # Extract calculation chains from formula dependencies
        calculation_chains = self._build_calculation_chains(analysis_result["formulas"])
        business_logic["calculation_chains"] = calculation_chains
        
        # Identify key metrics (cells with many dependencies)
        key_metrics = self._identify_key_metrics(analysis_result["formulas"])
        business_logic["key_metrics"] = key_metrics
        
        return business_logic
    
    def _build_calculation_chains(self, formulas: List[FormulaInfo]) -> List[List[str]]:
        """Build calculation dependency chains"""
        chains = []
        
        # Create dependency graph
        graph = {}
        for formula in formulas:
            graph[f"{formula.sheet}!{formula.cell}"] = {
                "dependencies": [f"{formula.sheet}!{dep}" for dep in formula.dependencies],
                "formula": formula.formula
            }
        
        # Find calculation chains (simplified)
        for node, info in graph.items():
            if info["dependencies"]:
                chain = [node] + info["dependencies"]
                chains.append(chain)
        
        return chains
    
    def _identify_key_metrics(self, formulas: List[FormulaInfo]) -> List[Dict[str, Any]]:
        """Identify key metrics based on formula complexity and dependencies"""
        metrics = []
        
        for formula in formulas:
            if formula.complexity >= 5 or len(formula.dependencies) >= 3:
                metrics.append({
                    "sheet": formula.sheet,
                    "cell": formula.cell,
                    "formula": formula.formula,
                    "complexity": formula.complexity,
                    "dependencies": formula.dependencies,
                    "category": formula.category
                })
        
        return metrics
    
    def _analyze_security(self, file_path: Path) -> Dict[str, Any]:
        """Analyze security aspects of the Excel file"""
        security_analysis = {
            "vba_present": False,
            "external_links": False,
            "macros_enabled": False,
            "security_risks": []
        }
        
        try:
            # Check for VBA/macros
            wb = openpyxl.load_workbook(file_path, keep_vba=True)
            if hasattr(wb, 'vba_archive'):
                security_analysis["vba_present"] = True
                security_analysis["macros_enabled"] = True
                security_analysis["security_risks"].append("VBA macros detected - potential security risk")
            
            wb.close()
        except Exception as e:
            logger.warning(f"Security analysis failed: {str(e)}")
        
        return security_analysis
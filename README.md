# Excel-to-Web Application Generator

🚀 **Transform Excel files into interactive web applications instantly!**

This project provides a unified platform where users can upload Excel files (including templates, models, visual graphs, reports, and calculations) and instantly generate fully functional web applications that run immediately online.

## ✨ Features

- **Advanced Excel Analysis**: Template detection, formula extraction, chart recognition
- **Modular Code Generation**: Generate Streamlit dashboards or FastAPI backends
- **Instant Deployment**: Docker-based deployment with live URLs
- **Real-time Feedback**: Live progress tracking and status updates
- **Enhanced UI**: Beautiful, responsive interface with deployment management

## 🏗️ Architecture

The enhanced architecture includes:

- **Enhanced Excel Analyzer**: Advanced formula and template analysis
- **Modular Code Generator**: Template-based code generation
- **Instant Deployer**: Docker-based instant deployment
- **Unified Processor**: Single pipeline for processing
- **Enhanced Frontend**: Modern user interface

For detailed architecture documentation, see [ARCHITECTURE_OVERVIEW.md](ARCHITECTURE_OVERVIEW.md).

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Docker Engine

### Installation

1. Clone the repository:
```bash
git clone https://github.com/salahbendra-sudo/projectest.git
cd projectest
```

2. Install dependencies:
```bash
pip install -r requirements_enhanced.txt
```

3. **Set up Docker** (see [DOCKER_SETUP.md](DOCKER_SETUP.md) for detailed instructions):
```bash
# Verify Docker is installed and running
docker --version

# Test Docker
docker run hello-world
```

4. Run the application:
```bash
streamlit run enhanced_frontend.py
```

5. Upload your Excel file and generate your web app!

## 📋 Usage

1. **Upload**: Upload your Excel file (.xlsx, .xls, .xlsm)
2. **Analyze**: System automatically detects templates, formulas, and charts
3. **Generate**: Choose your app template (Streamlit or FastAPI)
4. **Deploy**: Get instant deployment with live URL
5. **Manage**: Monitor and control your deployed applications

## 🛠️ Components

### Core Modules

- `enhanced_excel_analyzer.py` - Advanced Excel file analysis
- `modular_code_generator.py` - Template-based code generation
- `instant_deployer.py` - Docker-based deployment system
- `unified_processor.py` - Unified processing pipeline
- `enhanced_frontend.py` - Enhanced user interface

### Supporting Files

- `requirements_enhanced.txt` - Python dependencies
- `ARCHITECTURE_OVERVIEW.md` - Detailed architecture documentation
- `test_architecture.py` - Architecture validation tests
- `test_enhanced_system.py` - System functionality tests

## 📊 Supported Excel Features

- Multiple worksheets and complex data structures
- Advanced formulas (financial, statistical, logical, lookup)
- Charts and visualizations with configuration preservation
- Business logic including calculation chains
- Data validation rules and conditional formatting

## 🔧 Development

### Testing

Run architecture validation:
```bash
python test_architecture.py
```

Run system tests:
```bash
python test_enhanced_system.py
```

### Extending the System

The modular architecture makes it easy to extend:
- Add new template types
- Support additional web frameworks
- Enhance Excel analysis capabilities
- Add deployment platforms

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For issues and questions, please open an issue on GitHub.

---

**Built with ❤️ for transforming Excel workflows into modern web applications**

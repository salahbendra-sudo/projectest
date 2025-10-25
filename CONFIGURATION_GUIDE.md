# Enhanced Excel Transformer - Configuration Guide

## 🚀 Quick Setup

### 1. Environment Configuration
Copy the example environment file and update with your API keys:

```bash
cp .env.example .env
```

### 2. Update .env with your API keys:
```env
# OpenRouter Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here

# DeepSeek Configuration
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# Model Configuration
ANALYSIS_MODEL=deepseek/deepseek-chat-v3-0324:free
GENERATION_MODEL=deepseek/deepseek-chat-v3-0324:free

# Provider Priority
PROVIDER_PRIORITY=openrouter,deepseek,template_engine,universal_fallback
```

## 🔧 Configuration Options

### API Providers

#### OpenRouter
- **Base URL**: `https://openrouter.ai/api/v1`
- **Supported Models**: Any model available on OpenRouter
- **Setup**: Get API key from [OpenRouter](https://openrouter.ai)

#### DeepSeek (OpenAI-Compatible)
- **Base URL**: `https://api.deepseek.com/v1` (default)
- **Supported Models**: `deepseek/deepseek-chat`, `deepseek/deepseek-chat-v3-0324:free`
- **Setup**: Get API key from [DeepSeek](https://platform.deepseek.com)

### Model Configuration

#### Available Models
```python
# OpenRouter Models
"openai/gpt-4"
"openai/gpt-3.5-turbo"
"anthropic/claude-3-sonnet"
"google/gemini-pro"
"deepseek/deepseek-chat-v3-0324:free"

# DeepSeek Models
"deepseek/deepseek-chat"
"deepseek/deepseek-chat-v3-0324:free"
```

#### Model Selection
You can use different models for different steps:
- **ANALYSIS_MODEL**: Model used for Excel analysis
- **GENERATION_MODEL**: Model used for code generation

### Provider Priority

Configure the order in which providers are tried:
```env
PROVIDER_PRIORITY=openrouter,deepseek,template_engine,universal_fallback
```

Available providers:
- `openrouter`: OpenRouter API
- `deepseek`: DeepSeek API
- `template_engine`: Business-specific templates
- `universal_fallback`: Guaranteed basic functionality

## 🎯 Usage Examples

### 1. Basic Usage (Default Configuration)
```python
from enhanced_excel_transformer import EnhancedExcelTransformer

transformer = EnhancedExcelTransformer()
result = transformer.transform_excel_to_app(file_content, filename)
```

### 2. Custom Model Configuration
```python
from enhanced_excel_transformer import EnhancedExcelTransformer

# Use different models for analysis and generation
transformer = EnhancedExcelTransformer(
    analysis_model="deepseek/deepseek-chat",
    generation_model="openai/gpt-4"
)

result = transformer.transform_excel_to_app(
    file_content, 
    filename,
    analysis_model="deepseek/deepseek-chat",
    generation_model="openai/gpt-4"
)
```

### 3. Custom Provider Priority
```python
import os

# Set provider priority via environment variable
os.environ["PROVIDER_PRIORITY"] = "deepseek,template_engine,universal_fallback"

from enhanced_excel_transformer import EnhancedExcelTransformer
transformer = EnhancedExcelTransformer()
result = transformer.transform_excel_to_app(file_content, filename)
```

### 4. Streamlit App Configuration
When using the Streamlit app, you can configure:
- **Primary Provider**: Select which LLM provider to use first
- **Analysis Model**: Model for Excel analysis
- **Generation Model**: Model for code generation

## 🔒 Security Configuration

### API Timeout Settings
```env
API_TIMEOUT=120  # Seconds
MAX_TOKENS=4000  # Maximum tokens per request
```

### File Size Limits
```env
MAX_FILE_SIZE=52428800  # 50MB in bytes
```

## 🛠️ Advanced Configuration

### Custom Base URLs
For self-hosted or alternative APIs:
```env
DEEPSEEK_BASE_URL=https://your-custom-api.com/v1
```

### Temperature Settings
Control creativity vs consistency:
```env
TEMPERATURE=0.3  # Lower = more consistent, Higher = more creative
```

### Provider Fallback Behavior
```env
# Try OpenRouter first, then DeepSeek, then templates
PROVIDER_PRIORITY=openrouter,deepseek,template_engine,universal_fallback

# Try DeepSeek first, skip OpenRouter
PROVIDER_PRIORITY=deepseek,template_engine,universal_fallback

# Use only templates (no API calls)
PROVIDER_PRIORITY=template_engine,universal_fallback
```

## 🚀 Deployment Configuration

### Streamlit Cloud
```env
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

### Docker Deployment
```dockerfile
ENV OPENROUTER_API_KEY=your_key
ENV DEEPSEEK_API_KEY=your_key
ENV PROVIDER_PRIORITY=openrouter,deepseek,template_engine,universal_fallback
```

## 🔍 Troubleshooting

### Common Issues

1. **API Key Not Configured**
   - Check that API keys are set in .env file
   - Verify environment variables are loaded

2. **Provider Fails**
   - System automatically falls back to next provider
   - Check provider priority configuration

3. **Model Not Available**
   - Verify model name spelling
   - Check if model is available on the selected provider

4. **Timeout Errors**
   - Increase API_TIMEOUT value
   - Check network connectivity

### Debug Mode
Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📊 Performance Optimization

### For Large Files
```env
MAX_TOKENS=8000  # Increase for complex Excel files
API_TIMEOUT=300  # Increase timeout for large files
```

### For Better Quality
```env
GENERATION_MODEL=openai/gpt-4  # Use more capable model
TEMPERATURE=0.1  # Lower temperature for more consistent results
```

### For Faster Results
```env
PROVIDER_PRIORITY=template_engine,universal_fallback  # Skip API calls
ANALYSIS_MODEL=deepseek/deepseek-chat-v3-0324:free  # Use free model
```

---

**🎯 Remember**: The system guarantees 100% success rate through intelligent fallbacks. Even if API providers fail, the template engine and universal fallback will always work!
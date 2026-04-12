# Dependency Documentation for Alien LLM Project

## Overview
This document provides comprehensive information about all dependencies required to deploy and run the Alien LLM project with translation functionality. It covers Python packages, system requirements, and setup instructions for both development (Mac) and production (iPad) environments.

## Python Package Dependencies

### Core Requirements (`requirements.txt`)
The following Python packages are essential for basic functionality:

- `flask`: Web framework for the server API
- `flask-cors`: Cross-origin resource sharing support
- `torch`: PyTorch deep learning framework
- `transformers`: Hugging Face transformers library for models
- `sentencepiece`: Required for Marian model tokenization
- `sacremoses`: Recommended for improved tokenization
- `httpx[socks]`: HTTP client library with SOCKS proxy support

### Installation
To install all required packages, run:
```bash
pip install -r scripts/requirements.txt
```

## Model Dependencies

### Translation Models
The system uses the Helsinki-NLP/opus-mt-en-zh model for English-to-Chinese translation. This model will be automatically downloaded and cached in:
```
models/translation/
```

### Language Generation Models
The system uses a Phi-3 model for text generation located at:
```
models/phi3/
```

## System Requirements

### Minimum Hardware
- CPU: Modern multi-core processor
- RAM: 8GB minimum (16GB+ recommended for optimal performance)
- Storage: 2GB free space (more for model caching)

### Supported Platforms
- Development: macOS (primary development environment)
- Production: iPadOS 14+/macOS 12+ (with native Apple Translation API)

### Python Environment
- Python 3.8 or higher
- Virtual environment recommended for isolation

## Development Environment Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd alien_llm
```

### 2. Set Up Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r scripts/requirements.txt
```

### 4. Download Models
The system will automatically download required models on first run. For offline deployment, ensure models are pre-downloaded:
```bash
# This will trigger model downloads
python -c "from scripts.translate import translate_to_chinese; translate_to_chinese('test')"
```

## Production Deployment (iPad)

### Transition to Native Apple Translation API
For iPad deployment, replace the Python translation module with native Apple Translation API integration:

1. Replace `scripts/translate.py` with Swift-based translation module
2. Maintain the same interface: `translate_to_chinese(english_text: str) -> str`
3. Use Apple's Translation framework with offline model support
4. Ensure language packs are pre-installed for offline functionality

### Required Configuration for iPad
- iOS/iPadOS 14+ or macOS 12 Monterey+
- Swift development environment
- Apple Translation framework integration

## Troubleshooting

### Common Issues

#### 1. Network Connection Issues
If experiencing network issues during model download:
- Install `socksio` for SOCKS proxy support
- Configure `HF_TOKEN` for higher rate limits with Hugging Face Hub
- Pre-download models in an environment with stable connection

#### 2. Memory Issues
- Increase system memory or use smaller models if available
- Close other applications during model loading

#### 3. GPU Acceleration
The system attempts to use MPS (Metal Performance Shaders) on Apple Silicon Macs automatically.

## Version Compatibility Notes

### Known Working Versions
- Python: 3.8+ (tested with 3.14)
- PyTorch: 2.10.0+
- Transformers: 5.5.3+
- SentencePiece: 0.2.1+

### Updating Dependencies
Always test the system after updating major dependencies, especially PyTorch and Transformers.

## Maintenance

### Updating Translation Models
To update to newer translation models:
1. Update the model identifier in `scripts/translate.py`
2. Clear the model cache directory: `models/translation/`
3. Test translation functionality thoroughly

### Model Cache Management
Translation models are cached locally in `models/translation/`. This directory can be safely deleted to force model re-download.

## For Deployers

### Checklist for New Deployment
- [ ] Verify Python version meets requirements
- [ ] Install all packages from `requirements.txt`
- [ ] Ensure sufficient disk space for model downloads
- [ ] Test generation functionality
- [ ] Test translation functionality
- [ ] Verify offline capabilities (when deployed to iPad)

### Environment Variables (Optional)
- `HF_TOKEN`: Hugging Face authentication token for higher rate limits
- `TRANSFORMERS_OFFLINE`: Set to 1 to force offline mode if models are pre-downloaded

## Security Considerations
- All model downloads happen over secure HTTPS connections
- No sensitive data is stored in plain text by default
- Consider using virtual environments to isolate dependencies
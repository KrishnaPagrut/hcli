# HCLI - Human Code Language Interface

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/React-18.2.0-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116.1-green.svg)](https://fastapi.tiangolo.com/)

Video Demo: https://www.youtube.com/watch?v=SaYtTa2IvbA 

A sophisticated web-based IDE that transforms Python code into human-readable format, enabling natural language code editing and collaboration. HCLI bridges the gap between traditional code and human understanding through advanced AST (Abstract Syntax Tree) processing and intelligent code transformation.

## 🚀 Features

### Core Functionality
- **Human-Readable Code Translation**: Convert Python code to `.pyh` (Python Human) format
- **Bidirectional Editing**: Edit code in natural language and convert back to Python
- **Real-time Diff Analysis**: Track and visualize changes between original and modified code
- **Repository Management**: Clone and analyze GitHub repositories
- **Monaco Editor Integration**: Professional code editing experience with syntax highlighting

### Advanced Capabilities
- **AST Processing**: Deep code analysis using Python's Abstract Syntax Tree
- **Change Tracking**: Intelligent diff detection and change application
- **File Management**: Comprehensive file explorer with support for complex directory structures
- **API-First Architecture**: RESTful API for seamless integration
- **Real-time Collaboration**: Web-based interface for team collaboration

## 🏗️ Architecture

### Frontend (React/TypeScript)
- **React 18.2.0** with TypeScript for type-safe development
- **Monaco Editor** for professional code editing experience
- **Tailwind CSS** for modern, responsive UI design
- **Zustand** for efficient state management
- **Axios** for API communication

### Backend (Python/FastAPI)
- **FastAPI** for high-performance API development
- **Uvicorn** ASGI server for production deployment
- **Pydantic** for data validation and serialization
- **Custom AST Processing** for code transformation
- **GitHub Integration** via PyGithub

### Core Modules
- **AST Chunker**: Breaks down Python code into manageable chunks
- **PHY Generator**: Converts AST to human-readable format
- **Diff Analyzer**: Detects and analyzes code changes
- **Change Applier**: Applies modifications back to Python code

## 📋 Prerequisites

- **Python 3.8+**
- **Node.js 16+** (recommended: 18.x)
- **npm 8+**
- **Git** for repository management

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/hcli.git
cd hcli
```

### 2. Backend Setup
```bash
# Install Python dependencies
pip install fastapi uvicorn flask flask-cors requests pygithub python-dotenv

# Or install from requirements.txt
pip install -r backend/requirements.txt
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

## 🚀 Quick Start

### 1. Start the Backend Server
```bash
# From the project root
python3 api_server.py
```
The API will be available at `http://localhost:8000`

### 2. Start the Frontend Development Server
```bash
# From the frontend directory
cd frontend
npm start
```
The web interface will be available at `http://localhost:3000`

### 3. Access the Application
- **Web Interface**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📚 API Documentation

### Core Endpoints

#### Repository Management
- `POST /crawl` - Crawl a repository and generate pyh files
- `GET /api/files` - Get directory contents for file explorer
- `GET /api/file/{file_path}` - Get specific file content

#### Code Transformation
- `POST /display-pyh` - Display pyh file content in readable format
- `POST /pyh-to-py` - Convert pyh changes back to Python code
- `GET /api/pyh-output/{file_path}` - Get pyh output for a Python file

#### File Operations
- `POST /api/save-user-phy` - Save user-edited PHY content
- `POST /api/apply-phy-changes` - Apply changes using diff analysis

### Example API Usage

```bash
# Crawl a repository
curl -X POST "http://localhost:8000/crawl" \
  -H "Content-Type: application/json" \
  -d '{"repo_path": "/path/to/repo", "output_dir": "out"}'

# Get file contents
curl "http://localhost:8000/api/files?directory=/path/to/repo"

# Get pyh output for a Python file
curl "http://localhost:8000/api/pyh-output/example.py?directory=/path/to/repo"
```

## 🔧 Configuration

### Environment Variables
```bash
# Backend configuration
export HCLI_REPO_PATH="/path/to/your/repos"
export HCLI_OUTPUT_DIR="out"

# Frontend configuration (optional)
export DANGEROUSLY_DISABLE_HOST_CHECK=true  # For development
```

### Proxy Configuration
The frontend is configured to proxy API requests to the backend. Update `frontend/package.json` if needed:
```json
{
  "proxy": "http://localhost:8000"
}
```

## 🧪 Usage Examples

### 1. Basic Code Transformation
```python
# Original Python code
def calculate_fibonacci(n):
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)
```

**Transforms to:**
```pyh
Function: calculate_fibonacci
Description: Calculates the nth Fibonacci number using recursion
Parameters: n (int) - The position in the Fibonacci sequence
Returns: int - The Fibonacci number at position n
Logic: 
  - If n is 0 or 1, return n
  - Otherwise, return the sum of the previous two Fibonacci numbers
```

### 2. Repository Analysis
```bash
# Clone and analyze a GitHub repository
curl -X POST "http://localhost:8000/crawl" \
  -H "Content-Type: application/json" \
  -d '{"repo_path": "https://github.com/user/repo", "output_dir": "analysis"}'
```

## 🏗️ Development

### Project Structure
```
hcli/
├── api_server.py              # FastAPI backend server
├── backend/                   # Backend modules
│   ├── app.py                # Flask alternative backend
│   └── requirements.txt      # Python dependencies
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── hooks/           # Custom React hooks
│   │   └── types/           # TypeScript type definitions
│   └── package.json         # Node.js dependencies
├── out/                      # Generated output files
├── repos/                    # Cloned repositories
└── *.py                     # Core processing modules
```

### Core Modules
- `ast_chunker.py` - AST processing and chunking
- `pyh_ast_generator.py` - Generate human-readable AST
- `pyh_ast_to_output.py` - Convert AST to readable format
- `diff_analyzer.py` - Analyze code differences
- `apply_changes_demo.py` - Apply changes to Python files
- `github_utils.py` - GitHub integration utilities

### Adding New Features
1. **Backend**: Add new endpoints in `api_server.py`
2. **Frontend**: Create components in `frontend/src/components/`
3. **Core Logic**: Extend modules in the root directory
4. **Testing**: Add tests for new functionality

## 🐛 Troubleshooting

### Common Issues

#### Frontend Won't Start
```bash
# Error: Invalid options object. Dev Server has been initialized...
# Solution: Use legacy OpenSSL provider
NODE_OPTIONS=--openssl-legacy-provider npm start
```

#### Backend Dependencies Missing
```bash
# Install missing FastAPI dependencies
pip install fastapi uvicorn
```

#### Port Conflicts
```bash
# Check what's running on ports
lsof -i :3000  # Frontend
lsof -i :8000  # Backend

# Kill processes if needed
pkill -f "react-scripts start"
pkill -f "api_server"
```

### Debug Mode
```bash
# Backend with debug logging
python3 api_server.py --log-level debug

# Frontend with verbose output
npm start -- --verbose
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use TypeScript for frontend development
- Add tests for new functionality
- Update documentation for API changes
- Use meaningful commit messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Monaco Editor** - Professional code editor
- **FastAPI** - Modern Python web framework
- **React** - Frontend library
- **Tailwind CSS** - Utility-first CSS framework
- **Python AST** - Abstract Syntax Tree processing

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/hcli/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/hcli/discussions)
- **Documentation**: [Wiki](https://github.com/yourusername/hcli/wiki)

## 🔮 Roadmap

- [ ] **Multi-language Support** - Extend beyond Python
- [ ] **Real-time Collaboration** - Live editing with multiple users
- [ ] **AI Integration** - Smart code suggestions and analysis
- [ ] **Plugin System** - Extensible architecture for custom transformations
- [ ] **Cloud Deployment** - Docker containers and cloud hosting
- [ ] **VS Code Extension** - Native IDE integration
- [ ] **Mobile App** - React Native mobile interface

---

**HCLI** - Making code human-readable, one transformation at a time. 🚀
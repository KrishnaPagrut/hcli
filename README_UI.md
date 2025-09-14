# 🎨 HCLI Web UI

A modern web interface for the Human Code Language Interface (HCLI) that allows users to edit Python code through natural language abstractions.

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ and npm
- Python 3.8+
- Git

### Installation

1. **Install Frontend Dependencies**
```bash
cd frontend
npm install
```

2. **Install Backend Dependencies**
```bash
cd backend
pip install -r requirements.txt
```

3. **Start the Development Servers**

**Terminal 1 - Backend:**
```bash
cd backend
python app.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

4. **Open the Application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

## 🎯 Features

### ✨ Core Features
- **Split-screen editing**: Edit .pyh.json files alongside Python code
- **GitHub integration**: Clone and push repositories directly
- **Real-time validation**: JSON syntax checking and error highlighting
- **Monaco Editor**: VS Code-quality editing experience
- **Anthropic-inspired design**: Clean, modern interface

### 🔧 Technical Features
- **React frontend** with styled-components
- **Flask backend** with CORS support
- **Monaco Editor** for code editing
- **GitHub API integration**
- **Real-time file synchronization**

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Bar (Top)                        │
├─────────────┬───────────────────────────────────────────────┤
│             │                                               │
│   File      │              Main Content Area                │
│   Tree      │                                               │
│   (Left)    │  ┌─────────────────┬─────────────────────────┐ │
│             │  │                 │                         │ │
│             │  │   .pyh Editor   │    .py Viewer/Editor    │ │
│             │  │   (Top Left)    │    (Top Right)          │ │
│             │  │                 │                         │ │
│             │  ├─────────────────┴─────────────────────────┤ │
│             │  │            Send Button (Bottom)           │ │
│             │  └───────────────────────────────────────────┘ │
└─────────────┴───────────────────────────────────────────────┘
```

## 📁 Project Structure

```
hcli/
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   │   ├── GitHubBar.jsx
│   │   │   ├── FileTree.jsx
│   │   │   ├── PyhEditor.jsx
│   │   │   ├── PyViewer.jsx
│   │   │   └── SendButton.jsx
│   │   ├── styles/          # Theme and styling
│   │   │   └── theme.js
│   │   ├── App.jsx          # Main app component
│   │   └── index.js         # Entry point
│   ├── public/
│   └── package.json
├── backend/                 # Python backend
│   ├── app.py              # Flask API server
│   └── requirements.txt
├── scripts/                # Your existing Python scripts
└── out/                    # Generated files
```

## 🎨 Design System

### Color Palette (Anthropic-inspired)
- **Primary**: Blue tones (#0ea5e9, #0284c7, etc.)
- **Neutral**: Gray tones (#f8fafc, #64748b, etc.)
- **Success**: Green (#22c55e)
- **Warning**: Orange (#f59e0b)
- **Error**: Red (#ef4444)

### Typography
- **Sans-serif**: System fonts (SF Pro, Segoe UI, etc.)
- **Monospace**: Monaco, Menlo, Ubuntu Mono

## 🔌 API Endpoints

### GitHub Integration
- `POST /api/clone` - Clone repository
- `POST /api/push` - Push changes

### File Management
- `GET /api/files` - List repository files
- `GET /api/file/<path>` - Get file content

### HCLI Operations
- `POST /api/generate-ast` - Generate AST/PHY files
- `POST /api/apply-changes` - Apply changes to Python code
- `POST /api/run-tests` - Run tests on files

## 🚀 Usage Workflow

1. **Clone Repository**
   - Enter GitHub repository URL
   - Click "Clone" button
   - Wait for repository to be cloned

2. **Select File**
   - Browse file tree on the left
   - Click on a Python file to select it

3. **Edit PHY File**
   - Edit the .pyh.json file in the top-left panel
   - See real-time JSON validation
   - View corresponding Python code in top-right panel

4. **Apply Changes**
   - Click "Apply Changes" button at bottom
   - Watch progress as changes are applied
   - See success/error feedback

5. **Push Changes**
   - Click "Push Changes" in GitHub bar
   - Changes are committed and pushed to repository

## 🛠️ Development

### Frontend Development
```bash
cd frontend
npm start          # Start development server
npm run build      # Build for production
npm test           # Run tests
```

### Backend Development
```bash
cd backend
python app.py      # Start Flask server
```

### Adding New Features

1. **New Component**: Add to `frontend/src/components/`
2. **New API Endpoint**: Add to `backend/app.py`
3. **Styling**: Update `frontend/src/styles/theme.js`

## 🔧 Configuration

### Environment Variables
```bash
# GitHub API
GITHUB_TOKEN=your_github_token

# Claude API
ANTHROPIC_API_KEY=your_claude_api_key

# Flask
FLASK_ENV=development
FLASK_DEBUG=True
```

### Customization
- **Theme**: Edit `frontend/src/styles/theme.js`
- **API Base URL**: Update proxy in `frontend/package.json`
- **Backend Port**: Change in `backend/app.py`

## 🐛 Troubleshooting

### Common Issues

1. **CORS Errors**
   - Ensure Flask-CORS is installed
   - Check that backend is running on port 5000

2. **Monaco Editor Not Loading**
   - Check browser console for errors
   - Ensure @monaco-editor/react is installed

3. **GitHub API Errors**
   - Verify GitHub token is set
   - Check repository permissions

4. **File Not Found**
   - Ensure file paths are correct
   - Check that files exist in repository

### Debug Mode
```bash
# Frontend
REACT_APP_DEBUG=true npm start

# Backend
FLASK_DEBUG=True python app.py
```

## 🚀 Deployment

### Production Build
```bash
# Frontend
cd frontend
npm run build

# Backend
cd backend
pip install -r requirements.txt
```

### Docker Deployment
```dockerfile
# Dockerfile example
FROM node:16-alpine as frontend
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

FROM python:3.9-alpine as backend
WORKDIR /app/backend
COPY backend/requirements.txt ./
RUN pip install -r requirements.txt
COPY backend/ ./
COPY --from=frontend /app/frontend/build ./static

EXPOSE 5000
CMD ["python", "app.py"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is part of the HCLI system. See the main repository for license information.

---

**Happy coding with HCLI! 🎉**

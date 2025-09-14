import React, { useState, useRef, useEffect } from 'react';
import { Editor } from '@monaco-editor/react';
import { FileCode, FileText, Eye, Edit3 } from 'lucide-react';
import { useStore } from '../hooks/useStore';
import { LineMapping } from '../types';

const EditorPanel: React.FC = () => {
  const { editor, updatePyhContent } = useStore();
  const [hoveredLine, setHoveredLine] = useState<number | null>(null);
  const [isPyReadOnly, setIsPyReadOnly] = useState(true);
  const pyhEditorRef = useRef<any>(null);
  const pyEditorRef = useRef<any>(null);

  // Handle hover highlighting
  const handlePyhLineHover = (lineNumber: number) => {
    setHoveredLine(lineNumber);
    
    // Find corresponding Python line
    const mapping = editor.lineMappings.find(m => m.pyhLine === lineNumber);
    if (mapping && pyEditorRef.current) {
      // Highlight the corresponding line in Python editor
      pyEditorRef.current.deltaDecorations([], [
        {
          range: {
            startLineNumber: mapping.pyLine,
            endLineNumber: mapping.pyLine,
            startColumn: 1,
            endColumn: 1,
          },
          options: {
            isWholeLine: true,
            className: 'hover-highlight',
            marginClassName: 'hover-highlight-margin',
          },
        },
      ]);
    }
  };

  const handlePyLineHover = (lineNumber: number) => {
    setHoveredLine(lineNumber);
    
    // Find corresponding PHY line
    const mapping = editor.lineMappings.find(m => m.pyLine === lineNumber);
    if (mapping && pyhEditorRef.current) {
      // Highlight the corresponding line in PHY editor
      pyhEditorRef.current.deltaDecorations([], [
        {
          range: {
            startLineNumber: mapping.pyhLine,
            endLineNumber: mapping.pyhLine,
            startColumn: 1,
            endColumn: 1,
          },
          options: {
            isWholeLine: true,
            className: 'hover-highlight',
            marginClassName: 'hover-highlight-margin',
          },
        },
      ]);
    }
  };

  const clearHighlights = () => {
    setHoveredLine(null);
    if (pyhEditorRef.current) {
      pyhEditorRef.current.deltaDecorations([], []);
    }
    if (pyEditorRef.current) {
      pyEditorRef.current.deltaDecorations([], []);
    }
  };

  const handlePyhEditorDidMount = (editor: any) => {
    pyhEditorRef.current = editor;
    
    // Add hover listeners
    editor.onMouseMove((e: any) => {
      if (e.target.position) {
        handlePyhLineHover(e.target.position.lineNumber);
      }
    });
    
    editor.onMouseLeave(() => {
      clearHighlights();
    });
  };

  const handlePyEditorDidMount = (editor: any) => {
    pyEditorRef.current = editor;
    
    // Add hover listeners
    editor.onMouseMove((e: any) => {
      if (e.target.position) {
        handlePyLineHover(e.target.position.lineNumber);
      }
    });
    
    editor.onMouseLeave(() => {
      clearHighlights();
    });
  };

  const handlePyhChange = (value: string | undefined) => {
    if (value !== undefined) {
      updatePyhContent(value);
    }
  };

  return (
    <div className="flex-1 flex">
      {/* PHY Editor (Left) */}
      <div className="flex-1 flex flex-col border-r border-neutral-200">
        <div className="flex items-center justify-between px-4 py-2 bg-neutral-50 border-b border-neutral-200">
          <div className="flex items-center space-x-2">
            <FileText className="h-4 w-4 text-yellow-500" />
            <span className="text-sm font-medium text-neutral-700">
              {editor.pyhContent ? 'main.pyh' : 'No file selected'}
            </span>
            <span className="text-xs text-neutral-500">(Human-readable)</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="text-xs text-neutral-500">
              {editor.hasUnsavedChanges ? 'Unsaved changes' : 'Saved'}
            </div>
          </div>
        </div>
        
        <div className="flex-1">
          <Editor
            height="100%"
            defaultLanguage="plaintext"
            value={editor.pyhContent}
            onChange={handlePyhChange}
            onMount={handlePyhEditorDidMount}
            theme="vs-light"
            options={{
              minimap: { enabled: false },
              scrollBeyondLastLine: false,
              fontSize: 14,
              fontFamily: 'Monaco, Menlo, "Ubuntu Mono", monospace',
              lineNumbers: 'on',
              wordWrap: 'on',
              automaticLayout: true,
              tabSize: 2,
              insertSpaces: true,
              renderWhitespace: 'selection',
              readOnly: false,
              cursorBlinking: 'blink',
              cursorStyle: 'line',
            }}
          />
        </div>
      </div>

      {/* Python Editor (Right) */}
      <div className="flex-1 flex flex-col">
        <div className="flex items-center justify-between px-4 py-2 bg-neutral-50 border-b border-neutral-200">
          <div className="flex items-center space-x-2">
            <FileCode className="h-4 w-4 text-primary-500" />
            <span className="text-sm font-medium text-neutral-700">
              {editor.pyContent ? 'main.py' : 'No file selected'}
            </span>
            <span className="text-xs text-neutral-500">
              ({isPyReadOnly ? 'Read-only' : 'Editable'})
            </span>
          </div>
          <button
            onClick={() => setIsPyReadOnly(!isPyReadOnly)}
            className="flex items-center space-x-1 px-2 py-1 text-xs bg-neutral-100 hover:bg-neutral-200 rounded transition-colors"
          >
            {isPyReadOnly ? <Edit3 className="h-3 w-3" /> : <Eye className="h-3 w-3" />}
            <span>{isPyReadOnly ? 'Edit' : 'View'}</span>
          </button>
        </div>
        
        <div className="flex-1">
          <Editor
            height="100%"
            defaultLanguage="python"
            value={editor.pyContent}
            onMount={handlePyEditorDidMount}
            theme="vs-light"
            options={{
              minimap: { enabled: false },
              scrollBeyondLastLine: false,
              fontSize: 14,
              fontFamily: 'Monaco, Menlo, "Ubuntu Mono", monospace',
              lineNumbers: 'on',
              wordWrap: 'on',
              automaticLayout: true,
              tabSize: 4,
              insertSpaces: true,
              renderWhitespace: 'selection',
              readOnly: isPyReadOnly,
              cursorBlinking: 'blink',
              cursorStyle: 'line',
            }}
          />
        </div>
      </div>
    </div>
  );
};

export default EditorPanel;

import React, { useState, useRef, useEffect } from 'react';

interface TwoPanelEditorProps {
  pyhContent: string;   // text output from pyh_ast_to_output.py
  pyContent: string;    // actual Python code
}

const TwoPanelEditor: React.FC<TwoPanelEditorProps> = ({ pyhContent, pyContent }) => {
  const [leftWidth, setLeftWidth] = useState(50); // percentage
  const [isDragging, setIsDragging] = useState(false);
  const [hoveredLine, setHoveredLine] = useState<number | null>(null);
  const [activeLine, setActiveLine] = useState<number | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);


  // Split content into lines
  const pyhLines = pyhContent.split('\n');
  const pyLines = pyContent.split('\n');

  // Handle mouse down on divider
  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  // Handle mouse move for resizing
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isDragging || !containerRef.current) return;
      
      const containerRect = containerRef.current.getBoundingClientRect();
      const newLeftWidth = ((e.clientX - containerRect.left) / containerRect.width) * 100;
      
      // Constrain between 20% and 80%
      const constrainedWidth = Math.min(Math.max(newLeftWidth, 20), 80);
      setLeftWidth(constrainedWidth);
    };

    const handleMouseUp = () => {
      setIsDragging(false);
    };

    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging]);

  // Handle line hover for highlighting
  const handleLineHover = (lineNumber: number, panel: 'pyh' | 'py') => {
    setHoveredLine(lineNumber);
    // Mock highlighting - in real implementation, this would map to corresponding lines
    if (panel === 'pyh') {
      // For now, just highlight the same line number on the right
      setHoveredLine(lineNumber);
    }
  };

  const handleLineLeave = () => {
    setHoveredLine(null);
  };

  // Handle textarea change for editable content
  const handlePyhChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    // In a real implementation, this would update the pyhContent state
    // and trigger diff generation
    console.log('PYH content changed:', e.target.value);
  };

  // Handle textarea focus for active line highlighting
  const handleTextareaFocus = (e: React.FocusEvent<HTMLTextAreaElement>) => {
    const textarea = e.target;
    const cursorPosition = textarea.selectionStart;
    const textBeforeCursor = textarea.value.substring(0, cursorPosition);
    const lineNumber = textBeforeCursor.split('\n').length;
    setActiveLine(lineNumber);
  };

  const handleTextareaBlur = () => {
    setActiveLine(null);
  };

  // Show placeholder if no content
  if (!pyhContent && !pyContent) {
    return (
      <div className="flex h-full w-full bg-gray-50 items-center justify-center">
        <div className="text-center text-gray-500">
          <div className="text-lg font-medium mb-2">No file selected</div>
          <div className="text-sm">Select a Python file from the file explorer to view its content</div>
        </div>
      </div>
    );
  }

  return (
    <div 
      ref={containerRef}
      className="flex h-full w-full bg-gray-50"
    >
      {/* Left Panel - PYH Content (Editable) */}
      <div 
        className="bg-gray-100 border-r border-gray-300 font-mono text-sm relative"
        style={{ width: `${leftWidth}%` }}
      >
        {/* Line Numbers */}
        <div className="absolute left-0 top-0 w-8 bg-gray-200 border-r border-gray-300 h-full overflow-hidden">
          {pyhLines.map((_, index) => (
            <div
              key={index}
              className={`h-5 text-xs text-gray-500 flex items-center justify-center ${
                hoveredLine === index + 1 ? 'bg-blue-100' : ''
              } ${activeLine === index + 1 ? 'bg-blue-200' : ''}`}
            >
              {index + 1}
            </div>
          ))}
        </div>

        {/* Content */}
        <div className="pl-10 pr-2 py-2 h-full">
          <textarea
            value={pyhContent}
            onChange={handlePyhChange}
            onFocus={handleTextareaFocus}
            onBlur={handleTextareaBlur}
            className="w-full h-full resize-none border-none outline-none bg-transparent text-gray-800 leading-5 min-h-0"
            placeholder="PYH content will appear here..."
            spellCheck={false}
            style={{ height: 'calc(100vh - 200px)' }}
          />
        </div>
      </div>

      {/* Resizable Divider */}
      <div
        className={`w-1 bg-gray-300 cursor-col-resize hover:bg-gray-400 transition-colors ${
          isDragging ? 'bg-gray-500' : ''
        }`}
        onMouseDown={handleMouseDown}
      >
        <div className="w-full h-full flex items-center justify-center">
          <div className="w-0.5 h-8 bg-gray-400 rounded"></div>
        </div>
      </div>

      {/* Right Panel - PY Content (Read-only) */}
      <div 
        className="bg-white font-mono text-sm relative"
        style={{ width: `${100 - leftWidth}%` }}
      >
        {/* Line Numbers */}
        <div className="absolute left-0 top-0 w-8 bg-gray-100 border-r border-gray-300 h-full overflow-hidden">
          {pyLines.map((_, index) => (
            <div
              key={index}
              className={`h-5 text-xs text-gray-500 flex items-center justify-center ${
                hoveredLine === index + 1 ? 'bg-blue-100' : ''
              }`}
            >
              {index + 1}
            </div>
          ))}
        </div>

        {/* Content */}
        <div className="pl-10 pr-2 py-2 h-full">
          <div className="w-full h-full overflow-auto" style={{ height: 'calc(100vh - 200px)' }}>
            {pyLines.map((line, index) => (
              <div
                key={index}
                className={`h-5 leading-5 text-gray-800 ${
                  hoveredLine === index + 1 ? 'bg-blue-50' : ''
                }`}
                onMouseEnter={() => handleLineHover(index + 1, 'py')}
                onMouseLeave={handleLineLeave}
              >
                {line || '\u00A0'} {/* Non-breaking space for empty lines */}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TwoPanelEditor;

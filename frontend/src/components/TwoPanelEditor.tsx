import React, { useState, useRef, useEffect } from 'react';
import { useStore } from '../hooks/useStore';
import { Edit3, Save, Eye } from 'lucide-react';

interface TwoPanelEditorProps {
  pyhContent: string;   // text output from pyh_ast_to_output.py
  pyContent: string;    // actual Python code
}

const TwoPanelEditor: React.FC<TwoPanelEditorProps> = ({ pyhContent, pyContent }) => {
  const { repository, updatePyhContent, saveUserPhy, isLoading, editor } = useStore();
  const [leftWidth, setLeftWidth] = useState(50); // percentage
  const [isDragging, setIsDragging] = useState(false);
  const [hoveredLine, setHoveredLine] = useState<number | null>(null);
  const [activeLine, setActiveLine] = useState<number | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);


  // Split content into lines
  const pyhLines = pyhContent.split('\n');
  const pyLines = pyContent.split('\n');
  
  // Generate PHY content from AST structure and create proper line mappings
  const generatePhyContentWithMappings = () => {
    const lines: string[] = [];
    const lineMappings: Array<{pyhLine: number, pyLineRange: [number, number], nodeId: string}> = [];
    
    const renderNode = (node: any, indent = 0): void => {
      const pad = "    ".repeat(indent);
      const sig = node.signature;
      const desc = node.description;
      const lineRange = node.line_range;
      const nodeId = node.id;
      
      // Show signature
      if (sig) {
        const lineNumber = lines.length + 1;
        lines.push(`${pad}${sig}`);
        
        if (lineRange) {
          lineMappings.push({
            pyhLine: lineNumber,
            pyLineRange: lineRange,
            nodeId: nodeId
          });
        }
        
        if (desc) {
          const descLineNumber = lines.length + 1;
          lines.push(`${pad}    ${desc}`);
          
          if (lineRange) {
            lineMappings.push({
              pyhLine: descLineNumber,
              pyLineRange: lineRange,
              nodeId: nodeId
            });
          }
        }
      } else if (desc) {
        const lineNumber = lines.length + 1;
        lines.push(`${pad}${desc}`);
        
        if (lineRange) {
          lineMappings.push({
            pyhLine: lineNumber,
            pyLineRange: lineRange,
            nodeId: nodeId
          });
        }
      }
      
      // Recurse into children
      for (const child of node.children || []) {
        renderNode(child, indent + 1);
      }
    };
    
    // Use PHY data from the store
    if (editor.pyhData?.phy_chunks?.main) {
      renderNode(editor.pyhData.phy_chunks.main);
    } else {
      // Fallback: try to parse pyhContent as JSON
      try {
        const phyData = JSON.parse(pyhContent);
        if (phyData?.phy_chunks?.main) {
          renderNode(phyData.phy_chunks.main);
        }
      } catch (e) {
        console.log('Could not parse PHY data, using existing content');
      }
    }
    
    return { lines, lineMappings };
  };
  
  const { lines: actualPhyLines, lineMappings: generatedMappings } = generatePhyContentWithMappings();
  
  // Use generated content if available, otherwise fall back to original
  const finalPhyLines = actualPhyLines.length > 0 ? actualPhyLines : pyhLines;
  const finalMappings = generatedMappings.length > 0 ? generatedMappings : editor.lineMappings || [];
  
  // Debug logging for test03
  console.log('Generated PHY lines:', actualPhyLines.length);
  console.log('Generated mappings:', generatedMappings.length);
  console.log('Final PHY lines:', finalPhyLines.length);
  console.log('Final mappings:', finalMappings.length);
  console.log('Using generated content:', actualPhyLines.length > 0);
  
  // Create maps for highlighting ranges using generated mappings
  const pyhToPyRanges = new Map<number, [number, number]>();
  const pyToPyhLines = new Map<number, number>();
  
  finalMappings.forEach(mapping => {
    // Map PHY line to Python line range
    if (mapping.pyLineRange) {
      pyhToPyRanges.set(mapping.pyhLine, mapping.pyLineRange);
      
      // Map each Python line in the range to the PHY line
      const [start, end] = mapping.pyLineRange;
      for (let line = start; line <= end; line++) {
        pyToPyhLines.set(line, mapping.pyhLine);
      }
    }
  });

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

  // Line hover highlighting with ranges
  const handleLineHover = (lineNumber: number, panel: 'pyh' | 'py') => {
    if (panel === 'pyh') {
      // PHY line hovered - highlight this PHY line and corresponding Python lines
      setHoveredLine(lineNumber);
    } else {
      // Python line hovered - highlight the corresponding PHY line
      const mappedPyhLine = pyToPyhLines.get(lineNumber);
      if (mappedPyhLine) {
        setHoveredLine(mappedPyhLine);
      }
    }
  };

  const handleLineLeave = () => {
    setHoveredLine(null);
  };

  // Handle textarea change for editable content
  const handlePyhChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newContent = e.target.value;
    updatePyhContent(newContent);
    setHasUnsavedChanges(true);
  };

  // Handle save button
  const handleSave = async () => {
    if (repository.selectedFile) {
      await saveUserPhy(repository.selectedFile, pyhContent);
      setHasUnsavedChanges(false);
    }
  };

  // Handle edit toggle
  const handleEditToggle = () => {
    setIsEditing(!isEditing);
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

  // Show loading state
  if (isLoading) {
    return (
      <div className="flex h-full w-full bg-gray-900 items-center justify-center">
        <div className="text-center text-gray-400">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <div className="text-lg font-medium mb-2 text-gray-300">Loading file content...</div>
          <div className="text-sm">Please wait while we load the file</div>
        </div>
      </div>
    );
  }

  // Show placeholder if no content
  if (!pyhContent && !pyContent) {
    return (
      <div className="flex h-full w-full bg-gray-900 items-center justify-center">
        <div className="text-center text-gray-400">
          <div className="text-lg font-medium mb-2 text-gray-300">No file selected</div>
          <div className="text-sm">Select a Python file from the file explorer to view its content</div>
        </div>
      </div>
    );
  }

  return (
    <div 
      ref={containerRef}
      className="flex h-full w-full bg-gray-900 overflow-hidden"
      style={{ maxHeight: '100vh' }}
    >
      {/* Left Panel - PYH Content (Editable) */}
      <div 
        className="bg-gray-800 border-r border-gray-700 font-mono text-sm relative flex flex-col shadow-lg"
        style={{ width: `${leftWidth}%` }}
      >
        {/* Header with Edit Toggle and Save Button */}
        <div className="flex items-center justify-between p-4 bg-gradient-to-r from-gray-800 to-gray-750 border-b border-gray-600 shadow-lg">
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full bg-cyan-400 shadow-sm"></div>
              <span className="text-sm font-bold text-cyan-300 tracking-wide">PHY CONTENT</span>
            </div>
            {hasUnsavedChanges && (
              <span className="text-xs text-orange-300 font-medium bg-orange-900/30 px-2 py-1 rounded-full border border-orange-600/50">• Unsaved changes</span>
            )}
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={handleEditToggle}
              className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-bold transition-all duration-300 ${
                isEditing 
                  ? 'bg-gradient-to-r from-blue-600 to-blue-500 text-white hover:from-blue-500 hover:to-blue-400 shadow-lg shadow-blue-500/25 transform hover:scale-105' 
                  : 'bg-gradient-to-r from-gray-700 to-gray-600 text-gray-300 hover:from-gray-600 hover:to-gray-500 border border-gray-500 shadow-md hover:shadow-lg'
              }`}
            >
              {isEditing ? <Eye className="h-3 w-3" /> : <Edit3 className="h-3 w-3" />}
              <span>{isEditing ? 'VIEW' : 'EDIT'}</span>
            </button>
            {isEditing && (
              <button
                onClick={handleSave}
                disabled={!hasUnsavedChanges}
                className="flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-bold transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed bg-gradient-to-r from-emerald-600 to-emerald-500 text-white hover:from-emerald-500 hover:to-emerald-400 shadow-lg shadow-emerald-500/25 transform hover:scale-105 disabled:transform-none"
              >
                <Save className="h-3 w-3" />
                <span>SAVE</span>
              </button>
            )}
          </div>
        </div>

        {/* Content Area */}
        <div className="flex-1 relative bg-gray-900">
          {/* Content */}
          <div className="px-3 py-3 h-full">
            {isEditing ? (
              <textarea
                value={pyhContent}
                onChange={handlePyhChange}
                onFocus={handleTextareaFocus}
                onBlur={handleTextareaBlur}
                className="w-full h-full resize-none border-none outline-none bg-transparent text-gray-100 min-h-0 font-mono"
                placeholder="Edit PHY content here..."
                spellCheck={false}
                style={{ 
                  height: 'calc(100vh - 200px)',
                  lineHeight: '22px',
                  fontSize: '14px',
                  maxHeight: 'calc(100vh - 200px)'
                }}
              />
            ) : (
              <div className="flex h-full" style={{ maxHeight: 'calc(100vh - 200px)' }}>
                {/* Line Numbers */}
                <div className="flex-shrink-0 bg-gray-800 text-gray-500 text-right pr-3 select-none border-r border-gray-700 overflow-y-auto" style={{ minWidth: '50px', maxHeight: 'calc(100vh - 200px)' }}>
                  {finalPhyLines.map((_, index) => (
                    <div
                      key={index}
                      className="text-xs font-mono"
                      style={{ 
                        minHeight: '22px', 
                        lineHeight: '22px'
                      }}
                    >
                      {index + 1}
                    </div>
                  ))}
                </div>
                
                {/* Content */}
                <div 
                  className="flex-1 overflow-auto text-gray-100 font-mono"
                  style={{ 
                    lineHeight: '22px',
                    fontSize: '14px',
                    whiteSpace: 'pre-wrap',
                    maxHeight: 'calc(100vh - 200px)'
                  }}
                >
                  {finalPhyLines.map((line, index) => {
                    const lineNumber = index + 1;
                    const hasMapping = pyhToPyRanges.has(lineNumber);
                    const isHighlighted = hoveredLine === lineNumber;
                    
                    return (
                      <div
                        key={index}
                        className={`${
                          isHighlighted ? 'bg-cyan-500/20 border-l-4 border-cyan-300 shadow-lg shadow-cyan-500/20' : ''
                        } ${activeLine === lineNumber ? 'bg-cyan-400/30 border-l-4 border-cyan-200 shadow-lg shadow-cyan-400/30' : ''} ${
                          hasMapping ? 'cursor-pointer hover:bg-gray-800/50' : ''
                        } transition-all duration-200 px-2 py-0.5`}
                        style={{ 
                          minHeight: '22px', 
                          lineHeight: '22px',
                          whiteSpace: 'pre-wrap',
                          wordBreak: 'break-all'
                        }}
                        onMouseEnter={() => hasMapping && handleLineHover(lineNumber, 'pyh')}
                        onMouseLeave={handleLineLeave}
                        onClick={() => setActiveLine(lineNumber)}
                      >
                        <span className="text-gray-100">{line || '\u00A0'}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Resizable Divider */}
      <div
        className={`w-2 bg-gradient-to-b from-gray-700 to-gray-600 cursor-col-resize hover:from-gray-600 hover:to-gray-500 transition-all duration-300 ${
          isDragging ? 'from-gray-500 to-gray-400 shadow-lg' : ''
        }`}
        onMouseDown={handleMouseDown}
      >
        <div className="w-full h-full flex items-center justify-center">
          <div className="w-1 h-12 bg-gradient-to-b from-cyan-400 to-emerald-400 rounded-full shadow-lg"></div>
        </div>
      </div>

      {/* Right Panel - PY Content (Read-only) */}
      <div 
        className="bg-gray-900 font-mono text-sm relative flex flex-col shadow-lg"
        style={{ width: `${100 - leftWidth}%` }}
      >
        {/* Header with Edit Toggle and Save Button */}
        <div className="flex items-center justify-between p-4 bg-gradient-to-r from-gray-800 to-gray-750 border-b border-gray-600 shadow-lg">
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full bg-emerald-400 shadow-sm"></div>
              <span className="text-sm font-bold text-emerald-300 tracking-wide">PYTHON CODE</span>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {/* Empty space to match PHY header height */}
            <div className="h-6"></div>
          </div>
        </div>

        {/* Content Area */}
        <div className="flex-1 relative bg-gray-900">
          {/* Content */}
          <div className="px-3 py-3 h-full">
            <div className="flex h-full" style={{ maxHeight: 'calc(100vh - 200px)' }}>
              {/* Line Numbers */}
              <div className="flex-shrink-0 bg-gray-800 text-gray-500 text-right pr-3 select-none border-r border-gray-700 overflow-y-auto" style={{ minWidth: '50px', maxHeight: 'calc(100vh - 200px)' }}>
                {pyLines.map((_, index) => (
                  <div
                    key={index}
                    className="text-xs font-mono"
                    style={{ 
                      minHeight: '22px', 
                      lineHeight: '22px'
                    }}
                  >
                    {index + 1}
                  </div>
                ))}
              </div>
              
              {/* Content */}
              <div 
                className="flex-1 overflow-auto font-mono" 
                style={{ 
                  lineHeight: '22px',
                  fontSize: '14px',
                  whiteSpace: 'pre-wrap',
                  paddingTop: '0px',
                  maxHeight: 'calc(100vh - 200px)'
                }}
              >
                {pyLines.map((line, index) => {
                  const lineNumber = index + 1;
                  const hasMapping = pyToPyhLines.has(lineNumber);
                  
                // Check if this line is in a highlighted range
                const isInHighlightedRange = hoveredLine && pyhToPyRanges.has(hoveredLine) ? 
                  (() => {
                    const range = pyhToPyRanges.get(hoveredLine);
                    if (!range) return false;
                    const [start, end] = range;
                    return lineNumber >= start && lineNumber <= end;
                  })() : false;
                  
                  // Simple syntax highlighting using CSS classes
                  const getSyntaxClass = (text: string) => {
                    if (/^\s*(class|def|if|else|elif|for|while|try|except|finally|with|import|from|return|yield|lambda|and|or|not|in|is|as|pass|break|continue|raise|assert|del|global|nonlocal)\b/.test(text)) {
                      return 'text-blue-400 font-semibold';
                    }
                    if (/\b(True|False|None)\b/.test(text)) {
                      return 'text-orange-400 font-semibold';
                    }
                    if (/\b\d+\.?\d*\b/.test(text)) {
                      return 'text-yellow-400';
                    }
                    if (/^#/.test(text)) {
                      return 'text-gray-500';
                    }
                    if (/["'`]/.test(text)) {
                      return 'text-green-400';
                    }
                    return 'text-gray-100';
                  };
                  
                  return (
                    <div
                      key={index}
                      className={`${
                        isInHighlightedRange ? 'bg-emerald-500/20 border-l-4 border-emerald-300 shadow-lg shadow-emerald-500/20' : ''
                      } ${hasMapping ? 'cursor-pointer hover:bg-gray-800/50' : ''} transition-all duration-200 px-2 py-0.5`}
                      style={{ 
                        minHeight: '22px', 
                        lineHeight: '22px',
                        whiteSpace: 'pre-wrap',
                        wordBreak: 'break-all'
                      }}
                      onMouseEnter={() => hasMapping && handleLineHover(lineNumber, 'py')}
                      onMouseLeave={handleLineLeave}
                    >
                      <span className={getSyntaxClass(line)}>
                        {line || '\u00A0'}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TwoPanelEditor;

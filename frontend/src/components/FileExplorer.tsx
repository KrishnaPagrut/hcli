import React, { useState, useEffect } from 'react';
import { 
  ChevronRight, 
  ChevronDown, 
  File, 
  Folder, 
  FolderOpen,
  FileCode,
  Loader
} from 'lucide-react';
import { useStore } from '../hooks/useStore';

interface FileExplorerProps {
  onFileSelect: (filePath: string) => void;
}

interface FileNode {
  name: string;
  type: 'file' | 'directory';
  path: string;
  children?: FileNode[];
}

const FileExplorer: React.FC<FileExplorerProps> = ({ onFileSelect }) => {
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const { repository, isLoading, error, loadFiles } = useStore();
  const files = repository.files;

  // Update selected file when repository changes
  useEffect(() => {
    if (repository.selectedFile) {
      setSelectedFile(repository.selectedFile);
    }
  }, [repository.selectedFile]);

  // Load files when directory changes
  useEffect(() => {
    if (repository.currentDirectory) {
      loadFiles(repository.currentDirectory);
    }
  }, [repository.currentDirectory, loadFiles]);

  const toggleNode = (nodePath: string) => {
    const newExpanded = new Set(expandedNodes);
    if (newExpanded.has(nodePath)) {
      newExpanded.delete(nodePath);
    } else {
      newExpanded.add(nodePath);
    }
    setExpandedNodes(newExpanded);
  };

  const handleFileClick = (filePath: string) => {
    setSelectedFile(filePath);
    onFileSelect(filePath);
  };

  const getFileIcon = (fileName: string) => {
    if (fileName.endsWith('.py')) {
      return <FileCode className="h-4 w-4 text-blue-500" />;
    } else {
      return <File className="h-4 w-4 text-gray-500" />;
    }
  };

  const renderNode = (node: FileNode, level: number = 0): React.ReactNode => {
    const isExpanded = expandedNodes.has(node.path);
    const isSelected = selectedFile === node.path;
    const hasChildren = node.children && node.children.length > 0;
    const isFolder = node.type === 'directory';

    return (
      <div key={node.path}>
        <div
          className={`flex items-center py-1 px-2 cursor-pointer hover:bg-gray-100 transition-colors ${
            isSelected ? 'bg-blue-50 border-r-2 border-blue-500' : ''
          }`}
          style={{ paddingLeft: `${level * 16 + 8}px` }}
          onClick={() => {
            if (isFolder) {
              toggleNode(node.path);
            } else {
              handleFileClick(node.path);
            }
          }}
        >
          {isFolder && (
            <div className="mr-1">
              {isExpanded ? (
                <ChevronDown className="h-3 w-3 text-gray-500" />
              ) : (
                <ChevronRight className="h-3 w-3 text-gray-500" />
              )}
            </div>
          )}
          
          <div className="mr-2">
            {isFolder ? (
              isExpanded ? (
                <FolderOpen className="h-4 w-4 text-blue-500" />
              ) : (
                <Folder className="h-4 w-4 text-blue-500" />
              )
            ) : (
              getFileIcon(node.name)
            )}
          </div>
          
          <span className={`text-sm truncate ${
            isSelected ? 'text-blue-700 font-medium' : isFolder ? 'font-bold text-gray-800' : 'text-gray-700'
          }`}>
            {node.name}
          </span>
        </div>
        
        {isFolder && isExpanded && hasChildren && (
          <div>
            {node.children!.map(child => renderNode(child, level + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="w-64 bg-gray-50 border-r border-gray-300 h-full overflow-y-auto">
      <div className="p-3">
        <h3 className="text-sm font-semibold text-gray-800 mb-2">Files</h3>
        
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <Loader className="h-6 w-6 animate-spin text-gray-500" />
            <span className="ml-2 text-sm text-gray-500">Loading files...</span>
          </div>
        ) : error ? (
          <div className="text-center py-8">
            <div className="text-red-500 text-sm">{error}</div>
            <button 
              onClick={() => window.location.reload()} 
              className="mt-2 text-xs text-blue-500 hover:underline"
            >
              Retry
            </button>
          </div>
        ) : files.length > 0 ? (
          files.map(node => renderNode(node))
        ) : (
          <div className="text-center py-8 text-sm text-gray-500">
            No files found. Select a directory and click "Crawl" to load files.
          </div>
        )}
      </div>
    </div>
  );
};

export default FileExplorer;

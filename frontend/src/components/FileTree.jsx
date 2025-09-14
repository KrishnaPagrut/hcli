import React, { useState } from 'react';
import styled from 'styled-components';
import { 
  ChevronRight, 
  ChevronDown, 
  File, 
  Folder, 
  FolderOpen,
  FileCode,
  FileJson
} from 'lucide-react';
import theme from '../styles/theme';

const FileTreeContainer = styled.div`
  width: 300px;
  background: ${props => props.theme.colors.background.secondary};
  border-right: 1px solid ${props => props.theme.colors.border.light};
  overflow-y: auto;
  height: 100%;
`;

const TreeNode = styled.div`
  display: flex;
  align-items: center;
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  cursor: pointer;
  font-size: ${props => props.theme.typography.fontSize.sm};
  color: ${props => props.theme.colors.text.secondary};
  transition: background-color 0.2s ease;
  
  &:hover {
    background: ${props => props.theme.colors.background.tertiary};
  }
  
  ${props => props.selected && `
    background: ${props.theme.colors.primary[50]};
    color: ${props.theme.colors.primary[700]};
    border-right: 2px solid ${props.theme.colors.primary[500]};
  `}
`;

const TreeNodeContent = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  flex: 1;
  min-width: 0;
`;

const TreeNodeLabel = styled.span`
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

const TreeNodeChildren = styled.div`
  margin-left: ${props => props.theme.spacing.lg};
`;

const FileIcon = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  flex-shrink: 0;
`;

const FileTree = ({ files, selectedFile, onFileSelect }) => {
  const [expandedNodes, setExpandedNodes] = useState(new Set());

  const toggleNode = (nodePath) => {
    const newExpanded = new Set(expandedNodes);
    if (newExpanded.has(nodePath)) {
      newExpanded.delete(nodePath);
    } else {
      newExpanded.add(nodePath);
    }
    setExpandedNodes(newExpanded);
  };

  const getFileIcon = (fileName) => {
    if (fileName.endsWith('.py')) {
      return <FileCode size={16} color={theme.colors.primary[500]} />;
    } else if (fileName.endsWith('.pyh.json')) {
      return <FileJson size={16} color={theme.colors.warning[500]} />;
    } else if (fileName.endsWith('.json')) {
      return <FileJson size={16} color={theme.colors.neutral[500]} />;
    } else {
      return <File size={16} color={theme.colors.neutral[500]} />;
    }
  };

  const renderNode = (node, level = 0) => {
    const isExpanded = expandedNodes.has(node.path);
    const isSelected = selectedFile === node.path;
    const hasChildren = node.children && node.children.length > 0;
    const isDirectory = node.type === 'directory';

    return (
      <div key={node.path}>
        <TreeNode
          selected={isSelected}
          onClick={() => {
            if (isDirectory) {
              toggleNode(node.path);
            } else {
              onFileSelect(node.path);
            }
          }}
          style={{ paddingLeft: `${level * 16 + 16}px` }}
        >
          <TreeNodeContent>
            {isDirectory && (
              <FileIcon>
                {isExpanded ? (
                  <ChevronDown size={14} />
                ) : (
                  <ChevronRight size={14} />
                )}
              </FileIcon>
            )}
            
            <FileIcon>
              {isDirectory ? (
                isExpanded ? (
                  <FolderOpen size={16} color={theme.colors.primary[500]} />
                ) : (
                  <Folder size={16} color={theme.colors.primary[500]} />
                )
              ) : (
                getFileIcon(node.name)
              )}
            </FileIcon>
            
            <TreeNodeLabel>{node.name}</TreeNodeLabel>
          </TreeNodeContent>
        </TreeNode>
        
        {isDirectory && isExpanded && hasChildren && (
          <TreeNodeChildren>
            {node.children.map(child => renderNode(child, level + 1))}
          </TreeNodeChildren>
        )}
      </div>
    );
  };

  // Sample file structure for demonstration
  const sampleFiles = files || [
    {
      name: 'src',
      type: 'directory',
      path: '/src',
      children: [
        {
          name: 'main.py',
          type: 'file',
          path: '/src/main.py'
        },
        {
          name: 'utils.py',
          type: 'file',
          path: '/src/utils.py'
        }
      ]
    },
    {
      name: 'out',
      type: 'directory',
      path: '/out',
      children: [
        {
          name: 'main.pyh.json',
          type: 'file',
          path: '/out/main.pyh.json'
        },
        {
          name: 'utils.pyh.json',
          type: 'file',
          path: '/out/utils.pyh.json'
        }
      ]
    },
    {
      name: 'README.md',
      type: 'file',
      path: '/README.md'
    }
  ];

  return (
    <FileTreeContainer>
      {sampleFiles.map(node => renderNode(node))}
    </FileTreeContainer>
  );
};

export default FileTree;

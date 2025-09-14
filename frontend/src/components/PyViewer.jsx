import React from 'react';
import styled from 'styled-components';
import { Editor } from '@monaco-editor/react';
import { FileCode, Eye, Edit3 } from 'lucide-react';
import theme from '../styles/theme';

const ViewerContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
  background: ${props => props.theme.colors.background.primary};
`;

const ViewerHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: ${props => props.theme.spacing.md};
  background: ${props => props.theme.colors.background.secondary};
  border-bottom: 1px solid ${props => props.theme.colors.border.light};
`;

const HeaderLeft = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
`;

const ViewerTitle = styled.h3`
  margin: 0;
  font-size: ${props => props.theme.typography.fontSize.lg};
  font-weight: ${props => props.theme.typography.fontWeight.semibold};
  color: ${props => props.theme.colors.text.primary};
`;

const ModeIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: ${props => props.theme.typography.fontSize.sm};
  font-weight: ${props => props.theme.typography.fontWeight.medium};
  background: ${props => props.theme.colors.primary[50]};
  color: ${props => props.theme.colors.primary[600]};
`;

const ToggleButton = styled.button`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  border: 1px solid ${props => props.theme.colors.border.medium};
  border-radius: ${props => props.theme.borderRadius.md};
  background: ${props => props.theme.colors.background.primary};
  color: ${props => props.theme.colors.text.secondary};
  font-size: ${props => props.theme.typography.fontSize.sm};
  font-weight: ${props => props.theme.typography.fontWeight.medium};
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: ${props => props.theme.colors.background.tertiary};
    border-color: ${props => props.theme.colors.primary[300]};
  }
`;

const ViewerWrapper = styled.div`
  flex: 1;
  position: relative;
`;

const DiffOverlay = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 5;
`;

const DiffLine = styled.div`
  position: absolute;
  left: 0;
  right: 0;
  height: 20px;
  background: ${props => {
    if (props.type === 'added') return props.theme.colors.success[100];
    if (props.type === 'removed') return props.theme.colors.error[100];
    if (props.type === 'modified') return props.theme.colors.warning[100];
    return 'transparent';
  }};
  border-left: 3px solid ${props => {
    if (props.type === 'added') return props.theme.colors.success[500];
    if (props.type === 'removed') return props.theme.colors.error[500];
    if (props.type === 'modified') return props.theme.colors.warning[500];
    return 'transparent';
  }};
`;

const PyViewer = ({ 
  content, 
  fileName = 'untitled.py',
  isReadOnly = true,
  onToggleMode,
  diffData = null 
}) => {
  const getModeText = () => {
    return isReadOnly ? 'Read-only' : 'Editable';
  };

  const getModeIcon = () => {
    return isReadOnly ? <Eye size={16} /> : <Edit3 size={16} />;
  };

  return (
    <ViewerContainer>
      <ViewerHeader>
        <HeaderLeft>
          <FileCode size={20} color={theme.colors.primary[500]} />
          <ViewerTitle>{fileName}</ViewerTitle>
          <ModeIndicator>
            {getModeIcon()}
            {getModeText()}
          </ModeIndicator>
        </HeaderLeft>
        
        <ToggleButton onClick={onToggleMode}>
          {isReadOnly ? <Edit3 size={16} /> : <Eye size={16} />}
          {isReadOnly ? 'Edit' : 'View'}
        </ToggleButton>
      </ViewerHeader>
      
      <ViewerWrapper>
        <Editor
          height="100%"
          defaultLanguage="python"
          value={content}
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
            readOnly: isReadOnly,
            bracketPairColorization: { enabled: true },
            guides: {
              bracketPairs: true,
              indentation: true
            }
          }}
        />
        
        {diffData && (
          <DiffOverlay>
            {diffData.map((diff, index) => (
              <DiffLine
                key={index}
                type={diff.type}
                style={{
                  top: `${(diff.lineNumber - 1) * 20}px`
                }}
              />
            ))}
          </DiffOverlay>
        )}
      </ViewerWrapper>
    </ViewerContainer>
  );
};

export default PyViewer;

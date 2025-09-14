import React, { useState, useRef } from 'react';
import styled from 'styled-components';
import { Editor } from '@monaco-editor/react';
import { FileJson, AlertCircle, CheckCircle } from 'lucide-react';
import theme from '../styles/theme';

const EditorContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
  background: ${props => props.theme.colors.background.primary};
`;

const EditorHeader = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  padding: ${props => props.theme.spacing.md};
  background: ${props => props.theme.colors.background.secondary};
  border-bottom: 1px solid ${props => props.theme.colors.border.light};
`;

const EditorTitle = styled.h3`
  margin: 0;
  font-size: ${props => props.theme.typography.fontSize.lg};
  font-weight: ${props => props.theme.typography.fontWeight.semibold};
  color: ${props => props.theme.colors.text.primary};
`;

const StatusIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: ${props => props.theme.typography.fontSize.sm};
  font-weight: ${props => props.theme.typography.fontWeight.medium};
  
  ${props => props.status === 'valid' && `
    background: ${props.theme.colors.success[50]};
    color: ${props.theme.colors.success[600]};
  `}
  
  ${props => props.status === 'invalid' && `
    background: ${props.theme.colors.error[50]};
    color: ${props.theme.colors.error[600]};
  `}
  
  ${props => props.status === 'warning' && `
    background: ${props.theme.colors.warning[50]};
    color: ${props.theme.colors.warning[600]};
  `}
`;

const EditorWrapper = styled.div`
  flex: 1;
  position: relative;
`;

const ErrorOverlay = styled.div`
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: ${props => props.theme.colors.error[50]};
  border-top: 1px solid ${props => props.theme.colors.error[200]};
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  font-size: ${props => props.theme.typography.fontSize.sm};
  color: ${props => props.theme.colors.error[700]};
  z-index: 10;
`;

const PyhEditor = ({ 
  content, 
  onChange, 
  fileName = 'untitled.pyh.json',
  hasChanges = false,
  isReadOnly = true 
}) => {
  const [isValid, setIsValid] = useState(true);
  const [error, setError] = useState(null);
  const editorRef = useRef(null);

  const validateJSON = (jsonString) => {
    try {
      JSON.parse(jsonString);
      setIsValid(true);
      setError(null);
      return true;
    } catch (e) {
      setIsValid(false);
      setError(e.message);
      return false;
    }
  };

  const handleEditorChange = (value) => {
    if (value !== undefined) {
      validateJSON(value);
      onChange(value);
    }
  };

  const handleEditorDidMount = (editor, monaco) => {
    editorRef.current = editor;
    
    // Configure JSON language features
    monaco.languages.json.jsonDefaults.setDiagnosticsOptions({
      validate: true,
      allowComments: false,
      schemas: []
    });
  };

  const getStatus = () => {
    if (!isValid) return 'invalid';
    if (hasChanges) return 'warning';
    return 'valid';
  };

  const getStatusText = () => {
    if (!isValid) return 'Invalid JSON';
    if (hasChanges) return 'Unsaved changes';
    return 'Valid JSON';
  };

  const getStatusIcon = () => {
    if (!isValid) return <AlertCircle size={16} />;
    if (hasChanges) return <AlertCircle size={16} />;
    return <CheckCircle size={16} />;
  };

  return (
    <EditorContainer>
      <EditorHeader>
        <FileJson size={20} color={theme.colors.warning[500]} />
        <EditorTitle>{fileName} (Human-readable)</EditorTitle>
        <StatusIndicator status={getStatus()}>
          {getStatusIcon()}
          {getStatusText()}
        </StatusIndicator>
      </EditorHeader>
      
      <EditorWrapper>
        <Editor
          height="100%"
          defaultLanguage={isReadOnly ? "plaintext" : "json"}
          value={content}
          onChange={handleEditorChange}
          onMount={handleEditorDidMount}
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
            readOnly: isReadOnly,
            bracketPairColorization: { enabled: !isReadOnly },
            guides: {
              bracketPairs: !isReadOnly,
              indentation: true
            }
          }}
        />
        
        {error && (
          <ErrorOverlay>
            <AlertCircle size={16} style={{ marginRight: '8px' }} />
            {error}
          </ErrorOverlay>
        )}
      </EditorWrapper>
    </EditorContainer>
  );
};

export default PyhEditor;

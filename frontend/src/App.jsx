import React, { useState, useEffect } from 'react';
import styled, { ThemeProvider } from 'styled-components';
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';
import theme from './styles/theme';
import GitHubBar from './components/GitHubBar';
import FileTree from './components/FileTree';
import PyhEditor from './components/PyhEditor';
import PyViewer from './components/PyViewer';
import SendButtonComponent from './components/SendButton';

const AppContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: ${props => props.theme.colors.background.primary};
`;

const MainContent = styled.div`
  display: flex;
  flex: 1;
  overflow: hidden;
`;

const LeftPanel = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
`;

const RightPanel = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
  flex: 1;
`;

const SplitContainer = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
`;

const ResizeHandle = styled(PanelResizeHandle)`
  background: ${props => props.theme.colors.border.medium};
  opacity: 0.2;
  transition: opacity 0.2s ease;
  
  &:hover {
    opacity: 0.5;
  }
  
  &[data-panel-group-direction="horizontal"] {
    height: 11px;
    cursor: row-resize;
  }
  
  &[data-panel-group-direction="vertical"] {
    width: 11px;
    cursor: col-resize;
  }
`;

function App() {
  // State management
  const [selectedFile, setSelectedFile] = useState(null);
  const [pyhContent, setPyhContent] = useState('');
  const [pyContent, setPyContent] = useState('');
  const [hasChanges, setHasChanges] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [sendStatus, setSendStatus] = useState('idle');
  const [sendMessage, setSendMessage] = useState('');
  const [progress, setProgress] = useState(0);
  const [isPyReadOnly, setIsPyReadOnly] = useState(true);

  // Sample data for demonstration
  const samplePyhContent = `function fibonacci(takes input n)
    base case: if n is less than or equal to 0 return an empty list, if n equals 1 return [0]
    initialize a list fibs with [0, 1]
    for each index i from 2 up to n, append the sum of the two previous numbers to the list
    return the list of Fibonacci numbers

when run as main: set n=10, call fibonacci(n), and print the resulting sequence`;

  const samplePyContent = `def fibonacci(n):
    """Calculate fibonacci sequence up to n terms"""
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    
    fibs = [0, 1]
    for i in range(2, n):
        fibs.append(fibs[i-1] + fibs[i-2])
    
    return fibs

if __name__ == "__main__":
    n = 10
    sequence = fibonacci(n)
    print(f"The first {n} Fibonacci numbers are: {sequence}")`;

  // Initialize with sample data
  useEffect(() => {
    setPyhContent(samplePyhContent);
    setPyContent(samplePyContent);
  }, [samplePyhContent, samplePyContent]);

  // GitHub integration handlers
  const handleClone = async (repoUrl, branch) => {
    setIsLoading(true);
    try {
      // Simulate GitHub clone
      console.log('Cloning repository:', repoUrl, 'branch:', branch);
      await new Promise(resolve => setTimeout(resolve, 2000)); // Simulate API call
      setIsConnected(true);
      setSendMessage('Repository cloned successfully');
    } catch (error) {
      console.error('Clone failed:', error);
      setSendMessage('Failed to clone repository');
    } finally {
      setIsLoading(false);
    }
  };

  const handlePush = async () => {
    setIsLoading(true);
    try {
      // Simulate GitHub push
      console.log('Pushing changes to repository');
      await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate API call
      setSendMessage('Changes pushed successfully');
    } catch (error) {
      console.error('Push failed:', error);
      setSendMessage('Failed to push changes');
    } finally {
      setIsLoading(false);
    }
  };

  // File selection handler
  const handleFileSelect = async (filePath) => {
    setSelectedFile(filePath);
    setHasChanges(false);
    setSendStatus('idle');
    setSendMessage('');
    
    try {
      // Load Python file content
      const pyResponse = await fetch(`/api/file/${filePath}`);
      if (pyResponse.ok) {
        const pyData = await pyResponse.json();
        setPyContent(pyData.content);
      }
      
      // Load PHY output (human-readable format)
      const pyhPath = filePath.replace('.py', '.pyh.json');
      const pyhResponse = await fetch(`/api/pyh-output/${pyhPath}`);
      if (pyhResponse.ok) {
        const pyhData = await pyhResponse.json();
        setPyhContent(pyhData.content);
      } else {
        // Fallback to sample content if PHY file doesn't exist
        setPyhContent(samplePyhContent);
      }
    } catch (error) {
      console.error('Error loading files:', error);
      // Use sample content as fallback
      setPyhContent(samplePyhContent);
      setPyContent(samplePyContent);
    }
  };

  // Content change handlers
  const handlePyhContentChange = (content) => {
    setPyhContent(content);
    setHasChanges(true);
    setSendStatus('idle');
    setSendMessage('');
  };

  // Send changes handler
  const handleSendChanges = async () => {
    setSendStatus('idle');
    setProgress(0);
    setSendMessage('Validating changes...');
    
    try {
      // Simulate validation
      setProgress(25);
      await new Promise(resolve => setTimeout(resolve, 500));
      
      setSendMessage('Applying changes to Python code...');
      setProgress(50);
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setSendMessage('Running tests...');
      setProgress(75);
      await new Promise(resolve => setTimeout(resolve, 800));
      
      setProgress(100);
      setSendStatus('success');
      setSendMessage('Changes applied successfully! All tests passed.');
      setHasChanges(false);
      
      // Simulate updating the Python content
      setTimeout(() => {
        setPyContent(pyContent + '\n# Updated by HCLI');
      }, 1000);
      
    } catch (error) {
      setSendStatus('error');
      setSendMessage('Failed to apply changes: ' + error.message);
      setProgress(0);
    }
  };

  // Toggle Python editor mode
  const handleTogglePyMode = () => {
    setIsPyReadOnly(!isPyReadOnly);
  };

  return (
    <ThemeProvider theme={theme}>
      <AppContainer>
        <GitHubBar
          onClone={handleClone}
          onPush={handlePush}
          isConnected={isConnected}
          isLoading={isLoading}
        />
        
        <MainContent>
          <LeftPanel>
            <FileTree
              selectedFile={selectedFile}
              onFileSelect={handleFileSelect}
            />
          </LeftPanel>
          
          <RightPanel>
            <SplitContainer>
              <PanelGroup direction="horizontal">
                <Panel defaultSize={50} minSize={30}>
                  <PyhEditor
                    content={pyhContent}
                    onChange={handlePyhContentChange}
                    fileName={selectedFile ? selectedFile.replace('.py', '.pyh') : "main.pyh"}
                    hasChanges={hasChanges}
                    isReadOnly={true}
                  />
                </Panel>
                
                <ResizeHandle />
                
                <Panel defaultSize={50} minSize={30}>
                  <PyViewer
                    content={pyContent}
                    fileName="main.py"
                    isReadOnly={isPyReadOnly}
                    onToggleMode={handleTogglePyMode}
                  />
                </Panel>
              </PanelGroup>
            </SplitContainer>
            
            <SendButtonComponent
              onSend={handleSendChanges}
              isDisabled={!hasChanges || !isConnected}
              status={sendStatus}
              message={sendMessage}
              progress={progress}
            />
          </RightPanel>
        </MainContent>
      </AppContainer>
    </ThemeProvider>
  );
}

export default App;

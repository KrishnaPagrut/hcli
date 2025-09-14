import React from 'react';
import TopBar from './components/TopBar';
import FileExplorer from './components/FileExplorer';
import TwoPanelEditor from './components/TwoPanelEditor';
import SubmitButton from './components/SubmitButton';
import { useStore } from './hooks/useStore';

const App: React.FC = () => {
  const { isLoading, error, selectFile, editor } = useStore();

  const handleFileSelect = (filePath: string) => {
    console.log(`File selected: ${filePath}`);
    selectFile(filePath);
  };

  return (
    <div className="h-screen flex flex-col bg-neutral-50">
      <TopBar />
      
      <div className="flex-1 flex overflow-hidden">
        <FileExplorer onFileSelect={handleFileSelect} />
        
        <div className="flex-1 flex flex-col">
          <div className="flex-1">
            <TwoPanelEditor 
              pyhContent={editor.pyhContent}
              pyContent={editor.pyContent}
            />
          </div>
          <SubmitButton />
        </div>
      </div>

      {/* Loading overlay */}
      {isLoading && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 flex items-center space-x-3">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
            <span className="text-neutral-700">Loading...</span>
          </div>
        </div>
      )}

      {/* Error toast */}
      {error && (
        <div className="fixed top-4 right-4 bg-red-50 border border-red-200 rounded-lg p-4 shadow-lg z-50">
          <div className="flex items-center space-x-2">
            <div className="text-red-600">⚠️</div>
            <span className="text-red-800 text-sm">{error}</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;

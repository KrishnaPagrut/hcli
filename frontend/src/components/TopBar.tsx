import React, { useState, useEffect } from 'react';
import { useStore } from '../hooks/useStore';
import { FolderOpen, Search, Github } from 'lucide-react';

const TopBar: React.FC = () => {
  const [selectedBranch, setSelectedBranch] = useState('main');
  const [isDirectoryDialogOpen, setIsDirectoryDialogOpen] = useState(false);
  const [isGitHubDialogOpen, setIsGitHubDialogOpen] = useState(false);
  const [repoUrl, setRepoUrl] = useState('');
  const [directoryInput, setDirectoryInput] = useState('');
  const { crawlRepository, isLoading, repository, setCurrentDirectory, loadFiles, cloneGitHubRepo } = useStore();


  const handleCrawlDirectory = async () => {
    console.log("Crawling current directory:", repository.currentDirectory);
    await crawlRepository(repository.currentDirectory);
  };

  // Debounced directory loading
  useEffect(() => {
    const timer = setTimeout(() => {
      if (directoryInput.trim() && directoryInput !== repository.currentDirectory) {
        setCurrentDirectory(directoryInput.trim());
        loadFiles(directoryInput.trim());
      }
    }, 500); // 500ms delay

    return () => clearTimeout(timer);
  }, [directoryInput, repository.currentDirectory, setCurrentDirectory, loadFiles]);

  const handleDirectoryChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setDirectoryInput(event.target.value);
  };

  const handleDirectoryConfirm = async () => {
    setIsDirectoryDialogOpen(false);
    if (directoryInput.trim()) {
      setCurrentDirectory(directoryInput.trim());
      await loadFiles(directoryInput.trim());
    }
  };

  const handleDirectorySelect = () => {
    setDirectoryInput(repository.currentDirectory);
    setIsDirectoryDialogOpen(true);
  };

  const handleGitHubClone = () => {
    setIsGitHubDialogOpen(true);
  };

  const handleRepoUrlChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRepoUrl(event.target.value);
  };

  const handleGitHubConfirm = async () => {
    if (repoUrl.trim()) {
      setIsGitHubDialogOpen(false);
      await cloneGitHubRepo(repoUrl.trim());
      setRepoUrl('');
    }
  };

  const handleGitHubCancel = () => {
    setIsGitHubDialogOpen(false);
    setRepoUrl('');
  };

  const handleBranchChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const branch = event.target.value;
    setSelectedBranch(branch);
    console.log(`Selected branch: ${branch}`);
  };

  return (
    <div className="sticky top-0 z-50 bg-gray-100 border-b border-gray-300 shadow-sm">
      <div className="flex justify-between items-center px-4 py-2">
        {/* Left - GitHub Logo */}
        <div className="flex items-center">
          <svg 
            className="h-6 w-6 text-gray-600 mr-2" 
            fill="currentColor" 
            viewBox="0 0 24 24"
          >
            <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
          </svg>
          <span className="text-gray-800 font-medium">HCLI IDE</span>
        </div>

        {/* Center - Action Buttons */}
        <div className="flex-1 flex justify-center space-x-3">
          <button
            onClick={handleGitHubClone}
            disabled={isLoading}
            className="px-4 py-2 bg-gray-800 text-white rounded-md hover:bg-gray-900 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            <Github className="h-4 w-4" />
            <span>Clone GitHub</span>
          </button>
          
          <button
            onClick={handleCrawlDirectory}
            disabled={isLoading}
            className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            <Search className="h-4 w-4" />
            <span>Crawl</span>
          </button>
        </div>

        {/* Right - Directory and Branch Selectors */}
        <div className="flex items-center space-x-3">
          {/* Current Directory Display */}
          <div className="flex items-center space-x-2">
            <div className="flex items-center space-x-2 px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-700">
              <FolderOpen className="h-4 w-4" />
              <span className="text-sm max-w-64 truncate" title={repository.currentDirectory}>
                {repository.currentDirectory}
              </span>
            </div>
            <button
              onClick={handleDirectorySelect}
              className="px-3 py-2 border border-gray-300 rounded-md bg-white text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              Change
            </button>
          </div>
          
          {/* Branch Selector */}
          <select
            value={selectedBranch}
            onChange={handleBranchChange}
            className="px-3 py-2 border border-gray-300 rounded-md bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="main">main</option>
            <option value="dev">dev</option>
            <option value="feature-x">feature-x</option>
          </select>
        </div>
      </div>
      
      {/* Directory Selection Dialog */}
      {isDirectoryDialogOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-96 max-w-md mx-4">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Select Directory</h3>
            <div className="space-y-4">
              <div>
                <label htmlFor="directory-path" className="block text-sm font-medium text-gray-700 mb-2">
                  Directory Path
                </label>
                <input
                  type="text"
                  id="directory-path"
                  value={directoryInput}
                  onChange={handleDirectoryChange}
                  placeholder="/path/to/your/directory"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => setIsDirectoryDialogOpen(false)}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500"
                >
                  Cancel
                </button>
                <button
                  onClick={handleDirectoryConfirm}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  Load Directory
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* GitHub Clone Dialog */}
      {isGitHubDialogOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-96 max-w-md mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Clone GitHub Repository</h3>
            <div className="space-y-4">
              <div>
                <label htmlFor="repo-url" className="block text-sm font-medium text-gray-700 mb-2">
                  Repository URL
                </label>
                <input
                  id="repo-url"
                  type="url"
                  value={repoUrl}
                  onChange={handleRepoUrlChange}
                  placeholder="https://github.com/username/repository"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div className="flex justify-end space-x-3">
                <button
                  onClick={handleGitHubCancel}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500"
                >
                  Cancel
                </button>
                <button
                  onClick={handleGitHubConfirm}
                  disabled={!repoUrl.trim() || isLoading}
                  className="px-4 py-2 bg-gray-800 text-white rounded-md hover:bg-gray-900 focus:outline-none focus:ring-2 focus:ring-gray-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? 'Cloning...' : 'Clone Repository'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TopBar;

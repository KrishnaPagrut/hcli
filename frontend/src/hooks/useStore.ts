import { create } from 'zustand';
import { AppState, RepositoryState, EditorState } from '../types';

const initialRepositoryState: RepositoryState = {
  isConnected: false,
  repoUrl: '',
  branch: 'main',
  files: [],
  selectedFile: null,
  currentDirectory: '/Users/krishnapagrut/Developer/hcli_test',
};

const initialEditorState: EditorState = {
  pyhContent: '',
  pyContent: '',
  lineMappings: [],
  diffs: [],
  isEditing: false,
  hasUnsavedChanges: false,
};

interface AppStore extends AppState {
  // Repository actions
  setRepository: (repo: Partial<RepositoryState>) => void;
  setCurrentDirectory: (directory: string) => void;
  loadFiles: (directory?: string) => Promise<void>;
  cloneRepository: (url: string, branch: string) => Promise<void>;
  selectFile: (filePath: string) => Promise<void>;
  
  // Editor actions
  setEditor: (editor: Partial<EditorState>) => void;
  updatePyhContent: (content: string) => void;
  addDiff: (diff: any) => void;
  clearDiffs: () => void;
  
  // Workflow actions
  crawlRepository: (repoPath?: string) => Promise<void>;
  generatePyhForFile: (astFilePath: string) => Promise<void>;
  applyChanges: (pyFilePath: string) => Promise<void>;
  saveUserPhy: (pyFilePath: string, phyContent: string) => Promise<void>;
  applyPhyChanges: (pyFilePath: string) => Promise<void>;
  cloneGitHubRepo: (repoUrl: string) => Promise<void>;
  
  // App actions
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useStore = create<AppStore>((set, get) => ({
  // Initial state
  repository: initialRepositoryState,
  editor: initialEditorState,
  isLoading: false,
  error: null,

  // Repository actions
  setRepository: (repo) =>
    set((state) => ({
      repository: { ...state.repository, ...repo },
    })),

  setCurrentDirectory: (directory) =>
    set((state) => ({
      repository: { ...state.repository, currentDirectory: directory },
    })),

  loadFiles: async (directory?: string) => {
    set({ isLoading: true, error: null });
    try {
      const targetDirectory = directory || get().repository.currentDirectory;
      const response = await fetch(`/api/files?directory=${encodeURIComponent(targetDirectory)}`);
      
      if (!response.ok) {
        throw new Error('Failed to load files');
      }
      
      const data = await response.json();
      
      set({
        repository: {
          ...get().repository,
          files: data.files || [],
        },
        isLoading: false,
      });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to load files',
        isLoading: false,
      });
    }
  },

  cloneRepository: async (url: string, branch: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await fetch('/api/clone', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_url: url, branch }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to clone repository');
      }
      
      // Fetch files after cloning
      const filesResponse = await fetch(`/api/files?directory=${encodeURIComponent(get().repository.currentDirectory)}`);
      const filesData = await filesResponse.json();
      
      set({
        repository: {
          isConnected: true,
          repoUrl: url,
          branch,
          files: filesData.files,
          selectedFile: null,
          currentDirectory: get().repository.currentDirectory,
        },
        isLoading: false,
      });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Unknown error',
        isLoading: false,
      });
    }
  },

  selectFile: async (filePath: string) => {
    set({ isLoading: true, error: null });
    try {
      // Load Python file content
      const pyResponse = await fetch(`/api/file/${filePath}?directory=${encodeURIComponent(get().repository.currentDirectory)}`);
      const pyData = await pyResponse.json();
      
      // Load PHY output (human-readable format)
      const pyhResponse = await fetch(`/api/pyh-output/${filePath}?directory=${encodeURIComponent(get().repository.currentDirectory)}`);
      const pyhData = pyhResponse.ok ? await pyhResponse.json() : null;
      
      set((state) => ({
        repository: { ...state.repository, selectedFile: filePath },
        editor: {
          ...state.editor,
          pyContent: pyData.content,
          pyhContent: pyhData?.content || '',
          lineMappings: pyhData?.line_mappings || [],
          pyhData: pyhData?.phy_data || null,
          hasUnsavedChanges: false,
        },
        isLoading: false,
      }));
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to load file',
        isLoading: false,
      });
    }
  },

  // Editor actions
  setEditor: (editor) =>
    set((state) => ({
      editor: { ...state.editor, ...editor },
    })),

  updatePyhContent: (content) =>
    set((state) => ({
      editor: {
        ...state.editor,
        pyhContent: content,
        hasUnsavedChanges: true,
      },
    })),

  addDiff: (diff) =>
    set((state) => ({
      editor: {
        ...state.editor,
        diffs: [...state.editor.diffs, diff],
      },
    })),

  clearDiffs: () =>
    set((state) => ({
      editor: {
        ...state.editor,
        diffs: [],
      },
    })),

  // Workflow actions
  crawlRepository: async (repoPath?: string) => {
    set({ isLoading: true, error: null });
    try {
      const targetPath = repoPath || get().repository.currentDirectory;
      const response = await fetch('/api/crawl-repo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_path: targetPath }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to crawl repository');
      }
      
      const data = await response.json();
      console.log('Repository crawled:', data);
      
      // Load files after crawling
      await get().loadFiles(targetPath);
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to crawl repository',
        isLoading: false,
      });
    }
  },

  generatePyhForFile: async (astFilePath) => {
    set({ isLoading: true, error: null });
    try {
      const response = await fetch('/api/generate-pyh', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ast_file_path: astFilePath }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to generate PYH file');
      }
      
      const data = await response.json();
      console.log('PYH file generated:', data);
      
      set({ isLoading: false });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to generate PYH file',
        isLoading: false,
      });
    }
  },

  applyChanges: async (pyFilePath) => {
    set({ isLoading: true, error: null });
    try {
      const response = await fetch('/api/apply-changes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ py_file_path: pyFilePath }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to apply changes');
      }
      
      const data = await response.json();
      console.log('Changes applied:', data);
      
      // Clear unsaved changes after successful apply
      set((state) => ({
        editor: {
          ...state.editor,
          hasUnsavedChanges: false,
          diffs: [],
        },
        isLoading: false,
      }));
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to apply changes',
        isLoading: false,
      });
    }
  },

  saveUserPhy: async (pyFilePath: string, phyContent: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await fetch(`/api/save-user-phy?directory=${encodeURIComponent(get().repository.currentDirectory)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          py_file_path: pyFilePath, 
          phy_content: phyContent 
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to save user PHY content');
      }
      
      const data = await response.json();
      console.log('User PHY content saved:', data);
      
      set({ isLoading: false });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to save user PHY content',
        isLoading: false,
      });
    }
  },

  applyPhyChanges: async (pyFilePath: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await fetch(`/api/apply-phy-changes?directory=${encodeURIComponent(get().repository.currentDirectory)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ py_file_path: pyFilePath }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to apply PHY changes');
      }
      
      const data = await response.json();
      console.log('PHY changes applied:', data);
      
      // Clear unsaved changes after successful apply
      set((state) => ({
        editor: {
          ...state.editor,
          hasUnsavedChanges: false,
          diffs: [],
        },
        isLoading: false,
      }));
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to apply PHY changes',
        isLoading: false,
      });
    }
  },

  cloneGitHubRepo: async (repoUrl) => {
    set({ isLoading: true, error: null });
    try {
      const response = await fetch('/api/clone-repo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_url: repoUrl, force: false }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to clone repository');
      }
      
      const data = await response.json();
      console.log('Repository cloned:', data);
      
      // Update repository state with cloned repo info
      set((state) => ({
        repository: {
          ...state.repository,
          isConnected: true,
          repoUrl: repoUrl,
          currentDirectory: data.repo_path,
          files: data.files,
        },
        isLoading: false,
      }));
      
      // Auto-crawl the cloned repository
      console.log('Auto-crawling cloned repository...');
      await get().crawlRepository(data.repo_path);
      
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to clone repository',
        isLoading: false,
      });
    }
  },

  // App actions
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),
}));

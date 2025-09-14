import { create } from 'zustand';
import { AppState, RepositoryState, EditorState } from '../types';

const initialRepositoryState: RepositoryState = {
  isConnected: false,
  repoUrl: '',
  branch: 'main',
  files: [],
  selectedFile: null,
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
  cloneRepository: (url: string, branch: string) => Promise<void>;
  selectFile: (filePath: string) => Promise<void>;
  
  // Editor actions
  setEditor: (editor: Partial<EditorState>) => void;
  updatePyhContent: (content: string) => void;
  addDiff: (diff: any) => void;
  clearDiffs: () => void;
  
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
      const filesResponse = await fetch('/api/files');
      const filesData = await filesResponse.json();
      
      set({
        repository: {
          isConnected: true,
          repoUrl: url,
          branch,
          files: filesData.files,
          selectedFile: null,
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
      const pyResponse = await fetch(`/api/file/${filePath}`);
      const pyData = await pyResponse.json();
      
      // Load PHY output (human-readable format)
      const pyhResponse = await fetch(`/api/pyh-output/${filePath}`);
      const pyhData = pyhResponse.ok ? await pyhResponse.json() : null;
      
      set((state) => ({
        repository: { ...state.repository, selectedFile: filePath },
        editor: {
          ...state.editor,
          pyContent: pyData.content,
          pyhContent: pyhData?.content || '',
          lineMappings: pyhData?.line_mappings || [],
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

  // App actions
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),
}));

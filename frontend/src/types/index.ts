// Core types for the HCLI IDE

export interface FileNode {
  name: string;
  type: 'file' | 'directory';
  path: string;
  children?: FileNode[];
}

export interface LineMapping {
  pyhLine: number;
  pyLine: number;
  description: string;
  signature?: string;
  nodeId?: string;
  nodeType?: string;
  pyLineRange?: [number, number];
}

export interface DiffChange {
  type: 'added' | 'removed' | 'modified';
  lineRange: [number, number];
  originalContent: string;
  modifiedContent: string;
  description: string;
}

export interface PyhChunk {
  id: string;
  type: string;
  signature?: string;
  description: string;
  lineRange: [number, number];
  children?: PyhChunk[];
}

export interface RepositoryState {
  isConnected: boolean;
  repoUrl: string;
  branch: string;
  files: FileNode[];
  selectedFile: string | null;
  currentDirectory: string;
}

export interface EditorState {
  pyhContent: string;
  pyContent: string;
  lineMappings: LineMapping[];
  diffs: DiffChange[];
  isEditing: boolean;
  hasUnsavedChanges: boolean;
  pyhData?: any; // PHY AST data
}

export interface AppState {
  repository: RepositoryState;
  editor: EditorState;
  isLoading: boolean;
  error: string | null;
}

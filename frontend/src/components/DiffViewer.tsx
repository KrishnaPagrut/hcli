import React from 'react';
import { GitBranch, Plus, Minus, Edit3 } from 'lucide-react';
import { useStore } from '../hooks/useStore';
import { DiffChange } from '../types';

const DiffViewer: React.FC = () => {
  const { editor } = useStore();

  const getDiffIcon = (type: string) => {
    switch (type) {
      case 'added':
        return <Plus className="h-4 w-4 text-green-600" />;
      case 'removed':
        return <Minus className="h-4 w-4 text-red-600" />;
      case 'modified':
        return <Edit3 className="h-4 w-4 text-yellow-600" />;
      default:
        return <Edit3 className="h-4 w-4 text-neutral-600" />;
    }
  };

  const getDiffColor = (type: string) => {
    switch (type) {
      case 'added':
        return 'bg-green-50 border-green-200';
      case 'removed':
        return 'bg-red-50 border-red-200';
      case 'modified':
        return 'bg-yellow-50 border-yellow-200';
      default:
        return 'bg-neutral-50 border-neutral-200';
    }
  };

  const getDiffTextColor = (type: string) => {
    switch (type) {
      case 'added':
        return 'text-green-800';
      case 'removed':
        return 'text-red-800';
      case 'modified':
        return 'text-yellow-800';
      default:
        return 'text-neutral-800';
    }
  };

  if (editor.diffs.length === 0) {
    return (
      <div className="w-80 bg-white border-l border-neutral-200 flex flex-col">
        <div className="flex items-center px-4 py-2 bg-neutral-50 border-b border-neutral-200">
          <GitBranch className="h-4 w-4 text-neutral-500 mr-2" />
          <span className="text-sm font-medium text-neutral-700">Changes</span>
        </div>
        
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center text-neutral-500">
            <GitBranch className="h-12 w-12 mx-auto mb-3 text-neutral-300" />
            <p className="text-sm">No changes detected</p>
            <p className="text-xs mt-1">Edit the PHY file to see diffs</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-80 bg-white border-l border-neutral-200 flex flex-col">
      <div className="flex items-center justify-between px-4 py-2 bg-neutral-50 border-b border-neutral-200">
        <div className="flex items-center">
          <GitBranch className="h-4 w-4 text-neutral-500 mr-2" />
          <span className="text-sm font-medium text-neutral-700">Changes</span>
        </div>
        <span className="text-xs text-neutral-500">
          {editor.diffs.length} change{editor.diffs.length !== 1 ? 's' : ''}
        </span>
      </div>
      
      <div className="flex-1 overflow-y-auto">
        {editor.diffs.map((diff, index) => (
          <div
            key={index}
            className={`border-b border-neutral-100 p-3 ${getDiffColor(diff.type)}`}
          >
            <div className="flex items-start space-x-2">
              <div className="flex-shrink-0 mt-0.5">
                {getDiffIcon(diff.type)}
              </div>
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2 mb-1">
                  <span className={`text-xs font-medium ${getDiffTextColor(diff.type)}`}>
                    {diff.type.charAt(0).toUpperCase() + diff.type.slice(1)}
                  </span>
                  <span className="text-xs text-neutral-500">
                    Lines {diff.lineRange[0]}-{diff.lineRange[1]}
                  </span>
                </div>
                
                <div className="text-xs text-neutral-600 mb-2">
                  {diff.description}
                </div>
                
                {diff.originalContent && (
                  <div className="mb-2">
                    <div className="text-xs text-neutral-500 mb-1">Original:</div>
                    <div className="bg-neutral-100 rounded px-2 py-1 text-xs font-mono text-neutral-700">
                      {diff.originalContent}
                    </div>
                  </div>
                )}
                
                {diff.modifiedContent && (
                  <div>
                    <div className="text-xs text-neutral-500 mb-1">Modified:</div>
                    <div className="bg-neutral-100 rounded px-2 py-1 text-xs font-mono text-neutral-700">
                      {diff.modifiedContent}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DiffViewer;

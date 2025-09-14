import React, { useState } from 'react';
import { Send, Loader, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';
import { useStore } from '../hooks/useStore';

const SubmitButton: React.FC = () => {
  const { repository, applyPhyChanges, selectFile } = useStore();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error' | 'warning'>('idle');
  const [submitMessage, setSubmitMessage] = useState('');

  const handleSubmit = async () => {
    if (!repository.selectedFile) return;

    setIsSubmitting(true);
    setSubmitStatus('idle');
    setSubmitMessage('Applying changes...');

    try {
      // Use the new applyPhyChanges function from the store
      await applyPhyChanges(repository.selectedFile);
      
      setSubmitStatus('success');
      setSubmitMessage('PHY changes applied successfully!');
      
      // Reload the current file to show updated content instead of refreshing the page
      setTimeout(async () => {
        try {
          await selectFile(repository.selectedFile!);
          setSubmitStatus('idle');
          setSubmitMessage('');
        } catch (error) {
          console.error('Failed to reload file:', error);
          setSubmitStatus('warning');
          setSubmitMessage('Changes applied but failed to reload file. Please refresh manually.');
        }
      }, 2000);
    } catch (error) {
      setSubmitStatus('error');
      setSubmitMessage(error instanceof Error ? error.message : 'Unknown error occurred');
    } finally {
      setIsSubmitting(false);
    }
  };

  const getButtonVariant = () => {
    switch (submitStatus) {
      case 'success':
        return 'bg-green-600 hover:bg-green-700 text-white';
      case 'error':
        return 'bg-red-600 hover:bg-red-700 text-white';
      case 'warning':
        return 'bg-yellow-600 hover:bg-yellow-700 text-white';
      default:
        return 'bg-primary-600 hover:bg-primary-700 text-white';
    }
  };

  const getButtonIcon = () => {
    if (isSubmitting) {
      return <Loader className="h-4 w-4 animate-spin" />;
    }
    
    switch (submitStatus) {
      case 'success':
        return <CheckCircle className="h-4 w-4" />;
      case 'error':
        return <XCircle className="h-4 w-4" />;
      case 'warning':
        return <AlertTriangle className="h-4 w-4" />;
      default:
        return <Send className="h-4 w-4" />;
    }
  };

  const getButtonText = () => {
    if (isSubmitting) return 'Applying Changes...';
    
    switch (submitStatus) {
      case 'success':
        return 'Changes Applied Successfully';
      case 'error':
        return 'Apply Changes';
      case 'warning':
        return 'Apply Changes';
      default:
        return 'Apply Changes';
    }
  };

  const isDisabled = !repository.selectedFile || isSubmitting;

  return (
    <div className="bg-white border-t border-neutral-200 px-4 py-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={handleSubmit}
            disabled={isDisabled}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-colors disabled:bg-neutral-300 disabled:cursor-not-allowed ${getButtonVariant()}`}
          >
            {getButtonIcon()}
            <span>{getButtonText()}</span>
          </button>
          
          {repository.selectedFile && (
            <span className="text-sm text-neutral-600">
              Ready to apply PHY changes
            </span>
          )}
        </div>
        
        {submitMessage && (
          <div className={`text-sm px-3 py-1 rounded-md ${
            submitStatus === 'success' ? 'bg-green-50 text-green-700' :
            submitStatus === 'error' ? 'bg-red-50 text-red-700' :
            submitStatus === 'warning' ? 'bg-yellow-50 text-yellow-700' :
            'bg-neutral-50 text-neutral-700'
          }`}>
            {submitMessage}
          </div>
        )}
      </div>
    </div>
  );
};

export default SubmitButton;

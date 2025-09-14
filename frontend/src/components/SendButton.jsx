import React, { useState } from 'react';
import styled from 'styled-components';
import { Send, Loader, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';

const ButtonContainer = styled.div`
  padding: ${props => props.theme.spacing.lg};
  background: ${props => props.theme.colors.background.secondary};
  border-top: 1px solid ${props => props.theme.colors.border.light};
  display: flex;
  justify-content: center;
  align-items: center;
`;

const SendButton = styled.button`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.md};
  padding: ${props => props.theme.spacing.md} ${props => props.theme.spacing.xl};
  border: none;
  border-radius: ${props => props.theme.borderRadius.lg};
  font-size: ${props => props.theme.typography.fontSize.lg};
  font-weight: ${props => props.theme.typography.fontWeight.semibold};
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 200px;
  justify-content: center;
  
  ${props => props.variant === 'primary' && `
    background: ${props.theme.colors.primary[500]};
    color: ${props.theme.colors.text.inverse};
    box-shadow: ${props.theme.shadows.md};
    
    &:hover:not(:disabled) {
      background: ${props.theme.colors.primary[600]};
      transform: translateY(-1px);
      box-shadow: ${props.theme.shadows.lg};
    }
    
    &:active:not(:disabled) {
      transform: translateY(0);
    }
  `}
  
  ${props => props.variant === 'success' && `
    background: ${props.theme.colors.success[500]};
    color: ${props.theme.colors.text.inverse};
    box-shadow: ${props.theme.shadows.md};
  `}
  
  ${props => props.variant === 'error' && `
    background: ${props.theme.colors.error[500]};
    color: ${props.theme.colors.text.inverse};
    box-shadow: ${props.theme.shadows.md};
  `}
  
  ${props => props.variant === 'warning' && `
    background: ${props.theme.colors.warning[500]};
    color: ${props.theme.colors.text.inverse};
    box-shadow: ${props.theme.shadows.md};
  `}
  
  &:disabled {
    background: ${props => props.theme.colors.neutral[300]};
    color: ${props => props.theme.colors.neutral[500]};
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
  }
`;

const StatusMessage = styled.div`
  margin-top: ${props => props.theme.spacing.md};
  padding: ${props => props.theme.spacing.md};
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: ${props => props.theme.typography.fontSize.sm};
  font-weight: ${props => props.theme.typography.fontWeight.medium};
  text-align: center;
  
  ${props => props.type === 'success' && `
    background: ${props.theme.colors.success[50]};
    color: ${props.theme.colors.success[700]};
    border: 1px solid ${props.theme.colors.success[200]};
  `}
  
  ${props => props.type === 'error' && `
    background: ${props.theme.colors.error[50]};
    color: ${props.theme.colors.error[700]};
    border: 1px solid ${props.theme.colors.error[200]};
  `}
  
  ${props => props.type === 'warning' && `
    background: ${props.theme.colors.warning[50]};
    color: ${props.theme.colors.warning[700]};
    border: 1px solid ${props.theme.colors.warning[200]};
  `}
  
  ${props => props.type === 'info' && `
    background: ${props.theme.colors.primary[50]};
    color: ${props.theme.colors.primary[700]};
    border: 1px solid ${props.theme.colors.primary[200]};
  `}
`;

const ProgressBar = styled.div`
  width: 100%;
  height: 4px;
  background: ${props => props.theme.colors.neutral[200]};
  border-radius: ${props => props.theme.borderRadius.sm};
  overflow: hidden;
  margin-top: ${props => props.theme.spacing.sm};
`;

const ProgressFill = styled.div`
  height: 100%;
  background: ${props => props.theme.colors.primary[500]};
  border-radius: ${props => props.theme.borderRadius.sm};
  transition: width 0.3s ease;
  width: ${props => props.progress}%;
`;

const SendButtonComponent = ({ 
  onSend, 
  isDisabled = false, 
  status = 'idle',
  message = '',
  progress = 0 
}) => {
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async () => {
    if (isDisabled || isLoading) return;
    
    setIsLoading(true);
    try {
      await onSend();
    } finally {
      setIsLoading(false);
    }
  };

  const getButtonVariant = () => {
    switch (status) {
      case 'success': return 'success';
      case 'error': return 'error';
      case 'warning': return 'warning';
      default: return 'primary';
    }
  };

  const getButtonText = () => {
    if (isLoading) return 'Applying Changes...';
    switch (status) {
      case 'success': return 'Changes Applied Successfully';
      case 'error': return 'Apply Changes';
      case 'warning': return 'Apply Changes';
      default: return 'Apply Changes';
    }
  };

  const getButtonIcon = () => {
    if (isLoading) return <Loader size={20} className="animate-spin" />;
    switch (status) {
      case 'success': return <CheckCircle size={20} />;
      case 'error': return <XCircle size={20} />;
      case 'warning': return <AlertTriangle size={20} />;
      default: return <Send size={20} />;
    }
  };

  const getStatusType = () => {
    switch (status) {
      case 'success': return 'success';
      case 'error': return 'error';
      case 'warning': return 'warning';
      default: return 'info';
    }
  };

  return (
    <ButtonContainer>
      <div style={{ width: '100%', maxWidth: '400px' }}>
        <SendButton
          variant={getButtonVariant()}
          onClick={handleSend}
          disabled={isDisabled || isLoading}
        >
          {getButtonIcon()}
          {getButtonText()}
        </SendButton>
        
        {progress > 0 && progress < 100 && (
          <ProgressBar>
            <ProgressFill progress={progress} />
          </ProgressBar>
        )}
        
        {message && (
          <StatusMessage type={getStatusType()}>
            {message}
          </StatusMessage>
        )}
      </div>
    </ButtonContainer>
  );
};

export default SendButtonComponent;

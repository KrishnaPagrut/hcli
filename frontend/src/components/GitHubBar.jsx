import React, { useState } from 'react';
import styled from 'styled-components';
import { Github, Download, Upload, CheckCircle, XCircle } from 'lucide-react';
import theme from '../styles/theme';

const GitHubBarContainer = styled.div`
  background: ${props => props.theme.colors.background.primary};
  border-bottom: 1px solid ${props => props.theme.colors.border.light};
  padding: ${props => props.theme.spacing.md};
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.md};
  box-shadow: ${props => props.theme.shadows.sm};
`;

const InputGroup = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  flex: 1;
`;

const Input = styled.input`
  flex: 1;
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  border: 1px solid ${props => props.theme.colors.border.medium};
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: ${props => props.theme.typography.fontSize.sm};
  font-family: ${props => props.theme.typography.fontFamily.mono};
  
  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary[500]};
    box-shadow: 0 0 0 3px ${props => props.theme.colors.primary[100]};
  }
`;

const Button = styled.button`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  border: none;
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: ${props => props.theme.typography.fontSize.sm};
  font-weight: ${props => props.theme.typography.fontWeight.medium};
  cursor: pointer;
  transition: all 0.2s ease;
  
  ${props => props.variant === 'primary' && `
    background: ${props.theme.colors.primary[500]};
    color: ${props.theme.colors.text.inverse};
    
    &:hover {
      background: ${props.theme.colors.primary[600]};
    }
    
    &:disabled {
      background: ${props.theme.colors.neutral[300]};
      cursor: not-allowed;
    }
  `}
  
  ${props => props.variant === 'secondary' && `
    background: ${props.theme.colors.background.secondary};
    color: ${props.theme.colors.text.secondary};
    border: 1px solid ${props.theme.colors.border.medium};
    
    &:hover {
      background: ${props.theme.colors.background.tertiary};
    }
  `}
`;

const StatusIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: ${props => props.theme.typography.fontSize.sm};
  font-weight: ${props => props.theme.typography.fontWeight.medium};
  
  ${props => props.status === 'connected' && `
    background: ${props.theme.colors.success[50]};
    color: ${props.theme.colors.success[600]};
  `}
  
  ${props => props.status === 'disconnected' && `
    background: ${props.theme.colors.error[50]};
    color: ${props.theme.colors.error[600]};
  `}
  
  ${props => props.status === 'loading' && `
    background: ${props.theme.colors.warning[50]};
    color: ${props.theme.colors.warning[600]};
  `}
`;

const GitHubBar = ({ onClone, onPush, isConnected, isLoading }) => {
  const [repoUrl, setRepoUrl] = useState('');
  const [branch, setBranch] = useState('main');

  const handleClone = () => {
    if (repoUrl.trim()) {
      onClone(repoUrl.trim(), branch);
    }
  };

  const handlePush = () => {
    onPush();
  };

  const getStatus = () => {
    if (isLoading) return 'loading';
    return isConnected ? 'connected' : 'disconnected';
  };

  const getStatusText = () => {
    if (isLoading) return 'Connecting...';
    return isConnected ? 'Connected' : 'Disconnected';
  };

  return (
    <GitHubBarContainer>
      <Github size={20} color={theme.colors.neutral[600]} />
      
      <InputGroup>
        <Input
          type="text"
          placeholder="https://github.com/username/repository.git"
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
          disabled={isLoading}
        />
        
        <Input
          type="text"
          placeholder="branch"
          value={branch}
          onChange={(e) => setBranch(e.target.value)}
          disabled={isLoading}
          style={{ width: '120px' }}
        />
        
        <Button
          variant="primary"
          onClick={handleClone}
          disabled={isLoading || !repoUrl.trim()}
        >
          <Download size={16} />
          Clone
        </Button>
      </InputGroup>
      
      <Button
        variant="secondary"
        onClick={handlePush}
        disabled={!isConnected || isLoading}
      >
        <Upload size={16} />
        Push Changes
      </Button>
      
      <StatusIndicator status={getStatus()}>
        {getStatus() === 'connected' ? (
          <CheckCircle size={16} />
        ) : (
          <XCircle size={16} />
        )}
        {getStatusText()}
      </StatusIndicator>
    </GitHubBarContainer>
  );
};

export default GitHubBar;

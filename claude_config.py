"""
Claude Code SDK Configuration
This file contains pre-configured options for different use cases.
"""

from claude_code_sdk import ClaudeCodeOptions
from pathlib import Path
import os


class ClaudeConfig:
    """Pre-configured Claude Code options for different scenarios"""
    
    @staticmethod
    def basic_config():
        """Basic configuration for simple queries"""
        return ClaudeCodeOptions(
            system_prompt="You are a helpful AI assistant"
        )
    
    @staticmethod
    def development_config():
        """Configuration for development tasks"""
        return ClaudeCodeOptions(
            system_prompt="You are an expert Python developer. Write clean, well-documented code.",
            permission_mode='acceptEdits',
            cwd=os.getcwd(),
            allowed_tools=[
                "Read", "Write", "Edit", "MultiEdit", "Bash", 
                "Glob", "Grep", "WebSearch", "WebFetch"
            ]
        )
    
    @staticmethod
    def analysis_config():
        """Configuration for code analysis tasks"""
        return ClaudeCodeOptions(
            system_prompt="You are a code analysis expert. Provide detailed insights and recommendations.",
            permission_mode='plan',  # Planning mode - no execution
            allowed_tools=[
                "Read", "Glob", "Grep", "WebSearch"
            ]
        )
    
    @staticmethod
    def project_management_config():
        """Configuration for project management tasks"""
        return ClaudeCodeOptions(
            system_prompt="You are a project management assistant. Help organize, prioritize, and track tasks.",
            permission_mode='acceptEdits',
            allowed_tools=[
                "Read", "Write", "Edit", "Bash", "WebSearch"
            ]
        )
    
    @staticmethod
    def research_config():
        """Configuration for research tasks"""
        return ClaudeCodeOptions(
            system_prompt="You are a research assistant. Provide thorough, well-sourced information.",
            permission_mode='plan',
            allowed_tools=[
                "WebSearch", "WebFetch", "Read"
            ]
        )
    
    @staticmethod
    def custom_config(
        system_prompt: str = None,
        permission_mode: str = None,
        allowed_tools: list = None,
        cwd: str = None,
        **kwargs
    ):
        """Create a custom configuration"""
        config = ClaudeCodeOptions()
        
        if system_prompt:
            config.system_prompt = system_prompt
        if permission_mode:
            config.permission_mode = permission_mode
        if allowed_tools:
            config.allowed_tools = allowed_tools
        if cwd:
            config.cwd = cwd
            
        # Add any additional kwargs
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
                
        return config


# Pre-defined tool sets for common use cases
TOOL_SETS = {
    "file_operations": ["Read", "Write", "Edit", "MultiEdit", "Glob"],
    "code_analysis": ["Read", "Glob", "Grep"],
    "web_research": ["WebSearch", "WebFetch"],
    "system_commands": ["Bash"],
    "notebook_editing": ["NotebookEdit"],
    "task_management": ["TodoWrite"],
    "full_access": [
        "Read", "Write", "Edit", "MultiEdit", "Bash", "Glob", "Grep",
        "WebSearch", "WebFetch", "NotebookEdit", "TodoWrite"
    ]
}


def get_config_for_use_case(use_case: str, **overrides):
    """
    Get a pre-configured setup for common use cases
    
    Args:
        use_case: One of 'basic', 'development', 'analysis', 'project_management', 'research'
        **overrides: Additional parameters to override defaults
    
    Returns:
        ClaudeCodeOptions: Configured options
    """
    configs = {
        'basic': ClaudeConfig.basic_config,
        'development': ClaudeConfig.development_config,
        'analysis': ClaudeConfig.analysis_config,
        'project_management': ClaudeConfig.project_management_config,
        'research': ClaudeConfig.research_config
    }
    
    if use_case not in configs:
        raise ValueError(f"Unknown use case: {use_case}. Available: {list(configs.keys())}")
    
    config = configs[use_case]()
    
    # Apply overrides
    for key, value in overrides.items():
        if hasattr(config, key):
            setattr(config, key, value)
    
    return config


def add_tools_to_config(config: ClaudeCodeOptions, tool_set_name: str):
    """
    Add a predefined set of tools to a configuration
    
    Args:
        config: Existing ClaudeCodeOptions
        tool_set_name: Name of tool set from TOOL_SETS
    
    Returns:
        ClaudeCodeOptions: Updated configuration
    """
    if tool_set_name not in TOOL_SETS:
        raise ValueError(f"Unknown tool set: {tool_set_name}. Available: {list(TOOL_SETS.keys())}")
    
    tools = TOOL_SETS[tool_set_name]
    if config.allowed_tools:
        config.allowed_tools.extend(tools)
    else:
        config.allowed_tools = tools
    
    return config


# Example usage
if __name__ == "__main__":
    # Example 1: Get a development configuration
    dev_config = get_config_for_use_case('development')
    print("Development config:", dev_config.system_prompt)
    
    # Example 2: Get a custom configuration
    custom_config = get_config_for_use_case(
        'basic',
        system_prompt="You are a Python expert",
        permission_mode='acceptEdits',
        cwd='/path/to/project'
    )
    print("Custom config:", custom_config.system_prompt)
    
    # Example 3: Add tools to existing config
    basic_config = get_config_for_use_case('basic')
    add_tools_to_config(basic_config, 'file_operations')
    print("Basic config with file operations:", basic_config.allowed_tools)

"""Utility for managing .env file updates"""
import os
from pathlib import Path
from typing import Optional


class EnvManager:
    """Manage .env file updates"""
    
    def __init__(self, env_path: Optional[str] = None):
        """
        Initialize EnvManager
        
        Args:
            env_path: Path to .env file. If None, uses project root .env
        """
        if env_path is None:
            # Get project root (3 levels up from this file)
            backend_dir = Path(__file__).parent.parent.parent
            project_root = backend_dir.parent
            env_path = project_root / ".env"
        
        self.env_path = Path(env_path)
        
    def read_env(self) -> dict:
        """Read current .env file content as dictionary"""
        env_vars = {}
        
        if not self.env_path.exists():
            return env_vars
            
        with open(self.env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                    
                # Parse KEY=VALUE
                if '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
        
        return env_vars
    
    def write_env(self, env_vars: dict):
        """Write environment variables to .env file"""
        lines = []
        
        # Read existing file to preserve comments and order
        existing_lines = []
        if self.env_path.exists():
            with open(self.env_path, 'r', encoding='utf-8') as f:
                existing_lines = f.readlines()
        
        updated_keys = set()
        
        # Process existing lines
        for line in existing_lines:
            stripped = line.strip()
            
            # Keep comments and empty lines as-is
            if not stripped or stripped.startswith('#'):
                lines.append(line.rstrip())
                continue
            
            # Update existing key if in env_vars
            if '=' in stripped:
                key = stripped.split('=', 1)[0].strip()
                if key in env_vars:
                    lines.append(f"{key}={env_vars[key]}")
                    updated_keys.add(key)
                else:
                    lines.append(line.rstrip())
            else:
                lines.append(line.rstrip())
        
        # Add new keys that weren't in the file
        for key, value in env_vars.items():
            if key not in updated_keys:
                lines.append(f"{key}={value}")
        
        # Write back to file
        with open(self.env_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
            f.write('\n')  # Ensure file ends with newline
    
    def update_var(self, key: str, value: str):
        """Update single environment variable"""
        env_vars = self.read_env()
        env_vars[key] = value
        self.write_env(env_vars)
    
    def update_whatsapp_token(self, access_token: str):
        """
        Update WHATSAPP_ACCESS_TOKEN in .env file
        
        Args:
            access_token: The WhatsApp access token to save
        """
        self.update_var('WHATSAPP_ACCESS_TOKEN', access_token)
    
    def update_whatsapp_phone_number_id(self, phone_number_id: str):
        """
        Update WHATSAPP_PHONE_NUMBER_ID in .env file
        
        Args:
            phone_number_id: The WhatsApp phone number ID to save
        """
        self.update_var('WHATSAPP_PHONE_NUMBER_ID', phone_number_id)
    
    def update_whatsapp_business_account_id(self, waba_id: str):
        """
        Update WHATSAPP_BUSINESS_ACCOUNT_ID in .env file
        
        Args:
            waba_id: The WhatsApp Business Account ID to save
        """
        self.update_var('WHATSAPP_BUSINESS_ACCOUNT_ID', waba_id)
    
    def get_var(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get environment variable value"""
        env_vars = self.read_env()
        return env_vars.get(key, default)


# Global instance
env_manager = EnvManager()

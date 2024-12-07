import os
import subprocess
import json
from pathlib import Path
import pwd
import grp
from typing import Optional, Dict

class UserSetupError(Exception):
    """Custom exception for user setup errors"""
    pass

class CryFSManager:
    def __init__(self):
        self.config_dir = Path("/etc/cryfs-wizard")
        self.backup_config_dir = self.config_dir / "backup"
        
    def _confirm_action(self, message: str) -> bool:
        """
        Ask for user confirmation before proceeding with an action
        
        Args:
            message: The message describing the action to be confirmed
            
        Returns:
            bool: True if user confirmed, False otherwise
        """
        while True:
            response = input(f"{message} Your choice [y/n]: ").lower().strip()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            print("Please enter 'y' or 'n'")
        
    def setup_directories(self):
        """Create necessary configuration directories"""
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(self.backup_config_dir, exist_ok=True)
        
    def create_user(self, username: str, password: str, 
                    backup_config: Optional[Dict] = None) -> bool:
        """
        Create a new user with encrypted home directory
        
        Args:
            username: The username to create
            password: Password for the user
            backup_config: Optional backup configuration
        """
        try:
            # Check if user exists
            try:
                pwd.getpwnam(username)
                raise UserSetupError(f"User {username} already exists")
            except KeyError:
                pass

            # Confirm user creation
            if not self._confirm_action(f"Create new user '{username}'?"):
                raise UserSetupError("User creation cancelled")

            # Create user
            if self._confirm_action(f"Running: useradd -m {username}"):
                subprocess.run(['useradd', '-m', username], check=True)
            else:
                raise UserSetupError("User creation cancelled")
            
            # Set password
            if self._confirm_action("Set user password?"):
                proc = subprocess.Popen(['chpasswd'], stdin=subprocess.PIPE)
                proc.communicate(f"{username}:{password}".encode())
            else:
                raise UserSetupError("Password setup cancelled")
            
            # Setup encrypted directory
            crypt_base = Path(f"/home/.cryfs/{username}")
            mount_point = Path(f"/home/{username}")
            
            os.makedirs(crypt_base, exist_ok=True)
            
            # Initialize CryFS
            config_file = self.config_dir / f"{username}_cryfs.conf"
            
            cryfs_command = f"cryfs --config {config_file} {crypt_base} {mount_point}"
            print(f"\nCryFS setup command:\n{cryfs_command}")
            print("\nNote: When running manually, you'll need to enter the password when prompted")
            
            if self._confirm_action("Would you like the wizard to execute this command now?"):
                env = os.environ.copy()
                env['CRYFS_FRONTEND'] = 'noninteractive'
                env['CRYFS_NO_UPDATE_CHECK'] = 'true'
                
                subprocess.run([
                    'cryfs',
                    '--config', str(config_file),
                    '-o', 'nonempty',
                    '--create-missing-basedir',
                    '--create-missing-mountpoint',
                    str(crypt_base),
                    str(mount_point)
                ], input=password.encode(), check=True, env=env)
                
                # Set correct ownership and permissions
                uid = pwd.getpwnam(username).pw_uid
                gid = grp.getgrnam(username).gr_gid
                
                # Change ownership of mount point to user
                subprocess.run(['chown', f'{username}:{username}', str(mount_point)], check=True)
                # Set permissions to 700 (rwx------)
                subprocess.run(['chmod', '700', str(mount_point)], check=True)
            else:
                print("\nSkipping automatic CryFS setup.")
                print("Please run the command manually to complete the encryption setup.")
                return True
            
            # Setup backup if configured
            if backup_config:
                self._setup_backup(username, backup_config)
            
            return True
            
        except Exception as e:
            raise UserSetupError(f"Failed to create user: {str(e)}")
    
    def _setup_backup(self, username: str, backup_config: Dict):
        """Setup rclone backup configuration"""
        if not self._confirm_action(f"Setup automatic backup for user '{username}'?"):
            raise UserSetupError("Backup setup cancelled")
            
        backup_conf = self.backup_config_dir / f"{username}_rclone.conf"
        
        # Create rclone config
        with open(backup_conf, 'w') as f:
            json.dump(backup_config, f)
            
        # Setup systemd service for automatic backup
        service_content = f"""[Unit]
Description=Backup service for {username}
After=network.target

[Service]
Type=oneshot
User={username}
ExecStart=/usr/bin/rclone sync /home/{username} remote:{username}-backup --config {backup_conf}

[Install]
WantedBy=multi-user.target
"""
        
        service_file = Path(f"/etc/systemd/system/backup-{username}.service")
        with open(service_file, 'w') as f:
            f.write(service_content)
            
        # Enable and start the service
        if self._confirm_action("Enable and start backup service?"):
            subprocess.run(['systemctl', 'enable', f'backup-{username}.service'])
            subprocess.run(['systemctl', 'start', f'backup-{username}.service'])
        else:
            raise UserSetupError("Backup service setup cancelled")

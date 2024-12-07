import click
from .core import CryFSManager, UserSetupError

@click.command()
@click.option('--username', prompt='Username', help='Username to create')
@click.option('--password', prompt=True, hide_input=True, 
              confirmation_prompt=True, help='User password')
@click.option('--backup/--no-backup', default=False, 
              help='Configure automatic backup')
def main(username: str, password: str, backup: bool):
    """Create a new user with encrypted home directory"""
    try:
        manager = CryFSManager()
        manager.setup_directories()
        
        backup_config = None
        if backup:
            backup_config = {
                'type': 'remote',
                'url': click.prompt('Backup server URL'),
                'user': click.prompt('Backup server username'),
                'password': click.prompt('Backup server password', 
                                      hide_input=True)
            }
        
        manager.create_user(username, password, backup_config)
        click.echo(f"Successfully created user {username}")
        
    except UserSetupError as e:
        click.echo(f"Error: {str(e)}", err=True)
        exit(1)

if __name__ == '__main__':
    main()

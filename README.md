# CryFS Wizard

A setup wizard for creating encrypted home directories with backup capabilities using CryFS and rclone.

## Features

- Create new system users with encrypted home directories using CryFS
- Optional automatic backup configuration using rclone
- Both GUI and CLI interfaces
- Secure password handling
- Systemd service integration for automated backups

## Requirements

- Debian Bookworm or compatible system
- Python 3.8 or higher
- Root/sudo privileges for user creation and system configuration

## Installation

1. Install system dependencies:
```bash
sudo apt install $(cat packages.txt)
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install the package:
```bash
pip install .
```

## Usage

### GUI Interface

Run the graphical wizard:
```bash
sudo -E cryfs-wizard-gui
```

The wizard will guide you through:
1. Creating a new username
2. Setting a secure password
3. Configuring optional remote backup

### CLI Interface

Run the command-line interface:
```bash
sudo cryfs-wizard-cli
```

Or with direct options:
```bash
sudo cryfs-wizard-cli --username newuser --backup
```

## Security

- Passwords are never stored in plaintext
- CryFS provides strong encryption for home directories
- Backup credentials are stored in protected configuration files
- All system operations require root privileges

## Project Structure

- `core.py`: Main CryFSManager class for user and backup management
- `gui.py`: PyQt5-based wizard interface
- `cli.py`: Click-based command line interface
- `packages.txt`: Required system packages

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

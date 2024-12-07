import sys
from PyQt5.QtWidgets import (QApplication, QWizard, QWizardPage, 
                            QLineEdit, QVBoxLayout, QLabel, 
                            QCheckBox, QMessageBox)
from .core import CryFSManager, UserSetupError

class UsernamePage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Create New User")
        
        layout = QVBoxLayout()
        
        username_label = QLabel("Username:")
        self.username_edit = QLineEdit()
        self.registerField("username*", self.username_edit)
        
        layout.addWidget(username_label)
        layout.addWidget(self.username_edit)
        self.setLayout(layout)

class PasswordPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Set Password")
        
        layout = QVBoxLayout()
        
        password_label = QLabel("Password:")
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.registerField("password*", self.password_edit)
        
        confirm_label = QLabel("Confirm Password:")
        self.confirm_edit = QLineEdit()
        self.confirm_edit.setEchoMode(QLineEdit.Password)
        self.registerField("confirm*", self.confirm_edit)
        
        layout.addWidget(password_label)
        layout.addWidget(self.password_edit)
        layout.addWidget(confirm_label)
        layout.addWidget(self.confirm_edit)
        self.setLayout(layout)
        
    def validatePage(self):
        if self.field("password") != self.field("confirm"):
            QMessageBox.warning(self, "Error", "Passwords do not match!")
            return False
        return True

class BackupPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Backup Configuration")
        
        layout = QVBoxLayout()
        
        self.backup_check = QCheckBox("Enable automatic backup")
        self.registerField("enable_backup", self.backup_check)
        
        self.server_edit = QLineEdit()
        self.server_edit.setPlaceholderText("Backup server URL")
        self.registerField("server", self.server_edit)
        
        self.backup_user = QLineEdit()
        self.backup_user.setPlaceholderText("Backup server username")
        self.registerField("backup_user", self.backup_user)
        
        self.backup_pass = QLineEdit()
        self.backup_pass.setPlaceholderText("Backup server password")
        self.backup_pass.setEchoMode(QLineEdit.Password)
        self.registerField("backup_pass", self.backup_pass)
        
        layout.addWidget(self.backup_check)
        layout.addWidget(self.server_edit)
        layout.addWidget(self.backup_user)
        layout.addWidget(self.backup_pass)
        self.setLayout(layout)

class SetupWizard(QWizard):
    def __init__(self):
        super().__init__()
        
        self.addPage(UsernamePage())
        self.addPage(PasswordPage())
        self.addPage(BackupPage())
        
        self.setWindowTitle("CryFS User Setup Wizard")
        
    def accept(self):
        try:
            manager = CryFSManager()
            manager.setup_directories()
            
            backup_config = None
            if self.field("enable_backup"):
                backup_config = {
                    'type': 'remote',
                    'url': self.field("server"),
                    'user': self.field("backup_user"),
                    'password': self.field("backup_pass")
                }
            
            manager.create_user(
                self.field("username"),
                self.field("password"),
                backup_config
            )
            
            QMessageBox.information(self, "Success", 
                                  "User created successfully!")
            super().accept()
            
        except UserSetupError as e:
            QMessageBox.critical(self, "Error", str(e))

def main():
    app = QApplication(sys.argv)
    wizard = SetupWizard()
    wizard.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

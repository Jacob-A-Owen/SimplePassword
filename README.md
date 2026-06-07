# SimplePassword

## Screenshot

![SimplePassword Screenshot](screenshot.png)

SimplePassword is a command-line password manager built in Python. The application allows users to create accounts, authenticate with a master password, securely store login credentials, generate strong passwords, search saved entries, and manage encrypted password records.

## Features

- User account creation and login
- Master password authentication
- SHA-256 password hashing
- Fernet encryption for stored credentials
- Add, view, search, and remove saved passwords
- Random password generation
- Persistent storage using JSON files
- Fuzzy search functionality using Difflib

## Technologies Used

- Python
- Cryptography (Fernet)
- Hashlib (SHA-256)
- JSON
- Difflib
- File I/O

## What I Learned

This project helped me gain experience with:

- User authentication and access control
- Password hashing and verification
- Symmetric encryption using Fernet
- Secure credential storage practices
- JSON-based data persistence
- Python file handling and data management
- Building menu-driven command-line applications

## How To Run

Install the required package:

```bash
pip install cryptography
```

Run the application:

```bash
python SimplePassword.py
```

## Project Structure

```text
SimplePassword.py
README.md
.gitignore
```

User data and encryption keys are generated locally when accounts are created and are excluded from GitHub using the .gitignore file.

## Future Improvements

- Export encrypted password backups
- Password strength analytics
- GUI version using Tkinter
- Multi-factor authentication
- Password breach checking API integration
- Cloud synchronization support

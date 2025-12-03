# Secure File Transfer System - User Manual

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Features Overview](#features-overview)
4. [How to Use](#how-to-use)
5. [SFTP Transfer (Server-to-Server)](#sftp-transfer-server-to-server)
6. [Troubleshooting](#troubleshooting)
7. [Security Features](#security-features)

---

## Introduction

The Secure File Transfer System is a web-based application that allows you to securely upload, download, and manage files with enterprise-grade encryption. All files are encrypted using hybrid encryption (AES-256 + RSA-2048) to ensure maximum security.

---

## Getting Started

### Accessing the System

1. Open your web browser and navigate to: `http://localhost:3000`
2. You will see the login page

### Creating an Account

1. Click on **"Register"** or navigate to the registration page
2. Fill in the required information:
   - **Username**: Choose a unique username
   - **Email**: Enter your email address
   - **Password**: Create a strong password (minimum 8 characters)
3. Click **"Register"**
4. You will be automatically logged in after successful registration

### Logging In

1. Enter your **username** and **password**
2. Click **"Login"**
3. You will be redirected to your dashboard

---

## Features Overview

### 🔐 Security Features
- **Hybrid Encryption**: Files are encrypted using AES-256 (symmetric) and RSA-2048 (asymmetric) encryption
- **Integrity Verification**: SHA-256 hash verification ensures files haven't been tampered with
- **Secure Authentication**: JWT-based authentication with secure token storage
- **Access Control**: Users can only access their own files (admins can access all)

### 📁 File Management
- **Upload Files**: Securely upload files of any type
- **Download Files**: Download and decrypt your files
- **Delete Files**: Remove files from the system
- **File List**: View all your uploaded files with details
- **Search Files**: Search through your files by name, type, or date
- **Pagination**: Navigate through large file lists with pagination controls

### 🔄 SFTP Transfer (Server-to-Server)
- **Encrypted SFTP Upload**: Encrypt files and transfer them to remote SFTP servers
- **Encrypted SFTP Download**: Download encrypted files from SFTP servers and decrypt them
- **Secure Transfer**: Files remain encrypted during SFTP transfer
- **Key Management**: Automatic encryption key generation and management

### 👨‍💼 Admin Features (Admin Users Only)
- **User Management**: View all registered users
- **Transfer Logs**: Monitor all file transfers
- **System Logs**: View system activity logs

---

## How to Use

### Uploading a File

1. **Navigate to Dashboard**: After logging in, you'll see the dashboard
2. **Click "Choose File"**: Click the button in the "Upload File" card
3. **Select File**: Choose the file you want to upload from your computer
4. **Wait for Upload**: 
   - A progress bar will show the upload progress
   - The file will be automatically encrypted during upload
   - You'll see a success message when complete
5. **File Appears in List**: The uploaded file will appear in the "My Files" section

**Note**: 
- Files are encrypted immediately upon upload
- The original filename is preserved
- File size and upload date are displayed

### Downloading a File

1. **Find Your File**: Locate the file in the "My Files" list
2. **Click Download Icon**: Click the download icon (⬇️) next to the file
3. **File Downloads**: 
   - The file will be automatically decrypted
   - It will download to your default download folder
   - The original filename will be preserved

**Troubleshooting Downloads**:
- If download fails, make sure you're logged in
- Old files (uploaded before the encryption update) may need to be re-uploaded
- Check your browser's download settings

### Deleting a File

1. **Find Your File**: Locate the file in the "My Files" list
2. **Click Delete Icon**: Click the delete icon (🗑️) next to the file
3. **Confirm Deletion**: Click "OK" in the confirmation dialog
4. **File Removed**: The file will be removed from both the system and your file list

**Warning**: 
- Deleted files cannot be recovered
- Both the encrypted file and database record are permanently deleted

### Viewing File Information

Each file in the "My Files" list shows:
- **Filename**: The original filename
- **File Size**: Size in Bytes, KB, MB, or GB
- **Upload Date**: When the file was uploaded

### Searching Files

1. **Use the Search Bar**: Located above the file list
2. **Enter Search Term**: Type any part of the filename, file type, size, or date
3. **Results Filter**: The list will automatically filter as you type
4. **Clear Search**: Delete the search text to see all files again

### Pagination

When you have many files:
- **Page Navigation**: Use the pagination controls at the bottom of the file list
- **Items Per Page**: Default is 10 files per page
- **Page Info**: Shows "Showing X-Y of Z files" to indicate your current view
- **Navigation Buttons**: Use First, Previous, Next, and Last buttons to navigate

---

## SFTP Transfer (Server-to-Server)

The Secure SFTP Transfer feature allows you to encrypt files and transfer them securely between servers via SFTP. Files are encrypted before transfer and can be decrypted on the receiving server.

### Understanding SFTP Transfer

**Workflow:**
- **Server A (Your System)**: Where you upload and encrypt files
- **Server B (Remote SFTP Server)**: Where encrypted files are stored
- **Encryption**: Files are encrypted using AES-256 + RSA-2048 before transfer
- **Transfer**: Encrypted files are transferred via secure SFTP protocol
- **Decryption**: Files can be downloaded and decrypted using encryption keys

### Uploading to SFTP Server (Server A → Server B)

**Step-by-Step Guide:**

1. **Navigate to SFTP Transfer Section**:
   - Scroll down on the Dashboard to find "Secure SFTP Transfer (Server A ↔ Server B)"
   - Click on the **"Upload to SFTP Server"** tab

2. **Configure SFTP Server Details**:
   - **SFTP Host (Server B)**: Enter the hostname or IP address of the remote SFTP server
     - Example: `sftp.example.com` or `192.168.1.100`
   - **SFTP Port**: Enter the SFTP port (default is 22)
   - **SFTP Username**: Enter your SSH/SFTP username for Server B
   - **SFTP Password**: Enter your SSH/SFTP password (optional if using SSH keys)
   - **Remote Path**: Specify where the file should be stored on Server B
     - Example: `/tmp/secure_transfers/myfile.enc`
     - If left empty, defaults to `/tmp/secure_transfers/[filename].enc`

3. **Select and Upload File**:
   - Click **"Choose File & Transfer to SFTP Server"**
   - Select the file you want to transfer
   - The system will:
     - Encrypt the file using hybrid encryption
     - Upload the encrypted file to the SFTP server
     - Display encryption keys for later decryption

4. **Save Encryption Keys**:
   - **Important**: After successful upload, you'll receive two keys:
     - **Encryption Key**: Used to decrypt the AES key
     - **Private Key**: Used for RSA decryption
   - **Copy these keys**: Click on the key fields to select and copy them
   - **Store securely**: Save these keys - you'll need them to decrypt the file later
   - **Auto-fill**: Keys are automatically filled in the download form for convenience

**What Happens:**
- File is encrypted on Server A
- Encrypted file is transferred to Server B via SFTP
- File remains encrypted on Server B
- Only someone with the encryption keys can decrypt it

### Downloading from SFTP Server (Server B → Server A)

**Step-by-Step Guide:**

1. **Navigate to Download Tab**:
   - In the "Secure SFTP Transfer" section, click **"Download from SFTP Server"** tab

2. **Configure SFTP Server Details**:
   - **SFTP Host (Server B)**: Enter the hostname or IP address of the remote SFTP server
   - **SFTP Port**: Enter the SFTP port (default is 22)
   - **SFTP Username**: Enter your SSH/SFTP username for Server B
   - **SFTP Password**: Enter your SSH/SFTP password (if required)
   - **Remote Path**: Enter the full path to the encrypted file on Server B
     - Example: `/tmp/secure_transfers/myfile.enc`

3. **Provide Encryption Keys**:
   - **Encryption Key**: Paste the encryption key from the upload operation
   - **Private Key**: Paste the private key from the upload operation
   - **Note**: If you uploaded the file using this system, keys are auto-filled

4. **Download and Decrypt**:
   - Click **"Download & Decrypt from SFTP Server"**
   - The system will:
     - Connect to the SFTP server
     - Download the encrypted file
     - Decrypt the file using the provided keys
     - Download the decrypted file to your computer

**What Happens:**
- Encrypted file is downloaded from Server B
- File is decrypted using the provided keys
- Decrypted file is saved to your download folder
- Original filename is restored (`.enc` extension removed)

### SFTP Authentication Methods

The system supports two authentication methods:

1. **Password Authentication**:
   - Enter your SFTP username and password
   - Simple and straightforward
   - Recommended for testing and development

2. **SSH Key Authentication** (Advanced):
   - Use SSH private keys instead of passwords
   - More secure for production environments
   - Contact your administrator for SSH key setup

### SFTP Transfer Best Practices

1. **Save Your Keys**:
   - Always save encryption keys after upload
   - Store them securely (password manager, encrypted file)
   - Without keys, files cannot be decrypted

2. **Verify Server Details**:
   - Double-check SFTP host, port, and credentials
   - Test connection before transferring important files
   - Ensure you have write permissions on the remote path

3. **Network Considerations**:
   - Large files may take time to transfer
   - Ensure stable network connection
   - SFTP transfers are resumable in case of interruption

4. **Security**:
   - Use strong SFTP passwords
   - Prefer SSH key authentication for production
   - Keep encryption keys secure and private
   - Don't share keys via insecure channels

5. **File Naming**:
   - Use descriptive filenames
   - The `.enc` extension is automatically added during upload
   - Original filename is preserved during download

### SFTP Troubleshooting

**Connection Failed:**
- Verify SFTP host and port are correct
- Check if the SFTP server is accessible from your network
- Ensure firewall allows SFTP connections (port 22 by default)
- Verify username and password are correct

**Upload Failed:**
- Check if you have write permissions on the remote path
- Verify the remote directory exists or can be created
- Ensure sufficient disk space on the remote server
- Check network connectivity

**Download Failed:**
- Verify the remote file path is correct
- Ensure the file exists on the SFTP server
- Check if encryption keys are correct and complete
- Verify you have read permissions on the remote file

**Decryption Failed:**
- Ensure encryption keys match the uploaded file
- Verify keys are copied completely (no truncation)
- Check if keys are from the same upload operation
- Try re-uploading the file if keys are lost

**Authentication Errors:**
- Verify username and password are correct
- Check if SSH key authentication is required instead
- Ensure account is not locked or expired
- Contact SFTP server administrator if issues persist

---

## Dashboard Interface

### Main Components

1. **Top Navigation Bar**:
   - System title
   - Your username and role
   - Admin button (if you're an admin)
   - Logout button

2. **Upload File Card** (Left Side):
   - "Choose File" button
   - Upload progress bar (when uploading)

3. **My Files Card** (Right Side):
   - List of all your uploaded files
   - Search bar to filter files
   - Download and Delete buttons for each file
   - File information (name, size, date)
   - Pagination controls for large file lists

4. **Secure SFTP Transfer Section** (Below File List):
   - Two tabs: "Upload to SFTP Server" and "Download from SFTP Server"
   - SFTP server configuration forms
   - Encryption key management
   - Transfer status messages

---

## Admin Features

If you have admin privileges, you'll see an **"Admin"** button in the top navigation bar.

### Admin Dashboard Features:

1. **User Management**:
   - View all registered users
   - See user roles and registration dates

2. **Transfer Logs**:
   - Monitor all file uploads and downloads
   - View transfer times and file sizes
   - Track IP addresses

3. **System Logs**:
   - View all system activities
   - Monitor admin actions
   - Track file operations

---

## Troubleshooting

### Common Issues

#### "Upload failed" Error
- **Check your internet connection**
- **Verify file size**: Very large files may take longer
- **Try again**: Sometimes network issues cause temporary failures
- **Check browser console**: Press F12 to see detailed error messages

#### "Download failed" Error
- **Verify you're logged in**: Your session may have expired
- **Re-login**: Log out and log back in
- **Old files**: Files uploaded before the encryption update need to be re-uploaded
- **Check file exists**: The file may have been deleted

#### "Delete failed" Error
- **Check permissions**: Make sure you own the file
- **Try refreshing**: Refresh the page and try again
- **Contact admin**: If the issue persists, contact your administrator

#### Can't See Files
- **Refresh the page**: Click the refresh button or press F5
- **Check login**: Make sure you're logged in
- **Clear cache**: Clear your browser cache and cookies

#### Session Expired
- **Re-login**: Your session may have expired
- **Check token**: The authentication token may be invalid
- **Clear storage**: Clear browser local storage and re-login

### Browser Compatibility

- **Chrome/Edge**: Fully supported (recommended)
- **Firefox**: Fully supported
- **Safari**: Supported (may have minor UI differences)
- **Opera**: Supported

### File Size Limits

- **Recommended**: Files under 100MB for best performance
- **Maximum**: Depends on server configuration (typically 100MB-1GB)
- **Large files**: May take longer to encrypt/decrypt

---

## Security Features Explained

### Encryption Process

1. **Upload**:
   - File is read into memory
   - A random AES-256 key is generated
   - File is encrypted with AES-256
   - AES key is encrypted with RSA-2048 public key
   - Both encrypted file and encrypted key are stored
   - SHA-256 hash is calculated for integrity verification

2. **Storage**:
   - Encrypted file is stored on the server
   - Encrypted keys are stored in the database
   - Original filename and metadata are stored separately

3. **Download**:
   - Encrypted file is retrieved
   - RSA private key is decrypted using master secret
   - AES key is decrypted using RSA private key
   - File is decrypted using AES key
   - SHA-256 hash is verified
   - Decrypted file is sent to your browser

### Best Practices

1. **Strong Passwords**: Use a strong, unique password
2. **Logout**: Always log out when finished, especially on shared computers
3. **File Names**: Avoid special characters in filenames
4. **Backup**: Keep backups of important files
5. **Updates**: Re-upload files if you encounter encryption-related errors

---

## Keyboard Shortcuts

- **F5**: Refresh the page
- **Ctrl/Cmd + F**: Search (in browser)
- **Esc**: Close dialogs (if applicable)

---

## Getting Help

### If You Need Assistance:

1. **Check this manual**: Review the troubleshooting section
2. **Browser Console**: Press F12 and check for error messages
3. **Contact Admin**: If you're an admin user, check the system logs
4. **Report Issues**: Note the error message and steps to reproduce

### Error Messages Explained

- **401 Unauthorized**: Your session expired - please log in again
- **403 Forbidden**: You don't have permission to access this resource
- **404 Not Found**: The requested file or resource doesn't exist
- **500 Internal Server Error**: Server error - try again or contact support

---

## System Requirements

### Client Side (Your Browser):
- Modern web browser (Chrome, Firefox, Safari, Edge)
- JavaScript enabled
- Cookies enabled
- Local storage enabled

### Server Side:
- Python 3.11+
- Flask backend
- React frontend
- Docker (for containerized deployment)

---

## Frequently Asked Questions (FAQ)

**Q: Can I upload multiple files at once?**  
A: Currently, you can upload one file at a time. Upload multiple files by repeating the upload process.

**Q: What file types are supported?**  
A: All file types are supported - documents, images, videos, archives, etc.

**Q: How secure is my data?**  
A: Files are encrypted with AES-256 and RSA-2048 encryption. Only you (and admins) can decrypt your files.

**Q: Can I recover deleted files?**  
A: No, deleted files are permanently removed and cannot be recovered.

**Q: How long are files stored?**  
A: Files are stored indefinitely until you delete them or an admin removes them.

**Q: Can I share files with other users?**  
A: Currently, files are private to each user. Sharing functionality may be added in future versions.

**Q: How does SFTP transfer work?**  
A: Files are encrypted on Server A, transferred via SFTP to Server B, and can be decrypted using the encryption keys provided during upload.

**Q: What if I lose my encryption keys?**  
A: Without encryption keys, files cannot be decrypted. Always save your keys securely after uploading files via SFTP.

**Q: Can I use SSH keys instead of passwords for SFTP?**  
A: Yes, SSH key authentication is supported. Contact your administrator for SSH key setup instructions.

**Q: What's the difference between regular upload and SFTP upload?**  
A: Regular upload stores files on the current server. SFTP upload transfers encrypted files to a remote SFTP server, allowing server-to-server transfers.

**Q: What happens if I forget my password?**  
A: Contact your administrator to reset your password.

**Q: Can I change my username or email?**  
A: Username and email changes require administrator assistance.

---

## Version Information

- **Current Version**: 2.0
- **Last Updated**: December 2025
- **Encryption**: AES-256 + RSA-2048
- **Authentication**: JWT (JSON Web Tokens)
- **New Features**: 
  - SFTP Server-to-Server Transfer
  - File Search and Pagination
  - Enhanced Navigation
  - Improved Error Handling

---

## Support

For technical support or questions:
1. Check this manual first
2. Review the troubleshooting section
3. Contact your system administrator
4. Check system logs (if you have admin access)

---

**Thank you for using the Secure File Transfer System!**


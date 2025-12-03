# Secure File Transfer System - System Guide

## What This System Does

The **Secure File Transfer System** is an enterprise-grade web application designed for secure file storage and transfer. It provides end-to-end encryption, ensuring that your files remain protected both in transit and at rest.

---

## System Overview

### Core Purpose
This system allows users to:
- **Securely upload** files with automatic encryption
- **Download** files with automatic decryption
- **Manage** their file library (view, delete)
- **Monitor** file transfers in real-time (for administrators)

### Key Features

#### 🔐 Security Features
1. **Hybrid Encryption**
   - Files are encrypted using **AES-256** (Advanced Encryption Standard)
   - Encryption keys are protected using **RSA-2048** (Rivest-Shamir-Adleman)
   - This combination provides both speed (AES) and key security (RSA)

2. **Integrity Verification**
   - Every file is verified using **SHA-256** hash
   - Ensures files haven't been tampered with or corrupted
   - Automatic verification on download

3. **Secure Authentication**
   - **JWT (JSON Web Tokens)** for session management
   - Password hashing using **bcrypt**
   - Role-based access control (User/Admin)

4. **Access Control**
   - Users can only access their own files
   - Administrators have access to all files and system logs
   - All actions are logged for audit purposes

#### 📁 File Management
- **Upload**: Encrypt and store files securely
- **Download**: Decrypt and retrieve files
- **Delete**: Permanently remove files and related data
- **List**: View all your uploaded files with metadata

#### 📊 Monitoring & Logging
- **Real-time Updates**: Socket.IO-based live transfer monitoring
- **Transfer Logs**: Track all uploads and downloads
- **System Logs**: Monitor all system activities
- **Admin Dashboard**: Comprehensive system overview for administrators

---

## How The System Works

### Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Browser   │ ◄─────► │   Frontend   │ ◄─────► │   Backend    │
│  (Client)   │         │   (React)    │         │   (Flask)    │
└─────────────┘         └──────────────┘         └─────────────┘
                                                         │
                                                         ▼
                                                ┌─────────────┐
                                                │  Database   │
                                                │  (SQLite)   │
                                                └─────────────┘
                                                         │
                                                         ▼
                                                ┌─────────────┐
                                                │ File System │
                                                │  (Encrypted │
                                                │    Files)   │
                                                └─────────────┘
```

### Technology Stack

**Frontend:**
- React.js - User interface
- Material-UI - UI components
- Axios - HTTP client
- Socket.IO Client - Real-time updates

**Backend:**
- Flask - Web framework
- Flask-SocketIO - WebSocket support
- Flask-JWT-Extended - Authentication
- SQLAlchemy - Database ORM
- Cryptography - Encryption/Decryption

**Database:**
- SQLite (can be configured for MySQL/PostgreSQL)

**Deployment:**
- Docker - Containerization
- Docker Compose - Orchestration
- Nginx - Reverse proxy (frontend)

---

## File Upload Process (Step-by-Step)

### What Happens When You Upload a File:

1. **File Selection**
   - User selects a file from their computer
   - File is read into browser memory

2. **Upload to Server**
   - File is sent to backend via HTTPS
   - Progress is tracked and displayed

3. **Encryption Process** (Backend)
   ```
   Original File
        ↓
   Generate Random AES-256 Key
        ↓
   Encrypt File with AES-256
        ↓
   Generate RSA-2048 Key Pair
        ↓
   Encrypt AES Key with RSA Public Key
        ↓
   Encrypt RSA Private Key with Master Secret
        ↓
   Calculate SHA-256 Hash
        ↓
   Store Encrypted File + Keys + Hash
   ```

4. **Storage**
   - Encrypted file saved to disk
   - Metadata stored in database:
     - Original filename
     - File size
     - Upload date
     - File hash (for integrity)
     - Encrypted keys
     - User ID

5. **Confirmation**
   - File appears in user's file list
   - Transfer logged for monitoring

---

## File Download Process (Step-by-Step)

### What Happens When You Download a File:

1. **Request**
   - User clicks download button
   - System verifies user has permission

2. **Retrieval**
   - Encrypted file read from disk
   - File metadata retrieved from database

3. **Decryption Process** (Backend)
   ```
   Encrypted File + Encrypted Keys
        ↓
   Decrypt RSA Private Key (using Master Secret)
        ↓
   Decrypt AES Key (using RSA Private Key)
        ↓
   Decrypt File (using AES Key)
        ↓
   Verify SHA-256 Hash
        ↓
   Send Decrypted File to User
   ```

4. **Delivery**
   - Decrypted file sent to browser
   - Browser downloads file to user's computer
   - Original filename preserved

5. **Logging**
   - Download logged for audit
   - Transfer statistics updated

---

## Security Architecture

### Encryption Layers

#### Layer 1: File Encryption (AES-256)
- **Purpose**: Encrypt the actual file content
- **Method**: Symmetric encryption (same key for encrypt/decrypt)
- **Why AES**: Fast and secure for large files
- **Key Size**: 256 bits (extremely secure)

#### Layer 2: Key Encryption (RSA-2048)
- **Purpose**: Protect the AES key
- **Method**: Asymmetric encryption (public/private key pair)
- **Why RSA**: Secure key exchange
- **Key Size**: 2048 bits (industry standard)

#### Layer 3: Private Key Protection (Fernet)
- **Purpose**: Protect the RSA private key
- **Method**: Symmetric encryption with master secret
- **Why Fernet**: Secure key storage
- **Key Derivation**: SHA-256 hash of application secret key

### Security Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    FILE UPLOAD                           │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Original File                                          │
│       │                                                 │
│       ▼                                                 │
│  ┌─────────────┐                                        │
│  │ Generate    │  Random AES-256 Key                    │
│  │ AES Key     │                                        │
│  └──────┬──────┘                                        │
│         │                                               │
│         ▼                                               │
│  ┌─────────────┐                                        │
│  │ Encrypt     │  File encrypted with AES-256          │
│  │ File        │                                        │
│  └──────┬──────┘                                        │
│         │                                               │
│         ▼                                               │
│  ┌─────────────┐                                        │
│  │ Generate    │  RSA-2048 Key Pair                    │
│  │ RSA Keys    │                                        │
│  └───┬─────┬───┘                                        │
│      │     │                                           │
│      ▼     ▼                                           │
│  ┌─────┐ ┌─────┐                                      │
│  │Pub  │ │Priv │  Encrypt AES key with Public Key      │
│  └──┬──┘ └──┬──┘                                      │
│     │       │                                         │
│     ▼       ▼                                         │
│  ┌─────────────┐                                      │
│  │ Encrypt     │  Private key encrypted with           │
│  │ Private Key │  Master Secret (Fernet)               │
│  └──────┬──────┘                                      │
│         │                                             │
│         ▼                                             │
│  ┌─────────────┐                                      │
│  │ Calculate   │  SHA-256 Hash for integrity           │
│  │ Hash        │                                        │
│  └──────┬──────┘                                      │
│         │                                             │
│         ▼                                             │
│  Store: Encrypted File + Encrypted Keys + Hash        │
│                                                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                  FILE DOWNLOAD                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Retrieve: Encrypted File + Encrypted Keys + Hash      │
│       │                                                 │
│       ▼                                                 │
│  ┌─────────────┐                                        │
│  │ Decrypt     │  Private key using Master Secret      │
│  │ Private Key │                                        │
│  └──────┬──────┘                                        │
│         │                                               │
│         ▼                                               │
│  ┌─────────────┐                                        │
│  │ Decrypt     │  AES key using RSA Private Key        │
│  │ AES Key     │                                        │
│  └──────┬──────┘                                        │
│         │                                               │
│         ▼                                               │
│  ┌─────────────┐                                        │
│  │ Decrypt     │  File using AES Key                   │
│  │ File        │                                        │
│  └──────┬──────┘                                        │
│         │                                               │
│         ▼                                               │
│  ┌─────────────┐                                        │
│  │ Verify     │  SHA-256 Hash                          │
│  │ Integrity   │                                        │
│  └──────┬──────┘                                        │
│         │                                               │
│         ▼                                               │
│  Send Decrypted File to User                            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Database Schema

### Tables

#### `users`
- Stores user accounts
- Fields: id, username, email, password_hash, role, created_at, is_active

#### `files`
- Stores file metadata
- Fields: id, filename, original_filename, file_path, file_size, file_hash, encrypted_key, encrypted_private_key, user_id, uploaded_at, mime_type

#### `file_transfers`
- Logs all file transfers
- Fields: id, user_id, file_id, transfer_type, transfer_status, bytes_transferred, transfer_time, timestamp, ip_address

#### `admin_logs`
- Logs administrative actions
- Fields: id, admin_id, action, target_type, target_id, details, ip_address, timestamp

---

## API Endpoints

### Authentication
- `POST /api/register` - Create new user account
- `POST /api/login` - Authenticate user
- `GET /api/me` - Get current user information

### File Operations
- `POST /api/upload` - Upload and encrypt file
- `GET /api/files` - List user's files
- `GET /api/files/<id>/download` - Download and decrypt file
- `DELETE /api/files/<id>` - Delete file

### Admin (Admin users only)
- `GET /api/admin/users` - List all users
- `GET /api/admin/logs` - Get system logs
- `GET /api/admin/transfers` - Get transfer logs

---

## Real-Time Features

### WebSocket Connection
- **Technology**: Socket.IO
- **Purpose**: Real-time transfer updates
- **Events**:
  - `transfer_update` - Notifies clients of file transfer events
  - `connect` - Client connects to monitoring server
  - `disconnect` - Client disconnects

### Monitoring
- Live transfer progress
- Real-time file list updates
- System status notifications

---

## System Components

### Backend Components

1. **app.py** - Main Flask application
   - Routes and request handling
   - File upload/download logic
   - API endpoints

2. **auth.py** - Authentication manager
   - User registration/login
   - JWT token management
   - Password hashing
   - Role verification

3. **encryption.py** - Encryption manager
   - AES encryption/decryption
   - RSA key generation
   - Hybrid encryption implementation

4. **integrity.py** - Integrity manager
   - SHA-256 hash calculation
   - Hash verification

5. **monitoring.py** - Monitoring manager
   - Transfer logging
   - Real-time updates via Socket.IO

6. **models.py** - Database models
   - User, File, FileTransfer, AdminLog models
   - Database relationships

7. **admin_logs.py** - Admin logging
   - Administrative action logging

### Frontend Components

1. **Dashboard.js** - Main user interface
   - File list display
   - Upload/download/delete actions
   - Help dialog

2. **Login.js** - Authentication interface
   - User login/registration

3. **AdminDashboard.js** - Admin interface
   - User management
   - System logs
   - Transfer monitoring

4. **api.js** - API service
   - HTTP request handling
   - Token management
   - Error handling

5. **socket.js** - WebSocket service
   - Real-time connection management

---

## Data Flow Examples

### Example 1: Uploading a 10MB PDF File

```
User Action: Select "document.pdf" (10MB)
     │
     ▼
Browser: Read file into memory
     │
     ▼
Browser: Send to /api/upload via HTTPS
     │
     ▼
Backend: Receive file (10MB)
     │
     ▼
Backend: Generate AES-256 key (32 bytes)
     │
     ▼
Backend: Encrypt file with AES (10MB → ~10MB encrypted)
     │
     ▼
Backend: Generate RSA-2048 key pair
     │
     ▼
Backend: Encrypt AES key with RSA public key
     │
     ▼
Backend: Encrypt RSA private key with master secret
     │
     ▼
Backend: Calculate SHA-256 hash of original file
     │
     ▼
Backend: Save encrypted file to disk
     │
     ▼
Backend: Save metadata to database
     │
     ▼
Backend: Return success response
     │
     ▼
Browser: Update file list
     │
     ▼
User: Sees file in "My Files" list
```

### Example 2: Downloading the Same File

```
User Action: Click download button
     │
     ▼
Browser: Request /api/files/123/download
     │
     ▼
Backend: Verify user permission
     │
     ▼
Backend: Read encrypted file from disk (~10MB)
     │
     ▼
Backend: Retrieve encrypted keys from database
     │
     ▼
Backend: Decrypt RSA private key using master secret
     │
     ▼
Backend: Decrypt AES key using RSA private key
     │
     ▼
Backend: Decrypt file using AES key (~10MB decrypted)
     │
     ▼
Backend: Verify SHA-256 hash
     │
     ▼
Backend: Send decrypted file to browser
     │
     ▼
Browser: Download file to user's computer
     │
     ▼
User: Receives "document.pdf" (original file)
```

---

## Security Guarantees

### What the System Protects Against:

1. **Data Theft**
   - Files are encrypted at rest
   - Even if server is compromised, files are unreadable without keys

2. **Data Tampering**
   - SHA-256 hash verification detects any modifications
   - Integrity check on every download

3. **Unauthorized Access**
   - JWT authentication required
   - Users can only access their own files
   - Role-based access control

4. **Key Theft**
   - AES keys encrypted with RSA
   - RSA private keys encrypted with master secret
   - Multiple layers of key protection

5. **Man-in-the-Middle Attacks**
   - HTTPS encryption in transit
   - End-to-end encryption

### What the System Does NOT Protect Against:

1. **Lost Master Secret**
   - If master secret is lost, encrypted private keys cannot be decrypted
   - Files become permanently inaccessible

2. **User Account Compromise**
   - If user's password is compromised, attacker can access their files
   - Use strong passwords and enable 2FA if available

3. **Physical Server Access**
   - If attacker has physical access to server, they could potentially access encrypted files
   - Server should be physically secured

---

## Performance Characteristics

### Upload Performance
- **Small files (<1MB)**: < 1 second
- **Medium files (1-10MB)**: 1-5 seconds
- **Large files (10-100MB)**: 5-30 seconds
- **Very large files (>100MB)**: 30+ seconds

### Download Performance
- Similar to upload, depends on file size
- Decryption adds minimal overhead (~5-10%)

### Encryption Overhead
- AES encryption: ~5-10% CPU overhead
- RSA operations: Minimal (only for key encryption)
- Overall: Negligible impact on user experience

---

## System Requirements

### Server Requirements
- **CPU**: 2+ cores recommended
- **RAM**: 2GB+ recommended
- **Storage**: Depends on file storage needs
- **Network**: Stable internet connection

### Client Requirements
- Modern web browser (Chrome, Firefox, Safari, Edge)
- JavaScript enabled
- Cookies enabled
- Local storage enabled

---

## Troubleshooting Guide

### Common Issues and Solutions

#### Issue: "File not found" on download
**Cause**: File may have been deleted or doesn't exist
**Solution**: Refresh the file list, re-upload if needed

#### Issue: "Private key not found" error
**Cause**: File uploaded before encryption update
**Solution**: Re-upload the file (old files need new encryption)

#### Issue: "Download failed" with no details
**Cause**: Network issue or server error
**Solution**: Check internet connection, try again, check server logs

#### Issue: "Delete failed"
**Cause**: Database constraint or permission issue
**Solution**: Refresh page, try again, contact admin if persists

#### Issue: Upload progress stuck
**Cause**: Network interruption or large file
**Solution**: Wait for completion, check network, try smaller file first

---

## Best Practices

### For Users
1. **Use Strong Passwords**: At least 12 characters, mix of letters, numbers, symbols
2. **Log Out**: Always log out when finished, especially on shared computers
3. **Backup Important Files**: Keep local backups of critical files
4. **Check File List**: Verify uploads completed successfully
5. **Report Issues**: Contact administrator if you encounter problems

### For Administrators
1. **Monitor Logs**: Regularly check system and transfer logs
2. **Backup Database**: Regular database backups
3. **Secure Server**: Keep server software updated
4. **Monitor Storage**: Watch disk space usage
5. **User Management**: Regularly review user accounts

---

## System Limitations

1. **File Size**: Limited by server configuration (typically 100MB-1GB)
2. **Concurrent Users**: Depends on server resources
3. **Storage**: Limited by available disk space
4. **Browser Support**: Requires modern browser with JavaScript
5. **Network**: Requires stable internet connection

---

## Future Enhancements (Potential)

- File sharing between users
- File versioning
- Folder organization
- Search functionality
- Mobile app
- Two-factor authentication (2FA)
- File expiration dates
- Bandwidth throttling
- Advanced admin features

---

## Conclusion

The Secure File Transfer System provides enterprise-grade security for file storage and transfer. With hybrid encryption, integrity verification, and comprehensive logging, your files are protected at every step of the process.

**Key Takeaways:**
- Files are encrypted with AES-256 + RSA-2048
- Every file is verified for integrity
- All actions are logged and auditable
- Users can only access their own files
- Administrators have comprehensive monitoring tools

For user instructions, see [USER_MANUAL.md](./USER_MANUAL.md)

For technical setup, see [README.md](./README.md)

---

**System Version**: 1.0  
**Last Updated**: December 2025  
**Encryption Standards**: AES-256, RSA-2048, SHA-256


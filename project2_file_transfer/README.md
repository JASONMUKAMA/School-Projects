# Secure File Transfer System

A secure, encrypted file transfer system with hybrid encryption (AES-256 + RSA-2048), real-time monitoring, and user management.

## Features

- 🔐 **Hybrid Encryption**: AES-256 (symmetric) + RSA-2048 (asymmetric)
- 🔒 **Integrity Verification**: SHA-256 hash verification
- 👥 **User Management**: Registration, authentication, and role-based access
- 📁 **File Operations**: Upload, download, and delete files
- 📊 **Real-time Monitoring**: Socket.IO-based transfer monitoring
- 👨‍💼 **Admin Dashboard**: User management, logs, and system monitoring
- 🐳 **Dockerized**: Easy deployment with Docker Compose

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Ports 3000 (frontend) and 5000 (backend) available

### Running the System

1. **Navigate to the project directory:**
   ```bash
   cd project2_file_transfer
   ```

2. **Start the services:**
   ```bash
   docker-compose up -d
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000/api

4. **Stop the services:**
   ```bash
   docker-compose down
   ```

## User Guide

For detailed instructions on how to use the system, see **[USER_MANUAL.md](./USER_MANUAL.md)**

## Architecture

### Backend (Flask)
- **Framework**: Flask with Flask-SocketIO
- **Database**: SQLite (can be configured for MySQL/PostgreSQL)
- **Authentication**: JWT (JSON Web Tokens)
- **Encryption**: Cryptography library (AES-256, RSA-2048)

### Frontend (React)
- **Framework**: React with Material-UI
- **State Management**: React Hooks
- **HTTP Client**: Axios
- **Real-time**: Socket.IO client

## API Endpoints

### Authentication
- `POST /api/register` - Register new user
- `POST /api/login` - Login user
- `GET /api/me` - Get current user info

### Files
- `POST /api/upload` - Upload file
- `GET /api/files` - List user's files
- `GET /api/files/<id>/download` - Download file
- `DELETE /api/files/<id>` - Delete file

### Admin (Admin only)
- `GET /api/admin/users` - List all users
- `GET /api/admin/logs` - Get system logs
- `GET /api/admin/transfers` - Get transfer logs

## Security

- **Encryption**: All files are encrypted using hybrid encryption
  - Files encrypted with AES-256
  - AES keys encrypted with RSA-2048
  - Private keys encrypted with master secret (Fernet)
- **Integrity**: SHA-256 hashes verify file integrity
- **Authentication**: JWT tokens with expiration
- **Authorization**: Role-based access control (user/admin)

## Development

### Backend Development

```bash
cd backend
pip install -r requirements.txt
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

### Frontend Development

```bash
cd frontend
npm install
npm start
```

## Docker Configuration

### Backend Container
- **Base Image**: python:3.11-slim
- **Port**: 5000
- **Volumes**: 
  - `./backend/database` → `/app/database`
  - `./backend/uploads` → `/app/uploads`
  - `./backend` → `/app` (for development)

### Frontend Container
- **Base Image**: node:18 (build), nginx:alpine (serve)
- **Port**: 3000 (mapped to 80 in container)
- **Volumes**: 
  - `./frontend/nginx.conf` → `/etc/nginx/conf.d/default.conf`

## Troubleshooting

### Common Issues

1. **Port already in use**: Change ports in `docker-compose.yml`
2. **Database errors**: Check database file permissions
3. **Upload fails**: Check file size limits and disk space
4. **Download fails**: Ensure file exists and encryption keys are available

### Logs

View backend logs:
```bash
docker-compose logs backend
```

View frontend logs:
```bash
docker-compose logs frontend
```

## File Structure

```
project2_file_transfer/
├── backend/
│   ├── app.py              # Main Flask application
│   ├── auth.py             # Authentication logic
│   ├── encryption.py       # Encryption/decryption
│   ├── models.py           # Database models
│   ├── monitoring.py       # Real-time monitoring
│   ├── requirements.txt   # Python dependencies
│   ├── Dockerfile         # Backend Docker image
│   ├── database/         # SQLite database (created at runtime)
│   └── uploads/           # Encrypted files (created at runtime)
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── services/      # API and Socket services
│   │   └── App.js         # Main app component
│   ├── public/            # Static files
│   ├── package.json       # Node dependencies
│   ├── Dockerfile         # Frontend Docker image
│   └── nginx.conf         # Nginx configuration
├── docker-compose.yml     # Docker Compose configuration
├── USER_MANUAL.md         # User manual
└── README.md             # This file
```

## License

This project is for educational purposes.

## Support

For user support, see [USER_MANUAL.md](./USER_MANUAL.md)

For technical issues, check the logs and troubleshooting section above.

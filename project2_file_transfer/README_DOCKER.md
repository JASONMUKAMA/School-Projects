# Docker Setup for Secure File Transfer System

## Quick Start

### Build and run all services:
```bash
docker-compose up --build
```

This will:
- Build both backend and frontend images
- Start the backend on port 5000
- Start the frontend on port 3000
- Initialize the database automatically

### Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- Default admin credentials:
  - Username: `admin`
  - Password: `admin123`

### Run in detached mode:
```bash
docker-compose up -d
```

### View logs:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Stop services:
```bash
docker-compose down
```

### Stop and remove volumes (clears database):
```bash
docker-compose down -v
```

## Development Mode

### Backend only:
```bash
cd backend
docker build -t file-transfer-backend .
docker run -p 5000:5000 -v $(pwd)/database:/app/database -v $(pwd)/uploads:/app/uploads file-transfer-backend
```

### Frontend only (development):
```bash
cd frontend
npm install
npm start
```

## Production Considerations

### Environment Variables

Create a `.env` file in the project root:
```env
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
DATABASE_URL=sqlite:///./database/filetransfer.db
FLASK_ENV=production
```

### Database

For production, consider using PostgreSQL or MySQL:
1. Update `docker-compose.yml` to include a database service
2. Update `DATABASE_URL` environment variable
3. Modify `config.py` to use the new database

### Security

- Change default admin password immediately
- Use strong SECRET_KEY and JWT_SECRET_KEY
- Enable HTTPS in production
- Configure proper CORS origins
- Use environment variables for sensitive data

## Troubleshooting

**Backend won't start:**
- Check logs: `docker-compose logs backend`
- Verify database directory permissions
- Ensure port 5000 is not in use

**Frontend can't connect to backend:**
- Check backend is running: `docker-compose ps`
- Verify nginx.conf proxy settings
- Check CORS configuration in backend

**Database errors:**
- Remove volumes and restart: `docker-compose down -v && docker-compose up`
- Check database directory permissions

**Build failures:**
- Clear Docker cache: `docker-compose build --no-cache`
- Check Docker has enough resources allocated

## Docker Commands Reference

```bash
# Build images
docker-compose build

# Start services
docker-compose up

# Start in background
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Execute command in container
docker-compose exec backend python init_db.py

# Restart a service
docker-compose restart backend

# View running containers
docker-compose ps
```


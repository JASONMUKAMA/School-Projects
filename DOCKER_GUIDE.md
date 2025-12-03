# Docker Guide for Both Projects

This guide provides instructions for running both projects using Docker.

## Prerequisites

- Docker installed (version 20.10+)
- Docker Compose installed (version 2.0+)
- For Project 1: Docker must have network access (host mode)

## Project 1: Vulnerability Scanner

### Quick Start

```bash
cd project1_vulnerability_scanner

# Build the image
docker-compose build

# Run a scan
docker-compose run --rm vulnerability-scanner python scanner.py --target 192.168.1.1 --report
```

### Important Notes

- Uses `host` network mode for network scanning capabilities
- Requires `privileged: true` for raw socket access
- Database and reports are persisted via volumes

### Example Commands

```bash
# Basic port scan
docker-compose run --rm vulnerability-scanner python scanner.py --target 192.168.1.1

# Full scan with password checking
docker-compose run --rm vulnerability-scanner python scanner.py --target 192.168.1.1 --full-scan --check-passwords --report

# Network discovery
docker-compose run --rm vulnerability-scanner python scanner.py --target 192.168.1.0/24
```

See [project1_vulnerability_scanner/README_DOCKER.md](project1_vulnerability_scanner/README_DOCKER.md) for detailed documentation.

---

## Project 2: Secure File Transfer System

### Quick Start

```bash
cd project2_file_transfer

# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d
```

### Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **Default Admin**: `admin` / `admin123`

### Services

The docker-compose setup includes:
- **Backend**: Flask API server (port 5000)
- **Frontend**: React app served via Nginx (port 3000)

### Development Mode

For development with hot-reload:

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Useful Commands

```bash
# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes (clears database)
docker-compose down -v

# Rebuild after code changes
docker-compose up --build

# Execute command in backend container
docker-compose exec backend python init_db.py
```

See [project2_file_transfer/README_DOCKER.md](project2_file_transfer/README_DOCKER.md) for detailed documentation.

---

## Troubleshooting

### Project 1 Issues

**Network scanning not working:**
- Ensure Docker has proper network permissions
- On Linux, you may need to run Docker with `--privileged` flag
- Verify `network_mode: host` is set in docker-compose.yml

**Permission denied:**
- Check Docker daemon is running
- Verify user has Docker permissions
- On Linux: `sudo usermod -aG docker $USER` (then log out/in)

### Project 2 Issues

**Backend won't start:**
- Check logs: `docker-compose logs backend`
- Verify port 5000 is not in use
- Check database directory permissions

**Frontend can't connect:**
- Verify backend is running: `docker-compose ps`
- Check nginx proxy configuration
- Review CORS settings in backend

**Build failures:**
- Clear cache: `docker-compose build --no-cache`
- Check Docker has enough resources (memory/CPU)
- Verify all files are present

### General Docker Issues

**Out of disk space:**
```bash
docker system prune -a
```

**View container status:**
```bash
docker-compose ps
```

**Restart a service:**
```bash
docker-compose restart backend
```

---

## Production Deployment

### Security Considerations

1. **Change default passwords** immediately
2. **Use environment variables** for secrets
3. **Enable HTTPS** in production
4. **Configure proper CORS** origins
5. **Use secrets management** (Docker secrets, Kubernetes secrets, etc.)

### Environment Variables

Create `.env` files for sensitive configuration:

**Project 2 Backend:**
```env
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
DATABASE_URL=sqlite:///./database/filetransfer.db
FLASK_ENV=production
```

### Database

For production, consider:
- PostgreSQL or MySQL instead of SQLite
- Database backups
- Connection pooling
- Read replicas for scaling

---

## Docker Compose Commands Reference

```bash
# Build images
docker-compose build

# Start services
docker-compose up

# Start in background
docker-compose up -d

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# View logs
docker-compose logs -f [service_name]

# Execute command
docker-compose exec [service] [command]

# Restart service
docker-compose restart [service]

# View status
docker-compose ps

# Rebuild specific service
docker-compose build [service]
```

---

For project-specific details, refer to:
- [Project 1 Docker README](project1_vulnerability_scanner/README_DOCKER.md)
- [Project 2 Docker README](project2_file_transfer/README_DOCKER.md)


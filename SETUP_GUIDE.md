# Setup Guide

Quick setup instructions for both projects.

## Project 1: Smart Vulnerability Scanner

### Prerequisites
- Python 3.8 or higher
- Nmap installed on your system
- Administrator/root privileges (for network scanning)

### Installation Steps

1. **Navigate to project directory:**
   ```bash
   cd project1_vulnerability_scanner
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Nmap:**
   - **Windows**: Download installer from https://nmap.org/download.html
   - **Linux**: `sudo apt-get install nmap` (Debian/Ubuntu) or `sudo yum install nmap` (RHEL/CentOS)
   - **macOS**: `brew install nmap`

4. **Run the scanner:**
   ```bash
   # Basic scan
   python scanner.py --target 192.168.1.1
   
   # Full scan with reports
   python scanner.py --target 192.168.1.1 --full-scan --report
   ```

### Important Notes
- The `database/` and `reports/` directories will be created automatically
- Always ensure you have authorization before scanning networks
- Some features require administrator/root privileges

---

## Project 2: Secure File Transfer System

### Prerequisites
- Python 3.8 or higher
- Node.js 16+ and npm
- MySQL (optional - SQLite is used by default)

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd project2_file_transfer/backend
   ```

2. **Create virtual environment (recommended):**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/macOS
   source venv/bin/activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize database:**
   ```bash
   python init_db.py
   ```
   This creates the database tables and a default admin user:
   - Username: `admin`
   - Password: `admin123`

5. **Start the backend server:**
   ```bash
   python app.py
   ```
   The server will run on `http://localhost:5000`

### Frontend Setup

1. **Open a new terminal and navigate to frontend directory:**
   ```bash
   cd project2_file_transfer/frontend
   ```

2. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```
   The frontend will open in your browser at `http://localhost:3000`

### Accessing the Application

1. Open your browser and go to `http://localhost:3000`
2. Login with the default admin credentials:
   - Username: `admin`
   - Password: `admin123`
3. **IMPORTANT**: Change the admin password after first login!

### Important Notes
- The `database/` and `uploads/` directories will be created automatically
- For production use, configure proper database credentials in `config.py`
- The encryption system in this demo generates new keypairs each time (see README for production considerations)

---

## Troubleshooting

### Project 1 Issues

**"Nmap not found" error:**
- Ensure Nmap is installed and in your system PATH
- On Windows, you may need to restart your terminal after installation

**Permission denied errors:**
- Run with administrator/root privileges
- On Linux/macOS: `sudo python scanner.py ...`

**Import errors:**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.8+)

### Project 2 Issues

**Backend won't start:**
- Check if port 5000 is already in use
- Ensure database initialization completed: `python init_db.py`
- Check for missing dependencies: `pip install -r requirements.txt`

**Frontend won't start:**
- Ensure Node.js is installed: `node --version`
- Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Check for port conflicts (default is 3000)

**Database errors:**
- Ensure the database directory exists and is writable
- Try reinitializing: `python init_db.py`

**CORS errors:**
- Ensure backend is running on port 5000
- Check `config.py` for correct CORS origins

---

## Next Steps

After setup:
1. Read the individual project README files for detailed documentation
2. Explore the code to understand the implementation
3. Customize for your needs
4. For production use, review security considerations in the README files

---

## Support

For detailed information about each project, see:
- [Project 1 README](project1_vulnerability_scanner/README.md)
- [Project 2 README](project2_file_transfer/README.md)


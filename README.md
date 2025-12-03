# Students Projects - Two Software-Based Projects

This repository contains two comprehensive software projects for educational purposes:

1. **Smart Vulnerability Scanner and Reporting Tool**
2. **Secure File Transfer and Monitoring System**

## Project 1: Smart Vulnerability Scanner and Reporting Tool

A lightweight Python-based tool that scans networks for vulnerabilities, performs device discovery, port scanning, and generates automated security reports.

### Key Features
- Device Discovery (ARP scanning, ICMP ping)
- Port Scanning (Nmap integration)
- Vulnerability Database (SQLite with CVE information)
- Password Checker (SSH, FTP, Telnet)
- Automated Reports (PDF and HTML)

### Tech Stack
- Python 3.8+
- Nmap
- Scapy
- SQLite
- ReportLab

### Quick Start
```bash
cd project1_vulnerability_scanner
pip install -r requirements.txt
python scanner.py --target 192.168.1.1 --report
```

**⚠️ WARNING**: Only scan networks you own or have explicit permission to scan!

See [project1_vulnerability_scanner/README.md](project1_vulnerability_scanner/README.md) for detailed documentation.

---

## Project 2: Secure File Transfer and Monitoring System

A secure file sharing system with end-to-end encryption, real-time monitoring, integrity verification, and comprehensive admin logging.

### Key Features
- User Authentication (Secure login system)
- AES/RSA Encryption (Hybrid encryption for files)
- Real-time Monitoring (Live transfer monitoring)
- Integrity Verification (SHA-256 checksums)
- Admin Logs (Comprehensive activity logging)
- React GUI (Modern web interface)

### Tech Stack
- **Backend**: Python, Flask, SQLite/MySQL
- **Frontend**: React, Material-UI
- **Encryption**: Cryptography library (AES-256, RSA-2048)

### Quick Start

#### Backend Setup
```bash
cd project2_file_transfer/backend
pip install -r requirements.txt
python init_db.py
python app.py
```

#### Frontend Setup
```bash
cd project2_file_transfer/frontend
npm install
npm start
```

Default admin credentials:
- Username: `admin`
- Password: `admin123` (change after first login!)

See [project2_file_transfer/README.md](project2_file_transfer/README.md) for detailed documentation.

---

## Project Structure

```
Students Projects/
├── project1_vulnerability_scanner/
│   ├── scanner.py
│   ├── device_discovery.py
│   ├── port_scanner.py
│   ├── vulnerability_db.py
│   ├── password_checker.py
│   ├── report_generator.py
│   ├── database/
│   ├── reports/
│   ├── requirements.txt
│   └── README.md
│
├── project2_file_transfer/
│   ├── backend/
│   │   ├── app.py
│   │   ├── models.py
│   │   ├── auth.py
│   │   ├── encryption.py
│   │   ├── integrity.py
│   │   ├── monitoring.py
│   │   ├── admin_logs.py
│   │   ├── config.py
│   │   ├── init_db.py
│   │   ├── requirements.txt
│   │   ├── uploads/
│   │   └── database/
│   ├── frontend/
│   │   ├── src/
│   │   ├── public/
│   │   ├── package.json
│   │   └── README.md
│   └── README.md
│
└── README.md (this file)
```

## Requirements

### For Project 1
- Python 3.8+
- Nmap installed on system
- Administrator/root privileges for network scanning

### For Project 2
- Python 3.8+
- Node.js 16+ and npm
- MySQL (optional, SQLite used by default)

## Installation

### Option 1: Docker (Recommended)

#### Project 1
```bash
cd project1_vulnerability_scanner
docker-compose build
docker-compose run --rm vulnerability-scanner python scanner.py --target 192.168.1.1 --report
```
See [project1_vulnerability_scanner/README_DOCKER.md](project1_vulnerability_scanner/README_DOCKER.md) for details.

#### Project 2
```bash
cd project2_file_transfer
docker-compose up --build
```
Access at http://localhost:3000
See [project2_file_transfer/README_DOCKER.md](project2_file_transfer/README_DOCKER.md) for details.

### Option 2: Manual Installation

#### Project 1
```bash
# Install Python dependencies
cd project1_vulnerability_scanner
pip install -r requirements.txt

# Install Nmap
# Windows: Download from https://nmap.org/download.html
# Linux: sudo apt-get install nmap
# macOS: brew install nmap
```

#### Project 2
```bash
# Backend
cd project2_file_transfer/backend
pip install -r requirements.txt
python init_db.py

# Frontend
cd ../frontend
npm install
```

## Security Notes

### Project 1
- **Authorization Required**: Always obtain proper authorization before scanning networks
- **Legal Compliance**: Unauthorized scanning is illegal in many jurisdictions
- **Educational Use**: This tool is for educational and authorized security testing only

### Project 2
- **Change Default Passwords**: Always change default admin credentials
- **Key Management**: In production, implement secure key storage for RSA private keys
- **HTTPS**: Use HTTPS in production environments
- **Database Security**: Secure database access and credentials

## License

These projects are for educational purposes only.

## Contributing

These are student projects. Feel free to use them as learning resources or starting points for your own projects.

## Support

For issues or questions, please refer to the individual project README files for detailed documentation.

---

**Note**: Both projects are designed for educational purposes. Always follow ethical guidelines and legal requirements when using security tools.


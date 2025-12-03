import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Paper,
  Typography,
  Button,
  Box,
  AppBar,
  Toolbar,
  Grid,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  IconButton,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  InputAdornment,
  Drawer,
  Divider,
  ListItemIcon,
  Breadcrumbs,
  Link,
  Pagination,
  Tabs,
  Tab,
  Alert,
} from '@mui/material';
import {
  CloudUpload,
  Folder,
  Settings,
  Logout,
  Delete,
  Download,
  Help,
  Search,
  GetApp,
  Home,
  Menu,
  Lock,
  LockOpen,
} from '@mui/icons-material';
import { fileAPI } from '../services/api';
import { getSocket } from '../services/socket';

const Dashboard = () => {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [user, setUser] = useState(null);
  const [helpOpen, setHelpOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [encryptTabValue, setEncryptTabValue] = useState(0);
  const [page, setPage] = useState(1);
  const [rowsPerPage] = useState(10);
  const [encryptStatus, setEncryptStatus] = useState(null);
  const [decryptStatus, setDecryptStatus] = useState(null);
  const [sftpConfig, setSftpConfig] = useState({
    host: '',
    port: '22',
    username: '',
    password: '',
    remotePath: ''
  });
  const [sftpDownloadConfig, setSftpDownloadConfig] = useState({
    host: '',
    port: '22',
    username: '',
    password: '',
    remotePath: '',
    encryptedKey: '',
    encryptedPrivateKey: ''
  });
  const navigate = useNavigate();

  useEffect(() => {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      setUser(JSON.parse(userStr));
    }

    loadFiles();

    // Connect to socket for real-time updates
    const socket = getSocket();
    socket.on('transfer_update', (data) => {
      console.log('Transfer update:', data);
      loadFiles(); // Reload files on transfer update
    });

    return () => {
      socket.off('transfer_update');
    };
  }, []);

  const loadFiles = async () => {
    try {
      const response = await fileAPI.list();
      setFiles(response.data);
    } catch (err) {
      console.error('Error loading files:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploadProgress(0);

    try {
      await fileAPI.upload(file, (progress) => {
        setUploadProgress(progress);
      });
      await loadFiles();
      setUploadProgress(0);
    } catch (err) {
      console.error('Upload error:', err);
      alert('Upload failed: ' + (err.response?.data?.error || 'Unknown error'));
    }
  };

  const handleDownload = async (fileId, filename) => {
    try {
      const response = await fileAPI.download(fileId);
      
      // Handle blob response
      if (response.data instanceof Blob) {
        const url = window.URL.createObjectURL(response.data);
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', filename);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
      } else {
        // If response is not a blob, try to create blob from data
        const blob = new Blob([response.data], { type: response.headers['content-type'] || 'application/octet-stream' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', filename);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
      }
    } catch (err) {
      console.error('Download error:', err);
      let errorMsg = 'Download failed';
      
      if (err.response) {
        if (err.response.status === 404) {
          const responseError = err.response.data?.error || '';
          if (responseError.includes('not found on server') || responseError.includes('File not found on server')) {
            errorMsg = 'File not found on server. The file may have been deleted or the server was restarted. Please re-upload the file.';
          } else {
            errorMsg = 'File not found. It may have been deleted. Please refresh the page.';
          }
        } else if (err.response.data && err.response.data.error) {
          errorMsg = err.response.data.error;
        } else {
          errorMsg = `Server error (${err.response.status}). Please try again.`;
        }
      } else if (err.message) {
        errorMsg = err.message;
      }
      
      alert(`Download failed: ${errorMsg}`);
      // Refresh file list in case file was deleted
      await loadFiles();
    }
  };

  const handleDelete = async (fileId) => {
    if (!window.confirm('Are you sure you want to delete this file?')) return;

    try {
      await fileAPI.delete(fileId);
      await loadFiles();
      alert('File deleted successfully');
    } catch (err) {
      console.error('Delete error:', err);
      const errorMsg = err.response?.data?.error || err.message || 'Delete failed';
      alert(`Delete failed: ${errorMsg}`);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  // Filter files based on search query
  const filteredFiles = files.filter(file => {
    if (!searchQuery) return true;
    const lowerQuery = searchQuery.toLowerCase();
    return (
      file.original_filename?.toLowerCase().includes(lowerQuery) ||
      file.mime_type?.toLowerCase().includes(lowerQuery) ||
      formatFileSize(file.file_size).toLowerCase().includes(lowerQuery) ||
      new Date(file.uploaded_at).toLocaleString().toLowerCase().includes(lowerQuery)
    );
  });

  // Pagination for files
  const startIndex = (page - 1) * rowsPerPage;
  const endIndex = startIndex + rowsPerPage;
  const paginatedFiles = filteredFiles.slice(startIndex, endIndex);
  const totalPages = Math.ceil(filteredFiles.length / rowsPerPage);

  const handlePageChange = (event, value) => {
    setPage(value);
  };

  const handleSftpUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setEncryptStatus({ type: 'info', message: 'Encrypting file and uploading to SFTP server...' });

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('sftp_host', sftpConfig.host);
      formData.append('sftp_port', sftpConfig.port);
      formData.append('sftp_username', sftpConfig.username);
      formData.append('sftp_password', sftpConfig.password);
      formData.append('sftp_remote_path', sftpConfig.remotePath || `/tmp/secure_transfers/${file.name}.enc`);
      
      const response = await fileAPI.sftpUpload(formData);
      
      if (response.data.success) {
        setEncryptStatus({ 
          type: 'success', 
          message: `File encrypted and uploaded successfully! Remote path: ${response.data.remote_path}. Save these keys for decryption:`,
          keys: {
            encryptedKey: response.data.encrypted_key,
            encryptedPrivateKey: response.data.encrypted_private_key
          }
        });
        // Store keys in download config for convenience
        setSftpDownloadConfig({
          ...sftpDownloadConfig,
          host: sftpConfig.host,
          port: sftpConfig.port,
          username: sftpConfig.username,
          password: sftpConfig.password,
          remotePath: response.data.remote_path,
          encryptedKey: response.data.encrypted_key,
          encryptedPrivateKey: response.data.encrypted_private_key
        });
      } else {
        throw new Error(response.data.error || 'Upload failed');
      }
      
      e.target.value = ''; // Reset input
    } catch (err) {
      console.error('SFTP upload error:', err);
      let errorMessage = 'SFTP upload failed';
      if (err.response?.status === 401 || err.response?.status === 422) {
        errorMessage = 'Authentication failed. Please log in again.';
      } else if (err.response?.data) {
        if (err.response.data instanceof Blob) {
          try {
            const text = await err.response.data.text();
            const errorData = JSON.parse(text);
            errorMessage = errorData.error || 'SFTP upload failed';
          } catch {
            errorMessage = err.message || 'SFTP upload failed';
          }
        } else {
          errorMessage = err.response.data.error || err.message || 'SFTP upload failed';
        }
      } else if (err.message) {
        errorMessage = err.message;
      }
      setEncryptStatus({ type: 'error', message: errorMessage });
    }
  };

  const handleSftpDownload = async () => {
    setDecryptStatus({ type: 'info', message: 'Downloading and decrypting file from SFTP server...' });

    try {
      const response = await fileAPI.sftpDownload({
        sftp_host: sftpDownloadConfig.host,
        sftp_port: sftpDownloadConfig.port,
        sftp_username: sftpDownloadConfig.username,
        sftp_password: sftpDownloadConfig.password,
        sftp_remote_path: sftpDownloadConfig.remotePath,
        encrypted_key: sftpDownloadConfig.encryptedKey,
        encrypted_private_key: sftpDownloadConfig.encryptedPrivateKey
      });
      
      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      const originalName = sftpDownloadConfig.remotePath.split('/').pop().replace('.enc', '');
      link.download = originalName;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      setDecryptStatus({ type: 'success', message: 'File downloaded and decrypted successfully! Download started.' });
    } catch (err) {
      console.error('SFTP download error:', err);
      let errorMessage = 'SFTP download/decrypt failed';
      if (err.response?.status === 401 || err.response?.status === 422) {
        errorMessage = 'Authentication failed. Please log in again.';
      } else if (err.response?.data) {
        if (err.response.data instanceof Blob) {
          try {
            const text = await err.response.data.text();
            const errorData = JSON.parse(text);
            errorMessage = errorData.error || 'SFTP download/decrypt failed';
          } catch {
            errorMessage = err.message || 'SFTP download/decrypt failed';
          }
        } else {
          errorMessage = err.response.data.error || err.message || 'SFTP download/decrypt failed';
        }
      } else if (err.message) {
        errorMessage = err.message;
      }
      setDecryptStatus({ type: 'error', message: errorMessage });
    }
  };

  const handleEncryptFile = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setEncryptStatus({ type: 'info', message: 'Encrypting file...' });

    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fileAPI.encryptFile(formData);
      
      // Check if response is actually an error (blob error responses)
      if (response.data instanceof Blob && response.data.size < 100) {
        const text = await response.data.text();
        try {
          const errorData = JSON.parse(text);
          throw new Error(errorData.error || 'Encryption failed');
        } catch (parseErr) {
          // If not JSON, it's likely the actual encrypted file
        }
      }
      
      const blob = new Blob([response.data], { type: 'application/octet-stream' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = file.name + '.enc';
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      setEncryptStatus({ type: 'success', message: 'File encrypted successfully! Download started.' });
      e.target.value = ''; // Reset input
    } catch (err) {
      console.error('Encryption error:', err);
      let errorMessage = 'Encryption failed';
      if (err.response?.status === 401 || err.response?.status === 422) {
        errorMessage = 'Authentication failed. Please log in again.';
      } else if (err.response?.data) {
        if (err.response.data instanceof Blob) {
          try {
            const text = await err.response.data.text();
            const errorData = JSON.parse(text);
            errorMessage = errorData.error || 'Encryption failed';
          } catch {
            errorMessage = err.message || 'Encryption failed';
          }
        } else {
          errorMessage = err.response.data.error || err.message || 'Encryption failed';
        }
      } else if (err.message) {
        errorMessage = err.message;
      }
      setEncryptStatus({ type: 'error', message: errorMessage });
    }
  };

  const handleDecryptFile = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setDecryptStatus({ type: 'info', message: 'Decrypting file...' });

    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fileAPI.decryptFile(formData);
      
      // Check if response is actually an error (blob error responses)
      if (response.data instanceof Blob && response.data.size < 100) {
        const text = await response.data.text();
        try {
          const errorData = JSON.parse(text);
          throw new Error(errorData.error || 'Decryption failed');
        } catch (parseErr) {
          // If not JSON, it's likely the actual decrypted file
        }
      }
      
      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      // Remove .enc extension if present
      const originalName = file.name.replace(/\.enc$/, '');
      link.download = originalName;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      setDecryptStatus({ type: 'success', message: 'File decrypted successfully! Download started.' });
      e.target.value = ''; // Reset input
    } catch (err) {
      console.error('Decryption error:', err);
      let errorMessage = 'Decryption failed';
      if (err.response?.status === 401 || err.response?.status === 422) {
        errorMessage = 'Authentication failed. Please log in again.';
      } else if (err.response?.data) {
        if (err.response.data instanceof Blob) {
          try {
            const text = await err.response.data.text();
            const errorData = JSON.parse(text);
            errorMessage = errorData.error || 'Decryption failed';
          } catch {
            errorMessage = err.message || 'Decryption failed';
          }
        } else {
          errorMessage = err.response.data.error || err.message || 'Decryption failed';
        }
      } else if (err.message) {
        errorMessage = err.message;
      }
      setDecryptStatus({ type: 'error', message: errorMessage });
    }
  };

  const isAdmin = user?.role === 'admin';

  return (
    <Box>
      <AppBar position="static">
        <Toolbar>
          <IconButton
            edge="start"
            color="inherit"
            onClick={() => setDrawerOpen(true)}
            sx={{ mr: 2, display: { xs: 'block', sm: 'none' } }}
          >
            <Menu />
          </IconButton>
          <Typography 
            variant="h6" 
            component="div" 
            sx={{ flexGrow: 1, cursor: 'pointer', fontWeight: 600 }}
            onClick={() => navigate('/dashboard')}
          >
            Secure File Transfer System
          </Typography>
          {user && (
            <Box sx={{ display: { xs: 'none', sm: 'flex' }, alignItems: 'center', gap: 1 }}>
              <Button
                color="inherit"
                startIcon={<Home />}
                onClick={() => navigate('/dashboard')}
                sx={{ textTransform: 'none' }}
              >
                Dashboard
              </Button>
              {isAdmin && (
                <Button
                  color="inherit"
                  startIcon={<Settings />}
                  onClick={() => navigate('/admin')}
                  sx={{ textTransform: 'none' }}
                >
                  Admin
                </Button>
              )}
              <Button
                color="inherit"
                startIcon={<Help />}
                onClick={() => setHelpOpen(true)}
                sx={{ textTransform: 'none' }}
              >
                Help
              </Button>
              <Typography 
                variant="body2" 
                sx={{ 
                  mx: 1, 
                  px: 1.5, 
                  py: 0.5, 
                  borderRadius: 1, 
                  bgcolor: 'rgba(255,255,255,0.1)' 
                }}
              >
                {user.username} ({user.role})
              </Typography>
              <Button
                color="inherit"
                startIcon={<Logout />}
                onClick={handleLogout}
                sx={{ textTransform: 'none' }}
              >
                Logout
              </Button>
            </Box>
          )}
        </Toolbar>
      </AppBar>

      {/* Navigation Drawer for Mobile */}
      <Drawer
        anchor="left"
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        PaperProps={{
          sx: { width: 280 }
        }}
      >
        <Box sx={{ pt: 2 }}>
          <Box sx={{ px: 3, pb: 2 }}>
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
              Navigation
            </Typography>
            {user && (
              <Typography variant="body2" color="text.secondary">
                {user.username} ({user.role})
              </Typography>
            )}
          </Box>
          <Divider />
          <List sx={{ pt: 1 }}>
            <ListItem 
              button 
              onClick={() => {
                navigate('/dashboard');
                setDrawerOpen(false);
              }}
              sx={{ py: 1.5 }}
            >
              <ListItemIcon>
                <Home />
              </ListItemIcon>
              <ListItemText primary="Dashboard" />
            </ListItem>
            {isAdmin && (
              <ListItem 
                button 
                onClick={() => {
                  navigate('/admin');
                  setDrawerOpen(false);
                }}
                sx={{ py: 1.5 }}
              >
                <ListItemIcon>
                  <Settings />
                </ListItemIcon>
                <ListItemText primary="Admin Panel" />
              </ListItem>
            )}
            <ListItem 
              button 
              onClick={() => {
                setHelpOpen(true);
                setDrawerOpen(false);
              }}
              sx={{ py: 1.5 }}
            >
              <ListItemIcon>
                <Help />
              </ListItemIcon>
              <ListItemText primary="Help & Guide" />
            </ListItem>
            <Divider sx={{ my: 1 }} />
            <ListItem 
              button 
              onClick={handleLogout}
              sx={{ py: 1.5 }}
            >
              <ListItemIcon>
                <Logout />
              </ListItemIcon>
              <ListItemText primary="Logout" />
            </ListItem>
          </List>
        </Box>
      </Drawer>

      <Container maxWidth="lg" sx={{ marginTop: 4, marginBottom: 4 }}>
        {/* Breadcrumbs */}
        <Breadcrumbs sx={{ mb: 3 }}>
          <Link
            component="button"
            variant="body1"
            onClick={() => navigate('/dashboard')}
            sx={{ textDecoration: 'none', color: 'primary.main', cursor: 'pointer' }}
          >
            Dashboard
          </Link>
          <Typography color="text.primary">My Files</Typography>
        </Breadcrumbs>

        {/* Main Content Grid */}
        <Grid container spacing={3}>
          {/* Upload File Card */}
          <Grid item xs={12} md={4}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
                  Upload File
                </Typography>
                <input
                  accept="*/*"
                  style={{ display: 'none' }}
                  id="file-upload"
                  type="file"
                  onChange={handleFileUpload}
                />
                <label htmlFor="file-upload">
                  <Button
                    variant="contained"
                    component="span"
                    fullWidth
                    startIcon={<CloudUpload />}
                    sx={{ mb: 2 }}
                  >
                    Choose File
                  </Button>
                </label>
                {uploadProgress > 0 && (
                  <Box sx={{ mt: 2 }}>
                    <LinearProgress variant="determinate" value={uploadProgress} />
                    <Typography variant="body2" align="center" sx={{ mt: 1 }}>
                      {uploadProgress}%
                    </Typography>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* My Files Card */}
          <Grid item xs={12} md={8}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
                  My Files
                </Typography>
                {!loading && files.length > 0 && (
                  <TextField
                    fullWidth
                    placeholder="Search files..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <Search />
                        </InputAdornment>
                      ),
                    }}
                    sx={{ mb: 2 }}
                  />
                )}
                {loading ? (
                  <Box sx={{ py: 4, textAlign: 'center' }}>
                    <Typography color="text.secondary">Loading...</Typography>
                  </Box>
                ) : files.length === 0 ? (
                  <Box sx={{ py: 4, textAlign: 'center' }}>
                    <Typography color="text.secondary">
                      No files uploaded yet
                    </Typography>
                  </Box>
                ) : filteredFiles.length === 0 ? (
                  <Box sx={{ py: 4, textAlign: 'center' }}>
                    <Typography color="text.secondary">
                      No files found matching your search
                    </Typography>
                  </Box>
                ) : (
                  <>
                    <List sx={{ maxHeight: '400px', overflow: 'auto' }}>
                      {paginatedFiles.map((file) => (
                        <ListItem
                          key={file.id}
                          sx={{ 
                            borderBottom: '1px solid',
                            borderColor: 'divider',
                            '&:last-child': { borderBottom: 'none' }
                          }}
                          secondaryAction={
                            <Box>
                              <IconButton
                                edge="end"
                                onClick={() => handleDownload(file.id, file.original_filename)}
                                color="primary"
                                sx={{ mr: 1 }}
                              >
                                <Download />
                              </IconButton>
                              <IconButton
                                edge="end"
                                onClick={() => handleDelete(file.id)}
                                color="error"
                              >
                                <Delete />
                              </IconButton>
                            </Box>
                          }
                        >
                          <ListItemText
                            primary={file.original_filename}
                            secondary={`${formatFileSize(file.file_size)} • ${new Date(file.uploaded_at).toLocaleString()}`}
                          />
                        </ListItem>
                      ))}
                    </List>
                    {totalPages > 1 && (
                      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3, mb: 1 }}>
                        <Pagination
                          count={totalPages}
                          page={page}
                          onChange={handlePageChange}
                          color="primary"
                          showFirstButton
                          showLastButton
                        />
                      </Box>
                    )}
                    <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 1, mb: 1 }}>
                      Showing {startIndex + 1}-{Math.min(endIndex, filteredFiles.length)} of {filteredFiles.length} files
                    </Typography>
                  </>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* SFTP Transfer Section */}
        <Card sx={{ mt: 4 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ mb: 1 }}>
              Secure SFTP Transfer (Server A ↔ Server B)
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph sx={{ mb: 3 }}>
              Encrypt files and transfer them securely between servers via SFTP. Files are encrypted before transfer and decrypted on receipt.
            </Typography>
            <Tabs 
              value={encryptTabValue} 
              onChange={(e, newValue) => setEncryptTabValue(newValue)} 
              sx={{ mb: 3, borderBottom: 1, borderColor: 'divider' }}
            >
              <Tab label="Upload to SFTP Server" icon={<Lock />} iconPosition="start" />
              <Tab label="Download from SFTP Server" icon={<LockOpen />} iconPosition="start" />
            </Tabs>

            {encryptTabValue === 0 && (
              <Box>
                <Typography variant="body2" color="text.secondary" paragraph sx={{ mb: 3 }}>
                  Upload a file to Server A, encrypt it, and transfer it to Server B via SFTP.
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="SFTP Host (Server B)"
                      value={sftpConfig.host}
                      onChange={(e) => setSftpConfig({...sftpConfig, host: e.target.value})}
                      required
                      variant="outlined"
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="SFTP Port"
                      type="number"
                      value={sftpConfig.port}
                      onChange={(e) => setSftpConfig({...sftpConfig, port: e.target.value})}
                      defaultValue="22"
                      variant="outlined"
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="SFTP Username"
                      value={sftpConfig.username}
                      onChange={(e) => setSftpConfig({...sftpConfig, username: e.target.value})}
                      required
                      variant="outlined"
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="SFTP Password"
                      type="password"
                      value={sftpConfig.password}
                      onChange={(e) => setSftpConfig({...sftpConfig, password: e.target.value})}
                      variant="outlined"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Remote Path (on Server B)"
                      value={sftpConfig.remotePath}
                      onChange={(e) => setSftpConfig({...sftpConfig, remotePath: e.target.value})}
                      placeholder="/tmp/secure_transfers/filename.enc"
                      variant="outlined"
                    />
                  </Grid>
                </Grid>
                <Box sx={{ mt: 3, mb: 2 }}>
                  <input
                    accept="*/*"
                    style={{ display: 'none' }}
                    id="sftp-upload-file"
                    type="file"
                    onChange={handleSftpUpload}
                  />
                  <label htmlFor="sftp-upload-file">
                    <Button
                      variant="contained"
                      component="span"
                      startIcon={<Lock />}
                      fullWidth
                      disabled={!sftpConfig.host || !sftpConfig.username}
                      size="large"
                    >
                      Choose File & Transfer to SFTP Server
                    </Button>
                  </label>
                </Box>
                {encryptStatus && (
                  <Alert severity={encryptStatus.type} sx={{ mt: 3 }}>
                    {encryptStatus.message}
                    {encryptStatus.keys && (
                      <Box sx={{ mt: 2 }}>
                        <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 2 }}>
                          Save these keys for decryption:
                        </Typography>
                        <TextField
                          fullWidth
                          label="Encryption Key"
                          value={encryptStatus.keys.encryptedKey}
                          InputProps={{
                            readOnly: true,
                          }}
                          size="small"
                          sx={{ mb: 2 }}
                          onClick={(e) => e.target.select()}
                          variant="outlined"
                        />
                        <TextField
                          fullWidth
                          label="Private Key"
                          value={encryptStatus.keys.encryptedPrivateKey}
                          InputProps={{
                            readOnly: true,
                          }}
                          multiline
                          rows={3}
                          size="small"
                          onClick={(e) => e.target.select()}
                          variant="outlined"
                        />
                      </Box>
                    )}
                  </Alert>
                )}
              </Box>
            )}

            {encryptTabValue === 1 && (
              <Box>
                <Typography variant="body2" color="text.secondary" paragraph sx={{ mb: 3 }}>
                  Download an encrypted file from Server B, decrypt it, and save it locally.
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="SFTP Host (Server B)"
                      value={sftpDownloadConfig.host}
                      onChange={(e) => setSftpDownloadConfig({...sftpDownloadConfig, host: e.target.value})}
                      required
                      variant="outlined"
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="SFTP Port"
                      type="number"
                      value={sftpDownloadConfig.port}
                      onChange={(e) => setSftpDownloadConfig({...sftpDownloadConfig, port: e.target.value})}
                      defaultValue="22"
                      variant="outlined"
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="SFTP Username"
                      value={sftpDownloadConfig.username}
                      onChange={(e) => setSftpDownloadConfig({...sftpDownloadConfig, username: e.target.value})}
                      required
                      variant="outlined"
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="SFTP Password"
                      type="password"
                      value={sftpDownloadConfig.password}
                      onChange={(e) => setSftpDownloadConfig({...sftpDownloadConfig, password: e.target.value})}
                      variant="outlined"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Remote Path (on Server B)"
                      value={sftpDownloadConfig.remotePath}
                      onChange={(e) => setSftpDownloadConfig({...sftpDownloadConfig, remotePath: e.target.value})}
                      placeholder="/tmp/secure_transfers/filename.enc"
                      required
                      variant="outlined"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Encryption Key (from upload)"
                      value={sftpDownloadConfig.encryptedKey}
                      onChange={(e) => setSftpDownloadConfig({...sftpDownloadConfig, encryptedKey: e.target.value})}
                      placeholder="Paste the encryption key from upload response"
                      multiline
                      rows={2}
                      variant="outlined"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Private Key (from upload)"
                      value={sftpDownloadConfig.encryptedPrivateKey}
                      onChange={(e) => setSftpDownloadConfig({...sftpDownloadConfig, encryptedPrivateKey: e.target.value})}
                      placeholder="Paste the private key from upload response"
                      multiline
                      rows={3}
                      variant="outlined"
                    />
                  </Grid>
                </Grid>
                <Box sx={{ mt: 3, mb: 2 }}>
                  <Button
                    variant="contained"
                    startIcon={<LockOpen />}
                    onClick={handleSftpDownload}
                    fullWidth
                    disabled={!sftpDownloadConfig.host || !sftpDownloadConfig.username || !sftpDownloadConfig.remotePath}
                    size="large"
                  >
                    Download & Decrypt from SFTP Server
                  </Button>
                </Box>
                {decryptStatus && (
                  <Alert severity={decryptStatus.type} sx={{ mt: 3 }}>
                    {decryptStatus.message}
                  </Alert>
                )}
              </Box>
            )}
          </CardContent>
        </Card>
      </Container>

      {/* Help Dialog */}
      <Dialog open={helpOpen} onClose={() => setHelpOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Help & User Guide</DialogTitle>
        <DialogContent>
          <Typography variant="h6" gutterBottom>How to Use the System</Typography>
          
          <Typography variant="subtitle1" sx={{ mt: 2, fontWeight: 'bold' }}>Uploading Files</Typography>
          <Typography variant="body2" paragraph>
            1. Click "Choose File" button<br/>
            2. Select a file from your computer<br/>
            3. Wait for upload to complete (progress bar will show)<br/>
            4. Your file will appear in the "My Files" list
          </Typography>

          <Typography variant="subtitle1" sx={{ mt: 2, fontWeight: 'bold' }}>Downloading Files</Typography>
          <Typography variant="body2" paragraph>
            1. Find your file in the "My Files" list<br/>
            2. Click the download icon (⬇️) next to the file<br/>
            3. The file will be automatically decrypted and downloaded<br/>
            4. Check your browser's download folder
          </Typography>

          <Typography variant="subtitle1" sx={{ mt: 2, fontWeight: 'bold' }}>Deleting Files</Typography>
          <Typography variant="body2" paragraph>
            1. Find your file in the "My Files" list<br/>
            2. Click the delete icon (🗑️) next to the file<br/>
            3. Confirm deletion in the popup<br/>
            4. File will be permanently removed
          </Typography>

          <Typography variant="subtitle1" sx={{ mt: 2, fontWeight: 'bold' }}>Troubleshooting</Typography>
          <Typography variant="body2" paragraph>
            • <strong>Download fails?</strong> Make sure you're logged in. Old files may need to be re-uploaded.<br/>
            • <strong>Delete fails?</strong> Refresh the page and try again.<br/>
            • <strong>Can't see files?</strong> Refresh the page (F5) or log out and log back in.<br/>
            • <strong>Upload fails?</strong> Check your internet connection and try again.
          </Typography>

          <Typography variant="subtitle1" sx={{ mt: 2, fontWeight: 'bold' }}>Security Features</Typography>
          <Typography variant="body2" paragraph>
            • All files are encrypted with AES-256 + RSA-2048 encryption<br/>
            • Files are verified with SHA-256 integrity checks<br/>
            • Only you (and admins) can access your files<br/>
            • Files are automatically encrypted on upload and decrypted on download
          </Typography>

          <Typography variant="body2" sx={{ mt: 2, fontStyle: 'italic', color: 'text.secondary' }}>
            For detailed documentation, download the complete user manual below.
          </Typography>
          
          <Box sx={{ mt: 3, display: 'flex', justifyContent: 'center' }}>
            <Button
              variant="contained"
              startIcon={<GetApp />}
              onClick={() => {
                const link = document.createElement('a');
                link.href = '/USER_MANUAL.md';
                link.download = 'USER_MANUAL.md';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
              }}
            >
              Download User Manual (Markdown)
            </Button>
          </Box>
          
          <Typography variant="caption" sx={{ mt: 2, display: 'block', textAlign: 'center', color: 'text.secondary' }}>
            Note: The manual downloads as a Markdown (.md) file. You can open it in Microsoft Word and save it as .docx format.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setHelpOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Dashboard;


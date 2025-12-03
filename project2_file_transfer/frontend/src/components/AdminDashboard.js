import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Paper,
  Typography,
  Box,
  AppBar,
  Toolbar,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tabs,
  Tab,
  TextField,
  InputAdornment,
  Breadcrumbs,
  Link,
  IconButton,
  TablePagination,
} from '@mui/material';
import { ArrowBack, Search, Home } from '@mui/icons-material';
import { adminAPI } from '../services/api';
import { getSocket } from '../services/socket';

const AdminDashboard = () => {
  const [tabValue, setTabValue] = useState(0);
  const [logs, setLogs] = useState([]);
  const [transfers, setTransfers] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [transfersPage, setTransfersPage] = useState(0);
  const [logsPage, setLogsPage] = useState(0);
  const [usersPage, setUsersPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const navigate = useNavigate();

  useEffect(() => {
    loadData();

    // Connect to socket for real-time updates
    const socket = getSocket();
    socket.on('transfer_update', (data) => {
      loadTransfers();
    });

    return () => {
      socket.off('transfer_update');
    };
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      await Promise.all([loadLogs(), loadTransfers(), loadUsers()]);
    } finally {
      setLoading(false);
    }
  };

  const loadLogs = async () => {
    try {
      const response = await adminAPI.getLogs(100);
      setLogs(response.data);
    } catch (err) {
      console.error('Error loading logs:', err);
    }
  };

  const loadTransfers = async () => {
    try {
      const response = await adminAPI.getTransfers();
      setTransfers(response.data);
    } catch (err) {
      console.error('Error loading transfers:', err);
    }
  };

  const loadUsers = async () => {
    try {
      const response = await adminAPI.getUsers();
      setUsers(response.data);
    } catch (err) {
      console.error('Error loading users:', err);
    }
  };

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
    setSearchQuery(''); // Clear search when switching tabs
  };

  // Filter functions
  const filterTransfers = (transfers, query) => {
    if (!query) return transfers;
    const lowerQuery = query.toLowerCase();
    return transfers.filter(transfer => 
      transfer.filename?.toLowerCase().includes(lowerQuery) ||
      transfer.transfer_type?.toLowerCase().includes(lowerQuery) ||
      transfer.transfer_status?.toLowerCase().includes(lowerQuery) ||
      transfer.user_id?.toString().includes(lowerQuery) ||
      new Date(transfer.timestamp).toLocaleString().toLowerCase().includes(lowerQuery)
    );
  };

  const filterLogs = (logs, query) => {
    if (!query) return logs;
    const lowerQuery = query.toLowerCase();
    return logs.filter(log => 
      log.admin_username?.toLowerCase().includes(lowerQuery) ||
      log.action?.toLowerCase().includes(lowerQuery) ||
      log.target_type?.toLowerCase().includes(lowerQuery) ||
      log.details?.toLowerCase().includes(lowerQuery) ||
      new Date(log.timestamp).toLocaleString().toLowerCase().includes(lowerQuery)
    );
  };

  const filterUsers = (users, query) => {
    if (!query) return users;
    const lowerQuery = query.toLowerCase();
    return users.filter(user => 
      user.username?.toLowerCase().includes(lowerQuery) ||
      user.email?.toLowerCase().includes(lowerQuery) ||
      user.role?.toLowerCase().includes(lowerQuery) ||
      user.id?.toString().includes(lowerQuery) ||
      new Date(user.created_at).toLocaleDateString().toLowerCase().includes(lowerQuery)
    );
  };

  const filteredTransfers = filterTransfers(transfers, searchQuery);
  const filteredLogs = filterLogs(logs, searchQuery);
  const filteredUsers = filterUsers(users, searchQuery);

  // Pagination handlers
  const handleTransfersPageChange = (event, newPage) => {
    setTransfersPage(newPage);
  };

  const handleLogsPageChange = (event, newPage) => {
    setLogsPage(newPage);
  };

  const handleUsersPageChange = (event, newPage) => {
    setUsersPage(newPage);
  };

  const handleRowsPerPageChange = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setTransfersPage(0);
    setLogsPage(0);
    setUsersPage(0);
  };

  // Get paginated data
  const getPaginatedData = (data, page, rowsPerPage) => {
    const startIndex = page * rowsPerPage;
    return data.slice(startIndex, startIndex + rowsPerPage);
  };

  return (
    <Box>
      <AppBar position="static">
        <Toolbar>
          <Button
            color="inherit"
            startIcon={<Home />}
            onClick={() => navigate('/dashboard')}
            sx={{ mr: 2 }}
          >
            Dashboard
          </Button>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Admin Dashboard
          </Typography>
          <IconButton
            color="inherit"
            onClick={() => navigate('/dashboard')}
            title="Back to Dashboard"
          >
            <ArrowBack />
          </IconButton>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ marginTop: 4 }}>
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
          <Typography color="text.primary">Admin Panel</Typography>
        </Breadcrumbs>

        <Paper>
          <Tabs value={tabValue} onChange={handleTabChange}>
            <Tab label="File Transfers" />
            <Tab label="Admin Logs" />
            <Tab label="Users" />
          </Tabs>

          <Box sx={{ padding: 3 }}>
            {/* Search Bar */}
            <TextField
              fullWidth
              placeholder="Search..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                ),
              }}
              sx={{ marginBottom: 2 }}
            />

            {tabValue === 0 && (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Timestamp</TableCell>
                      <TableCell>User</TableCell>
                      <TableCell>File</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell>Size</TableCell>
                      <TableCell>Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {filteredTransfers.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={6} align="center">
                          {searchQuery ? 'No transfers found matching your search' : 'No transfers found'}
                        </TableCell>
                      </TableRow>
                    ) : (
                      getPaginatedData(filteredTransfers, transfersPage, rowsPerPage).map((transfer) => (
                      <TableRow key={transfer.id}>
                        <TableCell>
                          {new Date(transfer.timestamp).toLocaleString()}
                        </TableCell>
                        <TableCell>{transfer.user_id}</TableCell>
                        <TableCell>{transfer.filename || 'N/A'}</TableCell>
                        <TableCell>{transfer.transfer_type}</TableCell>
                        <TableCell>
                          {(transfer.bytes_transferred / 1024).toFixed(2)} KB
                        </TableCell>
                        <TableCell>{transfer.transfer_status}</TableCell>
                      </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
                <TablePagination
                  component="div"
                  count={filteredTransfers.length}
                  page={transfersPage}
                  onPageChange={handleTransfersPageChange}
                  rowsPerPage={rowsPerPage}
                  onRowsPerPageChange={handleRowsPerPageChange}
                  rowsPerPageOptions={[5, 10, 25, 50]}
                />
              </TableContainer>
            )}

            {tabValue === 1 && (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Timestamp</TableCell>
                      <TableCell>Admin</TableCell>
                      <TableCell>Action</TableCell>
                      <TableCell>Target</TableCell>
                      <TableCell>Details</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {filteredLogs.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={5} align="center">
                          {searchQuery ? 'No logs found matching your search' : 'No logs found'}
                        </TableCell>
                      </TableRow>
                    ) : (
                      getPaginatedData(filteredLogs, logsPage, rowsPerPage).map((log) => (
                      <TableRow key={log.id}>
                        <TableCell>
                          {new Date(log.timestamp).toLocaleString()}
                        </TableCell>
                        <TableCell>{log.admin_username}</TableCell>
                        <TableCell>{log.action}</TableCell>
                        <TableCell>
                          {log.target_type} {log.target_id ? `#${log.target_id}` : ''}
                        </TableCell>
                        <TableCell>{log.details || 'N/A'}</TableCell>
                      </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
                <TablePagination
                  component="div"
                  count={filteredLogs.length}
                  page={logsPage}
                  onPageChange={handleLogsPageChange}
                  rowsPerPage={rowsPerPage}
                  onRowsPerPageChange={handleRowsPerPageChange}
                  rowsPerPageOptions={[5, 10, 25, 50]}
                />
              </TableContainer>
            )}

            {tabValue === 2 && (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>ID</TableCell>
                      <TableCell>Username</TableCell>
                      <TableCell>Email</TableCell>
                      <TableCell>Role</TableCell>
                      <TableCell>Created</TableCell>
                      <TableCell>Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {filteredUsers.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={6} align="center">
                          {searchQuery ? 'No users found matching your search' : 'No users found'}
                        </TableCell>
                      </TableRow>
                    ) : (
                      getPaginatedData(filteredUsers, usersPage, rowsPerPage).map((user) => (
                      <TableRow key={user.id}>
                        <TableCell>{user.id}</TableCell>
                        <TableCell>{user.username}</TableCell>
                        <TableCell>{user.email}</TableCell>
                        <TableCell>{user.role}</TableCell>
                        <TableCell>
                          {new Date(user.created_at).toLocaleDateString()}
                        </TableCell>
                        <TableCell>
                          {user.is_active ? 'Active' : 'Inactive'}
                        </TableCell>
                      </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
                <TablePagination
                  component="div"
                  count={filteredUsers.length}
                  page={usersPage}
                  onPageChange={handleUsersPageChange}
                  rowsPerPage={rowsPerPage}
                  onRowsPerPageChange={handleRowsPerPageChange}
                  rowsPerPageOptions={[5, 10, 25, 50]}
                />
              </TableContainer>
            )}
          </Box>
        </Paper>
      </Container>
    </Box>
  );
};

export default AdminDashboard;


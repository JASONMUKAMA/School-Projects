/**
 * Socket.IO Service
 * Handles real-time communication
 */

import io from 'socket.io-client';

// Use relative URL in production/Docker, absolute in development
const SOCKET_URL = process.env.REACT_APP_SOCKET_URL || 
  (process.env.NODE_ENV === 'production' ? window.location.origin : 'http://localhost:5000');

let socket = null;

export const connectSocket = () => {
  if (!socket) {
    socket = io(SOCKET_URL, {
      transports: ['websocket'],
    });
    
    socket.on('connect', () => {
      console.log('Connected to monitoring server');
    });
    
    socket.on('disconnect', () => {
      console.log('Disconnected from monitoring server');
    });
  }
  return socket;
};

export const disconnectSocket = () => {
  if (socket) {
    socket.disconnect();
    socket = null;
  }
};

export const getSocket = () => {
  if (!socket) {
    return connectSocket();
  }
  return socket;
};

export default { connectSocket, disconnectSocket, getSocket };


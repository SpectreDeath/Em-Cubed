import React from 'react';
import { Container, Typography, Paper, Box, Button } from '@mui/material';
import { useState, useEffect } from 'react';
import io from 'socket.io-client';

function App() {
  const [message, setMessage] = useState('Loading...');
  const [data, setData] = useState(null);

  useEffect(() => {
    // In a real app, we would connect to the telemetry API and WebSocket
    // For now, we'll simulate
    setMessage('Em-Cubed Observability Dashboard');
    setData({
      status: 'ready',
      timestamp: new Date().toISOString(),
      skills_monitored: 0,
      executions_per_minute: 0
    });
  }, []);

  return (
    <Container maxWidth="md">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" align="center">
          Em-Cubed Observability Dashboard
        </Typography>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6">System Status</Typography>
          <Typography>{message}</Typography>
          {data && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2">
                <strong>Status:</strong> {data.status}
              </Typography>
              <Typography variant="body2">
                <strong>Timestamp:</strong> {data.timestamp}
              </Typography>
              <Typography variant="body2">
                <strong>Skills Monitored:</strong> {data.skills_monitored}
              </Typography>
              <Typography variant="body2">
                <strong>Executions/Min:</strong> {data.executions_per_minute}
              </Typography>
            </Box>
          )}
          <Button variant="contained" color="primary" size="small">
            Refresh
          </Button>
        </Paper>
      </Box>
    </Container>
  );
}

export default App;
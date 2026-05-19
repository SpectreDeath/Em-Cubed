import React from 'react';
import { Container, Typography, Paper, Box, Button, CircularProgress, Tab, Tabs, Stack, Grid, Card, CardContent, CardHeader } from '@mui/material';
import { useState, useEffect } from 'react';
import io from 'socket.io-client';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function App() {
  const [message, setMessage] = useState('Loading...');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [socket, setSocket] = useState(null);
  const [tabValue, setTabValue] = useState(0); // 0: Overview, 1: Skills, 2: Executions
  const [skillMetrics, setSkillMetrics] = useState([]);
  const [recentExecutions, setRecentExecutions] = useState([]);
  const [executionHistory, setExecutionHistory] = useState([]);

  useEffect(() => {
    // Fetch initial data
    fetchOverviewData();
    fetchSkillsData();
    fetchRecentExecutions();
    
    // Set up WebSocket connection for real-time updates
    const socketIO = io(process.env.REACT_APP_API_URL || 'http://localhost:8000');
    setSocket(socketIO);
    
    socketIO.on('connect', () => {
      console.log('Connected to WebSocket');
      // Subscribe to telemetry updates
      socketIO.emit('subscribe_telemetry');
    });
    
    socketIO.on('telemetry_update', (data) => {
      // Update dashboard with real-time data
      if (data.data && data.data.overall_stats) {
        setData(prevData => ({
          ...prevData,
          ...data.data.overall_stats,
          timestamp: new Date().toISOString()
        }));
      }
    });
    
    socketIO.on('skill_metrics_update', (data) => {
      if (data.data) {
        setSkillMetrics(data.data);
      }
    });
    
    socketIO.on('recent_executions_update', (data) => {
      if (data.data) {
        setRecentExecutions(data.data);
        // Update execution history for chart
        setExecutionHistory(prev => {
          const newData = [...prev, ...data.data];
          // Keep only last 50 entries for performance
          return newData.slice(-50);
        });
      }
    });
    
    // Cleanup on unmount
    return () => {
      socketIO.disconnect();
    };
  }, []);

  const fetchOverviewData = async () => {
    try {
      const response = await fetch('/telemetry/stats');
      const result = await response.json();
      
      setData({
        status: result.status || 'healthy',
        timestamp: new Date().toISOString(),
        total_executions: result.total_executions || 0,
        success_rate: result.overall_success_rate || 0,
        unique_skills: result.unique_skills || 0,
        avg_execution_time: result.avg_execution_time_ms || 0
      });
    } catch (error) {
      console.error('Error fetching overview data:', error);
      setMessage('Error loading overview data');
    } finally {
      setLoading(false);
    }
  };

  const fetchSkillsData = async () => {
    try {
      const response = await fetch('/telemetry/skills');
      const result = await response.json();
      setSkillMetrics(result.skills || []);
    } catch (error) {
      console.error('Error fetching skills data:', error);
    }
  };

  const fetchRecentExecutions = async () => {
    try {
      const response = await fetch('/telemetry/recent?limit=20');
      const result = await response.json();
      setRecentExecutions(result.executions || []);
    } catch (error) {
      console.error('Error fetching recent executions:', error);
    }
  };

  const handleRefresh = async () => {
    setLoading(true);
    await fetchOverviewData();
    await fetchSkillsData();
    await fetchRecentExecutions();
  };

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
    if (newValue === 1) { // Skills tab
      fetchSkillsData();
    } else if (newValue === 2) { // Executions tab
      fetchRecentExecutions();
    }
  };

  if (loading) {
    return (
      <Container maxWidth="md">
        <Box sx={{ my: 4, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <CircularProgress />
          <Typography sx={{ ml: 2 }}>Loading dashboard data...</Typography>
        </Box>
      </Container>
    );
  }

  const statusColor = data?.status === 'healthy' ? 'success' : data?.status === 'degraded' ? 'warning' : 'error';

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" align="center">
          Em-Cubed Observability Dashboard
        </Typography>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6">System Status</Typography>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h5">
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Box sx={{ width: 12, height: 12, borderRadius: '50%', backgroundColor: statusColor, mr: 2 }} />
                <Typography>{data?.status?.toUpperCase() || 'UNKNOWN'}</Typography>
              </Box>
            </Typography>
            <Button 
              variant="contained" 
              color={data?.status === 'healthy' ? 'success' : 'error'} 
              size="small"
              onClick={handleRefresh}
            >
              Refresh
            </Button>
          </Box>
          <Box sx={{ mt: 2 }}>
            <Grid container spacing={2}>
              <Grid item xs={6} sm={3}>
                <Typography variant="body2">
                  <strong>Timestamp:</strong> {' '}
                  {data?.timestamp ? new Date(data.timestamp).toLocaleTimeString() : 'N/A'}
                </Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="body2">
                  <strong>Skills Monitored:</strong> {' '}
                  {data?.unique_skills || 0}
                </Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="body2">
                  <strong>Total Executions:</strong> {' '}
                  {data?.total_executions || 0}
                </Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="body2">
                  <strong>Success Rate:</strong> {' '}
                  {`${(data?.success_rate || 0) * 100}%`}
                </Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="body2">
                  <strong>Avg Exec Time:</strong> {' '}
                  {`${Math.round(data?.avg_execution_time || 0)}ms`}
                </Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="body2">
                  <strong>Executions/Min:</strong> {' '}
                  {Math.round(((data?.total_executions || 0) / Math.max(1, (Date.now() - new Date().setHours(0,0,0,0)) / 60000)) || 0)}
                </Typography>
              </Grid>
            </Grid>
          </Box>
        </Paper>
        
        <Tabs value={tabValue} onChange={handleTabChange} sx={{ mt: 3 }}>
          <Tab label="Overview" />
          <Tab label="Skills" />
          <Tab label="Executions" />
        </Tabs>
        
        {tabValue === 0 && (
          <>
            <Paper sx={{ p: 3, mt: 3 }}>
              <Typography variant="h6">Execution Trends (Last Hour)</Typography>
              <Box sx={{ mt: 2 }}>
                {executionHistory.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={executionHistory.map((exec, index) => ({
                      name: `Exec ${index + 1}`,
                      success: exec.success ? 1 : 0,
                      time: exec.execution_time_ms || 0
                    }))}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line type="monotone" dataKey="success" stroke="#8884d8" activeDot={{ r: 8 }} />
                      <Line type="monotone" dataKey="time" stroke="#82ca9d" />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <Typography color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
                    No execution data available yet
                  </Typography>
                )}
              </Box>
            </Paper>
            
            <Paper sx={{ p: 3, mt: 3 }}>
              <Typography variant="h6">System Health</Typography>
              <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Box sx={{ width: 16, height: 16, borderRadius: '50%', backgroundColor: statusColor, mr: 2 }} />
                  <Typography variant="body5">
                    Overall Status: <strong>{data?.status?.toUpperCase() || 'UNKNOWN'}</strong>
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Box sx={{ width: 16, height: 16, borderRadius: '50%', backgroundColor: data?.success_rate && data?.success_rate > 0.9 ? 'success' : data?.success_rate && data?.success_rate > 0.7 ? 'warning' : 'error', mr: 2 }} />
                  <Typography variant="body5">
                    Success Rate: <strong>{`${(data?.success_rate || 0) * 100}%`}</strong>
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Box sx={{ width: 16, height: 16, borderRadius: '50%', backgroundColor: data?.total_executions && data?.total_executions < 1000 ? 'success' : data?.total_executions && data?.total_executions < 5000 ? 'warning' : 'error', mr: 2 }} />
                  <Typography variant="body5">
                    Total Executions: <strong>{data?.total_executions || 0}</strong>
                  </Typography>
                </Box>
              </Box>
            </Paper>
          </>
        )}
        
        {tabValue === 1 && (
          <Paper sx={{ p: 3, mt: 3 }}>
            <Typography variant="h6">Skill Performance Metrics</Typography>
            {skillMetrics.length > 0 ? (
              <Box sx={{ mt: 2, overflowX: 'auto' }}>
                <table sx={{ minWidth: 650 }}>
                  <thead>
                    <tr>
                      <th sx={{ textAlign: 'left', py: 2 }}>Skill ID</th>
                      <th sx={{ textAlign: 'left', py: 2 }}>Total Executions</th>
                      <th sx={{ textAlign: 'left', py: 2 }}>Success Rate</th>
                      <th sx={{ textAlign: 'left', py: 2 }}>Avg Time (ms)</th>
                      <th sx={{ textAlign: 'left', py: 2 }}>Last Executed</th>
                    </tr>
                  </thead>
                  <tbody>
                    {skillMetrics.map((skill, index) => (
                      <tr key={index} sx={{ borderBottom: `1px solid #e0e0e0` }}>
                        <td sx={{ py: 2 }}>{skill.skill_id || 'Unknown'}</td>
                        <td sx={{ py: 2 }}>{skill.count || 0}</td>
                        <td sx={{ py: 2 }}>
                          {`${(skill.success_rate || 0) * 100}%`}
                        </td>
                        <td sx={{ py: 2 }}>{Math.round(skill.avg_time_ms || 0)}ms</td>
                        <td sx={{ py: 2 }}>{skill.last_executed ? new Date(skill.last_executed).toLocaleTimeString() : 'Never'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </Box>
            ) : (
              <Typography color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
                No skill metrics available
              </Typography>
            )}
          </Paper>
        )}
        
        {tabValue === 2 && (
          <Paper sx={{ p: 3, mt: 3 }}>
            <Typography variant="h6">Recent Executions</Typography>
            {recentExecutions.length > 0 ? (
              <Box sx={{ mt: 2, overflowX: 'auto' }}>
                <table sx={{ minWidth: 700 }}>
                  <thead>
                    <tr>
                      <th sx={{ textAlign: 'left', py: 2 }}>Skill ID</th>
                      <th sx={{ textAlign: 'left', py: 2 }}>Status</th>
                      <th sx={{ textAlign: 'left', py: 2 }}>Execution Time</th>
                      <th sx={{ textAlign: 'left', py: 2 }}>Timestamp</th>
                      <th sx={{ textAlign: 'left', py: 2 }}>Context Size</th>
                    </tr>
                  </thead>
                  <tbody>
                    {recentExecutions.map((exec, index) => (
                      <tr key={index} sx={{ borderBottom: `1px solid #e0e0e0` }}>
                        <td sx={{ py: 2 }}>{exec.skill_id || 'Unknown'}</td>
                        <td sx={{ py: 2 }}>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Box sx={{ width: 10, height: 10, borderRadius: '50%', backgroundColor: exec.success ? '#4caf50' : '#f44336', mr: 1 }} />
                            {exec.success ? 'Success' : 'Failed'}
                          </Box>
                        </td>
                        <td sx={{ py: 2 }}>{exec.execution_time_ms ? `${exec.execution_time_ms}ms` : 'N/A'}</td>
                        <td sx={{ py: 2 }}>{exec.timestamp ? new Date(exec.timestamp).toLocaleTimeString() : 'N/A'}</td>
                        <td sx={{ py: 2 }}>{JSON.stringify(exec.context || {}).length} bytes</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </Box>
            ) : (
              <Typography color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
                No recent executions available
              </Typography>
            )}
          </Paper>
        )}
      </Box>
    </Container>
  );
}

export default App;
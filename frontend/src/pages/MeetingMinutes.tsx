import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  Divider,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  Chip,
} from '@mui/material';
import { tasksApi, Task } from '../api/tasks';

const MeetingMinutes: React.FC = () => {
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [taskId, setTaskId] = useState<number | null>(null);
  const [task, setTask] = useState<Task | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<Task[]>([]);

  // 轮询任务状态
  useEffect(() => {
    let interval: any;
    if (taskId && task?.status !== 'completed' && task?.status !== 'failed') {
      interval = setInterval(async () => {
        try {
          const updatedTask = await tasksApi.getTask(taskId);
          setTask(updatedTask);
          if (updatedTask.status === 'completed' || updatedTask.status === 'failed') {
            clearInterval(interval);
            loadHistory();
          }
        } catch (err) {
          console.error('Failed to poll task status', err);
          clearInterval(interval);
        }
      }, 2000);
    }
    return () => clearInterval(interval);
  }, [taskId, task]);

  const loadHistory = async () => {
    try {
      const tasks = await tasksApi.getTasks();
      setHistory(tasks.filter(t => t.task_type === 'meeting_minutes'));
    } catch (err) {
      console.error('Failed to load history', err);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const handleSubmit = async () => {
    if (!inputText.trim()) return;
    
    setLoading(true);
    setError(null);
    setTask(null);
    try {
      const newTask = await tasksApi.createMeetingMinutes(inputText);
      setTaskId(newTask.id);
      setTask(newTask);
      setInputText('');
    } catch (err: any) {
      setError(err.response?.data?.detail || '创建任务失败，请检查后端运行状态。');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'in_progress': return 'primary';
      case 'failed': return 'error';
      default: return 'default';
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>会议纪要处理</Typography>
      <Typography variant="body1" color="textSecondary" paragraph>
        上传或粘贴会议转录文本，AI将自动为您总结纪要。
      </Typography>

      <Paper sx={{ p: 3, mb: 4 }}>
        <TextField
          fullWidth
          multiline
          rows={8}
          variant="outlined"
          placeholder="请输入会议转录文本..."
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          sx={{ mb: 2 }}
        />
        <Button
          variant="contained"
          size="large"
          onClick={handleSubmit}
          disabled={loading || !inputText.trim()}
        >
          {loading ? <CircularProgress size={24} /> : '开始生成'}
        </Button>
      </Paper>

      {error && <Alert severity="error" sx={{ mb: 4 }}>{error}</Alert>}

      {task && (
        <Card sx={{ mb: 4, borderLeft: 6, borderColor: `${getStatusColor(task.status)}.main` }}>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">当前任务 (ID: {task.id})</Typography>
              <Chip label={task.status.toUpperCase()} color={getStatusColor(task.status) as any} />
            </Box>
            
            {task.status === 'in_progress' && (
              <Box display="flex" alignItems="center" gap={2}>
                <CircularProgress size={20} />
                <Typography>正在处理中，请稍候...</Typography>
              </Box>
            )}

            {task.status === 'completed' && (
              <Box>
                <Typography variant="subtitle1" fontWeight="bold">生成结果：</Typography>
                <Paper variant="outlined" sx={{ p: 2, mt: 1, backgroundColor: '#f9f9f9', whiteSpace: 'pre-wrap' }}>
                  {task.output_data}
                </Paper>
              </Box>
            )}

            {task.status === 'failed' && (
              <Typography color="error">出错啦: {task.error_message}</Typography>
            )}
          </CardContent>
        </Card>
      )}

      <Typography variant="h5" gutterBottom sx={{ mt: 4 }}>历史记录</Typography>
      <Divider sx={{ mb: 2 }} />
      <List>
        {history.length === 0 ? (
          <Typography color="textSecondary">暂无历史记录</Typography>
        ) : (
          history.map((h) => (
            <ListItem 
              key={h.id} 
              component={Paper} 
              variant="outlined" 
              sx={{ mb: 1, cursor: 'pointer', '&:hover': { backgroundColor: '#f5f5f5' } }}
              onClick={() => { setTask(h); setTaskId(h.id); }}
            >
              <ListItemText 
                primary={`任务 #${h.id}: ${h.title}`} 
                secondary={`状态: ${h.status} | 创建时间: ${new Date().toLocaleDateString()}`} 
              />
              <Chip size="small" label={h.status} color={getStatusColor(h.status) as any} />
            </ListItem>
          ))
        )}
      </List>
    </Box>
  );
};

export default MeetingMinutes;

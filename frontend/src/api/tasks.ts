import axiosInstance from './axios';

export interface Task {
  id: number;
  title: string;
  description: string | null;
  task_type: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  input_data: string | null;
  output_data: string | null;
  error_message: string | null;
}

export const tasksApi = {
  createMeetingMinutes: async (inputText: string): Promise<Task> => {
    const params = new URLSearchParams();
    params.append('input_text', inputText);
    const response = await axiosInstance.post(`/tasks/meeting-minutes?${params.toString()}`);
    return response.data;
  },
  
  getTasks: async (): Promise<Task[]> => {
    const response = await axiosInstance.get('/tasks/');
    return response.data;
  },
  
  getTask: async (id: number): Promise<Task> => {
    const response = await axiosInstance.get(`/tasks/${id}`);
    return response.data;
  },
};

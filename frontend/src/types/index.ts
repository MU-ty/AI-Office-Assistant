export interface User {
  id: number
  username: string
  email: string
  full_name?: string
  is_active: boolean
}

export interface Task {
  id: number
  user_id: number
  title: string
  description?: string
  task_type: string
  status: string
  input_data?: string
  output_data?: string
  created_at: string
  updated_at: string
}

export interface Document {
  id: number
  user_id: number
  title: string
  content?: string
  document_type: string
  file_size?: number
  created_at: string
  updated_at: string
}

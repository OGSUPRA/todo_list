export interface User {
  id: string;
  username: string;
  email: string;
  avatar_path: string | null;
  created_at: string;
}

export interface Task {
  id: string;
  title: string;
  description: string;
  status: "todo" | "done";
  is_deleted: boolean;
  created_at: string;
  updated_at: string;
}

export interface LoginPayload {
  username: string;
  password: string;
}

export interface RegisterPayload {
  username: string;
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

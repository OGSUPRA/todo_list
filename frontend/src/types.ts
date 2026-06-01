export type UserRole = "admin" | "vip" | "standard";
export type PublicRole = "vip" | "standard";

export interface User {
  id: string;
  username: string;
  email: string;
  avatar_path: string | null;
  role: UserRole;
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
  role: PublicRole;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface PaginationMeta {
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
  sort_by: string;
  sort_order: string;
}

export interface TaskSummary {
  total: number;
  todo: number;
  done: number;
  archived: number;
}

export interface TaskListResponse {
  items: Task[];
  meta: PaginationMeta;
  summary: TaskSummary;
}

export interface NamedMetric {
  label: string;
  value: number;
}

export interface MonitoringLinks {
  dozzle: string;
  pgweb: string;
}

export interface AdminOverviewResponse {
  monitoring: MonitoringLinks;
  role_counts: NamedMetric[];
  task_counts: NamedMetric[];
  request_volume: NamedMetric[];
  action_breakdown: NamedMetric[];
  status_breakdown: NamedMetric[];
  top_paths: NamedMetric[];
}

export interface AuditEvent {
  id: string;
  category: string;
  action: string;
  path: string;
  method: string;
  status_code: number;
  duration_ms: number;
  username: string | null;
  role: string | null;
  client_ip: string | null;
  request_id: string | null;
  created_at: string;
  details: Record<string, unknown> | null;
}

export interface AuditEventsResponse {
  items: AuditEvent[];
  meta: PaginationMeta;
}

export interface AdminUser {
  id: string;
  username: string;
  email: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  task_summary: TaskSummary;
}

export interface AdminUsersResponse {
  items: AdminUser[];
  meta: PaginationMeta;
}

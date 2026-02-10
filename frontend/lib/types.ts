export interface FolderStatus {
  name: string;
  count: number;
}

export interface CoreFileStatus {
  name: string;
  exists: boolean;
}

export interface VaultStatus {
  initialized: boolean;
  folders: FolderStatus[];
  core_files: CoreFileStatus[];
}

export interface ActionItem {
  id: string;
  filename: string;
  type: string;
  sender: string;
  subject: string;
  priority: string;
  received: string;
  status: string;
  snippet: string;
}

export interface ProcessResult {
  processed: number;
  actions: string[];
}

export interface Approval {
  id: string;
  filename: string;
  action: string;
  source_file: string;
  created: string;
  expires: string;
  status: string;
  priority: string;
  subject: string;
  reason: string;
}

export interface DashboardMetrics {
  needs_action: number;
  pending_approval: number;
  done_today: number;
  active_plans: number;
  mtd_revenue: string;
  monthly_target: string;
  alerts: string[];
  recent_activity: string[];
  agent_health: string;
}

export interface SectionValidation {
  section: string;
  description: string;
  present: boolean;
}

export interface HandbookData {
  content: string;
  validation: SectionValidation[];
  is_complete: boolean;
}

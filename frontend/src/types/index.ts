export interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

export interface Token {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface DefectItem {
  defect_id: number;
  class_name: string;
  confidence: number;
  bbox: number[];
  area_px: number;
  area_mm2: number;
  length_mm: number;
  width_mm: number;
  perimeter_mm: number;
  panel?: string;
  is_glare: boolean;
  glare_score: number;
}

export interface Inspection {
  id: string;
  vehicle_number: string;
  vehicle_model?: string;
  owner_name?: string;
  inspector_name?: string;
  image_path: string;
  result_path?: string;
  mask_path?: string;
  defects?: DefectItem[];
  severity_score?: number;
  severity_label?: string;
  confidence?: number;
  total_area_mm2?: number;
  defect_count?: number;
  repair_cost_min?: number;
  repair_cost_max?: number;
  repair_cost_estimated?: number;
  time_required?: string;
  priority?: string;
  recommendation?: string;
  created_at: string;
  has_report: boolean;
}

export interface InspectionList {
  total: number;
  page: number;
  limit: number;
  items: Inspection[];
}

export interface MonthlyCount { month: string; count: number; avg_cost: number; }
export interface SeverityCount { label: string; count: number; percentage: number; }

export interface DashboardData {
  total_inspections: number;
  critical_defects: number;
  avg_severity: number;
  avg_repair_cost: number;
  monthly_inspections: MonthlyCount[];
  severity_distribution: SeverityCount[];
  recent_inspections: Inspection[];
}

export type SeverityLabel = 'Minor' | 'Low' | 'Moderate' | 'High' | 'Critical';

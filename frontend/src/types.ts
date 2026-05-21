export interface Equipment {
  id: string;
  asset_tag: string;
  name: string;
  manufacturer: string;
  model: string;
  location: string;
  install_date?: string;
  qr_payload: string;
}

export interface Citation {
  document_id: string;
  title: string;
  doc_type: string;
  excerpt: string;
  page?: number;
  score: number;
}

export interface AskResponse {
  answer: string;
  citations: Citation[];
  equipment?: Equipment;
  suggested_inspections: string[];
  confidence: string;
}

export interface ServiceTicket {
  id: string;
  equipment_id: string;
  title: string;
  description: string;
  priority: string;
  status: string;
  error_codes: string[];
  created_by: string;
  created_at: string;
}

export interface QRResolveResponse {
  equipment: Equipment;
  recent_tickets: ServiceTicket[];
  document_count: number;
}

export interface CachedAnswer {
  id: string;
  question: string;
  response: AskResponse;
  equipment_id?: string;
  cached_at: number;
}

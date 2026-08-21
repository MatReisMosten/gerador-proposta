// Espelha api/schemas.py — mudou lá, muda aqui.

export interface ProposalTypeField {
  id: string
  label: string
  type: 'text' | 'textarea' | 'select'
  placeholder: string
  required: boolean
  options: string[] | null
}

export interface ProposalType {
  id: string
  label: string
  mode: 'package' | 'llm_package' | 'llm_full'
  description: string
  fields: ProposalTypeField[]
  requires_form: boolean
  show_brief: boolean
  show_attachments: boolean
  hide_client: boolean
  hide_logo: boolean
}

export interface AuthStatus {
  authenticated: boolean
  password_required: boolean
}

export interface TemplateSummary {
  name: string
  size_label: string
  updated_at: string
  sections: Record<string, number>
  tokens: string[]
}

export interface ProposalMeta {
  client: string
  code: string
  type: string
  type_label: string
  size_label: string
  filename: string
  empty_tokens: number
}

export interface GenerateProposalResponse {
  token: string
  meta: ProposalMeta
}

export interface ApiErrorBody {
  detail: string
}

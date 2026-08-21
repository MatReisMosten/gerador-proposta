import type {
  AuthStatus,
  GenerateProposalResponse,
  ProposalType,
  TemplateSummary,
} from '../types'

export class ApiError extends Error {
  status: number

  constructor(status: number, detail: string) {
    super(detail)
    this.status = status
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const resp = await fetch(`/api${path}`, {
    credentials: 'include',
    ...init,
  })
  if (!resp.ok) {
    let detail = `Erro ${resp.status}`
    try {
      const body = await resp.json()
      detail = body?.detail || detail
    } catch {
      // resposta sem corpo JSON — mantém a mensagem genérica
    }
    throw new ApiError(resp.status, detail)
  }
  return resp.json() as Promise<T>
}

export function getProposalTypes(): Promise<ProposalType[]> {
  return request<ProposalType[]>('/proposal-types')
}

export function getTemplateSummary(): Promise<TemplateSummary> {
  return request<TemplateSummary>('/templates/summary')
}

export function getAuthStatus(): Promise<AuthStatus> {
  return request<AuthStatus>('/auth/status')
}

export function login(password: string): Promise<AuthStatus> {
  return request<AuthStatus>('/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ password }),
  })
}

export function logout(): Promise<void> {
  return request('/auth/logout', { method: 'POST' })
}

export async function extractText(
  file: File,
): Promise<{ text: string; truncated: boolean }> {
  const form = new FormData()
  form.append('file', file)
  return request('/extract-text', { method: 'POST', body: form })
}

export interface GeneratePayload {
  typeId: string
  clientName: string
  projectCode: string
  fieldValues: Record<string, string>
  brief: string
  transcription: string
  estimate: string
  logo: File | null
}

export function generateProposal(
  payload: GeneratePayload,
): Promise<GenerateProposalResponse> {
  const form = new FormData()
  form.append('type_id', payload.typeId)
  form.append('client_name', payload.clientName)
  form.append('project_code', payload.projectCode)
  form.append('fields_json', JSON.stringify(payload.fieldValues))
  form.append('brief', payload.brief)
  form.append('transcription', payload.transcription)
  form.append('estimate', payload.estimate)
  if (payload.logo) form.append('logo', payload.logo)

  return request<GenerateProposalResponse>('/proposals/generate', {
    method: 'POST',
    body: form,
  })
}

export function downloadUrl(token: string): string {
  return `/api/proposals/download/${token}`
}

/** Dispara o download do PPTX gerado sem navegar a página (blob + <a> temporário). */
export async function triggerDownload(token: string, filename: string): Promise<void> {
  const resp = await fetch(downloadUrl(token), { credentials: 'include' })
  if (!resp.ok) throw new ApiError(resp.status, 'Falha ao baixar o arquivo.')
  const blob = await resp.blob()
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
}

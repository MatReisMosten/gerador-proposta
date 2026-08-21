// Máscaras de campo — espelha api/formatting.py (validação real acontece
// no servidor; isto é só UX, nunca a fonte de verdade).

const PROJECT_CODE_RE = /^[A-Z]{3}\d{3}-\d{2}$/

export function formatProjectCode(raw: string): string {
  const chars = (raw || '').replace(/[^A-Za-z0-9]/g, '').toUpperCase()
  const letters = chars.replace(/[^A-Z]/g, '').slice(0, 3)
  const digits = chars.replace(/[^0-9]/g, '')
  const d1 = digits.slice(0, 3)
  const d2 = digits.slice(3, 5)
  let out = letters + d1
  if (d2 || digits.length > 3) out += `-${d2}`
  return out
}

export function isValidProjectCode(code: string): boolean {
  return PROJECT_CODE_RE.test((code || '').trim().toUpperCase())
}

export function formatMoneyBR(raw: string): string {
  const digits = (raw || '').replace(/\D/g, '')
  if (!digits) return ''
  const value = parseInt(digits.slice(0, 12), 10)
  const reais = Math.floor(value / 100)
  const cents = value % 100
  const reaisFmt = reais.toLocaleString('pt-BR')
  return `R$ ${reaisFmt},${String(cents).padStart(2, '0')}`
}

export function formatMonthsOnly(raw: string): string {
  const digits = (raw || '').replace(/\D/g, '').slice(0, 3)
  if (!digits) return ''
  return String(parseInt(digits, 10))
}

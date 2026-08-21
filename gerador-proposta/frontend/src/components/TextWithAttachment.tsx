import { useState } from 'react'
import { ApiError, extractText } from '../api/client'
import { FileDropzone } from './FileDropzone'

interface TextWithAttachmentProps {
  label: string
  value: string
  onChange: (value: string) => void
  placeholder?: string
  accept: string
  dropHint: string
  rows?: number
}

export function TextWithAttachment({
  label,
  value,
  onChange,
  placeholder,
  accept,
  dropHint,
  rows = 7,
}: TextWithAttachmentProps) {
  const [fileName, setFileName] = useState<string | null>(null)
  const [notice, setNotice] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function handleFile(file: File) {
    setError(null)
    setNotice(null)
    try {
      const { text, truncated } = await extractText(file)
      onChange(text)
      setFileName(file.name)
      if (truncated) setNotice('Texto truncado ao limite do campo.')
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Falha ao extrair texto do arquivo.')
    }
  }

  return (
    <div className="field">
      <label>{label}</label>
      <FileDropzone
        accept={accept}
        label="Arraste um arquivo ou clique para anexar"
        hint={dropHint}
        onFile={handleFile}
      />
      {fileName && (
        <p className="field-hint">
          Anexo: <b>{fileName}</b> — revise o texto abaixo.
        </p>
      )}
      {notice && <p className="field-hint">{notice}</p>}
      {error && <p className="field-error">{error}</p>}
      <textarea
        className="textarea"
        style={{ marginTop: '0.5rem' }}
        rows={rows}
        value={value}
        placeholder={placeholder}
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  )
}

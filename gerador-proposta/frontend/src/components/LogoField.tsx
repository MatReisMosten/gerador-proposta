import { useEffect, useState } from 'react'
import { FileDropzone } from './FileDropzone'

export function LogoField({
  file,
  onChange,
}: {
  file: File | null
  onChange: (file: File | null) => void
}) {
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)

  useEffect(() => {
    if (!file) {
      setPreviewUrl(null)
      return
    }
    const url = URL.createObjectURL(file)
    setPreviewUrl(url)
    return () => URL.revokeObjectURL(url)
  }, [file])

  return (
    <div className="field">
      <label>Logo do cliente (PNG/JPG)</label>
      <FileDropzone
        accept="image/png,image/jpeg"
        label="Arraste o logo ou clique para enviar"
        hint="PNG ou JPG · até 5MB"
        onFile={onChange}
      />
      {file && previewUrl && (
        <div className="file-preview">
          <img src={previewUrl} alt="Preview do logo" />
          <button
            type="button"
            className="file-preview__remove"
            onClick={() => onChange(null)}
          >
            Remover
          </button>
        </div>
      )}
    </div>
  )
}

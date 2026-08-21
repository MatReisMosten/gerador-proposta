import { useRef, useState } from 'react'
import type { DragEvent } from 'react'
import { UploadIcon } from './icons'

interface FileDropzoneProps {
  accept: string
  hint: string
  label: string
  onFile: (file: File) => void
}

export function FileDropzone({ accept, hint, label, onFile }: FileDropzoneProps) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [dragOver, setDragOver] = useState(false)

  function handleDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault()
    setDragOver(false)
    const file = event.dataTransfer.files?.[0]
    if (file) onFile(file)
  }

  return (
    <div
      className={`dropzone${dragOver ? ' is-dragover' : ''}`}
      onClick={() => inputRef.current?.click()}
      onDragOver={(e) => {
        e.preventDefault()
        setDragOver(true)
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={handleDrop}
      role="button"
      tabIndex={0}
    >
      <UploadIcon className="dropzone__icon" />
      <span>{label}</span>
      <span className="dropzone__hint">{hint}</span>
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        onChange={(e) => {
          const file = e.target.files?.[0]
          if (file) onFile(file)
          e.target.value = ''
        }}
      />
    </div>
  )
}

export function LoadingOverlay({ title, message }: { title: string; message: string }) {
  return (
    <div className="loading-overlay">
      <div className="loading-card">
        <div className="spinner" />
        <p className="loading-card__title">{title}</p>
        <p className="loading-card__msg">{message}</p>
      </div>
    </div>
  )
}

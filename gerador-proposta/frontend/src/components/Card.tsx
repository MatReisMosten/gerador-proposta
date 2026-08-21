import type { ReactNode } from 'react'

export function Card({ children }: { children: ReactNode }) {
  return <section className="card">{children}</section>
}

export function CardHead({
  title,
  hint,
  step,
  icon,
}: {
  title: string
  hint?: string
  step?: number
  icon?: ReactNode
}) {
  return (
    <div className="card-head">
      {step !== undefined ? (
        <div className="card-badge">{step}</div>
      ) : (
        <div className="card-icon">{icon}</div>
      )}
      <div>
        <p className="card-title">{title}</p>
        {hint && <p className="card-hint">{hint}</p>}
      </div>
    </div>
  )
}

import { useState } from 'react'
import { login } from '../api/client'
import { Card } from './Card'

export function LoginScreen({ onAuthenticated }: { onAuthenticated: () => void }) {
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const status = await login(password)
      if (status.authenticated) {
        onAuthenticated()
      } else {
        setError('Senha incorreta.')
      }
    } catch {
      setError('Falha ao conectar com o servidor.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-screen">
      <Card>
        <img src="/logo-mosten.png" alt="Mosten" className="app-header__logo" />
        <p className="app-header__title">Gerador de Propostas</p>
        <p className="app-header__subtitle" style={{ marginBottom: '1.25rem' }}>
          Informe a senha de acesso para continuar.
        </p>
        <form onSubmit={handleSubmit}>
          <div className="field">
            <label>Senha de acesso</label>
            <input
              className="input"
              type="password"
              autoFocus
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          {error && <p className="alert alert-error">{error}</p>}
          <button className="btn btn-primary btn-block" type="submit" disabled={loading}>
            Entrar
          </button>
        </form>
      </Card>
    </div>
  )
}

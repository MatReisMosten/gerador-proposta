import { useEffect, useState } from 'react'
import { getAuthStatus, getProposalTypes } from './api/client'
import { LoginScreen } from './components/LoginScreen'
import { WizardStepper } from './components/WizardStepper'
import { TypeStep } from './wizard/TypeStep'
import { InfoStep } from './wizard/InfoStep'
import { GenerateStep } from './wizard/GenerateStep'
import { useWizard } from './wizard/useWizard'
import type { ProposalType } from './types'

type LoadState = 'loading' | 'needs-auth' | 'ready' | 'error'

export default function App() {
  const [loadState, setLoadState] = useState<LoadState>('loading')
  const [types, setTypes] = useState<ProposalType[]>([])

  useEffect(() => {
    bootstrap()
  }, [])

  async function bootstrap() {
    setLoadState('loading')
    try {
      const auth = await getAuthStatus()
      if (auth.password_required && !auth.authenticated) {
        setLoadState('needs-auth')
        return
      }
      const proposalTypes = await getProposalTypes()
      setTypes(proposalTypes)
      setLoadState('ready')
    } catch {
      setLoadState('error')
    }
  }

  if (loadState === 'loading') {
    return <div className="app-shell">Carregando…</div>
  }

  if (loadState === 'needs-auth') {
    return <LoginScreen onAuthenticated={bootstrap} />
  }

  if (loadState === 'error') {
    return (
      <div className="app-shell">
        <p className="alert alert-error">
          Não foi possível conectar à API. Recarregue a página ou tente novamente em instantes.
        </p>
      </div>
    )
  }

  return <Wizard types={types} />
}

function Wizard({ types }: { types: ProposalType[] }) {
  const wizard = useWizard(types)

  return (
    <div className="app-shell">
      <header className="app-header">
        <img src="/logo-mosten.png" alt="Mosten" className="app-header__logo" />
        <p className="app-header__title">Gerador de Propostas</p>
        <p className="app-header__subtitle">
          Monte propostas comerciais Mosten a partir do template oficial.
        </p>
      </header>

      <WizardStepper
        current={wizard.step}
        maxReached={wizard.maxReached}
        skipInfo={wizard.skipInfo}
        onJump={wizard.goTo}
      />

      {wizard.step === 1 && <TypeStep wizard={wizard} />}
      {wizard.step === 2 && <InfoStep wizard={wizard} />}
      {wizard.step === 3 && <GenerateStep wizard={wizard} />}

      <p className="footer-note">
        Seus dados são utilizados apenas para gerar a proposta e não são armazenados.
      </p>
    </div>
  )
}

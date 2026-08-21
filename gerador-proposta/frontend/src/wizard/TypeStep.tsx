import { Card, CardHead } from '../components/Card'
import { ArrowRightIcon, InfoIcon } from '../components/icons'
import type { ProposalType } from '../types'
import type { WizardApi } from './useWizard'

function bannerText(t: ProposalType): string {
  if (t.mode === 'package') {
    if (t.id === 'clarion') {
      return 'Gera a oferta Clarion com o deck oficial estático. Sem formulário — avance direto para gerar o PPTX.'
    }
    return `Gera a oferta ${t.label} com os slides oficiais do template. Você preenche só os campos comerciais; o restante do layout permanece.`
  }
  if (t.mode === 'llm_package') {
    return `Gera a oferta ${t.label} isolando a seção do template — o LLM escreve os textos a partir do brief, sem nome nem logo do cliente.`
  }
  return 'Gera a proposta completa a partir do brief. O LLM escreve os textos nos espaços do template — sem redesenhar slides.'
}

export function TypeStep({ wizard }: { wizard: WizardApi }) {
  const { types, typeId, selectType, selectedType, goNext } = wizard

  return (
    <Card>
      <CardHead
        title="Tipo de proposta"
        hint="Escolha a oferta e avance para preencher os dados."
        step={1}
      />

      <div className="type-grid">
        {types.map((t) => (
          <button
            key={t.id}
            type="button"
            className={`type-card${t.id === typeId ? ' is-selected' : ''}`}
            onClick={() => selectType(t.id)}
          >
            <span className="type-card__title">{t.label}</span>
            <span className="type-card__desc">{t.description}</span>
          </button>
        ))}
      </div>

      {selectedType && (
        <div className="banner">
          <div className="card-icon">
            <InfoIcon />
          </div>
          <div>
            <strong>{selectedType.label}</strong>
            <p>{bannerText(selectedType)}</p>
          </div>
        </div>
      )}

      <div className="actions-row actions-row--end">
        <button className="btn btn-primary" onClick={goNext} disabled={!typeId}>
          Avançar <ArrowRightIcon />
        </button>
      </div>
    </Card>
  )
}

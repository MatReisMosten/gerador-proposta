export type WizardStep = 1 | 2 | 3

const STEPS: { num: WizardStep; title: string; hint: string }[] = [
  { num: 1, title: 'Tipo', hint: 'Escolha a oferta' },
  { num: 2, title: 'Informações', hint: 'Cliente e campos' },
  { num: 3, title: 'Gerar', hint: 'Revisar e baixar' },
]

interface WizardStepperProps {
  current: WizardStep
  maxReached: WizardStep
  skipInfo: boolean
  onJump: (step: WizardStep) => void
}

export function WizardStepper({ current, maxReached, skipInfo, onJump }: WizardStepperProps) {
  return (
    <>
      <div className="stepper">
        {STEPS.map((step, index) => {
          const isSkippedInfo = skipInfo && step.num === 2
          let state: 'done' | 'active' | 'todo' = 'todo'
          let mark: string = String(step.num)
          let hint = step.hint

          if (isSkippedInfo) {
            hint = 'Não se aplica'
            if (current >= 3) {
              state = 'done'
              mark = '✓'
            } else {
              mark = '—'
            }
          } else if (step.num < current) {
            state = 'done'
            mark = '✓'
          } else if (step.num === current) {
            state = 'active'
          }

          const lineFilled = skipInfo && step.num === 1 ? current >= 3 : step.num < current

          return (
            <div key={step.num} style={{ display: 'contents' }}>
              <div className={`stepper__node is-${state}`}>
                <div className="stepper__dot">{mark}</div>
                <div className="stepper__meta">
                  <b>{step.title}</b>
                  <span>{hint}</span>
                </div>
              </div>
              {index < STEPS.length - 1 && (
                <div className={`stepper__line${lineFilled ? ' is-filled' : ''}`} />
              )}
            </div>
          )
        })}
      </div>
      <div className="stepper-nav">
        {STEPS.map((step) => (
          <button
            key={step.num}
            className={`btn ${step.num === current ? 'btn-primary' : 'btn-secondary'}`}
            disabled={skipInfo && step.num === 2 ? true : step.num > maxReached}
            onClick={() => onJump(step.num)}
          >
            {step.num} · {step.title}
          </button>
        ))}
      </div>
    </>
  )
}

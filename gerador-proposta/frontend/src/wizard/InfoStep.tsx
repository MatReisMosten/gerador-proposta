import { useState } from 'react'
import { Card, CardHead } from '../components/Card'
import { LogoField } from '../components/LogoField'
import { TextWithAttachment } from '../components/TextWithAttachment'
import { ArrowLeftIcon, ArrowRightIcon, BriefIcon } from '../components/icons'
import { formatMoneyBR, formatMonthsOnly, isValidProjectCode } from '../utils/format'
import type { WizardApi } from './useWizard'

const MONEY_FIELD_IDS = new Set(['total', 'valor_suporte'])
const MONTHS_FIELD_IDS = new Set(['tempo_execucao'])

export function InfoStep({ wizard }: { wizard: WizardApi }) {
  const {
    selectedType,
    clientName,
    setClientName,
    projectCode,
    setProjectCode,
    fieldValues,
    setFieldValue,
    brief,
    setBrief,
    transcription,
    setTranscription,
    estimate,
    setEstimate,
    logoFile,
    setLogoFile,
    goNext,
    goBack,
  } = wizard

  const [touched, setTouched] = useState(false)

  if (!selectedType) return null

  const codeOk = isValidProjectCode(projectCode)
  const canAdvance = codeOk

  function handleFieldChange(id: string, raw: string) {
    let value = raw
    if (MONEY_FIELD_IDS.has(id)) value = formatMoneyBR(raw)
    else if (MONTHS_FIELD_IDS.has(id)) value = formatMonthsOnly(raw)
    setFieldValue(id, value)
  }

  return (
    <Card>
      <CardHead
        title="Informações da proposta"
        hint="Cliente, código e campos da oferta selecionada."
        step={2}
      />

      <div className="grid-2">
        {!selectedType.hide_client && (
          <div className="field">
            <label>Cliente</label>
            <input
              className="input"
              placeholder="NPH / Unisanta"
              value={clientName}
              onChange={(e) => setClientName(e.target.value)}
            />
          </div>
        )}
        <div className="field">
          <label>Código da proposta</label>
          <input
            className={`input${touched && !codeOk ? ' has-error' : ''}`}
            placeholder="BUI001-26"
            maxLength={9}
            value={projectCode}
            onChange={(e) => setProjectCode(e.target.value)}
            onBlur={() => setTouched(true)}
          />
          <span className="field-hint">
            Formato: 3 letras + 3 números + hífen + 2 números (ex.: BUI001-26).
          </span>
        </div>
      </div>

      {!selectedType.hide_logo && <LogoField file={logoFile} onChange={setLogoFile} />}

      {selectedType.fields.length > 0 && (
        <div className="card" style={{ boxShadow: 'none', marginTop: '0.5rem' }}>
          <CardHead
            title="Campos da oferta"
            hint="Valores que entram na proposta. O layout do template oficial não muda."
            icon={<BriefIcon />}
          />
          <div className="grid-2">
            {selectedType.fields.map((field) => (
              <div className="field" key={field.id} style={field.type === 'textarea' ? { gridColumn: '1 / -1' } : undefined}>
                <label>{field.label}</label>
                {field.type === 'textarea' ? (
                  <textarea
                    className="textarea"
                    rows={4}
                    placeholder={field.placeholder}
                    value={fieldValues[field.id] ?? ''}
                    onChange={(e) => handleFieldChange(field.id, e.target.value)}
                  />
                ) : field.type === 'select' ? (
                  <select
                    className="select"
                    value={fieldValues[field.id] ?? ''}
                    onChange={(e) => handleFieldChange(field.id, e.target.value)}
                  >
                    <option value="">Selecione…</option>
                    {(field.options ?? []).map((opt) => (
                      <option key={opt} value={opt}>
                        {opt}
                      </option>
                    ))}
                  </select>
                ) : (
                  <input
                    className="input"
                    placeholder={field.placeholder}
                    value={fieldValues[field.id] ?? ''}
                    onChange={(e) => handleFieldChange(field.id, e.target.value)}
                  />
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {selectedType.show_brief && (
        <TextWithAttachment
          label="Brief / contexto"
          value={brief}
          onChange={setBrief}
          accept=".txt,.md"
          dropHint="TXT ou MD — o texto preenche o campo abaixo para revisão"
          placeholder="Cliente, contexto, fricções, impacto no negócio, transformação desejada…"
        />
      )}

      {selectedType.show_attachments && (
        <>
          <TextWithAttachment
            label="Transcrição da reunião (opcional)"
            value={transcription}
            onChange={setTranscription}
            accept=".txt,.md,.vtt,.srt,.pdf"
            dropHint="TXT, MD, VTT, SRT ou PDF"
            placeholder="Cole aqui a transcrição da reunião…"
          />
          <TextWithAttachment
            label="Estimativa técnica (opcional)"
            value={estimate}
            onChange={setEstimate}
            accept=".pdf"
            dropHint="PDF"
            placeholder="Cole aqui a estimativa técnica ou anexe o PDF…"
          />
        </>
      )}

      {touched && !codeOk && (
        <p className="alert alert-error">
          Código inválido. Use o formato AAA999-99 (ex.: BUI001-26).
        </p>
      )}

      <div className="actions-row">
        <button className="btn btn-secondary" onClick={goBack}>
          <ArrowLeftIcon /> Voltar
        </button>
        <button
          className="btn btn-primary"
          onClick={() => {
            setTouched(true)
            if (canAdvance) goNext()
          }}
        >
          Avançar <ArrowRightIcon />
        </button>
      </div>
    </Card>
  )
}

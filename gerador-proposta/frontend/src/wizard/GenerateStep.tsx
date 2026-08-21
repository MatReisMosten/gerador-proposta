import { useState } from 'react'
import { Card, CardHead } from '../components/Card'
import { LoadingOverlay } from '../components/LoadingOverlay'
import { ApiError, generateProposal, triggerDownload } from '../api/client'
import { ArrowLeftIcon, DownloadIcon, ResultIcon, RocketIcon } from '../components/icons'
import type { GenerateProposalResponse } from '../types'
import type { WizardApi } from './useWizard'

export function GenerateStep({ wizard }: { wizard: WizardApi }) {
  const {
    selectedType,
    clientName,
    projectCode,
    fieldValues,
    brief,
    transcription,
    estimate,
    logoFile,
    goBack,
  } = wizard

  const [isGenerating, setGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<GenerateProposalResponse | null>(null)
  const [downloading, setDownloading] = useState(false)

  if (!selectedType) return null

  async function handleGenerate() {
    setError(null)
    setGenerating(true)
    try {
      const response = await generateProposal({
        typeId: selectedType!.id,
        clientName,
        projectCode,
        fieldValues,
        brief,
        transcription,
        estimate,
        logo: logoFile,
      })
      setResult(response)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Falha inesperada ao gerar a proposta.')
    } finally {
      setGenerating(false)
    }
  }

  async function handleDownload() {
    if (!result) return
    setDownloading(true)
    try {
      await triggerDownload(result.token, result.meta.filename)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Falha ao baixar o arquivo.')
    } finally {
      setDownloading(false)
    }
  }

  return (
    <Card>
      <CardHead title="Gerar proposta" hint="Revise e gere o PPTX oficial." step={3} />

      <p className="checklist">
        <b>Tipo:</b> {selectedType.label}
        {!selectedType.hide_client && (
          <>
            {' · '}
            <b>Cliente:</b> {clientName.trim() || '—'}
          </>
        )}
        {' · '}
        <b>Código:</b> {projectCode.trim() || '—'}
      </p>

      {error && <p className="alert alert-error">{error}</p>}

      <div className="grid-2" style={{ alignItems: 'start' }}>
        <button
          className="btn btn-primary btn-block"
          onClick={handleGenerate}
          disabled={isGenerating}
        >
          <RocketIcon /> Gerar {selectedType.label}
        </button>

        <div className="card" style={{ margin: 0, boxShadow: 'none' }}>
          <CardHead title="Resultado" hint="Download quando a geração terminar." icon={<ResultIcon />} />
          {!result ? (
            <div className="result-empty">
              <div className="result-icon">
                <ResultIcon />
              </div>
              <h4>Aguardando geração</h4>
              <p>Quando a proposta estiver pronta, o download aparece aqui.</p>
            </div>
          ) : (
            <div className="result-success">
              <div className="result-icon">
                <ResultIcon />
              </div>
              <h4>Proposta gerada</h4>
              <p>{result.meta.filename}</p>
              <div className="result-meta">
                <div>
                  <span>Cliente</span>
                  <b>{result.meta.client || '—'}</b>
                </div>
                <div>
                  <span>Código</span>
                  <b>{result.meta.code || '—'}</b>
                </div>
                <div>
                  <span>Tipo</span>
                  <b>{result.meta.type_label}</b>
                </div>
                <div>
                  <span>Tamanho</span>
                  <b>{result.meta.size_label}</b>
                </div>
              </div>
              <button
                className="btn btn-primary btn-block"
                style={{ marginTop: '0.9rem' }}
                onClick={handleDownload}
                disabled={downloading}
              >
                <DownloadIcon /> Baixar PPTX
              </button>
            </div>
          )}
        </div>
      </div>

      <div className="actions-row">
        <button className="btn btn-secondary" onClick={goBack} disabled={isGenerating}>
          <ArrowLeftIcon /> Voltar
        </button>
        <span />
      </div>

      {isGenerating && (
        <LoadingOverlay
          title={`Gerando ${selectedType.label}`}
          message="Isso pode levar alguns segundos…"
        />
      )}
    </Card>
  )
}

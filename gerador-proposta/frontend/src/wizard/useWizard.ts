import { useMemo, useState } from 'react'
import type { ProposalType } from '../types'
import type { WizardStep } from '../components/WizardStepper'
import { formatProjectCode } from '../utils/format'

export function useWizard(types: ProposalType[]) {
  const [step, setStepRaw] = useState<WizardStep>(1)
  const [maxReached, setMaxReached] = useState<WizardStep>(1)
  const [typeId, setTypeId] = useState<string>(
    () => types.find((t) => t.id === 'professional_service')?.id ?? types[0]?.id ?? '',
  )
  const [clientName, setClientName] = useState('')
  const [projectCode, setProjectCodeRaw] = useState('')
  const [fieldValues, setFieldValues] = useState<Record<string, string>>({})
  const [brief, setBrief] = useState('')
  const [transcription, setTranscription] = useState('')
  const [estimate, setEstimate] = useState('')
  const [logoFile, setLogoFile] = useState<File | null>(null)

  const selectedType = useMemo(
    () => types.find((t) => t.id === typeId) ?? types[0],
    [types, typeId],
  )

  const skipInfo = selectedType ? !selectedType.requires_form : false

  function setProjectCode(raw: string) {
    setProjectCodeRaw(formatProjectCode(raw))
  }

  function setFieldValue(id: string, value: string) {
    setFieldValues((prev) => ({ ...prev, [id]: value }))
  }

  function goTo(target: WizardStep) {
    setStepRaw(target)
    setMaxReached((prev) => (target > prev ? target : prev))
  }

  function goNext() {
    if (step >= 3) return
    goTo(skipInfo && step === 1 ? 3 : ((step + 1) as WizardStep))
  }

  function goBack() {
    if (step <= 1) return
    goTo(skipInfo && step === 3 ? 1 : ((step - 1) as WizardStep))
  }

  function selectType(id: string) {
    setTypeId(id)
    // campos de pacote não fazem sentido entre tipos diferentes
    setFieldValues({})
  }

  return {
    types,
    step,
    maxReached,
    selectedType,
    skipInfo,
    typeId,
    clientName,
    projectCode,
    fieldValues,
    brief,
    transcription,
    estimate,
    logoFile,
    setClientName,
    setProjectCode,
    setFieldValue,
    setBrief,
    setTranscription,
    setEstimate,
    setLogoFile,
    selectType,
    goTo,
    goNext,
    goBack,
  }
}

export type WizardApi = ReturnType<typeof useWizard>

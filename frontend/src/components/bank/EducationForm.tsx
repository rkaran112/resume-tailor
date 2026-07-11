import { useState, type FormEvent } from 'react'
import { educationHooks, type EducationEntryCreate } from '../../api/bank'

export function EducationForm() {
  const create = educationHooks.useCreate()
  const [institution, setInstitution] = useState('')
  const [degree, setDegree] = useState('')
  const [field, setField] = useState('')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [gpa, setGpa] = useState('')

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const body: EducationEntryCreate = {
      institution,
      degree,
      field,
      start_date: startDate,
      end_date: endDate || null,
      gpa: gpa || null,
    }
    create.mutate(body, {
      onSuccess: () => {
        setInstitution('')
        setDegree('')
        setField('')
        setStartDate('')
        setEndDate('')
        setGpa('')
      },
    })
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        placeholder="Institution"
        value={institution}
        onChange={(e) => setInstitution(e.target.value)}
        required
      />
      <input
        placeholder="Degree"
        value={degree}
        onChange={(e) => setDegree(e.target.value)}
        required
      />
      <input
        placeholder="Field"
        value={field}
        onChange={(e) => setField(e.target.value)}
        required
      />
      <input
        type="date"
        value={startDate}
        onChange={(e) => setStartDate(e.target.value)}
        required
      />
      <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
      <input placeholder="GPA" value={gpa} onChange={(e) => setGpa(e.target.value)} />
      <button type="submit" disabled={create.isPending}>
        Add education
      </button>
      {create.isError && <span className="error">{create.error.message}</span>}
    </form>
  )
}

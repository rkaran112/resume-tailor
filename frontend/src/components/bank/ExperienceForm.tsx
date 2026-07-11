import { useState, type FormEvent } from 'react'
import { experienceHooks, type ExperienceEntryCreate } from '../../api/bank'

export function ExperienceForm() {
  const create = experienceHooks.useCreate()
  const [company, setCompany] = useState('')
  const [title, setTitle] = useState('')
  const [location, setLocation] = useState('')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const body: ExperienceEntryCreate = {
      company,
      title,
      location,
      start_date: startDate,
      end_date: endDate || null,
    }
    create.mutate(body, {
      onSuccess: () => {
        setCompany('')
        setTitle('')
        setLocation('')
        setStartDate('')
        setEndDate('')
      },
    })
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        placeholder="Company"
        value={company}
        onChange={(e) => setCompany(e.target.value)}
        required
      />
      <input
        placeholder="Title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        required
      />
      <input
        placeholder="Location"
        value={location}
        onChange={(e) => setLocation(e.target.value)}
        required
      />
      <input
        type="date"
        value={startDate}
        onChange={(e) => setStartDate(e.target.value)}
        required
      />
      <input
        type="date"
        placeholder="End date (blank = present)"
        value={endDate}
        onChange={(e) => setEndDate(e.target.value)}
      />
      <button type="submit" disabled={create.isPending}>
        Add experience
      </button>
      {create.isError && <span className="error">{create.error.message}</span>}
    </form>
  )
}

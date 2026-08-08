import { useEffect, useState, type FormEvent } from 'react'
import { useContactInfo, useUpsertContactInfo, type ContactLink } from '../../api/bank'

export function ContactInfoForm() {
  const { data } = useContactInfo()
  const upsert = useUpsertContactInfo()

  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [phone, setPhone] = useState('')
  const [location, setLocation] = useState('')
  const [linksText, setLinksText] = useState('')

  useEffect(() => {
    if (!data) return
    setName(data.name)
    setEmail(data.email)
    setPhone(data.phone)
    setLocation(data.location)
    setLinksText(data.links.map((l) => `${l.label}=${l.url}`).join('\n'))
  }, [data])

  function parseLinks(): ContactLink[] {
    return linksText
      .split('\n')
      .map((line) => line.trim())
      .filter(Boolean)
      .map((line) => {
        const [label, ...rest] = line.split('=')
        return { label: label.trim(), url: rest.join('=').trim() }
      })
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    upsert.mutate({ name, email, phone, location, links: parseLinks() })
  }

  return (
    <form onSubmit={handleSubmit}>
      <input placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} required />
      <input
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
      />
      <input
        placeholder="Phone (optional)"
        value={phone}
        onChange={(e) => setPhone(e.target.value)}
      />
      <input
        placeholder="Location (optional)"
        value={location}
        onChange={(e) => setLocation(e.target.value)}
      />
      <textarea
        placeholder="Links, one per line as label=url"
        value={linksText}
        onChange={(e) => setLinksText(e.target.value)}
        rows={3}
      />
      <button className="btn-primary" type="submit" disabled={upsert.isPending}>
        Save contact info
      </button>
      {upsert.isError && <span className="error">{upsert.error.message}</span>}
    </form>
  )
}

import { useRef, useState, type ChangeEvent, type CSSProperties, type DragEvent } from 'react'
import { ApiError } from '../../api/client'
import { ProgressActivity } from '../ui/ProgressActivity'
import {
  useCommitResumeImport,
  useImportResume,
  type ImportedBullet,
  type ImportedContact,
  type ImportedContactLink,
  type ImportedEducationEntry,
  type ImportedExperienceEntry,
  type ImportedProject,
  type ImportedSkill,
  type ResumeImportPreview,
} from '../../api/resumeImport'

function pluralize(count: number, singular: string, plural: string): string {
  return `${count} ${count === 1 ? singular : plural}`
}

function parseTags(raw: string): string[] {
  return raw
    .split(',')
    .map((t) => t.trim())
    .filter(Boolean)
}

function updateListItem<T, K extends keyof T>(list: T[], index: number, field: K, value: T[K]): T[] {
  return list.map((item, i) => (i === index ? { ...item, [field]: value } : item))
}

function DedupPill({ alreadyExists }: { alreadyExists: boolean }) {
  return alreadyExists ? (
    <span className="pill pill-neutral">Already in your bank</span>
  ) : (
    <span className="pill pill-success">New</span>
  )
}

const rowStyle: CSSProperties = { display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 8 }

export function ResumeImportPanel() {
  const importResume = useImportResume()
  const commitImport = useCommitResumeImport()
  const [preview, setPreview] = useState<ResumeImportPreview | null>(null)
  const [summary, setSummary] = useState<string | null>(null)
  const [isDragOver, setIsDragOver] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  async function handleFile(file: File) {
    setSummary(null)
    const result = await importResume.mutateAsync(file)
    setPreview(result)
  }

  function handleDrop(e: DragEvent<HTMLDivElement>) {
    e.preventDefault()
    setIsDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file) void handleFile(file)
  }

  function handleFileInputChange(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (file) void handleFile(file)
    e.target.value = ''
  }

  // ---- include/exclude toggles ----

  function toggleContact() {
    setPreview(
      (prev) => prev && { ...prev, contact: { ...prev.contact, include: !prev.contact.include } }
    )
  }

  function toggleExperienceEntry(index: number) {
    setPreview((prev) => {
      if (!prev) return prev
      const experience = prev.experience.map((entry, i) =>
        i === index ? { ...entry, include: !entry.include } : entry
      )
      return { ...prev, experience }
    })
  }

  function toggleExperienceBullet(entryIndex: number, bulletIndex: number) {
    setPreview((prev) => {
      if (!prev) return prev
      const experience = prev.experience.map((entry, i) => {
        if (i !== entryIndex) return entry
        const bullets = entry.bullets.map((b, j) =>
          j === bulletIndex ? { ...b, include: !b.include } : b
        )
        return { ...entry, bullets }
      })
      return { ...prev, experience }
    })
  }

  function toggleSkill(index: number) {
    setPreview((prev) => {
      if (!prev) return prev
      const skills = prev.skills.map((s, i) => (i === index ? { ...s, include: !s.include } : s))
      return { ...prev, skills }
    })
  }

  function toggleProject(index: number) {
    setPreview((prev) => {
      if (!prev) return prev
      const projects = prev.projects.map((p, i) =>
        i === index ? { ...p, include: !p.include } : p
      )
      return { ...prev, projects }
    })
  }

  function toggleProjectBullet(projectIndex: number, bulletIndex: number) {
    setPreview((prev) => {
      if (!prev) return prev
      const projects = prev.projects.map((project, i) => {
        if (i !== projectIndex) return project
        const bullets = project.bullets.map((b, j) =>
          j === bulletIndex ? { ...b, include: !b.include } : b
        )
        return { ...project, bullets }
      })
      return { ...prev, projects }
    })
  }

  function toggleEducation(index: number) {
    setPreview((prev) => {
      if (!prev) return prev
      const education = prev.education.map((e, i) =>
        i === index ? { ...e, include: !e.include } : e
      )
      return { ...prev, education }
    })
  }

  // ---- inline field editing ----

  function updateContactField<K extends keyof ImportedContact>(field: K, value: ImportedContact[K]) {
    setPreview((prev) => prev && { ...prev, contact: { ...prev.contact, [field]: value } })
  }

  function updateContactLinkField<K extends keyof ImportedContactLink>(
    index: number,
    field: K,
    value: ImportedContactLink[K]
  ) {
    setPreview((prev) => {
      if (!prev) return prev
      return {
        ...prev,
        contact: { ...prev.contact, links: updateListItem(prev.contact.links, index, field, value) },
      }
    })
  }

  function addContactLink() {
    setPreview(
      (prev) =>
        prev && { ...prev, contact: { ...prev.contact, links: [...prev.contact.links, { label: '', url: '' }] } }
    )
  }

  function removeContactLink(index: number) {
    setPreview((prev) => {
      if (!prev) return prev
      return {
        ...prev,
        contact: { ...prev.contact, links: prev.contact.links.filter((_, i) => i !== index) },
      }
    })
  }

  function updateExperienceField<K extends keyof ImportedExperienceEntry>(
    index: number,
    field: K,
    value: ImportedExperienceEntry[K]
  ) {
    setPreview(
      (prev) => prev && { ...prev, experience: updateListItem(prev.experience, index, field, value) }
    )
  }

  function updateExperienceBulletField<K extends keyof ImportedBullet>(
    entryIndex: number,
    bulletIndex: number,
    field: K,
    value: ImportedBullet[K]
  ) {
    setPreview((prev) => {
      if (!prev) return prev
      const experience = prev.experience.map((entry, i) =>
        i === entryIndex
          ? { ...entry, bullets: updateListItem(entry.bullets, bulletIndex, field, value) }
          : entry
      )
      return { ...prev, experience }
    })
  }

  function updateSkillField<K extends keyof ImportedSkill>(index: number, field: K, value: ImportedSkill[K]) {
    setPreview((prev) => prev && { ...prev, skills: updateListItem(prev.skills, index, field, value) })
  }

  function updateProjectField<K extends keyof ImportedProject>(
    index: number,
    field: K,
    value: ImportedProject[K]
  ) {
    setPreview((prev) => prev && { ...prev, projects: updateListItem(prev.projects, index, field, value) })
  }

  function updateProjectBulletField<K extends keyof ImportedBullet>(
    projectIndex: number,
    bulletIndex: number,
    field: K,
    value: ImportedBullet[K]
  ) {
    setPreview((prev) => {
      if (!prev) return prev
      const projects = prev.projects.map((project, i) =>
        i === projectIndex
          ? { ...project, bullets: updateListItem(project.bullets, bulletIndex, field, value) }
          : project
      )
      return { ...prev, projects }
    })
  }

  function updateEducationField<K extends keyof ImportedEducationEntry>(
    index: number,
    field: K,
    value: ImportedEducationEntry[K]
  ) {
    setPreview(
      (prev) => prev && { ...prev, education: updateListItem(prev.education, index, field, value) }
    )
  }

  async function handleCommit() {
    if (!preview) return
    const result = await commitImport.mutateAsync(preview)
    const parts = [
      pluralize(result.experience_entries_created, 'experience entry', 'experience entries'),
      pluralize(result.bullets_created, 'bullet', 'bullets'),
      pluralize(result.skills_created, 'skill', 'skills'),
      pluralize(result.projects_created, 'project', 'projects'),
      pluralize(result.education_entries_created, 'education entry', 'education entries'),
    ]
    setSummary(
      `Added ${parts.join(', ')}${result.contact_updated ? ' — contact info updated.' : '.'}`
    )
    setPreview(null)
  }

  const disabledMessage =
    importResume.error instanceof ApiError && importResume.error.status === 503
      ? 'Resume import is turned off on this server. Set ENABLE_RESUME_IMPORT=true and an ' +
        'ANTHROPIC_API_KEY in the backend .env file, then restart the server.'
      : null

  return (
    <section style={{ marginBottom: 0 }}>
      {!preview && (
        <div
          onDragOver={(e) => {
            e.preventDefault()
            setIsDragOver(true)
          }}
          onDragLeave={() => setIsDragOver(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          style={{
            border: `2px dashed ${isDragOver ? 'var(--accent)' : 'var(--border-strong)'}`,
            borderRadius: 'var(--radius-md)',
            padding: 28,
            textAlign: 'center',
            cursor: 'pointer',
            color: 'var(--ink-muted)',
            fontSize: 13.5,
          }}
        >
          {importResume.isPending
            ? 'Reading your resume…'
            : 'Drop your resume as a PDF or LaTeX (.tex) file here, or click to choose a file'}
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.tex,application/pdf"
            onChange={handleFileInputChange}
            style={{ display: 'none' }}
          />
        </div>
      )}

      {importResume.isPending && (
        <ProgressActivity
          messages={[
            'Reading your resume…',
            'Pulling out your experience and skills…',
            'Checking it against your bank…',
            'Almost there…',
          ]}
        />
      )}

      {disabledMessage && <p className="error">{disabledMessage}</p>}
      {importResume.isError && !disabledMessage && (
        <p className="error">{importResume.error.message}</p>
      )}
      {summary && <p>{summary}</p>}

      {preview && (
        <div>
          <p>
            Here's what we found. Edit anything before it goes in. Items already in your bank
            start unchecked so you don't get doubles — check one anyway if you want to keep a new
            bullet nested under it.
          </p>

          <div className="card" style={{ marginBottom: 12 }}>
            <label className="checkbox-row" style={{ marginBottom: 8 }}>
              <input type="checkbox" checked={preview.contact.include} onChange={toggleContact} />
              Include contact info (replaces your current contact info)
            </label>
            <div style={rowStyle}>
              <input
                value={preview.contact.name}
                onChange={(e) => updateContactField('name', e.target.value)}
                placeholder="Name"
                style={{ flex: 1 }}
              />
              <input
                value={preview.contact.email}
                onChange={(e) => updateContactField('email', e.target.value)}
                placeholder="Email"
                style={{ flex: 1 }}
              />
            </div>
            <div style={rowStyle}>
              <input
                value={preview.contact.phone}
                onChange={(e) => updateContactField('phone', e.target.value)}
                placeholder="Phone"
                style={{ flex: 1 }}
              />
              <input
                value={preview.contact.location}
                onChange={(e) => updateContactField('location', e.target.value)}
                placeholder="Location"
                style={{ flex: 1 }}
              />
            </div>
            {preview.contact.links.map((link, i) => (
              <div key={i} style={{ display: 'flex', gap: 8, marginBottom: 6 }}>
                <input
                  value={link.label}
                  onChange={(e) => updateContactLinkField(i, 'label', e.target.value)}
                  placeholder="Label"
                  style={{ width: 120 }}
                />
                <input
                  value={link.url}
                  onChange={(e) => updateContactLinkField(i, 'url', e.target.value)}
                  placeholder="URL"
                  style={{ flex: 1 }}
                />
                <button className="btn-ghost" type="button" onClick={() => removeContactLink(i)}>
                  Remove
                </button>
              </div>
            ))}
            <button
              className="btn-ghost"
              type="button"
              onClick={addContactLink}
              style={{ fontSize: 12 }}
            >
              + Add link
            </button>
          </div>

          <h3>Experience</h3>
          {preview.experience.map((entry, i) => (
            <div key={i} className="card" style={{ marginBottom: 10 }}>
              <div className="checkbox-row" style={{ justifyContent: 'space-between' }}>
                <label className="checkbox-row">
                  <input
                    type="checkbox"
                    checked={entry.include}
                    onChange={() => toggleExperienceEntry(i)}
                  />
                  Experience entry
                </label>
                <DedupPill alreadyExists={entry.already_exists} />
              </div>
              <div style={rowStyle}>
                <input
                  value={entry.company}
                  onChange={(e) => updateExperienceField(i, 'company', e.target.value)}
                  placeholder="Company"
                  style={{ flex: 1 }}
                />
                <input
                  value={entry.title}
                  onChange={(e) => updateExperienceField(i, 'title', e.target.value)}
                  placeholder="Title"
                  style={{ flex: 1 }}
                />
              </div>
              <div style={rowStyle}>
                <input
                  value={entry.location}
                  onChange={(e) => updateExperienceField(i, 'location', e.target.value)}
                  placeholder="Location"
                  style={{ flex: 1 }}
                />
                <input
                  type="date"
                  value={entry.start_date}
                  onChange={(e) => updateExperienceField(i, 'start_date', e.target.value)}
                />
                <input
                  type="date"
                  value={entry.end_date ?? ''}
                  onChange={(e) => updateExperienceField(i, 'end_date', e.target.value || null)}
                />
              </div>
              <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                {entry.bullets.map((bullet, j) => (
                  <li key={j} style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 6 }}>
                    <input
                      type="checkbox"
                      checked={bullet.include}
                      onChange={() => toggleExperienceBullet(i, j)}
                    />
                    <input
                      value={bullet.text}
                      onChange={(e) => updateExperienceBulletField(i, j, 'text', e.target.value)}
                      style={{ flex: 1 }}
                    />
                    <DedupPill alreadyExists={bullet.already_exists} />
                  </li>
                ))}
              </ul>
            </div>
          ))}

          <h3>Skills</h3>
          <div className="card-list">
            {preview.skills.map((skill, i) => (
              <div key={i} className="card" style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                <input type="checkbox" checked={skill.include} onChange={() => toggleSkill(i)} />
                <input
                  value={skill.name}
                  onChange={(e) => updateSkillField(i, 'name', e.target.value)}
                  placeholder="Name"
                  style={{ flex: 1 }}
                />
                <input
                  value={skill.category}
                  onChange={(e) => updateSkillField(i, 'category', e.target.value)}
                  placeholder="Category"
                  style={{ flex: 1 }}
                />
                <DedupPill alreadyExists={skill.already_exists} />
              </div>
            ))}
          </div>

          <h3>Projects</h3>
          {preview.projects.map((project, i) => (
            <div key={i} className="card" style={{ marginBottom: 10 }}>
              <div className="checkbox-row" style={{ justifyContent: 'space-between' }}>
                <label className="checkbox-row">
                  <input type="checkbox" checked={project.include} onChange={() => toggleProject(i)} />
                  Project
                </label>
                <DedupPill alreadyExists={project.already_exists} />
              </div>
              <div style={rowStyle}>
                <input
                  value={project.name}
                  onChange={(e) => updateProjectField(i, 'name', e.target.value)}
                  placeholder="Name"
                  style={{ flex: 1 }}
                />
                <input
                  value={project.description}
                  onChange={(e) => updateProjectField(i, 'description', e.target.value)}
                  placeholder="Description"
                  style={{ flex: 2 }}
                />
              </div>
              <div style={rowStyle}>
                <input
                  defaultValue={project.tech_tags.join(', ')}
                  onBlur={(e) => updateProjectField(i, 'tech_tags', parseTags(e.target.value))}
                  placeholder="Tech tags (comma-separated)"
                  style={{ flex: 1 }}
                />
              </div>
              <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                {project.bullets.map((bullet, j) => (
                  <li key={j} style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 6 }}>
                    <input
                      type="checkbox"
                      checked={bullet.include}
                      onChange={() => toggleProjectBullet(i, j)}
                    />
                    <input
                      value={bullet.text}
                      onChange={(e) => updateProjectBulletField(i, j, 'text', e.target.value)}
                      style={{ flex: 1 }}
                    />
                    <DedupPill alreadyExists={bullet.already_exists} />
                  </li>
                ))}
              </ul>
            </div>
          ))}

          <h3>Education</h3>
          {preview.education.map((entry, i) => (
            <div key={i} className="card" style={{ marginBottom: 10 }}>
              <div className="checkbox-row" style={{ justifyContent: 'space-between' }}>
                <label className="checkbox-row">
                  <input type="checkbox" checked={entry.include} onChange={() => toggleEducation(i)} />
                  Education entry
                </label>
                <DedupPill alreadyExists={entry.already_exists} />
              </div>
              <div style={rowStyle}>
                <input
                  value={entry.institution}
                  onChange={(e) => updateEducationField(i, 'institution', e.target.value)}
                  placeholder="Institution"
                  style={{ flex: 1 }}
                />
                <input
                  value={entry.degree}
                  onChange={(e) => updateEducationField(i, 'degree', e.target.value)}
                  placeholder="Degree"
                  style={{ flex: 1 }}
                />
                <input
                  value={entry.field}
                  onChange={(e) => updateEducationField(i, 'field', e.target.value)}
                  placeholder="Field"
                  style={{ flex: 1 }}
                />
              </div>
              <div style={rowStyle}>
                <input
                  type="date"
                  value={entry.start_date}
                  onChange={(e) => updateEducationField(i, 'start_date', e.target.value)}
                />
                <input
                  type="date"
                  value={entry.end_date ?? ''}
                  onChange={(e) => updateEducationField(i, 'end_date', e.target.value || null)}
                />
                <input
                  value={entry.gpa}
                  onChange={(e) => updateEducationField(i, 'gpa', e.target.value)}
                  placeholder="GPA"
                  style={{ width: 100 }}
                />
              </div>
            </div>
          ))}

          <button className="btn-primary" onClick={handleCommit} disabled={commitImport.isPending}>
            {commitImport.isPending ? 'Adding to bank…' : 'Add to bank'}
          </button>
          <button className="btn-ghost" onClick={() => setPreview(null)}>
            Cancel
          </button>
          {commitImport.isError && <p className="error">{commitImport.error.message}</p>}
        </div>
      )}
    </section>
  )
}

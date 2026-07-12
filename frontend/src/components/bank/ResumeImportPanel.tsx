import { useRef, useState, type ChangeEvent, type DragEvent } from 'react'
import { ApiError } from '../../api/client'
import {
  useCommitResumeImport,
  useImportResume,
  type ResumeImportPreview,
} from '../../api/resumeImport'

function pluralize(count: number, singular: string, plural: string): string {
  return `${count} ${count === 1 ? singular : plural}`
}

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
      ? 'Resume import is disabled on this server.'
      : null

  return (
    <section style={{ border: '1px solid var(--border)', padding: 12, marginBottom: 16 }}>
      <h2>Import from resume</h2>

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
            border: `2px dashed ${isDragOver ? '#6a3bff' : 'var(--border)'}`,
            padding: 24,
            textAlign: 'center',
            cursor: 'pointer',
          }}
        >
          {importResume.isPending
            ? 'Reading your resume…'
            : 'Drop your resume PDF here, or click to choose a file'}
          <input
            ref={fileInputRef}
            type="file"
            accept="application/pdf"
            onChange={handleFileInputChange}
            style={{ display: 'none' }}
          />
        </div>
      )}

      {disabledMessage && <p className="error">{disabledMessage}</p>}
      {importResume.isError && !disabledMessage && (
        <p className="error">{importResume.error.message}</p>
      )}
      {summary && <p>{summary}</p>}

      {preview && (
        <div>
          <p>Review what we found — uncheck anything you don't want added to your bank.</p>

          <label>
            <input type="checkbox" checked={preview.contact.include} onChange={toggleContact} />
            Contact info: {preview.contact.name} ({preview.contact.email}) — this will replace
            your current contact info
          </label>

          <h3>Experience</h3>
          {preview.experience.map((entry, i) => (
            <div key={i} style={{ marginBottom: 8 }}>
              <label>
                <input
                  type="checkbox"
                  checked={entry.include}
                  onChange={() => toggleExperienceEntry(i)}
                />
                <strong>
                  {entry.company} — {entry.title}
                </strong>
              </label>
              <ul>
                {entry.bullets.map((bullet, j) => (
                  <li key={j}>
                    <label>
                      <input
                        type="checkbox"
                        checked={bullet.include}
                        onChange={() => toggleExperienceBullet(i, j)}
                      />
                      {bullet.text}
                    </label>
                  </li>
                ))}
              </ul>
            </div>
          ))}

          <h3>Skills</h3>
          <ul>
            {preview.skills.map((skill, i) => (
              <li key={i}>
                <label>
                  <input type="checkbox" checked={skill.include} onChange={() => toggleSkill(i)} />
                  {skill.name} ({skill.category})
                </label>
              </li>
            ))}
          </ul>

          <h3>Projects</h3>
          {preview.projects.map((project, i) => (
            <div key={i} style={{ marginBottom: 8 }}>
              <label>
                <input
                  type="checkbox"
                  checked={project.include}
                  onChange={() => toggleProject(i)}
                />
                <strong>{project.name}</strong>
              </label>
              <ul>
                {project.bullets.map((bullet, j) => (
                  <li key={j}>
                    <label>
                      <input
                        type="checkbox"
                        checked={bullet.include}
                        onChange={() => toggleProjectBullet(i, j)}
                      />
                      {bullet.text}
                    </label>
                  </li>
                ))}
              </ul>
            </div>
          ))}

          <h3>Education</h3>
          <ul>
            {preview.education.map((entry, i) => (
              <li key={i}>
                <label>
                  <input
                    type="checkbox"
                    checked={entry.include}
                    onChange={() => toggleEducation(i)}
                  />
                  {entry.institution} — {entry.degree}, {entry.field}
                </label>
              </li>
            ))}
          </ul>

          <button onClick={handleCommit} disabled={commitImport.isPending}>
            {commitImport.isPending ? 'Adding to bank…' : 'Add to bank'}
          </button>
          <button onClick={() => setPreview(null)}>Cancel</button>
          {commitImport.isError && <p className="error">{commitImport.error.message}</p>}
        </div>
      )}
    </section>
  )
}

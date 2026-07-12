import { useState } from 'react'
import {
  bulletHooks,
  educationHooks,
  experienceHooks,
  projectHooks,
  skillHooks,
} from '../../api/bank'
import type { JobDescription, MatchResult, Selection } from '../../api/tailoring'

interface SelectionReviewProps {
  jobDescription: JobDescription
  matchResult: MatchResult
  onConfirm: (selection: Selection) => void
  isSubmitting: boolean
}

function useToggleSet(initial: number[]) {
  const [selected, setSelected] = useState<Set<number>>(new Set(initial))
  function toggle(id: number) {
    setSelected((prev) => {
      const next = new Set(prev)
      if (next.has(id)) {
        next.delete(id)
      } else {
        next.add(id)
      }
      return next
    })
  }
  return [selected, toggle] as const
}

function ScoreBadge({ matched }: { matched: string[] | undefined }) {
  if (!matched || matched.length === 0) return null
  return <span style={{ color: '#6a3bff', fontSize: 12 }}> matched: {matched.join(', ')}</span>
}

export function SelectionReview({
  jobDescription,
  matchResult,
  onConfirm,
  isSubmitting,
}: SelectionReviewProps) {
  const { data: experienceEntries } = experienceHooks.useList()
  const { data: bullets } = bulletHooks.useList()
  const { data: skills } = skillHooks.useList()
  const { data: projects } = projectHooks.useList()
  const { data: educationEntries } = educationHooks.useList()

  const [selectedBulletIds, toggleBullet] = useToggleSet(
    matchResult.selected_experience_bullet_ids
  )
  const [selectedSkillIds, toggleSkill] = useToggleSet(matchResult.selected_skill_ids)
  const [selectedProjectIds, toggleProject] = useToggleSet(matchResult.selected_project_ids)
  const [selectedEducationIds, toggleEducation] = useToggleSet(
    matchResult.selected_education_ids
  )

  function handleConfirm() {
    onConfirm({
      selected_experience_bullet_ids: [...selectedBulletIds],
      selected_project_ids: [...selectedProjectIds],
      selected_skill_ids: [...selectedSkillIds],
      selected_education_ids: [...selectedEducationIds],
    })
  }

  return (
    <div>
      <h2>
        Review selection for {jobDescription.company} — {jobDescription.role_title}
      </h2>

      <h3>Experience</h3>
      {(experienceEntries ?? []).map((entry) => (
        <div key={entry.id} style={{ marginBottom: 12 }}>
          <strong>
            {entry.company} — {entry.title}
          </strong>
          <ul>
            {(bullets ?? [])
              .filter((bullet) => bullet.experience_entry_id === entry.id)
              .map((bullet) => (
                <li key={bullet.id}>
                  <label>
                    <input
                      type="checkbox"
                      checked={selectedBulletIds.has(bullet.id)}
                      onChange={() => toggleBullet(bullet.id)}
                    />
                    {bullet.text}
                    <ScoreBadge matched={matchResult.scoring_metadata.bullets?.[String(bullet.id)]} />
                  </label>
                </li>
              ))}
          </ul>
        </div>
      ))}

      <h3>Skills</h3>
      <ul>
        {(skills ?? []).map((skill) => (
          <li key={skill.id}>
            <label>
              <input
                type="checkbox"
                checked={selectedSkillIds.has(skill.id)}
                onChange={() => toggleSkill(skill.id)}
              />
              {skill.name} ({skill.category})
              <ScoreBadge matched={matchResult.scoring_metadata.skills?.[String(skill.id)]} />
            </label>
          </li>
        ))}
      </ul>

      <h3>Projects</h3>
      <ul>
        {(projects ?? []).map((project) => (
          <li key={project.id}>
            <label>
              <input
                type="checkbox"
                checked={selectedProjectIds.has(project.id)}
                onChange={() => toggleProject(project.id)}
              />
              {project.name}
              <ScoreBadge matched={matchResult.scoring_metadata.projects?.[String(project.id)]} />
            </label>
          </li>
        ))}
      </ul>

      <h3>Education</h3>
      <ul>
        {(educationEntries ?? []).map((entry) => (
          <li key={entry.id}>
            <label>
              <input
                type="checkbox"
                checked={selectedEducationIds.has(entry.id)}
                onChange={() => toggleEducation(entry.id)}
              />
              {entry.institution} — {entry.degree}, {entry.field}
            </label>
          </li>
        ))}
      </ul>

      <button onClick={handleConfirm} disabled={isSubmitting}>
        {isSubmitting ? 'Creating draft…' : 'Create draft'}
      </button>
    </div>
  )
}

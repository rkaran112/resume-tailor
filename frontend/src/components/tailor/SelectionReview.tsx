import { useState } from 'react'
import type { Bullet, Project, Skill } from '../../api/bank'
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

function splitByMatch<T>(
  items: T[],
  idOf: (item: T) => number,
  matches: Record<string, string[] | undefined>
): { matched: T[]; unmatched: T[] } {
  const matched: T[] = []
  const unmatched: T[] = []
  for (const item of items) {
    const keywords = matches[String(idOf(item))]
    ;(keywords && keywords.length > 0 ? matched : unmatched).push(item)
  }
  return { matched, unmatched }
}

function RecommendedPill({ matched }: { matched: string[] | undefined }) {
  if (!matched || matched.length === 0) return null
  return (
    <span
      title={`Matched on: ${matched.join(', ')}`}
      style={{
        marginLeft: 6,
        fontSize: 11,
        color: '#0a7a2f',
        background: '#e4f7e9',
        borderRadius: 10,
        padding: '1px 8px',
      }}
    >
      Recommended
    </span>
  )
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

  const bulletMatches = matchResult.scoring_metadata.bullets ?? {}
  const skillMatches = matchResult.scoring_metadata.skills ?? {}
  const projectMatches = matchResult.scoring_metadata.projects ?? {}

  const { matched: matchedSkills, unmatched: unmatchedSkills } = splitByMatch(
    skills ?? [],
    (s) => s.id,
    skillMatches
  )
  const { matched: matchedProjects, unmatched: unmatchedProjects } = splitByMatch(
    projects ?? [],
    (p) => p.id,
    projectMatches
  )

  function BulletRow({ bullet }: { bullet: Bullet }) {
    return (
      <li key={bullet.id}>
        <label>
          <input
            type="checkbox"
            checked={selectedBulletIds.has(bullet.id)}
            onChange={() => toggleBullet(bullet.id)}
          />
          {bullet.text}
          <RecommendedPill matched={bulletMatches[String(bullet.id)]} />
        </label>
      </li>
    )
  }

  function SkillRow({ skill }: { skill: Skill }) {
    return (
      <li key={skill.id}>
        <label>
          <input
            type="checkbox"
            checked={selectedSkillIds.has(skill.id)}
            onChange={() => toggleSkill(skill.id)}
          />
          {skill.name} ({skill.category})
          <RecommendedPill matched={skillMatches[String(skill.id)]} />
        </label>
      </li>
    )
  }

  function ProjectRow({ project }: { project: Project }) {
    return (
      <li key={project.id}>
        <label>
          <input
            type="checkbox"
            checked={selectedProjectIds.has(project.id)}
            onChange={() => toggleProject(project.id)}
          />
          {project.name}
          <RecommendedPill matched={projectMatches[String(project.id)]} />
        </label>
      </li>
    )
  }

  return (
    <div>
      <h2>
        Review selection for {jobDescription.company} — {jobDescription.role_title}
      </h2>
      <p>
        We pre-selected the best-matching content based on your job description — uncheck
        anything you don't want, or expand "Show all" to add more from your bank.
      </p>

      <h3>Experience</h3>
      {(experienceEntries ?? []).map((entry) => {
        const entryBullets = (bullets ?? []).filter(
          (bullet) => bullet.experience_entry_id === entry.id
        )
        const { matched, unmatched } = splitByMatch(entryBullets, (b) => b.id, bulletMatches)
        return (
          <div key={entry.id} style={{ marginBottom: 12 }}>
            <strong>
              {entry.company} — {entry.title}
            </strong>
            <ul>
              {matched.map((bullet) => (
                <BulletRow key={bullet.id} bullet={bullet} />
              ))}
            </ul>
            {unmatched.length > 0 && (
              <details>
                <summary>Show {unmatched.length} more bullet(s)</summary>
                <ul>
                  {unmatched.map((bullet) => (
                    <BulletRow key={bullet.id} bullet={bullet} />
                  ))}
                </ul>
              </details>
            )}
          </div>
        )
      })}

      <h3>Skills</h3>
      <ul>
        {matchedSkills.map((skill) => (
          <SkillRow key={skill.id} skill={skill} />
        ))}
      </ul>
      {unmatchedSkills.length > 0 && (
        <details>
          <summary>Show all skills ({unmatchedSkills.length} more)</summary>
          <ul>
            {unmatchedSkills.map((skill) => (
              <SkillRow key={skill.id} skill={skill} />
            ))}
          </ul>
        </details>
      )}

      <h3>Projects</h3>
      <ul>
        {matchedProjects.map((project) => (
          <ProjectRow key={project.id} project={project} />
        ))}
      </ul>
      {unmatchedProjects.length > 0 && (
        <details>
          <summary>Show all projects ({unmatchedProjects.length} more)</summary>
          <ul>
            {unmatchedProjects.map((project) => (
              <ProjectRow key={project.id} project={project} />
            ))}
          </ul>
        </details>
      )}

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

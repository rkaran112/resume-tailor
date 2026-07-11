import { useState } from 'react'
import { BulletForm } from '../components/bank/BulletForm'
import { BulletList } from '../components/bank/BulletList'
import { ContactInfoForm } from '../components/bank/ContactInfoForm'
import { EducationForm } from '../components/bank/EducationForm'
import { EducationList } from '../components/bank/EducationList'
import { ExperienceForm } from '../components/bank/ExperienceForm'
import { ExperienceList } from '../components/bank/ExperienceList'
import { ProjectForm } from '../components/bank/ProjectForm'
import { ProjectList } from '../components/bank/ProjectList'
import { SkillForm } from '../components/bank/SkillForm'
import { SkillList } from '../components/bank/SkillList'

const TABS = [
  'Skills',
  'Experience',
  'Projects',
  'Bullets',
  'Education',
  'Contact Info',
] as const
type Tab = (typeof TABS)[number]

export function BankPage() {
  const [tab, setTab] = useState<Tab>('Skills')

  return (
    <div>
      <h1>Resume Tailor — Bank</h1>
      <nav>
        {TABS.map((t) => (
          <button key={t} aria-current={tab === t} onClick={() => setTab(t)}>
            {t}
          </button>
        ))}
      </nav>

      {tab === 'Skills' && (
        <section>
          <h2>Skills</h2>
          <SkillForm />
          <SkillList />
        </section>
      )}
      {tab === 'Experience' && (
        <section>
          <h2>Experience</h2>
          <ExperienceForm />
          <ExperienceList />
        </section>
      )}
      {tab === 'Projects' && (
        <section>
          <h2>Projects</h2>
          <ProjectForm />
          <ProjectList />
        </section>
      )}
      {tab === 'Bullets' && (
        <section>
          <h2>Bullets</h2>
          <BulletForm />
          <BulletList />
        </section>
      )}
      {tab === 'Education' && (
        <section>
          <h2>Education</h2>
          <EducationForm />
          <EducationList />
        </section>
      )}
      {tab === 'Contact Info' && (
        <section>
          <h2>Contact Info</h2>
          <ContactInfoForm />
        </section>
      )}
    </div>
  )
}

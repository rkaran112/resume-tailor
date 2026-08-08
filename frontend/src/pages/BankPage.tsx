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
import { TitleMark } from '../components/motion/TitleMark'

const TABS = [
  'Skills',
  'Experience',
  'Projects',
  'Bullets',
  'Education',
  'Contact',
] as const
type Tab = (typeof TABS)[number]

const ADD_LABEL: Record<Tab, string> = {
  Skills: 'Add a skill',
  Experience: 'Add a role',
  Projects: 'Add a project',
  Bullets: 'Add a bullet',
  Education: 'Add education',
  Contact: 'Your contact details',
}

export function BankPage() {
  const [tab, setTab] = useState<Tab>('Skills')

  return (
    <div>
      <TitleMark as="h1">Bank</TitleMark>
      <p className="page-intro">
        Type it in once, edit any row later. Tailor pulls from here.
      </p>

      <div className="bank-tabs">
        <nav>
          {TABS.map((t) => (
            <button key={t} aria-current={tab === t} onClick={() => setTab(t)}>
              {t}
            </button>
          ))}
        </nav>
      </div>

      <section>
        <div className="composer">
          <div className="composer-title">{ADD_LABEL[tab]}</div>
          {tab === 'Skills' && <SkillForm />}
          {tab === 'Experience' && <ExperienceForm />}
          {tab === 'Projects' && <ProjectForm />}
          {tab === 'Bullets' && <BulletForm />}
          {tab === 'Education' && <EducationForm />}
          {tab === 'Contact' && <ContactInfoForm />}
        </div>

        {tab === 'Skills' && <SkillList />}
        {tab === 'Experience' && <ExperienceList />}
        {tab === 'Projects' && <ProjectList />}
        {tab === 'Bullets' && <BulletList />}
        {tab === 'Education' && <EducationList />}
      </section>
    </div>
  )
}

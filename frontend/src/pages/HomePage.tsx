import type { ReactNode } from 'react'
import { DrawMark } from '../components/motion/DrawMark'
import { MagneticButton } from '../components/motion/MagneticButton'
import { Reveal } from '../components/motion/Reveal'
import { TitleMark } from '../components/motion/TitleMark'

export type WorkPage = 'Bank' | 'Tailor' | 'Track'

interface HomePageProps {
  onNavigate: (page: WorkPage) => void
}

const STEPS: Array<{ num: string; page: WorkPage; title: string; desc: string }> = [
  {
    num: '01',
    page: 'Bank',
    title: 'Build your bank',
    desc: 'Save your experience, skills, and projects once — or import your current resume and we sort it for you.',
  },
  {
    num: '02',
    page: 'Tailor',
    title: 'Tailor to the job',
    desc: 'Paste a job listing. We pick your best-matching bullets; you approve every line, then download the PDF.',
  },
  {
    num: '03',
    page: 'Track',
    title: 'Track what you sent',
    desc: 'Every application in one list — which resume went out, when, and where it stands now.',
  },
]

const HOWTO: Array<{ title: string; body: string; tip?: ReactNode }> = [
  {
    title: 'Fill your bank once',
    body: 'Add every job, project, skill, and bullet point you might ever use — the raw material for any resume. Import a PDF or LaTeX resume to fill it in seconds, then edit any row inline.',
    tip: (
      <>
        <b>Tip:</b> tag bullets by theme (e.g. “backend”, “leadership”) — that’s what matching keys off.
      </>
    ),
  },
  {
    title: 'Paste the job you’re applying to',
    body: 'Drop the full job description into Tailor. It reads the posting and scores every bullet in your bank against it — no guessing, no AI rewriting your history.',
  },
  {
    title: 'Review and pick your lines',
    body: 'You see the best-matching bullets ranked, with the reasoning. Check the ones you want, uncheck the ones you don’t. Nothing goes on the page you didn’t approve.',
    tip: (
      <>
        <b>Optional:</b> let AI tighten wording or draft a cover letter — always shown to you before it lands.
      </>
    ),
  },
  {
    title: 'Download, then track it',
    body: 'Export a clean, consistent PDF from one fixed template — formatting is solved. Save it to Track and every application lives in one place: which resume went out, when, and where it stands.',
  },
]

const GOOD_TO_KNOW: Array<{ title: string; body: string }> = [
  {
    title: 'Matching is deterministic',
    body: 'Bullets are chosen by tag-based scoring against the job — not improvised by a model. Same inputs, same result, every time.',
  },
  {
    title: 'AI is opt-in, always',
    body: 'Wording polish and cover letters only run when you ask, and every change is shown for approval before it touches the page.',
  },
  {
    title: 'One template, done right',
    body: 'A single hand-built HTML/CSS template renders to PDF via headless Chromium, so spacing and typography never drift between applications.',
  },
]

export function HomePage({ onNavigate }: HomePageProps) {
  return (
    <div>
      <div className="hero">
        <div className="hero-ruled" aria-hidden="true" />
        <div className="hero-copy">
          <div className="eyebrow">A quieter way to apply</div>
          <h1 className="hero-title">
            Send the <span className="strike-word">same</span>{' '}
            <em className="fix-word">right</em> resume, every&nbsp;time.
          </h1>
          <p className="hero-sub">
            Save your experience once. Paste a job listing — Resume Tailor picks the bullets that
            fit, builds a clean PDF, and remembers where you applied.
          </p>
          <div className="hero-cta">
            <MagneticButton className="btn-primary" onClick={() => onNavigate('Bank')}>
              Start with your bank
            </MagneticButton>
          </div>
        </div>

        <div className="hero-demo">
          <div className="demo-doc" aria-hidden="true">
            <span className="demo-eyebrow">Your resume, tailored to the job</span>
            <div className="demo-line-title" />
            <div className="demo-row">
              <span className="demo-check demo-check-1">
                <DrawMark variant="check" delaySeconds={0.5} />
              </span>
              <div className="demo-line w-90" />
            </div>
            <div className="demo-row">
              <span className="demo-check demo-check-2">
                <DrawMark variant="check" delaySeconds={1.3} />
              </span>
              <div className="demo-line w-75" />
            </div>
            <div className="demo-row">
              <div className="demo-line w-85 demo-strike demo-strike-1">
                <DrawMark variant="strike" delaySeconds={2.1} />
              </div>
            </div>
            <div className="demo-row">
              <span className="demo-check demo-check-3">
                <DrawMark variant="check" delaySeconds={3.1} />
              </span>
              <div className="demo-line w-70" />
            </div>
            <div className="demo-row">
              <div className="demo-line w-60 demo-strike demo-strike-2">
                <DrawMark variant="strike" delaySeconds={3.8} />
              </div>
            </div>
            <span className="demo-chip">Recommended</span>
          </div>
        </div>
      </div>

      <div className="steps">
        {STEPS.map((step, i) => (
          <button
            key={step.page}
            className="step-card"
            style={{ animationDelay: `${0.25 + i * 0.12}s` }}
            onClick={() => onNavigate(step.page)}
          >
            <span className="step-num mono-num">{step.num}</span>
            <span className="step-title">{step.title}</span>
            <span className="step-desc">{step.desc}</span>
            <span className="step-go" aria-hidden="true">
              →
            </span>
          </button>
        ))}
      </div>

      <section className="howto">
        <TitleMark>How it works</TitleMark>
        <p className="howto-sub">Four steps, start to sent. You stay in control the whole way.</p>
        <div className="howto-list">
          {HOWTO.map((step, i) => (
            <Reveal delay={i * 0.06} key={step.title}>
              <div className="howto-step">
                <div className="howto-num">{String(i + 1).padStart(2, '0')}</div>
                <div>
                  <h3>{step.title}</h3>
                  <p>{step.body}</p>
                  {step.tip && <p className="howto-tip">{step.tip}</p>}
                </div>
              </div>
            </Reveal>
          ))}
        </div>
      </section>

      <section>
        <TitleMark>Good to know</TitleMark>
        <div className="good-to-know">
          {GOOD_TO_KNOW.map((item, i) => (
            <Reveal delay={i * 0.06} key={item.title}>
              <div className="gtk-card">
                <h4>{item.title}</h4>
                <p>{item.body}</p>
              </div>
            </Reveal>
          ))}
        </div>
      </section>

      <div className="hero-cta" style={{ marginBottom: 12 }}>
        <MagneticButton className="btn-primary" onClick={() => onNavigate('Bank')}>
          Start with your bank
        </MagneticButton>
      </div>
      <p className="hero-note">
        Nothing here is written by AI unless you ask. The optional polish and cover-letter tools
        always show you the change before it lands on the page.
      </p>
    </div>
  )
}

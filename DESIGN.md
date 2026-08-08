# Design System — Resume Tailor

## Product Context
- **What this is:** A single-user resume/CV tailoring tool and job-application tracker. Deterministic keyword matching (not LLM improvisation) selects bullets from a hand-curated content bank; a fixed HTML/CSS template renders to PDF via headless Chromium.
- **Who it's for:** One person (the tool's owner), managing their own job search — no multi-tenant chrome, no auth surface.
- **Space/industry:** Productivity / personal tooling, adjacent to resume builders (Kickresume, Teal) but closer in spirit to precision instruments (Linear, Raycast) than to consumer resume-template sites.
- **Project type:** Web app — three working screens (Bank, Tailor, Applications), forms- and data-dense, not a marketing site.
- **Memorable thing:** *Craft & precision* — every screen should read as deliberate, like a tool built by someone who takes their own job search seriously.

## Aesthetic Direction
- **Direction:** Refined/Editorial — grid-disciplined app chrome (it's a real tool, not a landing page) with one deliberate editorial risk.
- **Decoration level:** Intentional — hairline borders, tabular numbers, small-caps labels. Not bare (the old system-ui default), not busy.
- **Mood:** Quiet, exact, unmistakably hand-chosen. The one saturated color in the system should read as a decision, not decoration.
- **Reference research:** [21st.dev](https://21st.dev) (serif/sans editorial headline pairing, warm-neutral canvas, pill controls, "crafted, not AI slop" positioning) and [Linear](https://linear.app) (near-black precision-engineering canvas, restrained color, dense data as hero visual).
- **Naming the pivot:** The first proposal used a warm-cream canvas + terracotta accent + serif display — a well-known AI-generated-design default (cream #F4F1EA + serif + terracotta is a documented cliché). Revised to cooler graphite neutrals and a **vermilion "editor's mark" accent**, grounded in what the product actually does: curating and rewording resume content, like a red pen on a draft. The serif/sans pairing was kept because it's reasoned, not decorative — it echoes the Georgia-set resume this tool renders to PDF (`app/templates/resume_template.html`), so the tool visually rhymes with the document it produces.

## Typography
- **Display/Hero:** Fraunces (serif, variable, optical-size axis) — echoes the Georgia resume template; distinctive ink-trap detailing keeps it from reading as generic "elegant serif." Used for page titles, section headers, and the wordmark.
- **Body/UI:** Instrument Sans — clean geometric-humanist sans for forms, buttons, nav, bullet text, labels. Not Inter/Roboto/system-ui.
- **Data/Tables:** DM Sans with `font-feature-settings: "tnum" 1, "lnum" 1` — applications tracker dates/figures, any numeric column.
- **Code:** N/A — no code surfaces in this product.
- **Loading:** Google Fonts, `<link>` in `frontend/index.html` (Fraunces + Instrument Sans + DM Sans, `display=swap`).
- **Scale:**
  - Display H1: `clamp(32px, 4vw, 44px)` / 1.08 line-height, Fraunces 600, letter-spacing `-0.012em` — a light tightening (not Raycast's -0.11em; over-tightening a serif breaks it) borrowed from the 2026 precision-tool trend (Raycast/Linear "typography as pressure"), applied subtly so Fraunces still reads warm, not clenched.
  - Section H2: `24px` / 1.15, Fraunces 600
  - Subsection H3: `16px` / 1.3, Fraunces 600
  - Body: `15px` / 1.55, Instrument Sans 400
  - Label/caption: `12.5px` / 1.3, Instrument Sans 600, letter-spacing `0.02em`
  - Eyebrow (section labels): `11.5px`, Instrument Sans 600, uppercase, letter-spacing `0.08em`

## Color
- **Approach:** Restrained — one accent, cool neutrals, semantic colors kept clearly distinct in hue from the accent (the accent is itself a "red," so error uses a berry/magenta hue, not another red, to avoid twinning).
- **Accent (vermilion, "editor's mark"):** `#C6362A` light / `#E8674F` dark — primary actions, active nav state, focus rings, links.
- **Ink:** `#17181A` light / `#EDEDEC` dark — primary text.
- **Ink muted:** `#63666B` light / `#A4A6AA` dark — secondary text, meta.
- **Ink faint:** `#93969B` light / `#6E7075` dark — placeholders, disabled, captions.
- **Canvas (bg):** `#F5F3F3` light / `#131415` dark — cool, barely-tinted neutral, not warm cream.
- **Surface (cards):** `#FDFCFC` light / `#1C1D1F` dark.
- **Surface raised:** `#FFFFFF` light / `#232426` dark — modals, elevated panels.
- **Border:** `#DDD9D8` light / `#303234` dark. **Border strong:** `#C4BFBE` light / `#45474A` dark — inputs, dividers that need more presence.
- **Semantic:**
  - Success: `#3F7D53` / bg `#E6F0E9` (light), `#7FBE93` / bg `#1E2B22` (dark)
  - Warning: `#9C6B1F` / bg `#F3EAD6` (light), `#D6A855` / bg `#302818` (dark)
  - Error: `#B23D6B` / bg `#F5E4EC` (light), `#E28FB0` / bg `#2E1E26` (dark) — deliberately berry/magenta, not red, to stay distinguishable from the vermilion accent
  - Info: `#3B6E8F` / bg `#E5EEF2` (light), `#7FB0CC` / bg `#1E2A30` (dark)
- **Dark mode:** Not an inversion — surfaces redesigned (near-black graphite, not navy-tinted), accent brightened for contrast on dark, semantic colors lightened. Token-level: `:root` (light default) → `@media (prefers-color-scheme: dark)` → `:root[data-theme="dark"]` / `:root[data-theme="light"]` override both directions.

## Spacing
- **Base unit:** 8px
- **Density:** Comfortable — this is a forms-heavy CRUD app; the old system-ui default read cramped and unpolished, but full "spacious" marketing density would fight table/list scanability.
- **Scale:** 2xs(2) xs(4) sm(8) md(16) lg(24) xl(32) 2xl(48) 3xl(64)
- **Radius:** sm(6px) — inputs, buttons, chips; md(10px) — cards; lg(16px) — mockup frames/panels; full(999px) — pill nav, tags, status badges

## Layout
- **Approach:** Grid-disciplined overall (predictable single-column forms/lists on Bank and Applications), with one deliberate departure on Tailor: an asymmetric two-column **split-pane workbench** (~1.05fr / 0.95fr) — job-description input and the matched-bullet picker on the left, a permanently-visible live resume preview on the right, like an editor's split pane (Figma/VS Code) instead of a stacked scroll-down wizard form.
- **Max content width:** 1180px, centered, 32px side padding (18-20px on mobile).
- **Nav:** Pill-shaped tab group (Bank / Tailor / Applications), active tab filled ink-on-canvas, inactive tabs muted text on transparent.
- **Cards:** 1px hairline border, `var(--surface)` background, `var(--radius-md)`, no shadow at rest; the Tailor workbench frame and the embedded resume-preview page get `var(--shadow)` to read as a "raised" instrument panel / physical page.
- **Responsive:** Workbench collapses to single column under 760px (left panel stacks above the preview).

## Motion
- **Approach:** Intentional — subtle, functional, never decorative-only. One shared keyframe (`rise-in`: 8px rise + fade) still backs list-row and micro-interaction motion; `framer-motion` (new dependency) drives everything that needs viewport-detection, exit animation, or spring physics.
- **Page/tab switch:** `AnimatePresence mode="wait"` + `PageTransition.tsx` cross-fades + slides between Home/Bank/Tailor/Track (sequential exit-then-enter, not overlapping — avoids scrollbar/layout jump between pages of very different heights).
- **Signature moment (Home):** the hero headline still strikes through "same" and fades in "right" as before, and the hero demo's checks/strikes are now *literally hand-drawn* — `DrawMark.tsx`, dependency-free inline SVG stroked in via `stroke-dashoffset`, replacing the old opacity/scale fade — instead of a UI-badge checkmark. This is still the single orchestrated moment on the page; the rest of the site stays quiet.
- **Scroll reveals:** `Reveal.tsx` (framer-motion `whileInView`, fires once) wraps Home's "How it works" steps and "Good to know" cards, which previously had no entrance motion at all.
- **Section headers:** `TitleMark.tsx` draws the hand-drawn underline stroke once per header, on first scroll into view (framer-motion `pathLength`), replacing the old static masked-SVG underline — same wavy path, now actually drawn rather than just tinted.
- **Tactile CTA:** the two hero "Start with your bank" buttons get a bounded magnetic cursor-pull (`MagneticButton.tsx`, spring physics) — scoped to hero-tier CTAs only, not the ~10 other `.btn-primary` uses app-wide (form saves, inline table actions), where it would fight the precision-instrument feel of a data-dense tool.
- **List rows:** Bank/Track table rows mount with a small stagger (`.row-rise` + `rowRiseStyle()`, same `rise-in` keyframe, ~40ms/row) instead of appearing all at once.
- **Micro-interactions:** buttons press down 1px on `:active`; primary buttons gain a soft accent shadow on hover; step cards lift 2px + arrow nudges right; optional-panel "+" rotates 45° when open. All 120-180ms ease.
- **Transitions:** border-color / color on 150ms ease (hover, focus); background/color theme-switch at 250ms ease.
- **Respect `prefers-reduced-motion`** — CSS-only motion (`rise-in`, `.row-rise`, `DrawMark`) stays covered by the existing global `animation-duration: 0.01ms` override; every framer-motion component calls `useReducedMotion()` directly and skips its own animation, since JS-driven motion values aren't caught by that CSS rule.

## Voice
- **Plain words, premium tone.** Short sentences, active voice, no jargon: "Make the PDF" not "Finalize", "Find my matches" not "Match against bank", "turned off" not "disabled", "optional" not "opt-in".
- **Name things by what the user controls:** Bank / Tailor / Track (the nav is the product's three-step flow; the Home page teaches it in the same words).
- **Every page opens with one `.page-intro` sentence** saying what the screen is for.
- **Trust line pattern:** any AI feature states, right where the button is, that nothing changes without the user seeing and approving it first.

## Home (landing)
- Two-column top band: left is copy (eyebrow → display headline with the animated editor's mark → one-sentence sub → single primary CTA "Start with your bank"); right is the **live demo** (`.hero-demo`). Below, full-width: three clickable step cards (01 Build your bank / 02 Tailor to the job / 03 Track what you sent, staggered `rise-in`), then a small AI-trust footnote. Default view on load; wordmark click returns to it.
- **The demo IS the signature.** A stylized resume document (`.demo-doc`, tilted −1.4°, gently floating) shows the editor's mark working on a loop: vermilion check-marks land on strong bullets, a "Recommended" chip appears in the margin, and weak bullets get struck through in red pen and dim out. Pure CSS (staggered infinite keyframes on a shared 5.5s period so marks stay in sync). Under `prefers-reduced-motion` the marks are parked in their resolved state — the doc still reads as "marked up", never blank. It demonstrates the product and fills what was dead hero space.
- **Ruled-margin background (`.hero-ruled`).** A very faint horizontal-rule pattern (repeating 1px lines every 34px, masked to fade out toward the bottom ~78% of the hero) sits behind the hero copy, as if the headline is written on ruled paper being marked up — ties the "editor's mark" motif to the typography itself, not just the checkmark/strike motif. Opacity `0.55` light / `0.35` dark, deliberately near-subliminal — must never compete with the headline for attention. If it becomes visible enough to notice on a casual glance, it's too strong.

## Signature motif — the editor's mark
The vermilion accent is not just "primary color"; it's a red pen correcting a draft, and it recurs as a deliberate motif:
- **Section headers** (`.title-mark`) carry a rough hand-drawn underline — an SVG stroke applied via CSS `mask` so it inherits the themed accent in both light/dark.
- **Empty states** (`.empty-state`) are framed as a margin note: a large italic Fraunces pilcrow (¶) in accent, a short title, a one-line hint on what to do. Never a blank table with headers.
- **The hero demo** (above) is the motif in motion.

## Loading & long operations
- **Lists / tables** show a shimmer `TableSkeleton` (column widths cycle so it reads as tabular data, not a gray block), never bare "Loading…" text. The resume preview uses a page-shaped `PagePreviewSkeleton`.
- **Slow AI calls** (resume import, wording polish, cover-letter draft, PDF render) show a `ProgressActivity`: an indeterminate accent progress bar + a pulsing dot + rotating status lines that advance and hold on the last line (never cycle back — that would read as a stall). Copy is plain and specific per operation ("Pulling out your experience and skills…", "Rendering the PDF…").
- Components: `components/ui/Skeleton.tsx`, `components/ui/ProgressActivity.tsx`, `components/ui/EmptyState.tsx`.

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-07-12 | Initial design system created via `/design-consultation` | Research: 21st.dev + Linear. Memorable-thing answer: "Craft & precision." Approved preview: `resume-tailor-design-preview.html` (published as a Claude Artifact). |
| 2026-07-12 | Rejected first-pass palette (warm cream + terracotta + serif) | Flagged by the `artifact-design` skill as a documented AI-generated-design cliché. Replaced with cool graphite neutrals + vermilion "editor's mark" accent, tied to the product's actual editorial function rather than decorative warmth. |
| 2026-07-13 | Added Home landing page, plain-words copy pass, progressive disclosure, motion layer | User feedback: flow was hard to follow and the UI felt overwhelming. Home teaches the Bank → Tailor → Track flow; "Applications" nav renamed "Track"; resume import and the two AI panels collapse into `details.optional-panel` so screens open calm; single orchestrated animation moment lives in the hero (animated editor's mark), everything else is 120-250ms micro-interaction. |
| 2026-07-13 | Editor's-mark promoted to a system motif; landing demo; loading + empty-state system | Refinement pass (`/design-consultation`, update mode). User wanted a professional, non-generic look ("banks look AI"), demos on the landing page, and real loading bars for the slow steps, without adding feature complexity. Shipped: two-column hero with a looping CSS demo of a resume being marked up; `.title-mark` hand-drawn header underlines; red-pen `.empty-state`; `TableSkeleton`/`PagePreviewSkeleton` replacing "Loading…"; `ProgressActivity` (indeterminate bar + rotating copy) on all four LLM/PDF operations. |
| 2026-07-13 | Simplify pass: bank pared down, tab bar centered, resume-import removed, application editor redesigned | User asked to keep it minimal ("effort in → output out"), make the bank "as simple as copy-paste", centre the Bank tab bar, and fix the visually-weak application editor. Removed the resume-import panel from Bank for now (LaTeX/PDF import returns later); dropped the redundant per-section `h2` so the flow is tabs → composer → list; centred the Bank tab bar (`.bank-tabs`). Rebuilt the application detail editor into card `.panel`s (status meta, `.doc-link` download buttons, a clean status-change row) with a proper vertical connected `.timeline` (dots + line, newest-first). Fixed stray raw "Loading…" text (contact form, detail page). |
| 2026-07-13 | Bank composer cards + inline row editing; Home "How it works" walkthrough; Track stat cards; API base-URL hardening | Follow-up pass. (1) Bug: writes 404'd `{"detail":"Not Found"}` when `VITE_API_BASE_URL` lacked the `/api` suffix — `client.ts` now normalizes it on. (2) Bank forms reframed as `.composer` cards (labelled, no longer a bare wrapping input row); every list row gained inline Edit (flips cells to inputs, Save/Cancel, `tr.editing` accent tint) via the existing `useUpdate` hooks; non-essential fields (category, location, description, field, phone) made optional. (3) Home gained a numbered `.howto` walkthrough + `.good-to-know` reassurance cards so it teaches the flow and scrolls as a real landing. (4) Track gained a `.stat-row` (Total / In progress / Interviews / Offers) above the table. |
| 2026-07-15 | Motion-craft pass: hand-drawn marks, scroll reveals, page transitions, magnetic CTA | User asked for an "artist redesign" focused on smooth, creative animation; researched technique (not code — 21st.dev free-tier retrieval limit was maxed) via `mcp__21st__search` for self-drawing SVG and magnetic-button patterns. Added `framer-motion` (first JS animation dependency) used only where JS-driven viewport-detection/exit/physics is unavoidable: `PageTransition.tsx` (`AnimatePresence mode="wait"` between nav tabs), `Reveal.tsx` (scroll-triggered stagger for Home's howto/good-to-know sections, previously static), `TitleMark.tsx` (the `.title-mark` underline now actually draws once in view, was a static mask), `MagneticButton.tsx` (bounded cursor-pull, scoped to the two hero CTAs only). The hero demo's checks/strikes moved from opacity/scale fades to literal hand-drawn strokes (`DrawMark.tsx`, dependency-free `stroke-dashoffset`, kept off framer-motion since it's a non-interactive perpetual loop the existing CSS reduced-motion block already owns). Table rows across Bank/Track gained a small mount stagger (`.row-rise`). Supersedes the prior "single orchestrated moment; nothing else earns choreography" line — the hero is still the boldest moment, but reveals/transitions/magnetic-pull are now a deliberate, restrained second layer, not zero. |
| 2026-07-16 | General refresh pass via `/design-consultation` (update mode): confirmed system holds, added 2 typographic risks | Researched 2026 landscape: category convergence (Teal/Huntr/Enhancv) on purple-gradient hero + kanban screenshots + "AI Powered" feature grids confirmed the existing vermilion/graphite system was right to avoid it — no change needed there. Separately researched the 2026 "precision instrument" aesthetic (Raycast/Linear/Arc): dark-first as primary mode, non-round border-radii, negative letter-spacing at display sizes ("typography as pressure"), anti-"liquid-glass" clarity-over-decoration stance. Eureka: dark-first doesn't fit this product — Resume Tailor's deliverable is a printed/PDF resume (inherently light, paper-like), unlike screen-only tools like Raycast/Linear, so light stays primary and dark stays a fully-redesigned secondary mode (unchanged). Adopted two risks from the trend research, both subtle: (1) Fraunces H1 letter-spacing tightened to `-0.012em` (a light touch vs. Raycast's `-0.11em` — over-tightening breaks a serif); (2) `.hero-ruled`, a near-subliminal ruled-margin line pattern behind the Home hero headline, tying the "editor's mark" motif to the typography itself. Confirmed via HTML preview (`scratch/design-preview.html`) in both light and dark before shipping. |

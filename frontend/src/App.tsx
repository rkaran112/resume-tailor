import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AnimatePresence } from 'framer-motion'
import { useEffect, useState } from 'react'
import { PageTransition } from './components/motion/PageTransition'
import { ApplicationsPage } from './pages/ApplicationsPage'
import { BankPage } from './pages/BankPage'
import { HomePage } from './pages/HomePage'
import { TailorPage } from './pages/TailorPage'

const queryClient = new QueryClient()

const NAV_PAGES = ['Bank', 'Tailor', 'Track'] as const
type Page = 'Home' | (typeof NAV_PAGES)[number]

type Theme = 'light' | 'dark'

function useTheme() {
  const [theme, setTheme] = useState<Theme>(() => {
    const stored = localStorage.getItem('theme')
    if (stored === 'light' || stored === 'dark') return stored
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  })

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('theme', theme)
  }, [theme])

  return [theme, setTheme] as const
}

function AppShell() {
  const [page, setPage] = useState<Page>('Home')
  const [theme, setTheme] = useTheme()

  return (
    <div>
      <div className="topbar">
        <button className="wordmark" onClick={() => setPage('Home')} aria-label="Go to home">
          <em>R</em>esume Tailor
        </button>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <nav style={{ marginBottom: 0 }}>
            {NAV_PAGES.map((p) => (
              <button key={p} aria-current={page === p} onClick={() => setPage(p)}>
                {p}
              </button>
            ))}
          </nav>
          <button
            className="theme-toggle"
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          >
            {theme === 'dark' ? '☾ Dark' : '☀ Light'}
          </button>
        </div>
      </div>
      <AnimatePresence mode="wait">
        <PageTransition key={page}>
          {page === 'Home' && <HomePage onNavigate={setPage} />}
          {page === 'Bank' && <BankPage />}
          {page === 'Tailor' && <TailorPage />}
          {page === 'Track' && <ApplicationsPage />}
        </PageTransition>
      </AnimatePresence>
    </div>
  )
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppShell />
    </QueryClientProvider>
  )
}

export default App

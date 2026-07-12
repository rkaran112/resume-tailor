import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useState } from 'react'
import { ApplicationsPage } from './pages/ApplicationsPage'
import { BankPage } from './pages/BankPage'
import { TailorPage } from './pages/TailorPage'

const queryClient = new QueryClient()

const PAGES = ['Bank', 'Tailor', 'Applications'] as const
type Page = (typeof PAGES)[number]

function AppShell() {
  const [page, setPage] = useState<Page>('Bank')

  return (
    <div>
      <nav>
        {PAGES.map((p) => (
          <button key={p} aria-current={page === p} onClick={() => setPage(p)}>
            {p}
          </button>
        ))}
      </nav>
      {page === 'Bank' && <BankPage />}
      {page === 'Tailor' && <TailorPage />}
      {page === 'Applications' && <ApplicationsPage />}
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

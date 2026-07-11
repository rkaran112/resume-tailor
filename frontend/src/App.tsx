import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BankPage } from './pages/BankPage'

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BankPage />
    </QueryClientProvider>
  )
}

export default App

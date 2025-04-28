'use client'

import { useState } from 'react'
import { MockToggleButton } from '@/components/MockToggleButton'
import { ResultCard } from '@/components/ResultCard/ResultCard'
import { SearchInputWithButton } from '@/components/SearchInputWithButton'
import { WineAnalysisResponse } from '@/types/WineAnalysisResponse'

export default function WineChatPage() {
  // State
  const [query, setQuery] = useState('')
  const [response, setResponse] = useState<WineAnalysisResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [useMock, setUseMock] = useState(true)

  const showMockToggle = process.env.NEXT_PUBLIC_SHOW_MOCK_TOGGLE === "true";

  // Handler
  const handleSearch = async () => {
    if (!query.trim()) return
    setLoading(true)
    setResponse(null)

    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL
      const res = await fetch(`${baseUrl}/chat-search-wine`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          input: { query },
          context: {
            model: 'gemini-2.0-flash',
            user_id: 'demo-user',
            timestamp: new Date().toISOString(),
            ruleset: 'WSET Level 4 SAT',
            confidence: 0.9,
            use_mock: useMock,
          }
        })
      })
      const data = await res.json()
      setResponse({
        status: 'success',
        ...data.output
      })
    } catch (err) {
      console.error('Error calling API:', err)
      setResponse({
        status: 'error',
        error: 'Failed to fetch analysis.'
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="flex flex-col gap-3">
      <h1 className="text-3xl font-bold text-center">Wine Intelligence</h1>
      <p className="text-center text-zinc-400">Explore wine profiles with intelligent analyzer</p>

      <SearchInputWithButton
        value={query}
        onChange={setQuery}
        onSubmit={handleSearch}
        loading={loading}
      />
      {response?.status === 'error' && (
        <div className="bg-red-950 border border-red-700 p-3 rounded-md text-center text-red-400 text-sm break-words mt-4">
          {response.error || "An unexpected error occurred. Please try again."}
        </div>
      )}
      {response?.status === 'success' && (
        <ResultCard response={response} />
      )}

      {showMockToggle && (
        <MockToggleButton useMock={useMock} onToggle={() => setUseMock(!useMock)} />
      )}
    </main>
  )
}
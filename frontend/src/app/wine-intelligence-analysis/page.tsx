// src/app/wine-intelligence-analysis/page.tsx
'use client'

import { useState } from 'react'
import { SearchInput } from '@/components/SearchInput'
import { SubmitButton } from '@/components/SubmitButton'
import { ResultCard } from '@/components/ResultCard'
import { WineAnalysisResponse } from '@/types/WineAnalysisResponse'

export default function WineChatPage() {
  const showMockToggle = process.env.NEXT_PUBLIC_SHOW_MOCK_TOGGLE === "true";
  const [query, setQuery] = useState('')
  const [response, setResponse] = useState<WineAnalysisResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [useMock, setUseMock] = useState(true);
  
  const handleSubmit = async () => {
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
    <main className="min-h-screen bg-[#121212] text-white px-6 py-10 flex flex-col items-center">
      <h1 className="text-2xl font-bold mb-6">🍷 Wine Intelligence Analyzer</h1>

      <div className="w-full max-w-xl bg-gray-800 p-6 rounded-lg shadow-md">
        <SearchInput value={query} onChange={setQuery} />
  
        {showMockToggle && (
          <div className="mb-4 text-sm text-gray-300">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={useMock}
                onChange={() => setUseMock(!useMock)}
              />
              Use mock response (Dev only)
            </label>
          </div>
        )}
  
        <div className="w-full flex justify-center mt-4">
          <SubmitButton loading={loading} onClick={handleSubmit} />
        </div>
      </div>

      <div className="w-full flex justify-center">
        {response?.status === 'error' && (
          <p className="text-red-500 mt-4">{response.error}</p>
        )}

        {response?.status === 'success' && (
          <ResultCard response={response} />
        )}
      </div>

    </main>
  )
}

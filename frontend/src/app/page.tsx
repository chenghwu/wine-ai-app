'use client'

import { useState } from 'react'
import { useEffect } from 'react'
import { MockToggleButton } from '@/components/MockToggleButton'
import { ResultCard } from '@/components/ResultCard/ResultCard'
import { SearchInputWithButton } from '@/components/SearchInputWithButton'
import { ProgressIndicator } from '@/components/ProgressIndicator'
import { InlineCameraCapture } from '@/components/InlineCameraCapture'
import { WineAnalysisResponse } from '@/types/WineAnalysisResponse'
import { AnalysisStage, PROGRESS_MESSAGES, STAGE_PROGRESS } from '@/types/Progress'
import { getLastUpdatedLabel } from '@/utils/dateUtils'

export default function WineChatPage() {
  // State
  const [version, setVersion] = useState('')
  const [lastUpdated, setLastUpdated] = useState('')
  const [query, setQuery] = useState('')
  const [response, setResponse] = useState<WineAnalysisResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [currentStage, setCurrentStage] = useState<AnalysisStage>('parsing_query')
  const [progress, setProgress] = useState(0)
  const [showCamera, setShowCamera] = useState(false)
  const [analysisType, setAnalysisType] = useState<'text' | 'image'>('text')
  const [useMock, setUseMock] = useState(() => {
    return process.env.NEXT_PUBLIC_USE_MOCK === "true";
  });

  const showMockToggle = process.env.NEXT_PUBLIC_SHOW_MOCK_TOGGLE === "true";

  // Fetch version and last updated time
  useEffect(() => {
    const fetchMetadata = async () => {
      try {
        const baseUrl = process.env.NEXT_PUBLIC_API_URL
        const res = await fetch(`${baseUrl}/meta`)
        const data = await res.json()
        setVersion(data.version || '')
        setLastUpdated(data.last_updated || '')
      } catch (err) {
        console.error('Failed to fetch metadata', err)
      }
    }

    fetchMetadata()
  }, [])

  // Simulate progress stages for text analysis
  const simulateProgress = async () => {
    const stages: AnalysisStage[] = ['parsing_query', 'gathering_info', 'aggregating_results', 'analyzing_ai']
    
    for (let i = 0; i < stages.length; i++) {
      const stage = stages[i]
      setCurrentStage(stage)
      setProgress(STAGE_PROGRESS[stage])
      
      // Wait between stages (shorter for better UX)
      if (i < stages.length - 1) {
        await new Promise(resolve => setTimeout(resolve, 800))
      }
    }
  }

  // Simulate progress stages for image analysis
  const simulateImageProgress = async () => {
    const stages: AnalysisStage[] = ['processing_image', 'extracting_info', 'gathering_additional_data', 'analyzing_ai']
    
    for (let i = 0; i < stages.length; i++) {
      const stage = stages[i]
      setCurrentStage(stage)
      setProgress(STAGE_PROGRESS[stage])
      
      // Wait between stages (image processing takes longer)
      if (i < stages.length - 1) {
        await new Promise(resolve => setTimeout(resolve, 1200))
      }
    }
  }

  // Handler
  const handleSearch = async () => {
    if (!query.trim()) return
    setLoading(true)
    setResponse(null)
    setProgress(0)
    setAnalysisType('text')

    try {
      // Start progress simulation
      const progressPromise = simulateProgress()
      
      const baseUrl = process.env.NEXT_PUBLIC_API_URL
      const res = await fetch(`${baseUrl}/analyze-wine`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          input: { query },
          context: {
            model: process.env.NEXT_PUBLIC_GEMINI_MODEL,
            user_id: 'demo-user',
            timestamp: new Date().toISOString(),
            ruleset: 'WSET Level 4 SAT',
            confidence: 0.9,
            use_mock: useMock,
          }
        })
      })
      
      // Wait for both progress and API response
      const [data] = await Promise.all([res.json(), progressPromise])
      
      const result: WineAnalysisResponse = {
        status: 'success',
        ...data.output,
      };
      setResponse(result);
  
      // Clear query if successful
      if (result.status === 'success') {
        setQuery('');
      }

    } catch (err) {
      console.error('Error calling API:', err)
      setResponse({
        status: 'error',
        error: 'Failed to fetch analysis.'
      })
    } finally {
      setLoading(false)
      setProgress(0)
    }
  }

  const handleCameraClick = () => {
    setShowCamera(!showCamera)
  }

  const handleImageCapture = async (imageData: string) => {
    setShowCamera(false)
    setLoading(true)
    setResponse(null)
    setProgress(0)
    setAnalysisType('image')
    
    try {
      // Simulate progress for image analysis
      const progressPromise = simulateImageProgress()
      
      // Convert base64 to blob for upload
      const response = await fetch(imageData)
      const blob = await response.blob()
      const file = new File([blob], 'wine_label.jpg', { type: 'image/jpeg' })
      
      // Prepare form data
      const formData = new FormData()
      formData.append('file', file)
      formData.append('context', JSON.stringify({
        model: process.env.NEXT_PUBLIC_GEMINI_MODEL || 'gemini-2.5-flash',
        user_id: 'demo-user',
        timestamp: new Date().toISOString(),
        ruleset: 'WSET Level 4 SAT',
        confidence: 0.9,
        use_mock: useMock,
      }))
      
      const baseUrl = process.env.NEXT_PUBLIC_API_URL
      const res = await fetch(`${baseUrl}/analyze-wine-image`, {
        method: 'POST',
        body: formData
      })
      
      // Wait for both progress and API response
      const [data] = await Promise.all([res.json(), progressPromise])
      
      const result: WineAnalysisResponse = {
        status: 'success',
        ...data.output,
      }
      setResponse(result)
      
    } catch (err) {
      console.error('Error analyzing image:', err)
      setResponse({
        status: 'error',
        error: 'Failed to analyze wine from image. Please try again or enter the wine name manually.'
      })
    } finally {
      setLoading(false)
      setProgress(0)
    }
  }

  const handleCameraClose = () => {
    setShowCamera(false)
  }

  return (
    <div className="min-h-screen flex flex-col overflow-x-hidden">
      {/* Main content */}
      <main className="flex-grow flex flex-col items-center justify-center px-1 py-8 gap-2 pb-10">
        <h1 className="text-3xl font-bold text-center">
          Wine Intelligence{' '}
          {version && (
            <span className="text-sm text-zinc-400">v{version}</span>
          )}
        </h1>
        <p className="text-center text-zinc-400">Explore wine profiles with intelligent analyzer</p>

        <SearchInputWithButton
          value={query}
          onChange={setQuery}
          onSubmit={handleSearch}
          onCameraClick={handleCameraClick}
          loading={loading}
        />

        <ProgressIndicator
          isVisible={loading}
          currentStage={PROGRESS_MESSAGES[currentStage][analysisType]}
          progress={progress}
        />

        <InlineCameraCapture
          isVisible={showCamera}
          onClose={handleCameraClose}
          onImageCapture={handleImageCapture}
        />

        {response?.status === 'error' && (
          <div className="bg-red-950 border border-red-700 p-3 rounded-md text-center text-red-400 text-sm break-words mt-4">
            {response.error || "An unexpected error occurred. Please try again."}
          </div>
        )}
        {response?.status === 'success' && (
          <ResultCard response={response} />
        )}
      </main>

      {/* Footer */}
      <footer className="fixed bottom-0 left-0 w-full px-4 py-1 flex justify-between items-center text-xs text-zinc-400 bg-black z-50">
        <div>
          Last updated: {getLastUpdatedLabel(lastUpdated)}
        </div>
        {showMockToggle && (
          <div>
            <MockToggleButton useMock={useMock} onToggle={() => setUseMock(!useMock)} />
          </div>
        )}
      </footer>
    </div>
  )
}
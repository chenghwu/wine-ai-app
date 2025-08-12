'use client'

import { useState, useEffect } from 'react'
import { MockToggleButton } from '@/components/MockToggleButton'
import { ResultCard } from '@/components/ResultCard/ResultCard'
import { SearchInputWithButton } from '@/components/SearchInputWithButton'
import { ProgressIndicator } from '@/components/ProgressIndicator'
import { InlineCameraCapture } from '@/components/InlineCameraCapture'
import { AppMode } from '@/components/ModeToggle'
import { SearchHistory, HistoryItem } from '@/components/SearchHistory'
import { MenuResultCard } from '@/components/MenuResultCard'
import { WineAnalysisResponse } from '@/types/WineAnalysisResponse'
import { AnalysisStage, PROGRESS_MESSAGES, STAGE_PROGRESS } from '@/types/Progress'
import { getLastUpdatedLabel } from '@/utils/dateUtils'

interface MenuAnalysisResponse {
  status: string
  error?: string
  restaurant_info?: {
    name?: string
    cuisine_style: string
    confidence: number
  }
  menu_analysis?: {
    items_found: number
    extraction_method: string
  }
  wine_recommendations?: {
    menu_items: Array<{
      dish: {
        dish_name: string
        category?: string
        price?: string
        protein?: string
        cooking_method?: string
        cuisine_type?: string
        description?: string
      }
      wine_pairings: {
        specific_recommendations: Array<{
          wine_name: string
          vintage?: string
          region: string
          price_range?: string
          reasoning: string
          confidence?: number
        }>
        general_recommendations: Array<{
          grape_variety: string
          regions: string[]
          wine_style: string
          characteristics: string[]
          reasoning: string
        }>
      }
    }>
    overall_recommendations: Array<{
      category: string
      recommendation: string
      reasoning: string
    }>
  }
}

export default function WineChatPage() {
  // State
  const [version, setVersion] = useState('')
  const [lastUpdated, setLastUpdated] = useState('')
  const [query, setQuery] = useState('')
  const [wineResponse, setWineResponse] = useState<WineAnalysisResponse | null>(null)
  const [menuResponse, setMenuResponse] = useState<MenuAnalysisResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [currentStage, setCurrentStage] = useState<AnalysisStage>('parsing_query')
  const [progress, setProgress] = useState(0)
  const [showCamera, setShowCamera] = useState(false)
  const [analysisType, setAnalysisType] = useState<'text' | 'image'>('text')
  const [appMode, setAppMode] = useState<AppMode>('wine')
  const [searchHistory, setSearchHistory] = useState<HistoryItem[]>([])
  const [useMock, setUseMock] = useState(() => {
    return process.env.NEXT_PUBLIC_USE_MOCK === "true";
  });

  const showMockToggle = process.env.NEXT_PUBLIC_SHOW_MOCK_TOGGLE === "true";

  // Get current response based on active mode
  const getCurrentResponse = () => {
    return appMode === 'wine' ? wineResponse : menuResponse
  }

  // Load search history from sessionStorage
  useEffect(() => {
    const savedHistory = sessionStorage.getItem('wineSearchHistory')
    if (savedHistory) {
      try {
        const parsed = JSON.parse(savedHistory).map((item: HistoryItem & { timestamp: string }) => ({
          ...item,
          timestamp: new Date(item.timestamp)
        }))
        setSearchHistory(parsed)
      } catch (err) {
        console.error('Failed to load search history:', err)
      }
    }
  }, [])

  // Fetch version and last updated time
  useEffect(() => {
    const fetchMetadata = async () => {
      try {
        const baseUrl = process.env.NEXT_PUBLIC_API_URL
        console.log('Fetching metadata from:', `${baseUrl}/meta`)
        
        const res = await fetch(`${baseUrl}/meta`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
          signal: AbortSignal.timeout(5000) // 5 second timeout
        })
        
        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`)
        }
        
        const data = await res.json()
        console.log('Metadata response:', data)
        setVersion(data.version || '')
        setLastUpdated(data.last_updated || '')
      } catch (err) {
        console.error('Failed to fetch metadata', err)
        // Set fallback values to prevent UI issues
        setVersion('3.2.0')
        setLastUpdated('unknown')
      }
    }

    fetchMetadata()
  }, [])

  // Simulate progress stages for text analysis
  const simulateProgress = async () => {
    const stages: AnalysisStage[] = ['parsing_query', 'gathering_info', 'aggregating_results', 'analyzing_ai', 'finalizing_results']
    
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
    const stages: AnalysisStage[] = ['processing_image', 'extracting_info', 'gathering_additional_data', 'analyzing_ai', 'finalizing_results']
    
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

  // Wine-specific handlers
  const handleWineSearch = async () => {
    if (!query.trim()) return
    setLoading(true)
    setWineResponse(null)
    setProgress(0)
    setAnalysisType('text')

    try {
      // Start progress simulation
      const progressPromise = simulateProgress()
      
      const baseUrl = process.env.NEXT_PUBLIC_API_URL
      const res = await fetch(`${baseUrl}/analyze-wine`, {
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
      setWineResponse(result);
  
      // Save to history and clear query if successful
      if (result.status === 'success') {
        saveToHistory(result, 'wine', query)
        setQuery('');
      }

    } catch (err) {
      console.error('Error calling API:', err)
      setWineResponse({
        status: 'error',
        error: 'Failed to fetch analysis.'
      })
    } finally {
      setLoading(false)
      setProgress(0)
    }
  }

  const handleWineImageCapture = async (imageData: string) => {
    setShowCamera(false)
    setLoading(true)
    setWineResponse(null)
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
      setWineResponse(result)
      
      // Save to history if successful
      if (result.status === 'success') {
        saveToHistory(result, 'wine', 'Wine Label Photo')
      }
      
    } catch (err) {
      console.error('Error analyzing image:', err)
      setWineResponse({
        status: 'error',
        error: 'Failed to analyze wine from image. Please try again or enter the wine name manually.'
      })
    } finally {
      setLoading(false)
      setProgress(0)
    }
  }

  // Menu-specific handlers
  const handleFoodTextSearch = async () => {
    if (!query.trim()) return
    setLoading(true)
    setMenuResponse(null)
    setProgress(0)
    setAnalysisType('text')

    try {
      // Start progress simulation
      const progressPromise = simulateProgress()
      
      const baseUrl = process.env.NEXT_PUBLIC_API_URL
      const res = await fetch(`${baseUrl}/analyze-food-text`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          input: { food_description: query },
          context: {
            model: process.env.NEXT_PUBLIC_GEMINI_MODEL,
            timestamp: new Date().toISOString(),
            use_mock: useMock,
          }
        })
      })
      
      // Wait for both progress and API response
      const [data] = await Promise.all([res.json(), progressPromise])
      setMenuResponse(data)

      // Save to history and clear query if successful
      if (data.status === 'success') {
        saveToHistory(data, 'menu', query)
        setQuery('')
      }

    } catch (err) {
      console.error('Error calling food analysis API:', err)
      setMenuResponse({
        status: 'error',
        error: 'Failed to analyze food description.'
      })
    } finally {
      setLoading(false)
      setProgress(0)
    }
  }

  const handleMenuImageCapture = async (imageData: string) => {
    setShowCamera(false)
    setLoading(true)
    setMenuResponse(null)
    setProgress(0)
    setAnalysisType('image')
    
    try {
      // Simulate progress for menu image analysis
      const progressPromise = simulateImageProgress()
      
      // Convert base64 to blob for upload
      const response = await fetch(imageData)
      const blob = await response.blob()
      const file = new File([blob], 'menu_image.jpg', { type: 'image/jpeg' })
      
      // Prepare form data
      const formData = new FormData()
      formData.append('file', file)
      formData.append('context', JSON.stringify({
        model: process.env.NEXT_PUBLIC_GEMINI_MODEL || 'gemini-2.5-flash',
        user_id: 'demo-user',
        timestamp: new Date().toISOString(),
        use_mock: useMock,
      }))
      
      const baseUrl = process.env.NEXT_PUBLIC_API_URL
      const res = await fetch(`${baseUrl}/analyze-menu-image`, {
        method: 'POST',
        body: formData
      })
      
      // Wait for both progress and API response
      const [data] = await Promise.all([res.json(), progressPromise])
      setMenuResponse(data)
      
      // Save to history
      if (data.status === 'success') {
        saveToHistory(data, 'menu', 'Menu Analysis')
      }
      
    } catch (err) {
      console.error('Error analyzing menu image:', err)
      setMenuResponse({
        status: 'error',
        error: 'Failed to analyze menu image. Please try again.'
      })
    } finally {
      setLoading(false)
      setProgress(0)
    }
  }

  // History management
  const saveToHistory = (result: WineAnalysisResponse & { wine_recommendations?: { menu_items?: unknown[] } }, type: AppMode, query: string) => {
    const historyItem: HistoryItem = {
      id: Date.now().toString(),
      timestamp: new Date(),
      type,
      query,
      preview: type === 'wine' 
        ? `${'wine' in result ? result.wine : 'Wine analysis'}`
        : `${result.wine_recommendations?.menu_items?.length || 0} menu items found`,
      result
    }

    const updatedHistory = [historyItem, ...searchHistory].slice(0, 10) // Keep last 10
    setSearchHistory(updatedHistory)
    sessionStorage.setItem('wineSearchHistory', JSON.stringify(updatedHistory))
  }

  const handleSelectHistory = (item: HistoryItem) => {
    if (item.type === 'wine') {
      setWineResponse(item.result as WineAnalysisResponse)
    } else {
      setMenuResponse(item.result as MenuAnalysisResponse)
    }
    setAppMode(item.type)
  }
  
  const handleModeChange = (mode: AppMode) => {
    // Simply switch modes - results are preserved per mode
    setAppMode(mode)
  }

  const handleClearHistory = async () => {
    try {
      // Clear all frontend state and storage
      setSearchHistory([])
      setWineResponse(null)
      setMenuResponse(null)
      setQuery('')
      
      // Clear all browser storage
      sessionStorage.removeItem('wineSearchHistory')
      
      // Clear any other potential localStorage items (if any exist)
      try {
        const keysToRemove = []
        for (let i = 0; i < localStorage.length; i++) {
          const key = localStorage.key(i)
          if (key && (key.includes('wine') || key.includes('menu') || key.includes('search'))) {
            keysToRemove.push(key)
          }
        }
        keysToRemove.forEach(key => localStorage.removeItem(key))
        
        if (keysToRemove.length > 0) {
          console.log(`Cleared ${keysToRemove.length} localStorage items:`, keysToRemove)
        }
      } catch (storageError) {
        console.warn('Failed to clear localStorage:', storageError)
      }
      
      // Clear backend cache
      const baseUrl = process.env.NEXT_PUBLIC_API_URL
      const response = await fetch(`${baseUrl}/clear-cache`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      })
      
      const result = await response.json()
      console.log('Backend cache clearing result:', result)
      
      if (result.status === 'success') {
        console.log(`Successfully cleared ALL cache:`)
        console.log(`  • Frontend: Search history and current results cleared`)
        console.log(`  • Backend: ${result.files_cleared} cached files from categories: ${result.categories_cleared?.join(', ') || 'none'}`)
      } else if (result.status === 'disabled') {
        console.log('Frontend cache cleared. Backend cache clearing is disabled in production mode')
      } else {
        console.warn('Frontend cache cleared. Backend cache clearing failed:', result.message)
      }
    } catch (error) {
      console.error('Failed to clear backend cache:', error)
      console.log('Frontend cache was still cleared successfully')
    }
  }

  // Mode-specific unified handlers
  const handleSearch = () => {
    if (appMode === 'wine') {
      handleWineSearch()
    } else {
      handleFoodTextSearch()
    }
  }

  const handleImageCapture = (imageData: string) => {
    if (appMode === 'wine') {
      handleWineImageCapture(imageData)
    } else {
      handleMenuImageCapture(imageData)
    }
  }

  // UI handlers
  const handleCameraClick = () => {
    setShowCamera(!showCamera)
  }

  const handleCameraClose = () => {
    setShowCamera(false)
  }

  // Dynamic placeholders and button text based on mode
  const getPlaceholder = () => {
    if (appMode === 'wine') {
      return 'e.g. Opus One 2015'
    } else {
      return 'Describe dish or take menu photo'
    }
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
        <p className="text-center text-zinc-400">
          {appMode === 'wine' 
            ? 'Explore wine profiles with intelligent analyzer'
            : 'Find perfect wine pairings for your menu'
          }
        </p>

        {/* Search with integrated mode toggle and history */}
        <div className="w-full max-w-4xl space-y-2">
          <div className="flex items-center justify-end">
            <SearchHistory 
              history={searchHistory}
              onSelectHistory={handleSelectHistory}
              onClearHistory={handleClearHistory}
            />
          </div>
          
          <SearchInputWithButton
            value={query}
            onChange={setQuery}
            onSubmit={handleSearch}
            onCameraClick={handleCameraClick}
            loading={loading}
            placeholder={getPlaceholder()}
            currentMode={appMode}
            onModeChange={handleModeChange}
          />
        </div>

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

        {getCurrentResponse()?.status === 'error' && (
          <div className="bg-red-950 border border-red-700 p-3 rounded-md text-center text-red-400 text-sm break-words mt-4">
            {(getCurrentResponse() as { error?: string })?.error || "An unexpected error occurred. Please try again."}
          </div>
        )}
        
        {getCurrentResponse()?.status === 'success' && (
          <>
            {appMode === 'wine' ? (
              <ResultCard response={getCurrentResponse() as WineAnalysisResponse} />
            ) : (
              <MenuResultCard result={getCurrentResponse() as MenuAnalysisResponse} />
            )}
          </>
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
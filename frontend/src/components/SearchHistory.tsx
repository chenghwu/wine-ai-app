import React, { useState, useEffect, useRef } from 'react'
import { Clock, Wine, UtensilsCrossed } from 'lucide-react'
import { AppMode } from './ModeToggle'
import { WineAnalysisResponse } from '../types/WineAnalysisResponse'

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
    menu_items?: unknown[]
    overall_recommendations?: unknown[]
  }
  [key: string]: unknown
}

export interface HistoryItem {
  id: string
  timestamp: Date
  type: AppMode
  query: string
  preview: string
  result: WineAnalysisResponse | MenuAnalysisResponse
}

interface SearchHistoryProps {
  history: HistoryItem[]
  onSelectHistory: (item: HistoryItem) => void
  onClearHistory: () => Promise<void>
}

export function SearchHistory({ history, onSelectHistory, onClearHistory }: SearchHistoryProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [isClearing, setIsClearing] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const formatTimeAgo = (date: Date) => {
    const now = new Date()
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60))
    
    if (diffInMinutes < 1) return 'just now'
    if (diffInMinutes === 1) return '1 min ago'
    if (diffInMinutes < 60) return `${diffInMinutes} min ago`
    
    const diffInHours = Math.floor(diffInMinutes / 60)
    if (diffInHours === 1) return '1 hour ago'
    if (diffInHours < 24) return `${diffInHours} hours ago`
    
    return date.toLocaleDateString()
  }

  const handleSelectItem = (item: HistoryItem) => {
    onSelectHistory(item)
    setIsOpen(false)
  }

  const handleClearAll = async () => {
    setIsClearing(true)
    try {
      await onClearHistory()
      setIsOpen(false) // Close dropdown after clearing
    } catch (error) {
      console.error('Failed to clear history:', error)
    } finally {
      setIsClearing(false)
    }
  }

  if (history.length === 0) {
    return null
  }

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 text-sm text-zinc-400 hover:text-white transition-colors"
      >
        <Clock size={16} />
        Recent ({history.length})
        <span className={`transition-transform ${isOpen ? 'rotate-180' : ''}`}>
          ▼
        </span>
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 bg-zinc-800 border border-zinc-700 rounded-lg shadow-lg z-50 max-h-96 overflow-y-auto">
          <div className="p-3 border-b border-zinc-700 flex items-center justify-between">
            <h3 className="text-sm font-medium text-white">Recent Searches</h3>
            <button
              onClick={handleClearAll}
              disabled={isClearing}
              className="text-xs text-zinc-400 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isClearing ? 'Clearing...' : 'Clear all'}
            </button>
          </div>

          <div className="py-2">
            {history.map((item) => (
              <button
                key={item.id}
                onClick={() => handleSelectItem(item)}
                className="w-full px-3 py-3 text-left hover:bg-zinc-700 transition-colors border-b border-zinc-800 last:border-b-0"
              >
                <div className="flex items-start gap-3">
                  <div className="mt-0.5">
                    {item.type === 'wine' ? (
                      <Wine size={16} className="text-rose-400" />
                    ) : (
                      <UtensilsCrossed size={16} className="text-orange-400" />
                    )}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium text-white truncate">
                      {item.query}
                    </div>
                    <div className="text-xs text-zinc-400 truncate">
                      {item.preview}
                    </div>
                    <div className="text-xs text-zinc-500 mt-1">
                      {formatTimeAgo(item.timestamp)}
                    </div>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
'use client'

import { Camera, Wine, UtensilsCrossed } from 'lucide-react'
import { AppMode } from './ModeToggle'

interface Props {
  value: string
  onChange: (value: string) => void
  onSubmit: () => void
  onCameraClick: () => void
  loading: boolean
  placeholder?: string
  buttonText?: string
  currentMode: AppMode
  onModeChange: (mode: AppMode) => void
}

export function SearchInputWithButton({ 
  value, 
  onChange, 
  onSubmit, 
  onCameraClick, 
  loading, 
  placeholder = "e.g. Opus One 2015",
  buttonText = "Analyze",
  currentMode,
  onModeChange
}: Props) {
  return (
    <div className="relative w-full">
      <div className="w-full bg-zinc-800 rounded-lg border border-zinc-700 flex flex-col">
        {/* Input Field Row */}
        <div className="flex items-center">
          <input
            type="text"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder={placeholder}
            className="flex-1 px-4 py-3 bg-transparent text-white placeholder-zinc-500 focus:outline-none"
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !loading) {
                onSubmit()
              }
            }}
          />
        </div>

        {/* Mode Toggle and Action Buttons Row */}
        <div className="flex items-center justify-between border-zinc-700 px-2 py-2">
          {/* Mode Toggle Container */}
          <div className="flex bg-zinc-600 rounded-lg overflow-hidden">
            <button
              onClick={() => onModeChange('wine')}
              className={`flex items-center gap-1 px-3 py-1 text-sm font-medium transition-all ${
                currentMode === 'wine'
                  ? 'bg-rose-800 text-white'
                  : 'text-zinc-300 hover:text-white hover:bg-zinc-700'
              }`}
            >
              <Wine size={12} />
              Wine
            </button>
            
            <button
              onClick={() => onModeChange('menu')}
              className={`flex items-center gap-1 px-3 py-1 text-sm font-medium transition-all ${
                currentMode === 'menu'
                  ? 'bg-rose-800 text-white'
                  : 'text-zinc-300 hover:text-white hover:bg-zinc-700'
              }`}
            >
              <UtensilsCrossed size={12} />
              Menu
            </button>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-1">
            <button
              onClick={onCameraClick}
              disabled={loading}
              className="px-2 py-1 rounded-lg bg-zinc-600 hover:bg-zinc-700 text-zinc-300 disabled:opacity-50 flex items-center justify-center"
              title="Take photo"
            >
              <Camera size={16} />
            </button>
            <button
              onClick={onSubmit}
              disabled={loading}
              className="px-4 py-1 rounded-lg bg-rose-800 hover:bg-rose-900 text-sm font-medium disabled:opacity-50 text-white"
            >
              Analyze
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
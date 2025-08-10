import React from 'react'
import { Wine, UtensilsCrossed } from 'lucide-react'

export type AppMode = 'wine' | 'menu'

interface ModeToggleProps {
  currentMode: AppMode
  onModeChange: (mode: AppMode) => void
}

export function ModeToggle({ currentMode, onModeChange }: ModeToggleProps) {
  return (
    <div className="flex bg-zinc-800 rounded-lg border border-zinc-700 overflow-hidden">
      <button
        onClick={() => onModeChange('wine')}
        className={`flex items-center gap-1 px-3 py-1.5 text-xs font-medium transition-all border-r border-zinc-700 ${
          currentMode === 'wine'
            ? 'bg-rose-800 text-white'
            : 'text-zinc-400 hover:text-white hover:bg-zinc-700'
        }`}
      >
        <Wine size={12} />
        Wine
      </button>
      
      <button
        onClick={() => onModeChange('menu')}
        className={`flex items-center gap-1 px-3 py-1.5 text-xs font-medium transition-all ${
          currentMode === 'menu'
            ? 'bg-rose-800 text-white'
            : 'text-zinc-400 hover:text-white hover:bg-zinc-700'
        }`}
      >
        <UtensilsCrossed size={12} />
        Menu
      </button>
    </div>
  )
}
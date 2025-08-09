'use client'

interface ProgressIndicatorProps {
  isVisible: boolean
  currentStage: string
  progress: number // 0-100
}

export function ProgressIndicator({ isVisible, currentStage, progress }: ProgressIndicatorProps) {
  if (!isVisible) return null

  return (
    <div className="w-full mt-3 px-4 py-3 bg-zinc-900 rounded-lg border border-zinc-800">
      {/* Progress bar */}
      <div className="w-full bg-zinc-800 rounded-full h-2 mb-2">
        <div
          className="bg-slate-700 h-2 rounded-full transition-all duration-500 ease-out"
          style={{ width: `${progress}%` }}
        />
      </div>
      
      {/* Current stage text */}
      <div className="flex items-center justify-between text-sm">
        <span className="text-zinc-300">{currentStage}</span>
        <span className="text-zinc-500">{progress}%</span>
      </div>
    </div>
  )
}
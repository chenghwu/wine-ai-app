'use client'

interface MockToggleButtonProps {
  useMock: boolean
  onToggle: () => void
}

export function MockToggleButton({ useMock, onToggle }: MockToggleButtonProps) {
  return (
    <div className="fixed bottom-4 right-4 z-50 text-sm text-zinc-400">
      <button
        onClick={onToggle}
        aria-checked={useMock}
        role="switch"
        className={`px-4 py-2 rounded-lg border transition-colors duration-200 font-medium ${
          useMock
            ? 'bg-zinc-800 border-zinc-700 text-rose-500 hover:bg-zinc-700'
            : 'bg-zinc-800 border-zinc-700 text-green-500 hover:bg-zinc-700'
        }`}
      >
        {useMock ? 'Using Mock Response' : 'Real API Enabled'}
      </button>
    </div>
  )
}
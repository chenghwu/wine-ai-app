'use client'

interface Props {
  value: string
  onChange: (value: string) => void
  onSubmit: () => void
  loading: boolean
}

export function SearchInputWithButton({ value, onChange, onSubmit, loading }: Props) {
  return (
    <div className="relative w-full">
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="e.g. Opus One 2015"
        className="w-full px-4 py-2 pr-24 rounded-lg bg-zinc-800 text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-rose-800"
      />
      <button
        onClick={onSubmit}
        disabled={loading}
        className="absolute right-1 top-1 bottom-1 px-4 rounded-lg bg-rose-800 hover:bg-rose-900 text-sm font-semibold disabled:opacity-50"
      >
        {loading ? 'Analyzing...' : 'Analyze'}
      </button>
    </div>
  )
}
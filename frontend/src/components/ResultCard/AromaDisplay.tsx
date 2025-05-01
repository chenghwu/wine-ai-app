interface AromaDisplayProps {
  aroma: Record<string, string[]>
}

export function AromaDisplay({ aroma }: AromaDisplayProps) {
  const clusters = Object.entries(aroma || {})

  if (clusters.length === 0) return null

  return (
    <div className="text-sm text-zinc-300 grid gap-y-1 overflow-x-hidden">
      {clusters.map(([cluster, descriptors], index) => (
        <div
          key={cluster}
          className="grid grid-cols-[auto_1fr] items-start gap-x-1 min-w-0"
        >
          {/* Label only appears on the first row */}
          <div className="text-zinc-400 font-medium whitespace-nowrap">
            {index === 0 ? 'Aroma:' : <span className="invisible">Aroma:</span>}
          </div>

          <div className="text-zinc-300 leading-snug break-words">
            {/* Pill inline with descriptors */}
            <span className="bg-slate-700 text-zinc-200 text-xs font-semibold px-1.5 py-0.5 rounded-full text-[clamp(9px,2.5vw,12px)] inline-block mr-1">
              {cluster}
            </span>
            {descriptors.join(', ')}
          </div>
        </div>
      ))}
    </div>
  )
}
'use client'

interface CriteriaPillsProps {
  criteriaMet: string[];
}

export function CriteriaPills({ criteriaMet }: CriteriaPillsProps) {
  return (
    <div className="flex flex-wrap items-center gap-1">
        <span className="text-zinc-400 font-medium whitespace-nowrap">Criteria Met:</span>
        {['Balance', 'Length', 'Intensity', 'Complexity'].map((criterion) => (
          <span
            key={criterion}
            className={`px-1.5 py-0.5 text-[clamp(9px,2.5vw,12px)] rounded-full whitespace-nowrap ${
              criteriaMet.includes(criterion)
                ? 'bg-green-900 text-white'
                : 'bg-transparent border border-zinc-600 text-zinc-400'
            }`}
          >
            {criterion}
        </span>
        ))}
    </div>
  )
}
// Render SAT score section
'use client'

import { SATResult } from '@/types/WineAnalysisResponse'
import { QualityBarInline } from './QualityBarInline'

interface SATSectionProps {
  sat: SATResult
}

export function SATSection({ sat }: SATSectionProps) {
    return (
      <li className="mt-4 border-t border-zinc-700 pt-4 space-y-1 w-full max-w-full overflow-hidden">
        <h3 className="text-sm font-semibold text-zinc-400 uppercase tracking-wide mb-3">
          WSET Systematic Approach to Tasting Conclusion
        </h3>

        <p className="h-6">
          <span className="text-zinc-400 font-medium">Criteria Met:</span>{' '}
          <span className="text-zinc-200">{sat.criteria.join(', ')}</span>
        </p>
        {/*
        <p>
          <span className="text-zinc-400 font-medium">Score:</span>{' '}
          <span className="text-zinc-200">{sat.score} / 4</span>
        </p>
        */}
        <div className="flex items-center gap-2 text-sm w-full max-w-xs">
          <span className="text-zinc-400 font-medium">Quality:</span>{' '}
          <QualityBarInline quality={sat.quality} />
        </div>
        <p>
          <span className="text-zinc-400 font-medium">Clusters:</span>{' '}
          <span className="text-zinc-200">{sat.clusters.join(', ')}</span>
        </p>
        <p>
          <span className="text-zinc-400 font-medium">Descriptors:</span>{' '}
          <span className="text-zinc-200">{sat.descriptors.join(', ')}</span>
        </p>
      </li>
    )
  }  
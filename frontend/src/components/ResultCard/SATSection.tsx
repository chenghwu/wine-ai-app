// Render SAT score section
'use client'

import { SATResult } from '@/types/WineAnalysisResponse'
import { QualityBarInline } from './QualityBarInline'
import { CriteriaPills } from './CriteriaPills'

interface SATSectionProps {
  sat: SATResult
}

export function SATSection({ sat }: SATSectionProps) {
    return (
      <section className="mt-4 border-t border-zinc-700 pt-4 w-full">
        <h3 className="text-sm font-semibold text-zinc-400 uppercase tracking-wide mb-3">
          WSET Systematic Approach to Tasting Conclusion
        </h3>

        <div className="flex flex-col gap-2 text-sm">
          {/* Criteria Met */}
          <CriteriaPills criteriaMet={sat.criteria} />

          {/*
          <div className="flex">
            <span className="text-zinc-400 font-medium mr-1">Score:</span>
            <span className="text-zinc-200">{sat.score} / 4</span>
          </div>
          */}

          {/* Quality Bar */}
          <div className="flex items-center gap-1">
            <span className="text-zinc-400 font-medium">Quality:</span>
            <QualityBarInline quality={sat.quality} />
          </div>

          {/* Clusters */}
          <div className="flex">
            <span className="text-zinc-400 font-medium mr-1">Clusters:</span>
            <span className="text-zinc-200">{sat.clusters.join(', ')}</span>
          </div>

          {/* Descriptors */}
          <div className="flex">
            <span className="text-zinc-400 font-medium mr-1">Descriptors:</span>
            <span className="text-zinc-200">{sat.descriptors.join(', ')}</span>
          </div>
        </div>
      </section>
    )
  }  
'use client'

import { InfoItem } from './InfoItem'
import { SATSection } from './SATSection'
import { ReferenceSources } from './ReferenceSources'
import { FoodPairingSection } from './FoodPairingSection'
import { WineAnalysisResponse } from '@/types/WineAnalysisResponse'

interface ResultCardProps {
  response: WineAnalysisResponse
}

export function ResultCard({ response }: ResultCardProps) {
  if (response.status !== 'success') return null

  return (
    <div className="mt-2 w-full bg-zinc-800 border border-zinc-700 p-4 rounded-xl shadow-md space-y-4">
      <h2 className="text-xl font-semibold text-white">
        Analysis Result - {response.wine}
      </h2>

      <ul className="space-y-2 text-sm">
        <InfoItem label="Region" value={response.region} />
        <InfoItem label="Grape Varieties" value={response.grape_varieties} />
        <InfoItem label="Appearance" value={response.appearance} />
        <InfoItem label="Nose" value={response.nose} />
        <InfoItem label="Palate" value={response.palate} />
        <InfoItem label="Aging Potential" value={response.aging} />
        <InfoItem label="Avg. Price" value={response.average_price} />
        <InfoItem label="Analysis" value={response.analysis} />

        {response.sat && <SATSection sat={response.sat} />}
        <FoodPairingSection wineName={response.wine} />
        <ReferenceSources sources={response.reference_source} />
      </ul>
    </div>
  )
}
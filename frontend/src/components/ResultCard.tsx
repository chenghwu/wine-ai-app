'use client'

import React from 'react'
import { WineAnalysisResponse } from '@/types/WineAnalysisResponse'
import { SATResult } from '@/types/WineAnalysisResponse'

interface ResultCardProps {
  response: WineAnalysisResponse
}

export function ResultCard({ response }: ResultCardProps) {
  if (response.status !== 'success') return null

  return (
    <div className="mt-3 w-full max-w-2xl bg-zinc-800 border border-zinc-700 p-6 rounded-xl shadow-md space-y-4">
      <h2 className="text-xl font-semibold text-white">Analysis Result - {response.wine}</h2>
      <ul className="space-y-2 text-sm text-zinc-300">
        <InfoItem label="Grape Varieties" value={response.grape_varieties} />
        <InfoItem label="Appearance" value={response.appearance} />
        <InfoItem label="Nose" value={response.nose} />
        <InfoItem label="Palate" value={response.palate} />
        <InfoItem label="Aging Potential" value={response.aging} />
        <InfoItem label="Avg. Price" value={response.average_price} />
        <InfoItem label="Analysis" value={response.analysis} />

        {response.sat && <SATSection sat={response.sat} />}
        <ReferenceSources sources={response.reference_source} />
      </ul>
    </div>
  )
}

// Reusable component for displaying label-value pairs
function InfoItem({ label, value }: { label: string; value: string }) {
  return (
    <li>
      <span className="text-zinc-400 font-medium">{label}:</span>{' '}
      <span className="text-zinc-200">{value}</span>
    </li>
  )
}

// Render SAT score section
function SATSection({ sat }: { sat: SATResult }) {
  return (
    <li className="mt-4 space-y-1">
      <p>
        <span className="text-zinc-400 font-medium">Score:</span>{' '}
        <span className="text-zinc-200">{sat.score} / 4</span>
      </p>
      <p>
        <span className="text-zinc-400 font-medium">Quality:</span>{' '}
        <span className="text-zinc-200">{sat.quality}</span>
      </p>
      <p>
        <span className="text-zinc-400 font-medium">Criteria Met:</span>{' '}
        <span className="text-zinc-200">{sat.criteria.join(', ')}</span>
      </p>
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

// Render Reference Sources cleanly
function ReferenceSources({ sources }: { sources: string | string[] | undefined }) {
  const items = Array.isArray(sources) ? sources : sources ? [sources] : []

  return (
    <li className="mt-4">
      {items.length > 0 ? (
        <div>
          <span className="text-zinc-400 font-medium">Reference Source:</span>
          <ul className="list-disc list-inside text-sm text-zinc-300 mt-1 space-y-1">
            {items.map((src, index) => {
              const isUrl = src.trim().startsWith('http')
              return (
                <li key={index}>
                  {isUrl ? (
                    <a
                      href={src}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-400 hover:underline break-words"
                    >
                      {src}
                    </a>
                  ) : (
                    <span>{src}</span>
                  )}
                </li>
              )
            })}
          </ul>
        </div>
      ) : (
        <p className="text-zinc-500 italic">No sources provided.</p>
      )}
    </li>
  )
}
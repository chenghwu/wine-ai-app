'use client'

import React from 'react'
import { WineAnalysisResponse } from '@/types/WineAnalysisResponse'

interface ResultCardProps {
  response: WineAnalysisResponse
}

export function ResultCard({ response }: ResultCardProps) {
  if (response.status !== 'success') return null

  return (
    <div className="mt-8 w-full max-w-2xl bg-gray-800 p-4 rounded shadow">
      <h2 className="text-lg font-semibold mb-2">Analysis Result:</h2>
      <ul className="text-sm space-y-2">
        <InfoItem label="Wine" value={response.wine} />
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
      <strong>{label}:</strong> {value}
    </li>
  )
}

// Render SAT score section
function SATSection({ sat }: NonNullable<WineAnalysisResponse['sat']>) {
  return (
    <li className="mt-4 space-y-2">
      <p><strong>Score:</strong> {sat.score}</p>
      <p><strong>Quality:</strong> {sat.quality}</p>
      <p><strong>Criteria Met:</strong> {sat.criteria.join(', ')}</p>
      <p><strong>Clusters:</strong> {sat.matched_clusters.join(', ')}</p>
      <p><strong>Descriptors:</strong> {sat.matched_descriptors.join(', ')}</p>
    </li>
  )
}

// Render Reference Sources cleanly
function ReferenceSources({ sources }: { sources: string | string[] | undefined }) {
  const items = Array.isArray(sources) ? sources : sources ? [sources] : []

  return (
    <li>
      {items.length > 0 ? (
        <div>
          <strong>Reference Source:</strong>
          <ul className="list-disc list-inside text-sm text-gray-300 mt-1 space-y-1">
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
        <p className="text-gray-400 italic">No sources provided.</p>
      )}
    </li>
  )
}
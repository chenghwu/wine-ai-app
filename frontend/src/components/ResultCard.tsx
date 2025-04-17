'use client'

import React from 'react'
import { WineAnalysisResponse } from '@/types/WineAnalysisResponse'

interface ResultCardProps {
  response: WineAnalysisResponse
}

export function ResultCard({ response }: ResultCardProps) {
  // Early return if response is an error
  if (response.status !== 'success') return null

  return (
    <div className="mt-8 w-full max-w-2xl bg-gray-800 p-4 rounded shadow">
      <h2 className="text-lg font-semibold mb-2">Analysis Result:</h2>
      <ul className="text-sm space-y-2">
        <li><strong>Wine:</strong> {response.wine}</li>
        <li><strong>Appearance:</strong> {response.appearance}</li>
        <li><strong>Nose:</strong> {response.nose}</li>
        <li><strong>Palate:</strong> {response.palate}</li>
        <li><strong>Quality:</strong> {response.quality}</li>
        <li><strong>Aging Potential:</strong> {response.aging}</li>
        <li><strong>Avg. Price:</strong> {response.average_price}</li>
        {typeof response.analysis === 'string' ? (
            <p>{response.analysis}</p>
          ) : (
            <div className="mt-4 space-y-2">
              <p><strong>Score:</strong> {response.analysis.score}</p>
              <p><strong>Structured Quality:</strong> {response.analysis.structured_quality}</p>
              <p><strong>Criteria:</strong> {response.analysis.criteria.join(", ")}</p>
              <p><strong>Matched Clusters:</strong> {response.analysis.matched_clusters.join(", ")}</p>
              <p><strong>Descriptors:</strong> {response.analysis.matched_descriptors.join(", ")}</p>
            </div>
          )}
        <li>
          <strong>Reference Source:</strong>
          {response.reference_source?.length ? (
            <ul className="list-disc list-inside ml-4">
              {response.reference_source.map((src, index) => (
                <li key={index}>{src}</li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-400 italic">No sources provided.</p>
          )}
        </li>
      </ul>
    </div>
  )
}
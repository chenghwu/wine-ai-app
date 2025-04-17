'use client'

import React from 'react'

interface SubmitButtonProps {
  onClick: () => void
  loading: boolean
}

export function SubmitButton({ onClick, loading }: SubmitButtonProps) {
  return (
    <button
      className="mt-3 px-6 py-2 bg-green-600 hover:bg-green-700 rounded"
      onClick={onClick}
      disabled={loading}
    >
      {loading ? 'Analyzing...' : 'Analyze'}
    </button>
  )
}

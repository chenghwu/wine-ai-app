'use client'

import React from 'react'

interface SearchInputProps {
  value: string
  onChange: (value: string) => void
}

export function SearchInput({ value, onChange }: SearchInputProps) {
  return (
    <input
      className="w-full p-3 rounded text-black bg-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-green-500"
      type="text"
      placeholder="e.g. Opus One 2015"
      value={value}
      onChange={(e) => onChange(e.target.value)}
    />
  )
}

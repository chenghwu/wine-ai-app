// Reusable component for displaying label-value pairs
'use client'

interface InfoItemProps {
  label: string
  value: string
}

export function InfoItem({ label, value }: InfoItemProps) {
    return (
      <li>
        <span className="text-zinc-400 font-medium mr-1">{label}:</span>
        <span className="text-zinc-200">{value}</span>
      </li>
    )
  }
// Render Reference Sources cleanly
'use client'

import { useState } from 'react'
import { getDomainFromUrl } from '@/utils/url';

interface ReferenceSourcesProps {
  sources: string | string[] | undefined
}

export function ReferenceSources({ sources }: ReferenceSourcesProps) {
  const [collapsed, setCollapsed] = useState(true);
  const items = Array.isArray(sources) ? sources : sources ? [sources] : []

  return (
    <li className="mt-4 border-t border-zinc-700 pt-4 w-full max-w-full overflow-hidden">
      {items.length > 0 ? (
        <div>
          <h3 className="text-sm font-semibold text-zinc-400 uppercase tracking-wide mb-3">
            Reference Source
          </h3>
          <ul className="text-sm text-zinc-400 mt-1 space-y-1">
            {items.slice(0, collapsed ? 7 : items.length).map((src, index) => {
              const isUrl = src.trim().startsWith('http')
              return (
                <li key={index}>
                  {isUrl ? (
                    <a
                      href={src}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-zinc-400 hover:text-white underline break-words"
                    >
                      {getDomainFromUrl(src)}
                    </a>
                  ) : (
                    <span>{src}</span>
                  )}
                </li>
              );
            })}
          </ul>
          {items.length > 7 && (
            <button
              onClick={() => setCollapsed(!collapsed)}
              className="text-zinc-400 hover:text-white flex items-center gap-0.5 text-xs mt-1"            >
              {collapsed ? 'Show More' : 'Show Less'}
              {collapsed ? (
                <svg
                  className="w-3 h-3"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
                </svg>
              ) : (
                <svg
                  className="w-3 h-3"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 15l7-7 7 7" />
                </svg>
              )}
            </button>
          )}
        </div>
      ) : (
        <p className="text-zinc-500 italic">No sources provided.</p>
      )}
    </li>
  )
}
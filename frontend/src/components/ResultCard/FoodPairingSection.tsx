'use client'

import { useEffect, useState } from 'react'
import { FoodPairingResponse, FoodPairingCategory } from '@/types/FoodPairingResponse'
import FoodPairingCategoryIcons from '@/components/FoodPairingCategoryIcons'
import FoodPairingModal from '@/components/FoodPairing/FoodPairingModal'
import { Button } from '@/components/ui/button'

interface Props {
  wineName: string
}

export function FoodPairingSection({ wineName }: Props) {
  const [data, setData] = useState<FoodPairingResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [open, setOpen] = useState(false)
  const [selected, setSelected] = useState<FoodPairingCategory | null>(null)

  const fetchFoodPairings = async () => {
    setLoading(true)
    setError(null)
    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL
      const res = await fetch(`${baseUrl}/pair-food?wine_name=${encodeURIComponent(wineName)}`)
      const json = await res.json()
      if (json.status === 'paired' || json.status === 'cached') {
        setData(json.output)
      } else {
        setError(json.error || 'Unknown error')
      }
    } catch (err) {
      setError('Failed to fetch food pairings.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mt-5 border-t boder-zinc-700 pt-4">
      <h3 className="text-white text-lg font-semibold mb-2">Food Pairing Recommendations</h3>

      {!data ? (
        <>
          <Button onClick={fetchFoodPairings} disabled={loading}>
            {loading ? 'Loading...' : 'Show Food Pairing Recommendations'}
          </Button>
          {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
        </>
      ) : (
        <>
          <FoodPairingCategoryIcons
            categories={data.pairings.map((c) => c.category)}
            onCategoryClick={(category) => {
              const found = data.pairings.find((c) => c.category === category)
              if (found) {
                setSelected(found)
                setOpen(true)
              }
            }}
          />
          {selected && (
            <FoodPairingModal
              open={open}
              onClose={() => setOpen(false)}
              category={selected.category}
              examples={selected.examples}
            />
          )}
        </>
      )}
    </div>
  )
}
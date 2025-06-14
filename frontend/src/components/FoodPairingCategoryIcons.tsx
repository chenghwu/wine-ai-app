import { Card } from "@/components/ui/card"
import { foodIconMap } from "@/components/FoodPairing/iconMap"

type FoodPairingCategoryIconsProps = {
  categories: { label: string; iconKey: string }[]
  onCategoryClick: (category: string) => void
}

function IconWrapper({ children }: { children: React.ReactNode }) {
  return (
    <div className="w-7 h-7 flex items-center justify-center">
      {children}
    </div>
  )
}

export default function FoodPairingCategoryIcons({
  categories,
  onCategoryClick,
}: FoodPairingCategoryIconsProps) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
      {categories.map(({ label, iconKey }) => {
        const Icon = foodIconMap[iconKey] || foodIconMap.Other

        return (
          <Card
            key={label}
            onClick={() => onCategoryClick(label)}
            className="flex flex-col items-center justify-center p-3 border hover:shadow-lg hover:border-primary transition cursor-pointer rounded-xl bg-white dark:bg-zinc-700"
          >
            <IconWrapper>
              <Icon className="w-full h-full text-zinc-400 dark:text-zinc-400" />
            </IconWrapper>
            <span className="text-sm font-medium text-center text-zinc-200 dark:text-zinc-200">
              {label}
            </span>
          </Card>
        )
      })}
    </div>
  )
}
import { FC } from "react";
import { Card } from "@/components/ui/card";
import { Drumstick, Beef, Fish, Carrot, Utensils } from "lucide-react";

type FoodPairingCategoryIconsProps = {
  categories: string[];
  onCategoryClick: (category: string) => void;
};

const categoryIcons: Record<string, React.ReactNode> = {
  Beef: <Beef className="h-8 w-8 text-gray-400" />,
  Poultry: <Drumstick className="h-8 w-8 text-gray-400" />,
  Salmon: <Fish className="h-8 w-8 text-gray-400" />,
  Vegetables: <Carrot className="h-8 w-8 text-green-400" />,
  Default: <Utensils className="h-8 w-8 text-gray-400" />,
};

const FoodPairingCategoryIcons: FC<FoodPairingCategoryIconsProps> = ({ categories, onCategoryClick }) => {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
    {categories.map((category) => (
        <Card
        key={category}
        onClick={() => onCategoryClick(category)}
        className="flex flex-col items-center justify-center p-3 border hover:shadow-lg hover:border-primary transition cursor-pointer rounded-xl bg-white dark:bg-zinc-900"
        >
        {categoryIcons[category] ?? categoryIcons.Default}
        <span className="mt-1 text-sm font-medium text-center text-zinc-800 dark:text-zinc-100">
            {category}
        </span>
        </Card>
    ))}
    </div>
  );
};

export default FoodPairingCategoryIcons;
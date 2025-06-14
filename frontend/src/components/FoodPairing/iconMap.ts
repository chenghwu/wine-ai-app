// src/components/FoodPairing/iconMap.ts
import BeefIcon from "@/assets/icons/food/beef.svg";
import PorkIcon from "@/assets/icons/food/pork.svg";
import LambIcon from "@/assets/icons/food/lamb.svg";
import GameIcon from "@/assets/icons/food/game.svg";
import PoultryIcon from "@/assets/icons/food/poultry.svg";
import FishIcon from "@/assets/icons/food/fish.svg";
import ShellfishIcon from "@/assets/icons/food/shellfish.svg";
import SeafoodIcon from "@/assets/icons/food/seafood.svg";
import VegetablesIcon from "@/assets/icons/food/vegetables.svg";
import CheeseIcon from "@/assets/icons/food/cheese.svg";
import GrainsIcon from "@/assets/icons/food/grains.svg";
import BreadIcon from "@/assets/icons/food/bread.svg";
import LegumesIcon from "@/assets/icons/food/legumes.svg";
import FruitsIcon from "@/assets/icons/food/fruits.svg";
import NutsIcon from "@/assets/icons/food/nuts.svg";
import DessertIcon from "@/assets/icons/food/dessert.svg";
import SpicyIcon from "@/assets/icons/food/spicy.svg";
import SaucesIcon from "@/assets/icons/food/sauces.svg";
import OtherIcon from "@/assets/icons/food/other.svg";

export const foodIconMap: Record<string, React.FC<React.SVGProps<SVGSVGElement>>> = {
  Beef: BeefIcon,
  Pork: PorkIcon,
  Lamb: LambIcon,
  Game: GameIcon,
  Poultry: PoultryIcon,
  Fish: FishIcon,
  Shellfish: ShellfishIcon,
  Seafood: SeafoodIcon,
  Vegetables: VegetablesIcon,
  Cheese: CheeseIcon,
  "Grains & Pasta": GrainsIcon,
  "Bread & Pastry": BreadIcon,
  Legumes: LegumesIcon,
  Fruits: FruitsIcon,
  Nuts: NutsIcon,
  Dessert: DessertIcon,
  "Spicy / Asian": SpicyIcon,
  "Sauces & Condiments": SaucesIcon,
  Other: OtherIcon,
};
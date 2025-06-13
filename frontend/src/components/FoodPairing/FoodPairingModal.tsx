import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { FoodPairingExample } from "@/types/FoodPairingResponse";
import { ScrollArea } from "@/components/ui/scroll-area";

type Props = {
  open: boolean;
  onClose: () => void;
  category: string;
  examples: FoodPairingExample[];
};

export default function FoodPairingModal({ open, onClose, category, examples }: Props) {
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="text-xl font-bold">{category}</DialogTitle>
        </DialogHeader>
        <ScrollArea className="max-h-[400px] pr-2">
          <ul className="space-y-3 mt-1">
            {examples.map((item, idx) => (
              <li key={idx}>
                <p className="font-semibold text-base">{item.food}</p>
                <p className="text-sm text-muted-foreground">{item.reason}</p>
              </li>
            ))}
          </ul>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  );
}
// Render quality bar
'use client'

interface QualityBarInlineProps {
  quality: string
}

export function QualityBarInline({ quality }: QualityBarInlineProps) {
    const levels = ["Poor", "Acceptable", "Good", "Very Good", "Outstanding"];
    const currentIndex = levels.findIndex((q) => q.toLowerCase() === quality.toLowerCase());
  
    return (
      <div className="w-full max-w-xs">  
        {/* Segmented Bar */}
        <div className="flex w-full h-3 rounded overflow-hidden">
          {levels.map((_, index) => (
            <div
            key={index}
            className={`flex-1 ${
                index <= currentIndex ? 'bg-rose-800' : 'bg-zinc-700'
              } ${index < levels.length - 1 ? 'border-r border-zinc-800' : ''}`}
            />
        ))}
        </div>
  
        {/* Labels below each segment */}
        <div className="flex justify-between w-full text-[9px] text-zinc-400 mt-1">
          {levels.map((label) => (
            <span
            key={label}
            className="w-[20%] text-center leading-snug whitespace-nowrap overflow-hidden text-ellipsis"
            >
              {label}
            </span>
          ))}
        </div>
      </div>
    );
  }
import React, { useState } from 'react'
import { Wine, Utensils, DollarSign, ChefHat, ChevronDown, ChevronRight } from 'lucide-react'

interface MenuItem {
  dish_name: string
  category?: string
  price?: string
  protein?: string
  cooking_method?: string
  cuisine_type?: string
  description?: string
}

interface WineRecommendation {
  wine_name: string
  grape_variety?: string
  vintage?: string
  region: string
  price_range?: string
  reasoning: string
  confidence?: number
}

interface GeneralRecommendation {
  grape_variety: string
  regions: string[]
  wine_style: string
  characteristics: string[]
  reasoning: string
}

interface MenuItemWithPairings {
  dish: MenuItem
  wine_pairings: {
    specific_recommendations: WineRecommendation[]
    general_recommendations: GeneralRecommendation[]
  }
}

interface MenuAnalysisResponse {
  status: string
  restaurant_info?: {
    name?: string
    cuisine_style: string
    confidence: number
  }
  menu_analysis?: {
    items_found: number
    extraction_method: string
  }
  wine_recommendations?: {
    menu_items: MenuItemWithPairings[]
    overall_recommendations: Array<{
      category: string
      recommendation: string
      reasoning: string
    }>
  }
}

interface MenuResultCardProps {
  result: MenuAnalysisResponse
}

export function MenuResultCard({ result }: MenuResultCardProps) {
  const { restaurant_info, wine_recommendations } = result
  const [expandedItems, setExpandedItems] = useState<Set<number>>(new Set())
  
  const toggleExpanded = (index: number) => {
    setExpandedItems(prev => {
      const newSet = new Set(prev)
      if (newSet.has(index)) {
        newSet.delete(index)
      } else {
        newSet.add(index)
      }
      return newSet
    })
  }
  
  // Safety check for required data
  if (!restaurant_info || !wine_recommendations) {
    return (
      <div className="w-full max-w-4xl mx-auto bg-zinc-900 rounded-lg border border-zinc-700 p-3 mt-2">
        <div className="text-center text-zinc-400">
          No menu analysis data available
        </div>
      </div>
    )
  }

  return (
    <div className="w-full max-w-4xl mx-auto bg-zinc-900 rounded-lg border border-zinc-700 p-3 mt-2">
      {/* Restaurant Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <Utensils className="text-orange-400" size={24} />
          <div>
            <h2 className="text-xl font-bold text-white">
              {restaurant_info.name || 'Menu Analysis'}
            </h2>
            <p className="text-zinc-400 text-sm">
              {restaurant_info.cuisine_style} • {result.menu_analysis?.items_found || 0} items found
            </p>
          </div>
        </div>
      </div>

      {/* Menu Items with Wine Pairings */}
      <div className="space-y-6">
        {wine_recommendations.menu_items.map((item, index) => {
          const isExpanded = expandedItems.has(index)
          return (
            <div key={index} className="border border-zinc-800 rounded-lg">
              {/* Clickable Header */}
              <div 
                className="p-3 cursor-pointer hover:bg-zinc-800/50 transition-colors"
                onClick={() => toggleExpanded(index)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {isExpanded ? (
                      <ChevronDown className="text-zinc-400" size={20} />
                    ) : (
                      <ChevronRight className="text-zinc-400" size={20} />
                    )}
                    <h3 className="text-lg font-semibold text-white">
                      {item.dish.dish_name}
                    </h3>
                  </div>
                  {item.dish.price && (
                    <span className="text-rose-400 font-medium flex items-center gap-1">
                      <DollarSign size={16} />
                      {item.dish.price.replace('$', '')}
                    </span>
                  )}
                </div>
              </div>
              
              {/* Collapsible Content */}
              {isExpanded && (
                <div className="px-3 pb-3">
                  {/* Dish Details */}
                  <div className="mb-4">
                    <div className="flex flex-wrap gap-2 text-sm text-zinc-400 mb-2">
                      {item.dish.protein && (
                        <span className="bg-zinc-800 px-2 py-1 rounded flex items-center gap-1">
                          <ChefHat size={14} />
                          {item.dish.protein}
                        </span>
                      )}
                      {item.dish.cooking_method && (
                        <span className="bg-zinc-800 px-2 py-1 rounded">
                          {item.dish.cooking_method}
                        </span>
                      )}
                      {item.dish.cuisine_type && (
                        <span className="bg-zinc-800 px-2 py-1 rounded">
                          {item.dish.cuisine_type}
                        </span>
                      )}
                    </div>
                    
                    {item.dish.description && (
                      <p className="text-zinc-300 text-sm">{item.dish.description}</p>
                    )}
                  </div>

                  {/* Wine Recommendations */}
                  <div className="space-y-4">
                    {/* Specific Wine Recommendations */}
                    {item.wine_pairings.specific_recommendations.length > 0 && (
                      <div>
                        <h4 className="text-white font-medium mb-3 flex items-center gap-2">
                          <Wine className="text-rose-400" size={18} />
                          Recommended Wines
                        </h4>
                        <div className="space-y-3">
                          {item.wine_pairings.specific_recommendations.map((wine, wineIndex) => (
                            <div key={wineIndex} className="bg-zinc-800/50 rounded-lg p-4">
                              <div className="flex items-start justify-between mb-2">
                                <div>
                                  <h5 className="text-white font-medium">
                                    {wine.vintage && `${wine.vintage} `}{wine.wine_name}
                                  </h5>
                                  <div className="flex items-center gap-2 text-zinc-400 text-sm">
                                    {wine.grape_variety && (
                                      <span className="bg-zinc-600 px-2 py-0.5 rounded text-xs">
                                        {wine.grape_variety}
                                      </span>
                                    )}
                                    <span>{wine.region}</span>
                                  </div>
                                </div>
                                {wine.price_range && (
                                  <span className="text-zinc-300 text-sm bg-zinc-700 px-2 py-1 rounded">
                                    {wine.price_range}
                                  </span>
                                )}
                              </div>
                              <p className="text-zinc-300 text-sm italic">
                                &ldquo;{wine.reasoning}&rdquo;
                              </p>
                              {wine.confidence && (
                                <div className="mt-2">
                                  <div className="flex items-center gap-2">
                                    <span className="text-xs text-zinc-500">Confidence:</span>
                                    <div className="w-16 bg-zinc-700 rounded-full h-2">
                                      <div 
                                        className="bg-rose-500 h-2 rounded-full" 
                                        style={{ width: `${wine.confidence * 100}%` }}
                                      />
                                    </div>
                                    <span className="text-xs text-zinc-400">
                                      {Math.round(wine.confidence * 100)}%
                                    </span>
                                  </div>
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* General Wine Categories */}
                    {item.wine_pairings.general_recommendations.length > 0 && (
                      <div>
                        <h4 className="text-white font-medium mb-3 flex items-center gap-2">
                          <Wine className="text-orange-400" size={18} />
                          General Wine Categories
                        </h4>
                        <div className="space-y-3">
                          {item.wine_pairings.general_recommendations.map((category, catIndex) => (
                            <div key={catIndex} className="bg-zinc-800/30 rounded-lg p-4">
                              <h5 className="text-white font-medium mb-1">
                                {category.grape_variety}
                              </h5>
                              <p className="text-zinc-400 text-sm mb-2">
                                <strong>Style:</strong> {category.wine_style}
                              </p>
                              <p className="text-zinc-400 text-sm mb-2">
                                <strong>Regions:</strong> {category.regions.join(' / ')}
                              </p>
                              {category.characteristics.length > 0 && (
                                <p className="text-zinc-400 text-sm mb-2">
                                  <strong>Look for:</strong> {category.characteristics.join(', ')}
                                </p>
                              )}
                              <p className="text-zinc-300 text-sm italic">
                                &ldquo;{category.reasoning}&rdquo;
                              </p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* Overall Recommendations */}
      {wine_recommendations.overall_recommendations?.length > 0 && (
        <div className="mt-6 p-4 bg-zinc-800/30 rounded-lg">
          <h4 className="text-white font-medium mb-3">Overall Wine List Suggestions</h4>
          <div className="space-y-2">
            {wine_recommendations.overall_recommendations.map((rec, index) => (
              <div key={index}>
                <h5 className="text-zinc-300 font-medium">{rec.category}</h5>
                <p className="text-zinc-400 text-sm">{rec.recommendation}</p>
                <p className="text-zinc-500 text-xs italic">{rec.reasoning}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
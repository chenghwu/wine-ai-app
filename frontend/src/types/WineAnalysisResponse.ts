export interface SATResult {
    score: number
    quality: string
    criteria: string[]
    aroma: Record<string, string[]>
    clusters?: string[]     // optional for now
    descriptors?: string[]  // optional for now
  }

export type WineAnalysisResponse =
  | {
      status: 'success'
      wine: string
      grape_varieties: string
      appearance: string
      nose: string
      palate: string
      aging: string
      average_price: string
      analysis: string 
      sat: SATResult
      reference_source: string[]
    }
  | {
      status: 'error'
      error: string
    }
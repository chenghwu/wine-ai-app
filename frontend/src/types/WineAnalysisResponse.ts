export interface SATResult {
    score: number
    quality: string
    criteria: string[]
    clusters: string[]
    descriptors: string[]
  }

export type WineAnalysisResponse =
  | {
      status: 'success'
      wine: string
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
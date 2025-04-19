export type SATResultDetails = {
    score: number
    quality: string
    criteria: string[]
    matched_clusters: string[]
    matched_descriptors: string[]
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
      sat: SATResultDetails
      reference_source: string[]
    }
  | {
      status: 'error'
      error: string
    }
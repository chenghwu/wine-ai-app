export type WineAnalysisDetails = {
    score: number
    structured_quality: string
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
      quality: string
      aging: string
      average_price: string
      analysis: WineAnalysisDetails
      reference_source: string[]
    }
  | {
      status: 'error'
      error: string
    }
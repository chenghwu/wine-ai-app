export type AnalysisStage = 
  | 'parsing_query'
  | 'gathering_info'
  | 'aggregating_results'
  | 'analyzing_ai'
  | 'finalizing_results'
  | 'processing_image'
  | 'extracting_info'
  | 'gathering_additional_data'
  | 'completed'

export type AnalysisType = 'text' | 'image'

export interface ProgressUpdate {
  stage: AnalysisStage
  progress: number
  message: string
  analysisType: AnalysisType
}

export const PROGRESS_MESSAGES: Record<AnalysisStage, { text: string, image: string }> = {
  parsing_query: {
    text: 'Parsing your wine query...',
    image: 'Processing image...'
  },
  gathering_info: {
    text: 'Gathering wine information...',
    image: 'Extracting wine information...'
  },
  aggregating_results: {
    text: 'Aggregating search results...',
    image: 'Gathering additional data...'
  },
  analyzing_ai: {
    text: 'Analyzing with Wine Intelligence...',
    image: 'Analyzing with Wine Intelligence...'
  },
  finalizing_results: {
    text: 'Finalizing recommendations...',
    image: 'Finalizing analysis...'
  },
  processing_image: {
    text: 'Processing image...',
    image: 'Processing image...'
  },
  extracting_info: {
    text: 'Extracting wine information...',
    image: 'Extracting wine information...'
  },
  gathering_additional_data: {
    text: 'Gathering additional data...',
    image: 'Gathering additional data...'
  },
  completed: {
    text: 'Analysis completed',
    image: 'Analysis completed'
  }
}

export const STAGE_PROGRESS: Record<AnalysisStage, number> = {
  parsing_query: 10,
  gathering_info: 25,
  aggregating_results: 40,
  analyzing_ai: 55,
  finalizing_results: 60,
  processing_image: 20,
  extracting_info: 40,
  gathering_additional_data: 50,
  completed: 100
}
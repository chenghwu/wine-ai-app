export interface FoodPairingExample {
    food: string
    reason: string
  }
  
  export interface FoodPairingCategory {
    category: string
    examples: FoodPairingExample[]
  }
  
  export interface FoodPairingResponse {
    wine: string
    pairings: FoodPairingCategory[]
  }
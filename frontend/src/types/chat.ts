export interface MessageContent {
  type: 'text' | 'image_url' | 'html'
  text?: string
  image_url?: { url: string }
}

export interface StepInfo {
  step: number
  status: 'pending' | 'running' | 'completed' | 'error'
  message: string
  data?: any
}

export interface HotelData {
  name: string
  url?: string | null
  image?: string | null
  price: string
  score: string
  location: string
  facilities: string[]
}

export interface ToolCall {
  name: string
  arguments: Record<string, any>
  result?: string
  error?: string
  server_name?: string
}

export interface MapData {
  itinerary: any[]
  city: string
  coordsMap: Record<string, number[]>
  mapId: string
}

export interface Message {
  role: 'user' | 'assistant'
  content: MessageContent[]
  reasoning?: string
  isStreaming?: boolean
  toolCalls?: ToolCall[]
  hotelSteps?: StepInfo[]
  hotelsData?: HotelData[]
  travelSteps?: StepInfo[]
  mapData?: MapData
  routesData?: Record<string, any>
}

export interface TravelPlanDraft {
  destination: string | null
  origin: string | null
  start_date: string | null
  end_date: string | null
  people: number | null
  attractions: string[]
}

export interface ChatSession {
  id: string
  title: string
  messages: Message[]
  createdAt: number
  updatedAt: number
  draft?: TravelPlanDraft | null
  currentPlan?: any
  currentPlanMsgIndex?: number | null
}

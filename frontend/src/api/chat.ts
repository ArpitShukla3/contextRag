import { request } from './client'

export type MessageRole = 'user' | 'assistant'

export interface ChatMessage {
  id: string
  role: MessageRole
  content: string
  /** Sources cited by the assistant answer, if any. */
  sources: Array<{ document_id: string; chunk_index: number }> | null
}

export interface Conversation {
  id: string
  title: string
  created_at: string
  updated_at: string
}

export interface ConversationDetail extends Conversation {
  messages: ChatMessage[]
}

export interface ConversationListResponse {
  items: Conversation[]
  total: number
}

/** List conversations for the current user. */
export function listConversations(): Promise<ConversationListResponse> {
  return request<ConversationListResponse>('/api/chat/conversations')
}

/** Fetch a single conversation and its messages. */
export function getConversation(id: string): Promise<ConversationDetail> {
  return request<ConversationDetail>(`/api/chat/conversations/${id}`)
}

/** Create a new empty conversation. */
export function createConversation(title = 'New conversation'): Promise<Conversation> {
  return request<Conversation>('/api/chat/conversations', {
    method: 'POST',
    body: { title },
  })
}
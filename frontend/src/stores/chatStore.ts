import { create } from 'zustand'

interface ConversationState {
  /** Id of the active conversation, if one has been selected. */
  activeConversationId: string | null
  setActiveConversationId: (id: string | null) => void
  clearActiveConversation: () => void
}

export const useConversationStore = create<ConversationState>((set) => ({
  activeConversationId: null,
  setActiveConversationId: (id) => set({ activeConversationId: id }),
  clearActiveConversation: () => set({ activeConversationId: null }),
}))
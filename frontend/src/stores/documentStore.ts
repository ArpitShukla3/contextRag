import { create } from 'zustand'

interface DocumentState {
  /** Id of the document the user is currently working with. */
  selectedDocumentId: number | null
  setSelectedDocumentId: (id: number | null) => void
  clearSelectedDocument: () => void
}

export const useDocumentStore = create<DocumentState>((set) => ({
  selectedDocumentId: null,
  setSelectedDocumentId: (id) => set({ selectedDocumentId: id }),
  clearSelectedDocument: () => set({ selectedDocumentId: null }),
}))
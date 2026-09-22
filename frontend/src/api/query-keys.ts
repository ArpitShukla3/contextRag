export const documentKeys = {
  all: ['documents'] as const,
  detail: (id: number) => [...documentKeys.all, id] as const,
  chunks: (id: number) => [...documentKeys.detail(id), 'chunks'] as const,
}
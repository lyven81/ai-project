import type { Story } from '../types'

const BASE = '/api'

export async function fetchStory(): Promise<Story> {
  const res = await fetch(`${BASE}/story`)
  if (!res.ok) throw new Error('Failed to fetch story')
  return res.json()
}

export async function fetchCoverImage(): Promise<string> {
  const res = await fetch(`${BASE}/story/cover`)
  if (!res.ok) throw new Error('Failed to fetch cover')
  const data = await res.json()
  return data.image
}

export async function generatePageImage(
  pageNumber: number,
  optionId: string,
): Promise<string> {
  const res = await fetch(`${BASE}/generate/page-image`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ page_number: pageNumber, option_id: optionId }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error((err as any).detail || 'Failed to generate illustration')
  }
  const data = await res.json()
  return data.image
}

export async function editImage(imageBase64: string, instruction: string): Promise<string> {
  const res = await fetch(`${BASE}/edit/image`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image_base64: imageBase64, instruction }),
  })
  if (!res.ok) throw new Error('Failed to edit image')
  const data = await res.json()
  return data.image
}

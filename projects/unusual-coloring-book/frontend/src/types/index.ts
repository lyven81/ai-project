export interface PageOption {
  id: string       // 'a', 'b', 'c'
  preview: string
  story_text: string
}

export interface StoryPage {
  page: number
  chapter_title: string
  options: PageOption[]
}

export interface Story {
  id: string
  title: string
  subtitle: string
  total_pages: number
  pages: StoryPage[]
}

/** One completed page — option chosen, image generated. */
export interface ActivePage {
  page: number
  chapter_title: string
  option_id: string
  story_text: string
  image: string
}

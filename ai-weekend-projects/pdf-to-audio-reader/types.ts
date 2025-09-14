export type ContentType = 'heading_1' | 'heading_2' | 'paragraph' | 'image_description' | 'list_item';

export interface ParsedContent {
  type: ContentType;
  content: string;
}

// FIX: Added missing Bookmark interface, which was causing a compilation error in BookmarkPanel.tsx.
// The properties are inferred from its usage within the BookmarkPanel component.
export interface Bookmark {
  id: number;
  note: string;
  previewText: string;
  chapterIndex: number;
}

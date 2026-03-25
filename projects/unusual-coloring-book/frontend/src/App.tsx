import { useState, useEffect } from 'react'
import CoverPage from './pages/CoverPage'
import OptionSelector from './pages/OptionSelector'
import ColoringBook from './pages/ColoringBook'
import { fetchStory, fetchCoverImage, generatePageImage } from './utils/api'
import type { Story, ActivePage } from './types'

type AppState = 'loading' | 'cover' | 'choosing' | 'generating' | 'coloring'

export default function App() {
  const [appState, setAppState] = useState<AppState>('loading')
  const [story, setStory] = useState<Story | null>(null)
  const [coverImage, setCoverImage] = useState('')
  const [loadError, setLoadError] = useState('')

  // Page-by-page progress
  const [completedPages, setCompletedPages] = useState<ActivePage[]>([])
  const [choosingPage, setChoosingPage] = useState(1)       // which page we are choosing an option for
  const [viewingIndex, setViewingIndex] = useState(-1)       // -1 = cover
  const [generateError, setGenerateError] = useState('')

  // Load story data + cover image on mount (in parallel)
  useEffect(() => {
    Promise.all([fetchStory(), fetchCoverImage()])
      .then(([s, img]) => {
        setStory(s)
        setCoverImage(img)
        setAppState('cover')
      })
      .catch(() => setLoadError('Could not reach the backend. Is it running?'))
  }, [])

  const handleCoverClick = () => {
    setChoosingPage(1)
    setAppState('choosing')
  }

  const handleOptionSelect = async (optionId: string) => {
    if (!story) return
    setAppState('generating')
    setGenerateError('')

    const pageData = story.pages.find(p => p.page === choosingPage)
    if (!pageData) return

    const option = pageData.options.find(o => o.id === optionId)
    if (!option) return

    try {
      const image = await generatePageImage(choosingPage, optionId)
      const newPage: ActivePage = {
        page: choosingPage,
        chapter_title: pageData.chapter_title,
        option_id: optionId,
        story_text: option.story_text,
        image,
      }
      setCompletedPages(prev => [...prev, newPage])
      setViewingIndex(choosingPage - 1)  // jump to this new page
      setAppState('coloring')
    } catch (e) {
      setGenerateError(e instanceof Error ? e.message : 'Generation failed. Try again.')
      setAppState('choosing')
    }
  }

  const handleNextPage = () => {
    if (!story) return
    const nextPage = completedPages.length + 1
    if (nextPage > story.total_pages) return
    setChoosingPage(nextPage)
    setAppState('choosing')
  }

  const resetToStart = () => {
    setCompletedPages([])
    setChoosingPage(1)
    setViewingIndex(-1)
    setGenerateError('')
    setAppState('cover')
  }

  // ---- Render ----

  if (appState === 'loading') {
    return (
      <div style={loadingWrap}>
        <div style={spinner} />
        <p style={loadingText}>Preparing your coloring book...</p>
        {loadError && <p style={errorText}>{loadError}</p>}
      </div>
    )
  }

  if (appState === 'cover') {
    return <CoverPage coverImage={coverImage} story={story!} onStart={handleCoverClick} />
  }

  if ((appState === 'choosing' || appState === 'generating') && story) {
    const pageData = story.pages.find(p => p.page === choosingPage)!
    return (
      <OptionSelector
        pageData={pageData}
        totalPages={story.total_pages}
        isGenerating={appState === 'generating'}
        error={generateError}
        onSelect={handleOptionSelect}
        onBack={completedPages.length === 0 ? resetToStart : () => {
          setViewingIndex(completedPages.length - 1)
          setAppState('coloring')
        }}
      />
    )
  }

  if (appState === 'coloring' && story) {
    return (
      <ColoringBook
        story={story}
        completedPages={completedPages}
        viewingIndex={viewingIndex}
        onViewingIndexChange={setViewingIndex}
        onNextPage={handleNextPage}
        onBack={resetToStart}
      />
    )
  }

  return null
}

const loadingWrap: React.CSSProperties = {
  display: 'flex', flexDirection: 'column',
  alignItems: 'center', justifyContent: 'center',
  minHeight: '100vh', gap: 20,
  background: '#FFFDF7',
}
const spinner: React.CSSProperties = {
  width: 52, height: 52, borderRadius: '50%',
  border: '5px solid #FFD93D', borderTopColor: '#FF6B6B',
  animation: 'spin 1s linear infinite',
}
const loadingText: React.CSSProperties = {
  fontFamily: "'Fredoka One', cursive",
  fontSize: '1.3rem', color: '#2D3436',
}
const errorText: React.CSSProperties = {
  fontFamily: "'Nunito', sans-serif",
  fontSize: '0.95rem', color: '#c0392b',
  background: '#fff0f0', padding: '12px 20px',
  borderRadius: 12, maxWidth: 400, textAlign: 'center',
}

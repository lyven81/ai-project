import type { StoryPage } from '../types'

interface Props {
  pageData: StoryPage
  totalPages: number
  isGenerating: boolean
  error: string
  onSelect: (optionId: string) => void
  onBack: () => void
}

const OPTION_COLORS = ['#FF6B6B', '#4ECDC4', '#C3B1E1']
const OPTION_LABELS = ['A', 'B', 'C']

export default function OptionSelector({
  pageData,
  totalPages,
  isGenerating,
  error,
  onSelect,
  onBack,
}: Props) {
  return (
    <div style={styles.page}>
      <button style={styles.backBtn} onClick={onBack} disabled={isGenerating}>
        ← Back
      </button>

      {/* Header */}
      <div style={styles.header}>
        <div style={styles.pageTag}>
          Page {pageData.page} of {totalPages}
        </div>
        <h2 style={styles.chapterTitle}>{pageData.chapter_title}</h2>
        <p style={styles.prompt}>Choose how this part of the story unfolds:</p>
      </div>

      {/* Options */}
      <div style={styles.options}>
        {pageData.options.map((opt, i) => (
          <button
            key={opt.id}
            style={{
              ...styles.card,
              opacity: isGenerating ? 0.6 : 1,
              cursor: isGenerating ? 'not-allowed' : 'pointer',
            }}
            onClick={() => !isGenerating && onSelect(opt.id)}
            disabled={isGenerating}
          >
            <div style={{ ...styles.badge, background: OPTION_COLORS[i] }}>
              {OPTION_LABELS[i]}
            </div>
            <div style={styles.cardBody}>
              <p style={styles.preview}>{opt.preview}</p>
              <p style={styles.storyText}>{opt.story_text}</p>
            </div>
            {!isGenerating && (
              <span style={{ ...styles.choosePill, background: OPTION_COLORS[i] }}>
                Choose →
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Generating state */}
      {isGenerating && (
        <div style={styles.generatingBox}>
          <div style={styles.spinner} />
          <span style={styles.generatingText}>Drawing your illustration...</span>
        </div>
      )}

      {error && <p style={styles.error}>{error}</p>}
    </div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  page: {
    minHeight: '100vh',
    background: '#FFFDF7',
    maxWidth: 680,
    margin: '0 auto',
    padding: '32px 24px 60px',
  },
  backBtn: {
    background: 'none',
    border: '2px solid #ddd',
    borderRadius: 50,
    padding: '8px 20px',
    fontSize: '0.9rem',
    color: '#666',
    cursor: 'pointer',
    marginBottom: 32,
    fontFamily: "'Nunito', sans-serif",
  },
  header: {
    marginBottom: 32,
  },
  pageTag: {
    fontFamily: "'Fredoka One', cursive",
    fontSize: '0.85rem',
    color: '#aaa',
    textTransform: 'uppercase',
    letterSpacing: '0.08em',
    marginBottom: 10,
  },
  chapterTitle: {
    fontFamily: "'Fredoka One', cursive",
    fontSize: 'clamp(1.5rem, 5vw, 2.2rem)',
    color: '#2D3436',
    marginBottom: 10,
  },
  prompt: {
    fontFamily: "'Nunito', sans-serif",
    fontSize: '1rem',
    color: '#777',
  },
  options: {
    display: 'flex',
    flexDirection: 'column',
    gap: 18,
  },
  card: {
    background: '#fff',
    borderRadius: 20,
    padding: '22px 24px',
    boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
    border: '2px solid transparent',
    display: 'flex',
    alignItems: 'flex-start',
    gap: 18,
    textAlign: 'left',
    transition: 'box-shadow 0.2s, transform 0.15s',
    width: '100%',
  },
  badge: {
    width: 38,
    height: 38,
    borderRadius: '50%',
    color: '#fff',
    fontFamily: "'Fredoka One', cursive",
    fontSize: '1.1rem',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    flexShrink: 0,
  },
  cardBody: {
    flex: 1,
  },
  preview: {
    fontFamily: "'Fredoka One', cursive",
    fontSize: '1rem',
    color: '#2D3436',
    marginBottom: 8,
  },
  storyText: {
    fontFamily: "'Nunito', sans-serif",
    fontSize: '0.93rem',
    color: '#666',
    lineHeight: 1.7,
  },
  choosePill: {
    color: '#fff',
    borderRadius: 50,
    padding: '5px 14px',
    fontSize: '0.82rem',
    fontWeight: 700,
    fontFamily: "'Nunito', sans-serif",
    whiteSpace: 'nowrap',
    flexShrink: 0,
    alignSelf: 'center',
  },
  generatingBox: {
    display: 'flex',
    alignItems: 'center',
    gap: 14,
    marginTop: 28,
    padding: '20px 24px',
    background: '#fff',
    borderRadius: 16,
    boxShadow: '0 2px 12px rgba(0,0,0,0.07)',
  },
  spinner: {
    width: 28,
    height: 28,
    borderRadius: '50%',
    border: '4px solid #FFD93D',
    borderTopColor: '#FF6B6B',
    animation: 'spin 1s linear infinite',
    flexShrink: 0,
  },
  generatingText: {
    fontFamily: "'Nunito', sans-serif",
    fontSize: '1rem',
    color: '#555',
  },
  error: {
    fontFamily: "'Nunito', sans-serif",
    fontSize: '0.9rem',
    color: '#c0392b',
    background: '#fff0f0',
    borderRadius: 10,
    padding: '10px 16px',
    marginTop: 16,
  },
}

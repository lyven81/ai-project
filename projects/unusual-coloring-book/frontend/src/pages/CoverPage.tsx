import type { Story } from '../types'

interface Props {
  coverImage: string
  story: Story
  onStart: () => void
}

function base64ToDataUrl(b64: string) {
  if (b64.startsWith('data:')) return b64
  if (b64.startsWith('PHN2Zy') || b64.includes('svg')) return `data:image/svg+xml;base64,${b64}`
  return `data:image/png;base64,${b64}`
}

export default function CoverPage({ coverImage, story, onStart }: Props) {
  return (
    <div style={styles.page}>
      <div style={styles.inner}>
        {/* Cover image — click to begin */}
        <div style={styles.bookWrap} onClick={onStart} title="Click to begin your story">
          <img
            src={base64ToDataUrl(coverImage)}
            alt={story.title}
            style={styles.coverImg}
          />
          <div style={styles.coverOverlay}>
            <span style={styles.clickHint}>Click to begin your story →</span>
          </div>
        </div>

        {/* Title block */}
        <div style={styles.titleBlock}>
          <h1 style={styles.title}>{story.title}</h1>
          <p style={styles.subtitle}>{story.subtitle}</p>
        </div>

        {/* How it works */}
        <div style={styles.howItWorks}>
          <div style={styles.step}>
            <span style={styles.num}>1</span>
            <span style={styles.stepText}>Pick one of three story paths for each page</span>
          </div>
          <div style={styles.step}>
            <span style={styles.num}>2</span>
            <span style={styles.stepText}>An illustration is drawn just for your choice</span>
          </div>
          <div style={styles.step}>
            <span style={styles.num}>3</span>
            <span style={styles.stepText}>Colour it in, then continue to the next page</span>
          </div>
        </div>

        <button style={styles.startBtn} onClick={onStart}>
          Begin the Story →
        </button>

        <p style={styles.footer}>
          A classic fairy tale · {story.total_pages} pages · Illustrated by Gemini AI
        </p>
      </div>
    </div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  page: {
    minHeight: '100vh',
    background: 'linear-gradient(160deg, #FFFDF7 0%, #FFF3E0 100%)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '40px 24px',
  },
  inner: {
    maxWidth: 560,
    width: '100%',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: 28,
  },
  bookWrap: {
    position: 'relative',
    width: '100%',
    maxWidth: 420,
    cursor: 'pointer',
    borderRadius: 20,
    overflow: 'hidden',
    boxShadow: '0 12px 48px rgba(0,0,0,0.15)',
    transition: 'transform 0.2s, box-shadow 0.2s',
  },
  coverImg: {
    width: '100%',
    display: 'block',
  },
  coverOverlay: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    background: 'linear-gradient(transparent, rgba(0,0,0,0.55))',
    padding: '32px 20px 18px',
    display: 'flex',
    justifyContent: 'center',
  },
  clickHint: {
    color: '#fff',
    fontFamily: "'Nunito', sans-serif",
    fontWeight: 700,
    fontSize: '1rem',
    letterSpacing: '0.02em',
  },
  titleBlock: {
    textAlign: 'center',
  },
  title: {
    fontFamily: "'Fredoka One', cursive",
    fontSize: 'clamp(2rem, 6vw, 2.8rem)',
    color: '#2D3436',
    marginBottom: 8,
  },
  subtitle: {
    fontFamily: "'Nunito', sans-serif",
    fontSize: '1rem',
    color: '#777',
    fontStyle: 'italic',
  },
  howItWorks: {
    background: '#fff',
    borderRadius: 18,
    padding: '20px 28px',
    boxShadow: '0 2px 16px rgba(0,0,0,0.07)',
    width: '100%',
    display: 'flex',
    flexDirection: 'column',
    gap: 14,
  },
  step: {
    display: 'flex',
    alignItems: 'center',
    gap: 14,
  },
  num: {
    width: 32,
    height: 32,
    borderRadius: '50%',
    background: 'linear-gradient(135deg, #FF6B6B, #FFD93D)',
    color: '#fff',
    fontFamily: "'Fredoka One', cursive",
    fontSize: '1rem',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    flexShrink: 0,
  },
  stepText: {
    fontFamily: "'Nunito', sans-serif",
    fontSize: '0.95rem',
    color: '#444',
  },
  startBtn: {
    background: 'linear-gradient(135deg, #FF6B6B, #FFD93D)',
    color: '#fff',
    border: 'none',
    borderRadius: 50,
    padding: '16px 40px',
    fontSize: '1.1rem',
    fontWeight: 700,
    cursor: 'pointer',
    fontFamily: "'Nunito', sans-serif",
    boxShadow: '0 4px 20px rgba(255,107,107,0.35)',
  },
  footer: {
    fontFamily: "'Nunito', sans-serif",
    fontSize: '0.82rem',
    color: '#bbb',
    textAlign: 'center',
  },
}

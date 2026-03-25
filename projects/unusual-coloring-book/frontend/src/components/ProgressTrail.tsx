import { useEffect, useState } from 'react'

const STEPS = [
  { label: 'Building characters', emoji: '🎭' },
  { label: 'Writing the story', emoji: '✍️' },
  { label: 'Drawing illustrations', emoji: '🎨' },
  { label: 'Almost ready', emoji: '✨' },
]

interface Props {
  message?: string
}

export default function ProgressTrail({ message }: Props) {
  const [active, setActive] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setActive(prev => (prev < STEPS.length - 1 ? prev + 1 : prev))
    }, 1800)
    return () => clearInterval(interval)
  }, [])

  return (
    <div style={styles.wrapper}>
      <div style={styles.card}>
        <div style={styles.spinner} />
        <h2 style={styles.title}>Creating your coloring book...</h2>
        <div style={styles.steps}>
          {STEPS.map((step, i) => (
            <div key={i} style={{
              ...styles.step,
              opacity: i <= active ? 1 : 0.3,
              transform: i === active ? 'scale(1.05)' : 'scale(1)',
            }}>
              <span style={styles.emoji}>{step.emoji}</span>
              <span style={{
                ...styles.stepLabel,
                fontWeight: i === active ? 800 : 600,
                color: i === active ? '#2D3436' : '#b0b0b0',
              }}>
                {step.label}
                {i === active && <span style={styles.dots}>...</span>}
              </span>
              {i < active && <span style={styles.check}>✓</span>}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  wrapper: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '60vh',
  },
  card: {
    background: '#fff',
    borderRadius: 24,
    padding: '48px 56px',
    boxShadow: '0 8px 40px rgba(0,0,0,0.10)',
    textAlign: 'center',
    maxWidth: 420,
    width: '100%',
  },
  spinner: {
    width: 56,
    height: 56,
    borderRadius: '50%',
    border: '5px solid #FFD93D',
    borderTopColor: '#FF6B6B',
    animation: 'spin 1s linear infinite',
    margin: '0 auto 28px',
  },
  title: {
    fontFamily: "'Fredoka One', cursive",
    fontSize: '1.5rem',
    color: '#2D3436',
    marginBottom: 32,
  },
  steps: {
    display: 'flex',
    flexDirection: 'column',
    gap: 16,
    textAlign: 'left',
  },
  step: {
    display: 'flex',
    alignItems: 'center',
    gap: 12,
    transition: 'all 0.4s ease',
  },
  emoji: { fontSize: '1.4rem', width: 32 },
  stepLabel: {
    fontFamily: "'Nunito', sans-serif",
    fontSize: '1rem',
    flex: 1,
    transition: 'color 0.3s',
  },
  check: {
    color: '#6BCB77',
    fontWeight: 800,
    fontSize: '1.1rem',
  },
  dots: {
    animation: 'blink 1s step-end infinite',
  },
}

// Inject keyframes
const styleEl = document.createElement('style')
styleEl.textContent = `
  @keyframes spin { to { transform: rotate(360deg); } }
  @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }
`
document.head.appendChild(styleEl)

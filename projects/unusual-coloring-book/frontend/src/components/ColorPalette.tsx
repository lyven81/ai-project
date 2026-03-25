const PALETTE = [
  { name: 'Sunshine Yellow', hex: '#FFD93D' },
  { name: 'Coral Orange',    hex: '#FF6B6B' },
  { name: 'Sky Blue',        hex: '#4ECDC4' },
  { name: 'Mint Green',      hex: '#95E1D3' },
  { name: 'Soft Pink',       hex: '#F8A5C2' },
  { name: 'Lavender',        hex: '#C3B1E1' },
  { name: 'Grass Green',     hex: '#6BCB77' },
  { name: 'Royal Blue',      hex: '#4D96FF' },
  { name: 'Warm Brown',      hex: '#A0522D' },
  { name: 'Sand',            hex: '#F4D03F' },
  { name: 'Lilac',           hex: '#D7BDE2' },
  { name: 'Peach',           hex: '#FFDAB9' },
  { name: 'Cloud White',     hex: '#F8F9FA' },
  { name: 'Storm Grey',      hex: '#95A5A6' },
  { name: 'Midnight',        hex: '#2C3E50' },
  { name: 'Crimson',         hex: '#E74C3C' },
]

interface Props {
  selected: string
  onSelect: (hex: string) => void
}

export default function ColorPalette({ selected, onSelect }: Props) {
  return (
    <div style={styles.wrapper}>
      <div style={styles.label}>Pick a colour</div>
      <div style={styles.grid}>
        {PALETTE.map(c => (
          <button
            key={c.hex}
            title={c.name}
            onClick={() => onSelect(c.hex)}
            style={{
              ...styles.swatch,
              background: c.hex,
              border: selected === c.hex
                ? '3px solid #2D3436'
                : '3px solid transparent',
              transform: selected === c.hex ? 'scale(1.2)' : 'scale(1)',
              boxShadow: selected === c.hex
                ? '0 0 0 2px white, 0 0 0 4px #2D3436'
                : '0 2px 6px rgba(0,0,0,0.15)',
            }}
          />
        ))}
      </div>
      <div style={styles.selectedLabel}>
        <span style={{ background: selected, ...styles.dot }} />
        {PALETTE.find(c => c.hex === selected)?.name ?? selected}
      </div>
    </div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  wrapper: {
    background: '#fff',
    borderRadius: 16,
    padding: '14px 20px',
    boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
  },
  label: {
    fontFamily: "'Fredoka One', cursive",
    fontSize: '1rem',
    color: '#2D3436',
    marginBottom: 10,
  },
  grid: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: 8,
  },
  swatch: {
    width: 32,
    height: 32,
    borderRadius: '50%',
    cursor: 'pointer',
    transition: 'all 0.15s ease',
    padding: 0,
  },
  selectedLabel: {
    display: 'flex',
    alignItems: 'center',
    gap: 8,
    marginTop: 10,
    fontSize: '0.85rem',
    color: '#666',
    fontFamily: "'Nunito', sans-serif",
  },
  dot: {
    display: 'inline-block',
    width: 16,
    height: 16,
    borderRadius: '50%',
    border: '2px solid #ddd',
    flexShrink: 0,
  },
}

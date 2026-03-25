import { useRef, useState } from 'react'
import FloodFillCanvas, { type CanvasHandle } from '../components/FloodFillCanvas'
import ColorPalette from '../components/ColorPalette'
import { editImage } from '../utils/api'
import type { Story, ActivePage } from '../types'
import jsPDF from 'jspdf'

interface Props {
  story: Story
  completedPages: ActivePage[]
  viewingIndex: number        // index into completedPages (-1 = not used here)
  onViewingIndexChange: (i: number) => void
  onNextPage: () => void
  onBack: () => void
}

function base64ToDataUrl(b64: string) {
  if (b64.startsWith('data:')) return b64
  if (b64.startsWith('PHN2Zy') || b64.includes('svg')) return `data:image/svg+xml;base64,${b64}`
  return `data:image/png;base64,${b64}`
}

export default function ColoringBook({
  story,
  completedPages,
  viewingIndex,
  onViewingIndexChange,
  onNextPage,
  onBack,
}: Props) {
  const [selectedColor, setSelectedColor] = useState('#FFD93D')
  const [editInstruction, setEditInstruction] = useState('')
  const [isEditing, setIsEditing] = useState(false)
  const [editedImages, setEditedImages] = useState<Record<number, string>>({})
  const [isExporting, setIsExporting] = useState(false)
  const canvasRef = useRef<CanvasHandle>(null)

  const currentPage = completedPages[viewingIndex]
  const isLastCompleted = viewingIndex === completedPages.length - 1
  const canContinue = isLastCompleted && completedPages.length < story.total_pages

  // Use edited image if available, otherwise original
  const currentImage = currentPage
    ? (editedImages[viewingIndex] ?? currentPage.image)
    : ''

  const handleEditImage = async () => {
    if (!editInstruction.trim() || !currentPage) return
    setIsEditing(true)
    try {
      const updated = await editImage(currentImage, editInstruction)
      setEditedImages(prev => ({ ...prev, [viewingIndex]: updated }))
      setEditInstruction('')
    } catch {
      alert('Could not edit illustration. Try again.')
    } finally {
      setIsEditing(false)
    }
  }

  const handleExport = async () => {
    setIsExporting(true)
    try {
      const pdf = new jsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4' })
      const W = pdf.internal.pageSize.getWidth()
      const H = pdf.internal.pageSize.getHeight()
      const margin = 12

      completedPages.forEach((p, i) => {
        if (i > 0) pdf.addPage()
        pdf.setFillColor(255, 253, 247)
        pdf.rect(0, 0, W, H, 'F')

        const img = editedImages[i] ?? p.image
        try {
          pdf.addImage(base64ToDataUrl(img), 'PNG', margin, margin, W - margin * 2, H * 0.63)
        } catch {}

        const textY = margin + H * 0.63 + 6
        pdf.setFillColor(255, 255, 255)
        pdf.roundedRect(margin, textY, W - margin * 2, H - textY - margin, 6, 6, 'F')

        pdf.setFont('helvetica', 'bold')
        pdf.setFontSize(9)
        pdf.setTextColor(150, 150, 150)
        pdf.text(`Page ${p.page} — ${p.chapter_title}`, margin + 6, textY + 8)

        pdf.setFont('helvetica', 'normal')
        pdf.setFontSize(12)
        pdf.setTextColor(45, 52, 54)
        const lines = pdf.splitTextToSize(p.story_text, W - margin * 2 - 12)
        pdf.text(lines, margin + 6, textY + 16)

        pdf.setFont('helvetica', 'normal')
        pdf.setFontSize(8)
        pdf.setTextColor(180, 180, 180)
        pdf.text('Unusual Coloring Book — Cinderella', W / 2, H - 4, { align: 'center' })
      })

      pdf.save('cinderella-coloring-book.pdf')
    } catch {
      alert('PDF export failed. Try again.')
    } finally {
      setIsExporting(false)
    }
  }

  return (
    <div style={styles.page}>
      {/* Top bar */}
      <div style={styles.topBar}>
        <button style={styles.backBtn} onClick={onBack}>← New Book</button>
        <div style={styles.bookTitle}>{story.title}</div>
        <button
          style={{ ...styles.exportBtn, opacity: completedPages.length === 0 ? 0.5 : 1 }}
          onClick={handleExport}
          disabled={isExporting || completedPages.length === 0}
        >
          {isExporting ? 'Saving...' : '⬇ Export PDF'}
        </button>
      </div>

      <div style={styles.layout}>
        {/* Left: canvas */}
        <div style={styles.canvasCol}>
          <FloodFillCanvas
            ref={canvasRef}
            imageSrc={currentImage}
            selectedColor={selectedColor}
          />

          {/* Page navigation */}
          <div style={styles.pageNav}>
            <button
              style={styles.navBtn}
              onClick={() => onViewingIndexChange(Math.max(0, viewingIndex - 1))}
              disabled={viewingIndex <= 0}
            >← Prev</button>

            <span style={styles.pageLabel}>
              Page {(currentPage?.page) ?? '?'} of {completedPages.length}
              {completedPages.length < story.total_pages && ` (of ${story.total_pages} total)`}
            </span>

            <button
              style={styles.navBtn}
              onClick={() => onViewingIndexChange(Math.min(completedPages.length - 1, viewingIndex + 1))}
              disabled={viewingIndex >= completedPages.length - 1}
            >Next →</button>
          </div>

          {/* Canvas controls */}
          <div style={styles.canvasControls}>
            <button style={styles.controlBtn} onClick={() => canvasRef.current?.undo()}>↩ Undo</button>
            <button style={styles.controlBtn} onClick={() => canvasRef.current?.clear()}>🗑 Clear</button>
          </div>
        </div>

        {/* Right: sidebar */}
        <div style={styles.sidebar}>
          {/* Story text */}
          {currentPage && (
            <div style={styles.storyBox}>
              <div style={styles.pageTag}>Page {currentPage.page} — {currentPage.chapter_title}</div>
              <p style={styles.storyText}>{currentPage.story_text}</p>
            </div>
          )}

          {/* Thumbnail strip */}
          <div style={styles.thumbStrip}>
            <div style={styles.thumbLabel}>Pages</div>
            <div style={styles.thumbRow}>
              {completedPages.map((p, i) => (
                <div
                  key={i}
                  style={{
                    ...styles.thumb,
                    border: viewingIndex === i ? '3px solid #FF6B6B' : '3px solid #eee',
                    backgroundImage: `url(${base64ToDataUrl(editedImages[i] ?? p.image)})`,
                    backgroundSize: 'cover',
                  }}
                  onClick={() => onViewingIndexChange(i)}
                  title={`Page ${p.page}`}
                />
              ))}
              {/* Empty placeholders for ungenerated pages */}
              {Array.from({ length: story.total_pages - completedPages.length }).map((_, i) => (
                <div
                  key={`empty-${i}`}
                  style={{ ...styles.thumb, border: '3px dashed #ddd', color: '#ccc', fontSize: '0.7rem' }}
                >
                  {completedPages.length + i + 1}
                </div>
              ))}
            </div>
          </div>

          {/* Continue / done */}
          <div style={styles.continueBox}>
            {canContinue ? (
              <>
                <p style={styles.continueHint}>
                  Ready to continue? Choose how page {completedPages.length + 1} unfolds.
                </p>
                <button style={styles.continueBtn} onClick={onNextPage}>
                  Choose Page {completedPages.length + 1} →
                </button>
              </>
            ) : isLastCompleted && completedPages.length === story.total_pages ? (
              <>
                <p style={styles.doneText}>Your story is complete!</p>
                <button
                  style={styles.exportBtn2}
                  onClick={handleExport}
                  disabled={isExporting}
                >
                  {isExporting ? 'Saving...' : '⬇ Export PDF'}
                </button>
              </>
            ) : (
              <p style={styles.continueHint}>
                Navigate the pages to colour them in.
              </p>
            )}
          </div>

          {/* Color palette */}
          <ColorPalette selected={selectedColor} onSelect={setSelectedColor} />

          {/* Edit illustration */}
          <div style={styles.editBox}>
            <div style={styles.editLabel}>Adjust this illustration</div>
            <input
              style={styles.editInput}
              type="text"
              placeholder='e.g. "make the background darker"'
              value={editInstruction}
              onChange={e => setEditInstruction(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleEditImage()}
              disabled={isEditing}
            />
            <button
              style={{ ...styles.editBtn, opacity: isEditing || !editInstruction.trim() ? 0.5 : 1 }}
              onClick={handleEditImage}
              disabled={isEditing || !editInstruction.trim()}
            >
              {isEditing ? 'Updating...' : 'Update →'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  page: { minHeight: '100vh', background: '#FFFDF7', display: 'flex', flexDirection: 'column' },
  topBar: {
    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
    padding: '14px 24px', background: '#fff',
    boxShadow: '0 2px 12px rgba(0,0,0,0.07)', gap: 16,
    position: 'sticky', top: 0, zIndex: 100,
  },
  backBtn: {
    background: '#f5f5f5', border: 'none', borderRadius: 50,
    padding: '8px 18px', fontSize: '0.85rem', color: '#555',
    cursor: 'pointer', fontFamily: "'Nunito', sans-serif", fontWeight: 700,
  },
  bookTitle: {
    fontFamily: "'Fredoka One', cursive",
    fontSize: 'clamp(0.9rem, 2.5vw, 1.3rem)',
    color: '#2D3436', flex: 1, textAlign: 'center',
  },
  exportBtn: {
    background: '#4ECDC4', color: '#fff', border: 'none', borderRadius: 50,
    padding: '10px 20px', fontSize: '0.9rem', fontWeight: 700,
    cursor: 'pointer', fontFamily: "'Nunito', sans-serif", whiteSpace: 'nowrap',
  },
  layout: {
    display: 'grid', gridTemplateColumns: '1fr 320px',
    gap: 20, padding: '20px 24px', maxWidth: 1200, margin: '0 auto', width: '100%',
  },
  canvasCol: { display: 'flex', flexDirection: 'column', gap: 14 },
  pageNav: { display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 16 },
  navBtn: {
    background: '#FFD93D', color: '#2D3436', border: 'none', borderRadius: 50,
    padding: '9px 22px', fontSize: '0.9rem', fontWeight: 700,
    cursor: 'pointer', fontFamily: "'Nunito', sans-serif",
  },
  pageLabel: {
    fontFamily: "'Fredoka One', cursive", fontSize: '1rem',
    color: '#2D3436', minWidth: 160, textAlign: 'center',
  },
  canvasControls: { display: 'flex', gap: 10, justifyContent: 'center' },
  controlBtn: {
    background: '#fff', border: '2px solid #ddd', borderRadius: 50,
    padding: '7px 20px', fontSize: '0.85rem', color: '#555',
    cursor: 'pointer', fontFamily: "'Nunito', sans-serif", fontWeight: 700,
  },
  sidebar: { display: 'flex', flexDirection: 'column', gap: 16 },
  storyBox: {
    background: '#fff', borderRadius: 16, padding: '20px',
    boxShadow: '0 2px 12px rgba(0,0,0,0.07)',
  },
  pageTag: {
    fontFamily: "'Fredoka One', cursive", fontSize: '0.82rem',
    color: '#aaa', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.05em',
  },
  storyText: {
    fontFamily: "'Nunito', sans-serif", fontSize: '0.97rem',
    lineHeight: 1.75, color: '#2D3436',
  },
  thumbStrip: {
    background: '#fff', borderRadius: 16, padding: '16px 20px',
    boxShadow: '0 2px 12px rgba(0,0,0,0.07)',
  },
  thumbLabel: {
    fontFamily: "'Fredoka One', cursive", fontSize: '0.9rem',
    color: '#aaa', marginBottom: 10, textTransform: 'uppercase',
  },
  thumbRow: { display: 'flex', gap: 8, flexWrap: 'wrap' },
  thumb: {
    width: 44, height: 44, borderRadius: 10, cursor: 'pointer',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    transition: 'border 0.15s', backgroundSize: 'cover', backgroundPosition: 'center',
    flexShrink: 0,
  },
  continueBox: {
    background: '#fff', borderRadius: 16, padding: '20px',
    boxShadow: '0 2px 12px rgba(0,0,0,0.07)',
    display: 'flex', flexDirection: 'column', gap: 12,
  },
  continueHint: {
    fontFamily: "'Nunito', sans-serif", fontSize: '0.9rem', color: '#777', lineHeight: 1.5,
  },
  continueBtn: {
    background: 'linear-gradient(135deg, #FF6B6B, #FFD93D)',
    color: '#fff', border: 'none', borderRadius: 50,
    padding: '13px 20px', fontSize: '1rem', fontWeight: 700,
    cursor: 'pointer', fontFamily: "'Nunito', sans-serif",
  },
  doneText: {
    fontFamily: "'Fredoka One', cursive", fontSize: '1.1rem', color: '#2D3436',
  },
  exportBtn2: {
    background: '#4ECDC4', color: '#fff', border: 'none', borderRadius: 50,
    padding: '12px 20px', fontSize: '0.95rem', fontWeight: 700,
    cursor: 'pointer', fontFamily: "'Nunito', sans-serif",
  },
  editBox: {
    background: '#fff', borderRadius: 16, padding: '20px',
    boxShadow: '0 2px 12px rgba(0,0,0,0.07)',
  },
  editLabel: {
    fontFamily: "'Fredoka One', cursive", fontSize: '1rem', color: '#2D3436', marginBottom: 10,
  },
  editInput: {
    width: '100%', border: '2px solid #eee', borderRadius: 12,
    padding: '10px 14px', fontSize: '0.9rem',
    fontFamily: "'Nunito', sans-serif", outline: 'none', marginBottom: 10,
    boxSizing: 'border-box',
  },
  editBtn: {
    width: '100%', background: '#FF6B6B', color: '#fff', border: 'none',
    borderRadius: 50, padding: '10px', fontSize: '0.9rem', fontWeight: 700,
    cursor: 'pointer', fontFamily: "'Nunito', sans-serif",
  },
}

import { useRef, useEffect, useCallback, useState, forwardRef, useImperativeHandle } from 'react'
import { floodFill } from '../utils/floodFill'

interface Props {
  imageSrc: string   // base64 string
  selectedColor: string
  onEdit?: () => void
}

export interface CanvasHandle {
  undo: () => void
  clear: () => void
  toDataURL: () => string
}

const MAX_UNDO = 10

function base64ToSrc(base64: string): string {
  if (base64.startsWith('data:')) return base64
  if (base64.length < 200 && base64.includes('<svg')) return `data:image/svg+xml;base64,${btoa(base64)}`
  return `data:image/png;base64,${base64}`
}

const FloodFillCanvas = forwardRef<CanvasHandle, Props>(({ imageSrc, selectedColor, onEdit }, ref) => {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const undoStack = useRef<ImageData[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const drawImage = useCallback(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    setIsLoading(true)
    const img = new Image()
    img.crossOrigin = 'anonymous'
    img.onload = () => {
      canvas.width = img.naturalWidth || 600
      canvas.height = img.naturalHeight || 600
      ctx.fillStyle = '#FFFFFF'
      ctx.fillRect(0, 0, canvas.width, canvas.height)
      ctx.drawImage(img, 0, 0)
      undoStack.current = []
      setIsLoading(false)
    }
    img.onerror = () => {
      canvas.width = 600
      canvas.height = 600
      ctx.fillStyle = '#f5f5f5'
      ctx.fillRect(0, 0, 600, 600)
      ctx.strokeStyle = '#ccc'
      ctx.strokeRect(20, 20, 560, 560)
      ctx.fillStyle = '#aaa'
      ctx.font = '20px Nunito'
      ctx.textAlign = 'center'
      ctx.fillText('Illustration loading...', 300, 310)
      setIsLoading(false)
    }
    img.src = base64ToSrc(imageSrc)
  }, [imageSrc])

  useEffect(() => { drawImage() }, [drawImage])

  const handleClick = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const rect = canvas.getBoundingClientRect()
    const scaleX = canvas.width / rect.width
    const scaleY = canvas.height / rect.height
    const x = Math.floor((e.clientX - rect.left) * scaleX)
    const y = Math.floor((e.clientY - rect.top) * scaleY)

    // Save undo state
    const snapshot = ctx.getImageData(0, 0, canvas.width, canvas.height)
    undoStack.current = [snapshot, ...undoStack.current].slice(0, MAX_UNDO)

    floodFill(canvas, x, y, selectedColor)
  }, [selectedColor])

  useImperativeHandle(ref, () => ({
    undo() {
      const canvas = canvasRef.current
      if (!canvas || undoStack.current.length === 0) return
      const ctx = canvas.getContext('2d')
      if (!ctx) return
      const prev = undoStack.current.shift()!
      ctx.putImageData(prev, 0, 0)
    },
    clear() { drawImage() },
    toDataURL() { return canvasRef.current?.toDataURL('image/png') ?? '' }
  }))

  return (
    <div style={styles.wrapper}>
      {isLoading && (
        <div style={styles.loading}>
          <div style={styles.spinner} />
          <span>Loading illustration...</span>
        </div>
      )}
      <canvas
        ref={canvasRef}
        onClick={handleClick}
        style={{
          ...styles.canvas,
          cursor: 'crosshair',
          opacity: isLoading ? 0 : 1,
        }}
      />
    </div>
  )
})

FloodFillCanvas.displayName = 'FloodFillCanvas'
export default FloodFillCanvas

const styles: Record<string, React.CSSProperties> = {
  wrapper: {
    position: 'relative',
    width: '100%',
    borderRadius: 16,
    overflow: 'hidden',
    boxShadow: '0 4px 24px rgba(0,0,0,0.12)',
    background: '#fff',
    aspectRatio: '1',
  },
  canvas: {
    width: '100%',
    height: '100%',
    display: 'block',
    transition: 'opacity 0.3s',
  },
  loading: {
    position: 'absolute',
    inset: 0,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 12,
    color: '#aaa',
    fontSize: '0.9rem',
    fontFamily: "'Nunito', sans-serif",
  },
  spinner: {
    width: 36,
    height: 36,
    borderRadius: '50%',
    border: '4px solid #FFD93D',
    borderTopColor: '#FF6B6B',
    animation: 'spin 1s linear infinite',
  },
}

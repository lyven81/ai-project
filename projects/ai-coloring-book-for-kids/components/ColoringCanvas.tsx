
import React, { useRef, useEffect, useCallback, forwardRef, useImperativeHandle } from 'react';

interface ColoringCanvasProps {
  imageUrl: string;
  color: string;
  onHistoryChange: (canUndo: boolean) => void;
}

export interface CanvasHandle {
  undo: () => void;
}

export const ColoringCanvas = forwardRef<CanvasHandle, ColoringCanvasProps>(({ imageUrl, color, onHistoryChange }, ref) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const imageRef = useRef<HTMLImageElement | null>(null);
  const historyRef = useRef<ImageData[]>([]);

  const hexToRgb = (hex: string) => {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result
      ? {
          r: parseInt(result[1], 16),
          g: parseInt(result[2], 16),
          b: parseInt(result[3], 16),
        }
      : null;
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const context = canvas.getContext('2d', { willReadFrequently: true });
    if (!context) return;
    
    const img = new Image();
    img.crossOrigin = "anonymous";
    img.src = imageUrl;
    img.onload = () => {
      const parent = canvas.parentElement;
      if (parent) {
        const size = Math.min(parent.clientWidth, parent.clientHeight);
        canvas.width = size;
        canvas.height = size;
        context.drawImage(img, 0, 0, canvas.width, canvas.height);
        imageRef.current = img;

        // Save initial state for undo
        const initialImageData = context.getImageData(0, 0, canvas.width, canvas.height);
        historyRef.current = [initialImageData];
        onHistoryChange(false);
      }
    };
  }, [imageUrl, onHistoryChange]);

  const floodFill = useCallback((ctx: CanvasRenderingContext2D, startX: number, startY: number, fillColor: {r: number, g: number, b: number}) => {
    const canvas = ctx.canvas;
    const { width, height } = canvas;
    const imageData = ctx.getImageData(0, 0, width, height);
    const data = imageData.data;
    const startPos = (startY * width + startX) * 4;
    const startR = data[startPos];
    const startG = data[startPos + 1];
    const startB = data[startPos + 2];

    if (startR === fillColor.r && startG === fillColor.g && startB === fillColor.b) {
      return;
    }

    const isLine = (r: number, g: number, b: number) => r < 50 && g < 50 && b < 50;
    if (isLine(startR, startG, startB)) {
      return;
    }
    
    const tolerance = 30;
    const colorMatch = (pos: number) => {
        const r = data[pos];
        const g = data[pos + 1];
        const b = data[pos + 2];
        return Math.abs(r - startR) <= tolerance &&
               Math.abs(g - startG) <= tolerance &&
               Math.abs(b - startB) <= tolerance;
    };

    const pixelStack = [[startX, startY]];

    while (pixelStack.length) {
      const newPos = pixelStack.pop();
      if (!newPos) continue;

      let [x, y] = newPos;
      let currentPos = (y * width + x) * 4;

      while (y-- >= 0 && colorMatch(currentPos)) {
        currentPos -= width * 4;
      }
      currentPos += width * 4;
      ++y;

      let reachLeft = false;
      let reachRight = false;

      while (y++ < height - 1 && colorMatch(currentPos)) {
        data[currentPos] = fillColor.r;
        data[currentPos + 1] = fillColor.g;
        data[currentPos + 2] = fillColor.b;
        data[currentPos + 3] = 255;

        if (x > 0) {
          if (colorMatch(currentPos - 4)) {
            if (!reachLeft) {
              pixelStack.push([x - 1, y]);
              reachLeft = true;
            }
          } else if (reachLeft) {
            reachLeft = false;
          }
        }

        if (x < width - 1) {
          if (colorMatch(currentPos + 4)) {
            if (!reachRight) {
              pixelStack.push([x + 1, y]);
              reachRight = true;
            }
          } else if (reachRight) {
            reachRight = false;
          }
        }
        currentPos += width * 4;
      }
    }
    ctx.putImageData(imageData, 0, 0);
  }, []);

  const handleCanvasClick = (event: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    const rect = canvas.getBoundingClientRect();
    const x = Math.floor(event.clientX - rect.left);
    const y = Math.floor(event.clientY - rect.top);
    const rgbColor = hexToRgb(color);
    if (rgbColor) {
      floodFill(ctx, x, y, rgbColor);
      // Save state for undo
      const newImageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      historyRef.current.push(newImageData);
      onHistoryChange(true);
    }
  };

  useImperativeHandle(ref, () => ({
    undo: () => {
      if (historyRef.current.length <= 1) {
        return; // Cannot undo the initial state
      }

      historyRef.current.pop(); // Remove current state
      const previousState = historyRef.current[historyRef.current.length - 1];

      const canvas = canvasRef.current;
      const ctx = canvas?.getContext('2d');
      if (ctx && previousState) {
        ctx.putImageData(previousState, 0, 0);
      }

      onHistoryChange(historyRef.current.length > 1);
    }
  }));

  return (
    <canvas
      ref={canvasRef}
      onClick={handleCanvasClick}
      className="cursor-crosshair max-w-full max-h-full"
    />
  );
});

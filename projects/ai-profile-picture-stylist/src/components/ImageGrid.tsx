import React from 'react';
import { GeneratedImage } from '../types';
import { StyleCard } from './StyleCard';

interface ImageGridProps {
  images: GeneratedImage[];
}

export const ImageGrid: React.FC<ImageGridProps> = ({ images }) => {
  return (
    <div className="w-full max-w-5xl">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 lg:gap-8">
        {images.map((image) => (
          <StyleCard
            key={image.id}
            src={image.src}
            title={image.title}
            description={image.description}
          />
        ))}
      </div>
    </div>
  );
};
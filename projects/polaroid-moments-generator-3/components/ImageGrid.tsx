
import React from 'react';
import { PolaroidFrame } from './PolaroidFrame';

interface ImageGridProps {
    images: string[];
    captions: string[];
}

export const ImageGrid: React.FC<ImageGridProps> = ({ images, captions }) => {
    return (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-8 md:gap-12 p-4">
            {images.map((src, index) => (
                <PolaroidFrame
                    key={index}
                    imageUrl={src}
                    caption={captions[index]}
                    rotation={Math.random() * 6 - 3} // Random rotation between -3 and 3 degrees
                />
            ))}
        </div>
    );
};

'use client';

import React, { useState } from 'react';
import Image from 'next/image';

interface BoxPreviewData {
  id: string;
  name: string;
  imageUrl: string;
}

interface BoxSelectionGridProps {
  boxes: BoxPreviewData[];
  onBoxSelect: (boxId: string) => void;
}

export default function BoxSelectionGrid({ boxes, onBoxSelect }: BoxSelectionGridProps) {
  const [selectedBoxId, setSelectedBoxId] = useState<string | null>(null);

  const handleSelect = (box: BoxPreviewData) => {
    setSelectedBoxId(box.id);
    onBoxSelect(box.id); 
  };

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 mb-6">
      {boxes.length === 0 ? (
        <p className="text-center text-muted-foreground col-span-full">没有找到盒子。</p>
      ) : (
        boxes.map((box) => (
          <div
            key={box.id}
            className={`relative rounded-md overflow-hidden border-2 cursor-pointer transition-all duration-200 
                        ${
                          selectedBoxId === box.id
                            ? 'border-blue-500 ring-2 ring-blue-500 ring-offset-2'
                            : 'border-transparent hover:border-blue-300'
                        }`}
            onClick={() => handleSelect(box)}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => e.key === 'Enter' || e.key === ' ' ? handleSelect(box) : null}
          >
            <Image
              src={box.imageUrl}
              alt={box.name}
              width={400}
              height={225}
              className="object-cover w-full h-auto aspect-video"
              priority={false}
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/10 to-transparent"></div>
            <div className="absolute top-2 left-2 bg-black/50 text-white text-sm px-2 py-1 rounded">
              {box.name}
            </div>
          </div>
        ))
      )}
    </div>
  );
} 
'use client';

import React from 'react';
import { RtspSourceInfo } from '@/store/types';
import { Loader2 } from 'lucide-react';

interface VideoFrameProps {
  source: RtspSourceInfo;
}

const VideoFrame: React.FC<VideoFrameProps> = ({ source }) => {
  const streamUrl = source.mjpegStreamUrl || source.rawMjpegStreamUrl;

  return (
    <div className={`w-full h-full flex justify-center items-center overflow-hidden relative ${streamUrl ? '' : 'bg-gray-200'} rounded-md`}>
      <div className="relative w-full h-0 pt-[56.25%]">
        <div className="absolute inset-0 flex items-center justify-center">
          {streamUrl ? (
            <img
              src={streamUrl}
              alt={`Stream for ${source.url}`}
              className="w-full h-full object-cover rounded-md"
              onError={(e) => {
                console.error(`Error loading stream: ${streamUrl}`);
                (e.target as HTMLImageElement).style.opacity = '0'; 
              }}
            />
          ) : (
            // Loader positioned within the absolute container
            <div className="flex flex-col items-center justify-center text-gray-500">
              <Loader2 className="h-8 w-8 animate-spin mb-2" />
              <span>加载中...</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default VideoFrame; 
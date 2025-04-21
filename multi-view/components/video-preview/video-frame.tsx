'use client';

import React, { useState } from 'react';
import { RtspSourceInfo } from '@/store/types';
import { AlertTriangle, Loader2 } from 'lucide-react';

interface VideoFrameProps {
  source: RtspSourceInfo;
}

const VideoFrame: React.FC<VideoFrameProps> = ({ source }) => {
  const streamUrl = source.mjpegStreamUrl || source.rawMjpegStreamUrl;
  const [loadError, setLoadError] = useState(false);

  return (
    <div className={`w-full h-full flex justify-center items-center overflow-hidden relative ${streamUrl ? '' : 'bg-gray-200'} rounded-md`}>
      <div className="relative w-full h-0 pt-[56.25%]">
        <div className="absolute inset-0 flex items-center justify-center">
          {streamUrl && !loadError ? (
            <img
              src={streamUrl}
              alt={`Stream for ${source.url}`}
              className="w-full h-full object-cover rounded-md"
              onError={(e) => {
                console.error(`Error loading stream: ${streamUrl}`);
                setLoadError(true);
              }}
            />
          ) : streamUrl && loadError ? (
            // Error placeholder
            <div className="flex flex-col items-center justify-center text-gray-500">
              <AlertTriangle className="h-10 w-10 text-amber-500 mb-2" />
              <span className="text-center">视频流加载失败</span>
              <span className="text-xs text-gray-400 mt-1">{source.url}</span>
            </div>
          ) : (
            // No URL placeholder
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
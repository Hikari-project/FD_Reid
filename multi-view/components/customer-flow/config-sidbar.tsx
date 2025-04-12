'use client'

import React, { useMemo } from 'react'
import { useAppStore } from '@/store/useCustomerAnalysis';
import type { SourceStatus } from '@/store/types';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { toast } from 'sonner';
import Image from 'next/image';

const getStatusBadgeClass = (status: SourceStatus): string => {
    switch (status) {
        case 'idle':            return 'bg-gray-400';
        case 'loading_frame':   return 'bg-yellow-500 animate-pulse';
        case 'frame_loaded':    return 'bg-blue-500';
        case 'annotating':      return 'bg-purple-500';
        case 'annotated':       return 'bg-indigo-500';
        case 'analyzing':       return 'bg-orange-500 animate-pulse';
        case 'streaming':       return 'bg-green-600';
        case 'error_frame':
        case 'error_analysis':
        case 'error_rtsp':      return 'bg-red-500';
        default:                return 'bg-gray-400';
    }
};

export default function ConfigSidebar() {
  const sourcesObject = useAppStore(state => state.rtspSources);
  const sources = useMemo(() => Object.values(sourcesObject), [sourcesObject]);
  
  const activeSourceUrl = useAppStore((state) => state.activeSourceUrl);
  
  const setActiveSource = useAppStore(state => state.setActiveSource);
  const removeRtspSource = useAppStore(state => state.removeRtspSource);

  const handleSelectSource = (url: string) => {
    setActiveSource(url);
  };

  const handleRemoveSource = (e: React.MouseEvent, url: string) => {
    e.stopPropagation();


    try {
        removeRtspSource(url);
        toast.success(`Removed source: ${url.substring(0, 20)}...`);
    } catch (error) {
        console.error("Error removing source:", error);
        toast.error("Failed to remove source.");
    }
  };

  return (
    <div className="w-72 h-full bg-white rounded-md shadow-sm pt-4 flex flex-col">
      <h3 className="font-medium text-lg text-gray-700 w-full mb-2 px-4">RTSP 流源</h3>

      {sources.length === 0 ? (
        <div className="text-gray-500 text-sm py-6 text-center flex-1 px-4">
            还没有添加 RTSP 流源。使用上面的控件添加 RTSP 流源。
        </div>
      ) : (
        <div className="w-full space-y-2 overflow-y-auto flex-1 px-3 pb-3">
          {sources.map((source) => (
            <div
              key={source.url}
              className={cn(
                "border rounded-md p-3 cursor-pointer transition-all duration-150 ease-in-out",
                "hover:shadow-md hover:border-gray-300",
                activeSourceUrl === source.url
                    ? "border-blue-500 bg-blue-50 shadow-md ring-1 ring-blue-500"
                    : "border-gray-200 bg-white",
                source.status.startsWith('error') && activeSourceUrl !== source.url
                    ? "border-red-300 bg-red-50"
                    : ""
              )}
              onClick={() => handleSelectSource(source.url)}
              title={`Click to select: ${source.url}`}
            >
              <div className="flex justify-between items-start mb-2">
                <div className="truncate text-sm font-medium text-gray-800 pr-2 break-all" title={source.url}>
                  {source.url}
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-6 w-6 p-0 text-gray-400 hover:text-red-600 flex-shrink-0"
                  onClick={(e) => handleRemoveSource(e, source.url)}
                  title="Remove Source"
                >
                  ✕
                </Button>
              </div>

              <div className="text-xs flex items-center gap-2 mb-2">
                    <span className={cn(
                        "capitalize px-1.5 py-0.5 rounded text-white text-[10px] font-medium",
                        getStatusBadgeClass(source.status) // Use helper for color
                    )}>
                        {source.status.replace('_', ' ')}
                    </span>
                    {source.errorMessage && source.status.startsWith('error') &&
                     <span className='text-red-600 truncate font-medium' title={source.errorMessage}>
                        错误
                     </span>
                    }
              </div>

              {source.firstFrameDataUrl && !source.status.startsWith('error') && (
                 <div className='mt-1 border border-gray-200 rounded overflow-hidden'>
                     <img
                        src={source.firstFrameDataUrl}
                        alt={`Preview`}
                        className="w-full h-auto object-contain max-h-32"
                        loading="lazy"
                     />
                 </div>
              )}
               {source.status === 'error_frame' && (
                   <div className='mt-1 border border-dashed border-red-300 rounded h-20 flex items-center justify-center text-red-500 text-xs p-2'>
                       帧加载错误
                   </div>
               )}

            </div>
          ))}
        </div>
      )}
    </div>
  )
}
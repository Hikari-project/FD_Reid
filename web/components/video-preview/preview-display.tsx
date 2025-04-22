'use client';

import React, { useState, useMemo, useEffect } from 'react';
import PreviewSidebar from "./preview-sidebar";
import VideoFrame from "./video-frame";
import { useAppStore } from '@/store/useCustomerAnalysis';
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { ChevronLeft, ChevronRight, Video } from 'lucide-react';

type ViewMode = 'grid' | 'single';
const GRID_CELL_COUNT = 4;

const PlaceholderFrame = () => (
  <div className="w-full h-full overflow-hidden relative bg-gray-100 rounded-md border border-gray-200">
    <div className="relative w-full h-0 pt-[56.25%]">
      <div className="absolute inset-0 flex flex-col items-center justify-center text-gray-500 text-center p-2">
        <Video className="h-8 w-8 mb-2" />
        <p className="text-xs">请先前往客流分析</p>
        <p className="text-xs">进行配置</p>
      </div>
    </div>
  </div>
);

export default function PreviewDisplay() {
  const sourcesObject = useAppStore(state => state.rtspSources);
  const sources = useMemo(() => Object.values(sourcesObject), [sourcesObject]);
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [currentSourceIndex, setCurrentSourceIndex] = useState(0);

  useEffect(() => {
    if (sources.length > 0 && currentSourceIndex >= sources.length) {
      setCurrentSourceIndex(0);
    }
    if (sources.length === 0) {
      setCurrentSourceIndex(0);
    }
  }, [sources.length, currentSourceIndex]);

  useEffect(() => {
    if (viewMode === 'single' && sources.length > 0) {
      if (currentSourceIndex >= sources.length) {
        setCurrentSourceIndex(0);
      }
    }
  }, [viewMode, sources.length, currentSourceIndex]);

  const gridLayoutClass = useMemo(() => {
    return viewMode === 'grid' ? 'grid-cols-2' : 'grid-cols-1';
  }, [viewMode]);

  const handlePrevious = () => {
    if (sources.length === 0) return;
    setCurrentSourceIndex(prev => 
      prev === 0 ? sources.length - 1 : prev - 1
    );
  };

  const handleNext = () => {
    if (sources.length === 0) return;
    setCurrentSourceIndex(prev => 
      prev === sources.length - 1 ? 0 : prev + 1
    );
  };

  return (
    <div className="flex w-full h-[calc(100vh-48px)] p-2 bg-gray-100 gap-2">
      <PreviewSidebar />
      <div className="flex-1 flex flex-col min-h-0 bg-white rounded-md shadow-sm p-2">
        <div className="flex-shrink-0 space-x-2 p-2">
          <Button
            variant={viewMode === 'grid' ? 'secondary' : 'outline'}
            size="sm"
            onClick={() => setViewMode('grid')}
          >
            网格视图
          </Button>
          <Button
            variant={viewMode === 'single' ? 'secondary' : 'outline'}
            size="sm"
            onClick={() => setViewMode('single')}
            disabled={sources.length === 0}
          >
            单屏视图
          </Button>
        </div>

        <div className={cn(
          "flex-1 min-h-0 overflow-auto p-2",
          `grid ${gridLayoutClass} gap-2 ${viewMode === 'grid' ? 'auto-rows-fr' : 'auto-rows-auto'}`
        )}>
          {viewMode === 'grid' ? (
            Array.from({ length: GRID_CELL_COUNT }).map((_, index) => {
              const source = sources[index];
              return (
                <div className="min-h-0 flex" key={`grid-cell-${index}`}>
                  {source ? (
                    <div className="min-h-0 flex w-full h-full justify-center items-center">
                      <VideoFrame key={source.url} source={source} />
                    </div>
                  ) : (
                    <PlaceholderFrame />
                  )}
                </div>
              );
            })
          ) : sources.length > 0 ? (
            <div className="col-span-full flex flex-col h-full">
              <div className="flex-1 flex justify-center items-center w-full min-h-0">
                {sources[currentSourceIndex] && (
                  <VideoFrame 
                    key={sources[currentSourceIndex].url} 
                    source={sources[currentSourceIndex]}
                  />
                )}
              </div>
              <div className="flex-shrink-0 w-full flex justify-between items-center pt-2">
                <Button 
                  variant="outline" 
                  size="icon" 
                  onClick={handlePrevious}
                  disabled={sources.length <= 1}
                  className="rounded-full"
                >
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <div className="text-center">
                  <span className="text-sm text-gray-500">
                    {`${currentSourceIndex + 1}/${sources.length}`}
                  </span>
                </div>
                <Button 
                  variant="outline" 
                  size="icon" 
                  onClick={handleNext}
                  disabled={sources.length <= 1}
                  className="rounded-full"
                >
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          ) : (
            <div className="col-span-full flex items-center justify-center">
              <PlaceholderFrame />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

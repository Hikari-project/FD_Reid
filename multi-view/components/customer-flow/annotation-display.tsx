'use client'

import React, { useRef, useState, useEffect, useCallback, useMemo } from 'react';
import { Stage, Layer, Image as KonvaImage, Line, Circle } from 'react-konva';
import Konva from 'konva';
import useImage from 'use-image';

import ConfigHeader from '@/components/customer-flow/config-header';
import ConfigSidebar from '@/components/customer-flow/config-sidbar';

import { selectActiveSourceData, useAppStore } from '@/store/useCustomerAnalysis';
import type { Point } from '@/store/types';

import { toast } from 'sonner';
import { cn } from '@/lib/utils';
import Image from 'next/image';

const LINE_STROKE_WIDTH = 3;
const SELECTED_LINE_STROKE_WIDTH = 5;
const HIT_STROKE_WIDTH = 10;
const DOT_RADIUS = 6;
const DOT_FILL_COLOR = '#ffea00';
const DOT_HOVER_FILL_COLOR = '#ff8c00';
const LINE_COLOR = '#ff0000';
const SELECTED_LINE_COLOR = '#0000ff';
const HOVER_LINE_COLOR = '#add8e6';
const CLOSING_THRESHOLD = 15;

export default function AnnotationDisplay({ boxId }: { boxId: string }) {
  const activeSource = useAppStore(selectActiveSourceData);
  const annotationMode = useAppStore(state => state.annotationMode);
  const addAnnotationPoint = useAppStore(state => state.addAnnotationPoint);
  const closePolygon = useAppStore(state => state.closePolygon);
  const toggleLineSelection = useAppStore(state => state.toggleLineSelection);

  const stageRef = useRef<Konva.Stage>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const [stageDimensions, setStageDimensions] = useState({ width: 0, height: 0 });
  const [scale, setScale] = useState(1);
  const [image] = useImage(activeSource?.firstFrameDataUrl ?? '');
  const [isHoveringStartPoint, setIsHoveringStartPoint] = useState(false);
  const [hoveredLineIndex, setHoveredLineIndex] = useState<number | null>(null);

  // const points = activeSource?.annotation?.points ?? [];
  const points = useMemo(() => activeSource?.annotation?.points ?? [], [activeSource?.annotation?.points]);

  const isClosed = activeSource?.annotation?.isClosed ?? false;
  // const selectedLineIndices = activeSource?.annotation?.selectedLineIndices ?? [];
  const selectedLineIndices = useMemo(() => activeSource?.annotation?.selectedLineIndices ?? [], [activeSource?.annotation?.selectedLineIndices]);

  const canDraw = annotationMode === 'drawing' && !!activeSource && !isClosed && !activeSource.status.startsWith('error') && activeSource.status !== 'streaming' && activeSource.status !== 'analyzing';
  const canSelectLines = annotationMode === 'line_selection' && !!activeSource && isClosed && !activeSource.status.startsWith('error') && activeSource.status !== 'streaming' && activeSource.status !== 'analyzing';

  useEffect(() => {
    const calculateSize = () => {
      if (!containerRef.current || !activeSource?.imageDimensions) {
         if (!containerRef.current) {
            setStageDimensions({ width: 0, height: 0 });
            setScale(1);
            return;
         }
         const containerW = containerRef.current.offsetWidth;
         const containerH = containerRef.current.offsetHeight;
         setStageDimensions({ width: containerW, height: containerH });
         setScale(1);
         return;
      }

      const containerW = containerRef.current.offsetWidth;
      const containerH = containerRef.current.offsetHeight;
      const imgW = activeSource.imageDimensions.width;
      const imgH = activeSource.imageDimensions.height;

      const scaleX = containerW / imgW;
      const scaleY = containerH / imgH;
      const newScale = Math.min(scaleX, scaleY);

      const stageW = imgW * newScale;
      const stageH = imgH * newScale;

      setScale(newScale);
      setStageDimensions({ width: stageW, height: stageH });
    };

    calculateSize();

    const resizeObserver = new ResizeObserver(calculateSize);
    if (containerRef.current) {
      resizeObserver.observe(containerRef.current);
    }

    return () => {
       if (containerRef.current) {
        resizeObserver.unobserve(containerRef.current);
       }
       resizeObserver.disconnect();
    };
  }, [activeSource?.imageDimensions, activeSource?.url]); 


  const getScaledPointerPosition = useCallback(() => {
    if (!stageRef.current) return null;
    const pos = stageRef.current.getPointerPosition();
    if (!pos) return null;
    return { x: pos.x / scale, y: pos.y / scale };
  }, [scale]);


  const handleStageMouseDown = useCallback(() => {
    if (!canDraw || !activeSource?.url) return;

    const pos = getScaledPointerPosition();
    if (!pos) return;

    if (points.length >= 3 && !isClosed) {
      const firstPoint = points[0];
      const dx = firstPoint.x - pos.x;
      const dy = firstPoint.y - pos.y;
      const distance = Math.sqrt(dx * dx + dy * dy);

      if (distance * scale < CLOSING_THRESHOLD) {
        closePolygon(activeSource.url);
        setIsHoveringStartPoint(false);
        toast.success('Polygon closed. Select crossing lines.');
        return;
      }
    }

    addAnnotationPoint(activeSource.url, pos);

  }, [canDraw, points, isClosed, scale, activeSource?.url, getScaledPointerPosition, addAnnotationPoint, closePolygon]);


  const handleLineClick = useCallback((lineIndex: number) => {
     if (!canSelectLines || !activeSource?.url) return;
     toggleLineSelection(activeSource.url, lineIndex);
  }, [canSelectLines, activeSource?.url, toggleLineSelection]);


  const handleStartDotMouseEnter = useCallback(() => {
      if (canDraw && points.length >= 3 && !isClosed) {
          setIsHoveringStartPoint(true);
      }
  }, [canDraw, points.length, isClosed]);

  const handleStartDotMouseLeave = useCallback(() => {
      setIsHoveringStartPoint(false);
  }, []);

   const handleLineHover = useCallback((lineIndex: number | null) => {
       if (canSelectLines) {
           setHoveredLineIndex(lineIndex);
       }
   }, [canSelectLines]);

  const content = useMemo(() => {
    if (!activeSource) {
      return <div className="text-gray-500 text-center p-10">请从侧边栏选择一个 RTSP 流源开始。</div>;
    }

    if (activeSource.status === 'loading_frame') {
        return <div className="text-gray-500 text-center p-10 animate-pulse">加载第一帧...</div>;
    }

     if (activeSource.status.startsWith('error')) {
        return (
            <div className="text-red-600 text-center p-10 flex flex-col items-center justify-center">
                <p className="font-semibold text-lg mb-2">错误</p>
                <p>{activeSource.errorMessage || '发生了一个未知错误。'}</p>
            </div>
        );
     }

    return (
      <div className="relative w-full h-full bg-gray-900">
        {activeSource.status === 'streaming' && activeSource.mjpegStreamUrl && (
            <img
                src={activeSource.mjpegStreamUrl}
                // src={"http://localhost:8003/video_feed"}
                alt="MJPEG 流"
                className="absolute top-0 left-0 w-full h-full object-contain z-0" 
            />
        )}
       
        <Stage
            ref={stageRef}
            width={stageDimensions.width}
            height={stageDimensions.height}
            scaleX={scale}
            scaleY={scale}
            onMouseDown={handleStageMouseDown}
            style={{
                cursor: canDraw ? 'crosshair' : (canSelectLines ? 'pointer' : 'default'),
                position: 'absolute',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)', 
                zIndex: 10, 
            }}
            className="bg-transparent"
        >
          <Layer>
             {image && activeSource.status !== 'streaming' && activeSource.firstFrameDataUrl && (
                <KonvaImage
                    image={image}
                    width={activeSource.imageDimensions?.width}
                    height={activeSource.imageDimensions?.height}
                    listening={false}
                />
             )}

            {points.length > 0 && (
                <Line
                    points={points.flatMap((p: Point) => [p.x, p.y])}
                    stroke={LINE_COLOR}
                    strokeWidth={LINE_STROKE_WIDTH / scale}
                    closed={isClosed}
                    lineCap="round"
                    lineJoin="round"
                    listening={false}
                />
            )}

            {isClosed && points.length >= 2 && points.map((startPoint: Point, index: number) => {
                const nextIndex = (index + 1) % points.length;
                const endPoint = points[nextIndex];
                const isSelected = selectedLineIndices.includes(index);
                const isHovered = hoveredLineIndex === index;

                return (
                    <Line
                        key={`select-line-${activeSource.url}-${index}`}
                        points={[startPoint.x, startPoint.y, endPoint.x, endPoint.y]}
                        stroke={isSelected ? SELECTED_LINE_COLOR : (isHovered ? HOVER_LINE_COLOR : 'transparent')} // Show selection/hover
                        strokeWidth={(isSelected ? SELECTED_LINE_STROKE_WIDTH : HIT_STROKE_WIDTH) / scale } // Wider hit area, thinner if selected
                        hitStrokeWidth={HIT_STROKE_WIDTH / scale} 
                        listening={canSelectLines}
                        onClick={() => handleLineClick(index)}
                        onTap={() => handleLineClick(index)} 
                        onMouseEnter={() => handleLineHover(index)}
                        onMouseLeave={() => handleLineHover(null)}
                    />
                );
            })}

            {points.map((point: Point, index: number) => (
                <Circle
                    key={`dot-${activeSource.url}-${index}`}
                    x={point.x}
                    y={point.y}
                    radius={DOT_RADIUS / scale} 
                    fill={(index === 0 && isHoveringStartPoint && canDraw) ? DOT_HOVER_FILL_COLOR : DOT_FILL_COLOR}
                    shadowBlur={(index === 0 && isHoveringStartPoint && canDraw) ? (5 / scale) : 0} 
                    stroke="black"
                    strokeWidth={1 / scale}
                    listening={index === 0 && canDraw && points.length >=3}
                    onMouseEnter={handleStartDotMouseEnter}
                    onMouseLeave={handleStartDotMouseLeave}
                />
            ))}

          </Layer>
        </Stage>
      </div>
    );
  }, [
    activeSource, 
    image, 
    stageDimensions, 
    scale, 
    points, 
    isClosed, 
    selectedLineIndices, 
    hoveredLineIndex,
    canDraw,
    canSelectLines,
    isHoveringStartPoint,
    handleStageMouseDown,
    handleLineClick,
    handleStartDotMouseEnter,
    handleStartDotMouseLeave,
    handleLineHover
  ]);

  return (
    <div className="w-full h-full p-2 bg-gray-100">
      <div className="flex flex-col h-full gap-2">
        <ConfigHeader />

        <div className="flex flex-1 gap-2 overflow-hidden">
          <ConfigSidebar />

          <div className="flex-1 h-full bg-white rounded-md shadow-sm overflow-hidden flex flex-col">
            <div
               ref={containerRef}
               className={cn(
                 "relative flex-grow w-full bg-gray-200 flex items-center justify-center", 
                 ""
               )}
             >
                {content}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
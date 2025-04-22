'use client'

import React, { useRef, useState, useEffect, useCallback, useMemo } from 'react';
import { Stage, Layer, Image as KonvaImage, Line, Circle } from 'react-konva';
import Konva from 'konva';
import useImage from 'use-image';

import ConfigHeader from '@/components/customer-flow/config-header';
import ConfigSidebar from '@/components/customer-flow/config-sidbar';

import {
  selectActiveSourceData,
  useAppStore,
  selectActiveZoneType,
} from '@/store/useCustomerAnalysis';
import type { Point, Annotation, ZoneType } from '@/store/types';

import { toast } from 'sonner';
import { cn } from '@/lib/utils';

const LINE_STROKE_WIDTH = 3;
const SELECTED_LINE_STROKE_WIDTH = 5;
const HIT_STROKE_WIDTH = 10;
const DOT_RADIUS = 6;
const DOT_FILL_COLOR = '#ffea00';
const DOT_HOVER_FILL_COLOR = '#ff8c00';
const LINE_COLOR = '#00ff00';
const SELECTED_LINE_COLOR = '#ff0000';
const HOVER_LINE_COLOR = '#add8e6';
const CLOSING_THRESHOLD = 15;

export default function AnnotationDisplay() {
  const activeSource = useAppStore(selectActiveSourceData);
  const annotationMode = useAppStore(state => state.annotationMode);
  const addAnnotationPoint = useAppStore(state => state.addAnnotationPoint);
  const closePolygon = useAppStore(state => state.closePolygon);
  const toggleLineSelection = useAppStore(state => state.toggleLineSelection);
  const setZoneType = useAppStore(state => state.setZoneType);
  const zoneType = useAppStore(selectActiveZoneType);

  const stageRef = useRef<Konva.Stage>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const [stageDimensions, setStageDimensions] = useState({ width: 0, height: 0 });
  const [scale, setScale] = useState(1);
  const [image] = useImage(activeSource?.firstFrameDataUrl ?? '');
  const [isHoveringStartPoint, setIsHoveringStartPoint] = useState(false);
  const [hoveredLineIndex, setHoveredLineIndex] = useState<number | null>(null);

  const points = useMemo(() => activeSource?.annotation?.points ?? [], [activeSource?.annotation?.points]);

  const isClosed = activeSource?.annotation?.isClosed ?? false;
  const selectedLineIndices = useMemo(() => 
    activeSource?.annotation?.selectedLineIndices 
    ?? [], 
  [activeSource?.annotation?.selectedLineIndices]);

  const canDraw = 
    annotationMode === 'drawing' 
    && !!activeSource 
    && !isClosed 
    && !activeSource.status.startsWith('error') 
    && activeSource.status !== 'streaming' 
    && activeSource.status !== 'analyzing';
  const canSelectLines = 
    annotationMode === 'line_selection' 
    && !!activeSource 
    && isClosed 
    && !activeSource.status.startsWith('error') 
    && activeSource.status !== 'streaming' 
    && activeSource.status !== 'analyzing';

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
        toast.success('多边形闭合. 选择过线.');
        return;
      }
    }

    addAnnotationPoint(activeSource.url, pos);

  }, [
    canDraw, 
    points, 
    isClosed,
    scale, 
    activeSource?.url, 
    getScaledPointerPosition, 
    addAnnotationPoint, 
    closePolygon
  ]);


  const handleLineClick = useCallback((lineIndex: number) => {
    if (!canSelectLines || !activeSource?.url) return;
    toggleLineSelection(activeSource.url, lineIndex);
    toast.success('选择过线.');
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

   const handleZoneTypeChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
       if (!activeSource?.url || !canSelectLines) return;
       const selectedType = event.target.value as 'inside' | 'outside';
       setZoneType(activeSource.url, selectedType);
       toast.info(`区域类型设置为: ${selectedType === 'inside' ? '店内' : '店外'}`);
   }, [activeSource?.url, canSelectLines, setZoneType]);

  const polygonFillColor = useMemo(() => 
  zoneType === 'inside' 
  ? 'rgba(0, 255, 0, 0.3)'
  : zoneType === 'outside' 
    ? 'rgba(255, 255, 0, 0.3)' 
    : 'transparent', 
  [zoneType]);

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
        {canSelectLines && (
          <div className="absolute top-2 left-2 z-20 bg-white/80 backdrop-blur-sm p-2 rounded-md shadow text-sm">
            <p className="font-medium mb-1">选择区域类型:</p>
            <div className="flex gap-4">
              <label className="flex items-center gap-1 cursor-pointer">
                <input
                  type="radio"
                  name={`zoneType-${activeSource.url}`}
                  value="inside"
                  checked={zoneType === 'inside'}
                  onChange={handleZoneTypeChange}
                />
                店内 (Inside)
              </label>
              <label className="flex items-center gap-1 cursor-pointer">
                <input
                  type="radio"
                  name={`zoneType-${activeSource.url}`}
                  value="outside"
                  checked={zoneType === 'outside'}
                  onChange={handleZoneTypeChange}
                />
                店外 (Outside)
              </label>
            </div>
          </div>
        )}
        {activeSource.status === 'streaming' && activeSource.mjpegStreamUrl && activeSource.mjpegStreamUrl !== 'error' && (
          <img
            src={activeSource.mjpegStreamUrl}
            // src={"http://localhost:8003/video_feed"}
            alt="MJPEG 流"
            className="absolute top-0 left-0 w-full h-full object-contain z-0" 
          />
        )}
        {activeSource.status === 'streaming' && activeSource.mjpegStreamUrl && activeSource.mjpegStreamUrl === 'error' && (
          <div className="text-red-600 text-center p-10 flex flex-col items-center justify-center">
            <p className="font-semibold text-lg mb-2">错误</p>
            <p>无法连接到 RTSP 流。请检查流地址是否正确。</p>
          </div>
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
                strokeWidth={(isClosed ? LINE_STROKE_WIDTH : LINE_STROKE_WIDTH) / scale}
                closed={isClosed}
                lineCap="round"
                lineJoin="round"
                listening={false}
                fill={isClosed ? polygonFillColor : 'transparent'}
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
                  stroke={isSelected ? SELECTED_LINE_COLOR : (isHovered ? HOVER_LINE_COLOR : 'transparent')}
                  strokeWidth={(isSelected ? SELECTED_LINE_STROKE_WIDTH : HIT_STROKE_WIDTH) / scale }
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
    zoneType,
    polygonFillColor,
    selectedLineIndices, 
    hoveredLineIndex,
    canDraw,
    canSelectLines,
    isHoveringStartPoint,
    handleStageMouseDown,
    handleLineClick,
    handleZoneTypeChange,
    handleStartDotMouseEnter,
    handleStartDotMouseLeave,
    handleLineHover
  ]);

  return (
    <div className="w-full h-full p-2 bg-gray-100">
      <div className="flex flex-col h-full gap-2">
        <ConfigHeader />

        <div className="flex flex-1 h-full gap-2 overflow-hidden">
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
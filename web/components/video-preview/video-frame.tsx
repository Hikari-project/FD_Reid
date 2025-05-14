'use client';

import React, { useState, useRef, useEffect } from 'react';
import { RtspSourceInfo } from '@/store/types';
import { AlertTriangle, Loader2, Square } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';

interface VideoFrameProps {
  source: RtspSourceInfo;
}

interface ROIRectangle {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

const VideoFrame: React.FC<VideoFrameProps> = ({ source }) => {
  const streamUrl = source.mjpegStreamUrl || source.rawMjpegStreamUrl;
  const [loadError, setLoadError] = useState(false);
  const [isDrawingROI, setIsDrawingROI] = useState(false);
  const [roi, setRoi] = useState<ROIRectangle | null>(null);
  const [tempRoi, setTempRoi] = useState<ROIRectangle | null>(null);
  const [startPoint, setStartPoint] = useState<{x: number, y: number} | null>(null);
  const [imageLoaded, setImageLoaded] = useState(false);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  
  const imgRef = useRef<HTMLImageElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  
  const handleImageLoad = () => {
    console.log("图像已加载完成");
    setImageLoaded(true);
    
    setTimeout(() => {
      forceUpdateROI();
    }, 500);
  };
  
  const forceUpdateROI = () => {
    setRoi(null);
    setRefreshTrigger(prev => prev + 1);
  };
  
  useEffect(() => {
    const resizeObserver = new ResizeObserver(() => {
      if (imageLoaded && imgRef.current) {
        console.log("视频容器尺寸改变，重新计算ROI");
        forceUpdateROI();
      }
    });
    
    if (containerRef.current) {
      resizeObserver.observe(containerRef.current);
    }
    
    return () => {
      resizeObserver.disconnect();
    };
  }, [imageLoaded]);
  
  useEffect(() => {
    console.log("useEffect触发: imageLoaded=", imageLoaded, "refreshTrigger=", refreshTrigger);
    
    if (imageLoaded && imgRef.current && !roi) {
      console.log("准备设置默认ROI");
      requestAnimationFrame(() => {
        if (imgRef.current) {
          const rect = imgRef.current.getBoundingClientRect();
          console.log("图像尺寸:", rect.width, "x", rect.height);
          
          const centerX = rect.width / 2;
          const centerY = rect.height / 2;
          
          const roiWidth = rect.width * 0.6;
          const roiHeight = rect.height * 0.7;
          
          const x1 = centerX - roiWidth / 2;
          const y1 = centerY - roiHeight / 2;
          const x2 = centerX + roiWidth / 2;
          const y2 = centerY + roiHeight / 2;
          
          const defaultRoi = { x1, y1, x2, y2 };
          
          console.log("设置默认ROI:", defaultRoi);
          setRoi(defaultRoi);
          
          sendRoiToBackend(defaultRoi);
        }
      });
    }
  }, [imageLoaded, roi, refreshTrigger]);
  
  const handleMouseDown = (e: React.MouseEvent) => {
    if (!isDrawingROI || !imgRef.current) return;
    
    const rect = imgRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    setStartPoint({ x, y });
    setTempRoi({ x1: x, y1: y, x2: x, y2: y });
  };
  
  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDrawingROI || !startPoint || !imgRef.current) return;
    
    const rect = imgRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    setTempRoi({
      x1: startPoint.x,
      y1: startPoint.y,
      x2: x,
      y2: y
    });
  };
  
  const handleMouseUp = () => {
    if (!isDrawingROI || !tempRoi) return;
    
    const roiRect = {
      x1: Math.min(tempRoi.x1, tempRoi.x2),
      y1: Math.min(tempRoi.y1, tempRoi.y2),
      x2: Math.max(tempRoi.x1, tempRoi.x2),
      y2: Math.max(tempRoi.y1, tempRoi.y2)
    };
    
    setRoi(roiRect);
    setStartPoint(null);
    setIsDrawingROI(false);
    
    sendRoiToBackend(roiRect);
  };
  
  const sendRoiToBackend = async (roiRect: ROIRectangle) => {
    try {
      console.log("准备发送ROI到后端:", roiRect);
      console.log("当前视频源URL:", source.url);
      
      // 创建ROI数据
      const roiData = {
        sourceUrl: source.url,
        roi: [
          Math.round(roiRect.x1),
          Math.round(roiRect.y1), 
          Math.round(roiRect.x2), 
          Math.round(roiRect.y2)
        ]
      };
      
      console.log("发送数据:", JSON.stringify(roiData));
      
      const response = await fetch('/api/set-roi', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(roiData),
      });
      
      const result = await response.json();
      console.log("服务器响应:", result);
      
      if (response.ok) {
        toast.success('ROI区域设置成功！');
      } else {
        toast.error(`ROI区域设置失败: ${result.detail || '未知错误'}`);
        console.error('Failed to set ROI:', result);
      }
    } catch (error) {
      toast.error('网络错误，请重试');
      console.error('Error setting ROI:', error);
    }
  };
  
  const startDrawingROI = () => {
    setIsDrawingROI(true);
    setTempRoi(null);
    toast.info('请在视频上拖拽绘制矩形ROI区域');
  };
  
  const clearROI = () => {
    setRoi(null);
    setTempRoi(null);
    setTimeout(() => {
      forceUpdateROI();
    }, 100);
  };

  return (
    <div className={`w-full h-full flex flex-col justify-center items-center overflow-hidden relative ${streamUrl ? '' : 'bg-gray-200'} rounded-md`}>
      <div className="flex space-x-2 mb-2">
        <Button
          variant="outline"
          size="sm"
          onClick={startDrawingROI}
          disabled={!streamUrl || loadError}
        >
          <Square size={16} className="mr-1" />
          绘制ROI区域
        </Button>
        {roi && (
          <Button
            variant="outline"
            size="sm"
            onClick={clearROI}
          >
            清除ROI区域
          </Button>
        )}
        <Button
          variant="outline"
          size="sm"
          onClick={forceUpdateROI}
        >
          重置ROI位置
        </Button>
      </div>
      <div 
        className="relative w-full h-0 pt-[56.25%]"
        ref={containerRef}
      >
        <div 
          className="absolute inset-0 flex items-center justify-center"
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
        >
          {streamUrl && !loadError ? (
            <>
              <img
                ref={imgRef}
                src={streamUrl}
                alt={`Stream for ${source.url}`}
                className="w-full h-full object-cover rounded-md"
                onLoad={handleImageLoad}
                onError={(e) => {
                  console.error(`Error loading stream: ${streamUrl}`);
                  setLoadError(true);
                }}
              />
              {(roi || tempRoi) && (
                <div 
                  className="absolute pointer-events-none"
                  style={{
                    left: `${(roi || tempRoi)!.x1}px`,
                    top: `${(roi || tempRoi)!.y1}px`,
                    width: `${(roi || tempRoi)!.x2 - (roi || tempRoi)!.x1}px`,
                    height: `${(roi || tempRoi)!.y2 - (roi || tempRoi)!.y1}px`,
                    border: '3px solid blue',
                    backgroundColor: 'rgba(0, 0, 255, 0.1)'
                  }}
                >
                </div>
              )}
            </>
          ) : streamUrl && loadError ? (
            <div className="flex flex-col items-center justify-center text-gray-500">
              <AlertTriangle className="h-10 w-10 text-amber-500 mb-2" />
              <span className="text-center">视频流加载失败</span>
              <span className="text-xs text-gray-400 mt-1">{source.url}</span>
            </div>
          ) : (
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
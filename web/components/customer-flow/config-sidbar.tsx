'use client'

import React, { useMemo, useState } from 'react'
import { backendUrl, useAppStore } from '@/store/useCustomerAnalysis';
import type { SourceStatus } from '@/store/types';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { toast } from 'sonner';
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle, 
  DialogDescription,
  DialogFooter
} from '../ui/dialog';

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

// 添加状态名称到中文的转换函数
const getStatusName = (status: SourceStatus): string => {
  switch (status) {
    case 'idle':            return '空闲';
    case 'loading_frame':   return '加载中';
    case 'frame_loaded':    return '已加载';
    case 'annotating':      return '标注中';
    case 'annotated':       return '已标注';
    case 'analyzing':       return '分析中';
    case 'streaming':       return '流传输中';
    case 'error_frame':     return '帧错误';
    case 'error_analysis':  return '分析错误';
    case 'error_rtsp':      return '流错误';
    default:                return '未知状态';
  }
};

export default function ConfigSidebar() {
  const sourcesObject = useAppStore(state => state.rtspSources);
  const sources = useMemo(() => Object.values(sourcesObject), [sourcesObject]);
  
  const activeSourceUrl = useAppStore((state) => state.activeSourceUrl);
  
  const setActiveSource = useAppStore(state => state.setActiveSource);
  const removeRtspSource = useAppStore(state => state.removeRtspSource);

  // 添加状态管理删除确认对话框
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [sourceToDelete, setSourceToDelete] = useState<string | null>(null);

  const handleSelectSource = (url: string) => {
    setActiveSource(url);
  };

  const openDeleteDialog = (e: React.MouseEvent, url: string) => {
    e.stopPropagation();
    setSourceToDelete(url);
    setIsDeleteDialogOpen(true);
  };

  const confirmDelete = () => {
    if (sourceToDelete) {
      try {
        removeRtspSource(sourceToDelete);
        void fetch(`${backendUrl}/customer-flow/stop-analysis`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            rtsp_url: sourceToDelete,
          }),
        });
        toast.success("移除RTSP源成功");
      } catch (error) {
        console.error("Error removing source:", error);
        toast.error("移除RTSP源失败.");
      }
      setSourceToDelete(null);
      setIsDeleteDialogOpen(false);
    }
  };

  const cancelDelete = () => {
    setSourceToDelete(null);
    setIsDeleteDialogOpen(false);
  };

  return (
    <div className="w-72 h-[calc(100dvh-12.5rem)] bg-white rounded-md shadow-sm pt-4 flex flex-col">
      <div className='flex justify-between items-center'>
        <h3 className="font-medium text-lg text-gray-700 w-full mb-2 px-4">RTSP 流源</h3>
        
      </div>

      {sources.length === 0 ? (
        <div className="text-gray-500 text-sm py-6 text-center flex-1 px-4">
            还没有添加 RTSP 流源。使用上面的控件添加 RTSP 流源。
        </div>
      ) : (
        <div className="w-full space-y-2 h-full overflow-y-auto flex-1 px-3 pb-3">
          {sources.map((source) => source.url !== 'error' && (
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
                  onClick={(e) => openDeleteDialog(e, source.url)}
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
                        {getStatusName(source.status)}
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
      {/* 删除确认弹窗 */}
      <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>确认删除</DialogTitle>
            <DialogDescription>
              您确定要删除此RTSP源吗？
              你可以重新添加当前源，但是会触发算法重新运行。
            </DialogDescription>
          </DialogHeader>
          {sourceToDelete && (
            <div className="py-2">
              <p className="text-sm font-medium text-gray-700">要删除的RTSP源:</p>
              <p className="text-sm text-gray-600 mt-1 break-all">{sourceToDelete}</p>
            </div>
          )}
          <DialogFooter className="flex space-x-2 sm:justify-end">
            <Button type="button" variant="outline" onClick={cancelDelete}>
              取消
            </Button>
            <Button type="button" variant="destructive" onClick={confirmDelete}>
              删除
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
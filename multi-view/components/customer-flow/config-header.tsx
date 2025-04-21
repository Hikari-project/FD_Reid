'use client'

import React, { useState, useRef, useCallback, ChangeEvent } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useAppStore, selectActiveSourceData } from '@/store/useCustomerAnalysis';
import { toast } from 'sonner';
import EditBox from './edit-box';
import { useBoxStore } from '@/store/useBoxmanagement';


export default function ConfigHeader() {
  const [manualRtspInput, setManualRtspInput] = useState<string>('');
  const [selectedFileName, setSelectedFileName] = useState<string>('');
  const [isEditBoxOpen, setIsEditBoxOpen] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const addRtspSources = useAppStore(state => state.addRtspSources);
  const undoLastPoint = useAppStore(state => state.undoLastPoint);
  const clearAnnotation = useAppStore(state => state.clearAnnotation);
  const startAnalysis = useAppStore(state => state.startAnalysis);
  const setGlobalStatus = useAppStore(state => state.setGlobalStatus);
  const setAnnotationMode = useAppStore(state => state.setAnnotationMode);
  
  const activeSource = useAppStore(selectActiveSourceData);
  const activeSourceUrl = useAppStore(state => state.activeSourceUrl);
  const annotationMode = useAppStore(state => state.annotationMode);
  const globalStatus = useAppStore(state => state.globalStatus);
  const canUndo =
    !!activeSource &&
    annotationMode === 'drawing' &&
    !activeSource.annotation.isClosed &&
    activeSource.annotation.points.length > 0;

  const canClear =
    !!activeSource &&
    (activeSource.annotation.points.length > 0 ||
     activeSource.annotation.selectedLineIndices.length > 0 ||
     activeSource.annotation.isClosed);

  const canStartAnalysis =
    !!activeSource &&
    activeSource.status === 'annotated' &&
    activeSource.annotation.isClosed &&
    activeSource.annotation.selectedLineIndices.length > 0;

   const canManuallyEnterAnnotation =
    !!activeSource &&
    (activeSource.status === 'frame_loaded' || activeSource.status === 'annotated' || activeSource.status === 'error_analysis') &&
    annotationMode === 'idle';

  const isProcessing = globalStatus === 'loading_file' || globalStatus === 'processing_file';
  const isSourceBusy = !!activeSource && ['loading_frame', 'analyzing', 'streaming'].includes(activeSource.status);

  const currentBox = useBoxStore(state => state);

  const handleFileChange = useCallback((event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) {
      setSelectedFileName('');
      return;
    }

    if (file.type !== 'text/plain') {
       toast.error("文件类型错误. 请上传一个 .txt 文件.");
       if (fileInputRef.current) fileInputRef.current.value = '';
       setSelectedFileName('');
       return;
    }

    setSelectedFileName(file.name);
    setGlobalStatus('loading_file');
    toast.promise(
      new Promise<void>(async (resolve, reject) => {
        try {
          const reader = new FileReader();
          reader.onload = async (e) => {
          const text = e.target?.result as string;
          if (text) {
            const urls = text
            .split('\n')
            .map(line => line.trim())
            .filter(line => line.length > 0 && (line.startsWith('rtsp://') || line.startsWith('http://') || line.startsWith('https://'))); // Basic validation

            if (urls.length === 0) {
                throw new Error("No valid RTSP URLs found in the file.");
            }

            setGlobalStatus('processing_file');
            await addRtspSources(urls);
            setGlobalStatus('idle');
            resolve();
          } else {
            throw new Error("File is empty or could not be read.");
          }
          };
          reader.onerror = () => {
            throw new Error("Error reading file.");
          };
          reader.readAsText(file);
        } catch (error: any) {
          console.error("File processing error:", error);
          setGlobalStatus('error', error.message || 'Failed to process file');
          setSelectedFileName('');
          reject(error);
        } finally {
          if (fileInputRef.current) fileInputRef.current.value = '';
          setGlobalStatus('idle');
        }
      }),
      {
        loading: '处理文件中...',
        success: 'RTSP源添加成功!',
        error: (err) => `错误: ${err.message || '处理文件失败'}`,
      }
    );
  }, [addRtspSources, setGlobalStatus]);

  const handleManualAdd = useCallback(async () => {
    const url = manualRtspInput.trim();
    if (!url) {
      toast.error("请输入一个 RTSP URL.");
      return;
    }
    if (!url.startsWith('rtsp://')) {
      toast.error("URL格式错误. 必须以 rtsp:// 开头");
      return;
    }

    // if (url !== 'rtsp://47.97.71.139:8003/video_feed4' 
    //   && url !== 'rtsp://47.97.71.139:8003/video_feed3'
    //   && url !== 'rtsp://47.97.71.139:8003/video_feed2'
    //   && url !== 'rtsp://47.97.71.139:8003/video_feed1'
    // ) {
    //   setTimeout(() => {
    //     toast.error("连接失败，请检查 URL 是否正确。");
    //   }, 2000);
    //   return;
    // }

    setGlobalStatus('processing_file');
    toast.promise(
      addRtspSources([url]),
      {
        loading: `RTSP 源添加中...`,
        success: `RTSP 源 ${url} 添加成功.`,
        error: `RTSP 源 ${url} 添加失败.`
      }
    )
    setManualRtspInput('');
    
  }, [manualRtspInput, addRtspSources, setGlobalStatus]);

  const handleUndoClick = useCallback(() => {
    if (canUndo && activeSourceUrl) {
      undoLastPoint(activeSourceUrl);
    }
  }, [canUndo, activeSourceUrl, undoLastPoint]);

  const handleClearClick = useCallback(() => {
    if (canClear && activeSourceUrl) {
      clearAnnotation(activeSourceUrl);
      toast.success("标注清除.");
    }
  }, [canClear, activeSourceUrl, clearAnnotation]);

  const handleStartAnalysisClick = useCallback(() => {
    if (canStartAnalysis && activeSourceUrl) {
      toast.promise(
        startAnalysis(activeSourceUrl),
        {
          loading: '开始分析...',
          success: '分析开始, 等待流...',
          error: (err) => `分析错误: ${err?.message || '未知错误'}`,
        }
      );
    } else if (activeSource && !canStartAnalysis) {
      if (!activeSource.annotation.isClosed) {
        toast.error("请先闭合多边形.");
      } else if (activeSource.annotation.selectedLineIndices.length === 0) {
        toast.error("请至少选择一条过线.");
      } else {
        toast.error("无法在当前状态下开始分析.");
      }
    }
  }, [canStartAnalysis, activeSourceUrl, startAnalysis, activeSource]);

  const handleEnterAnnotationMode = useCallback(() => {
    if (canManuallyEnterAnnotation && activeSource) {
      const targetMode = activeSource.annotation.isClosed ? 'line_selection' : 'drawing';
      setAnnotationMode(targetMode);
      toast.success(`Entered ${targetMode === 'drawing' ? 'drawing' : 'line selection'} mode.`);
    }
  }, [canManuallyEnterAnnotation, activeSource, setAnnotationMode]);


  return (
    <div className="bg-white p-4 rounded-md shadow-sm">
      <div className="flex flex-wrap justify-between items-start gap-4">
        <div className="flex flex-col gap-4">
          <div className="flex items-center gap-2">
             <span className="font-medium text-sm">RTSP 流文件 :</span>
            <div className="flex flex-1 items-center border rounded-md overflow-hidden min-w-[250px]">
              <input
                id="file-upload"
                type="file"
                accept=".txt"
                onChange={handleFileChange}
                ref={fileInputRef}
                className="hidden"
                disabled={isProcessing}
              />
              <label
                htmlFor="file-upload"
                className={`px-3 py-2 cursor-pointer border-r whitespace-nowrap ${isProcessing ? 'bg-gray-300 text-gray-500 cursor-not-allowed' : 'bg-gray-100 hover:bg-gray-200 text-gray-700'}`}
              >
                {isProcessing ? '处理中...' : '选择一个 .txt 文件'}
              </label>
              <div className={`px-3 py-2 flex-1 text-sm truncate ${selectedFileName ? 'text-gray-800' : 'text-gray-400'}`}>
                {selectedFileName || '没有文件选中'}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-6">
            <span className="font-medium text-sm w-20 whitespace-nowrap">单个 RTSP 流 :</span>
            <div className="flex items-center border rounded-md overflow-hidden flex-1 min-w-[250px]">
              <Input
                value={manualRtspInput}
                onChange={(e) => setManualRtspInput(e.target.value)}
                placeholder="输入单个 RTSP URL (e.g., rtsp://...)"
                className="rounded-r-none flex-1 border-0 focus:ring-0"
                disabled={isProcessing}
              />
              <Button
                onClick={handleManualAdd}
                className="bg-blue-500 hover:bg-blue-600 rounded-l-none px-3"
                disabled={isProcessing || !manualRtspInput.trim()}
              >
                添加
              </Button>
            </div>
          </div>
        </div>
        <div className='flex flex-col gap-2'>
        <div className="flex items-center gap-3 justify-end flex-wrap">
            {/* <Button
                onClick={handleEnterAnnotationMode}
                disabled={!canManuallyEnterAnnotation || isProcessing || isSourceBusy}
                variant="outline"
                title={!activeSource ? "Select a source first" : !canManuallyEnterAnnotation ? "Cannot annotate in current state" : "Start/Edit Annotation"}
            >
                编辑标注
            </Button>

           <div className="border-l h-8 mx-2"></div> */}

          <Button
            onClick={handleUndoClick}
            disabled={!canUndo || isProcessing || isSourceBusy}
            variant="outline"
            title={!canUndo ? "Cannot undo" : "Undo last point"}
          >
            撤销点
          </Button>
          <Button
            onClick={handleClearClick}
            disabled={!canClear || isProcessing || isSourceBusy}
            variant="outline"
            title={!canClear ? "Nothing to clear" : "Clear current annotation"}
          >
            清除标注
          </Button>
            <Button
              onClick={handleStartAnalysisClick}
              disabled={!canStartAnalysis || isProcessing || isSourceBusy}
              className="bg-green-500 hover:bg-green-600 text-white"
              title={!canStartAnalysis ? "Annotation incomplete or source busy" : "Start customer flow analysis"}
            >
              开始分析
            </Button>
        </div>
          <div className='flex justify-end'>
            <Button 
              onClick={() => setIsEditBoxOpen(true)} 
              disabled={isProcessing || isSourceBusy}
              className='bg-blue-500 hover:bg-blue-600'
            >
              编辑盒子
            </Button>
          </div>
        </div>
      </div>

      <EditBox
        isOpen={isEditBoxOpen}
        onOpenChange={setIsEditBoxOpen}
      />
    </div>
  );
}
'use client'

import React, { useState, useRef, useCallback, ChangeEvent } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useAppStore, selectActiveSourceData } from '@/store/useCustomerAnalysis';
import { toast } from 'sonner';


export default function ConfigHeader() {
  const [manualRtspInput, setManualRtspInput] = useState<string>('');
  const [selectedFileName, setSelectedFileName] = useState<string>('');
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

  const handleFileChange = useCallback((event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) {
      setSelectedFileName('');
      return;
    }

    if (file.type !== 'text/plain') {
       toast.error("Invalid file type. Please upload a .txt file.");
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
            }
        }),
        {
            loading: 'Processing file...',
            success: 'Sources added successfully!',
            error: (err) => `Error: ${err.message || 'Failed to process file'}`,
        }
    );
  }, [addRtspSources, setGlobalStatus]);

  const handleManualAdd = useCallback(async () => {
    const url = manualRtspInput.trim();
    if (!url) {
        toast.error("Please enter an RTSP URL.");
        return;
    }
    if (!url.startsWith('rtsp://') && !url.startsWith('http://') && !url.startsWith('https://')) {
       toast.error("Invalid URL format. Must start with rtsp://, http:// or https://");
       return;
    }

    setGlobalStatus('processing_file');
    toast.promise(
        addRtspSources([url]),
        {
            loading: `Adding ${url}...`,
            success: `Source ${url} added.`,
            error: `Failed to add source ${url}.`
        }
    )
    //   .finally(() => {
    //     setManualRtspInput(''); 
    // });
  }, [manualRtspInput, addRtspSources, setGlobalStatus]);

  const handleUndoClick = useCallback(() => {
    if (canUndo && activeSourceUrl) {
      undoLastPoint(activeSourceUrl);
    }
  }, [canUndo, activeSourceUrl, undoLastPoint]);

  const handleClearClick = useCallback(() => {
    if (canClear && activeSourceUrl) {
      clearAnnotation(activeSourceUrl);
      toast.success("Annotation cleared.");
    }
  }, [canClear, activeSourceUrl, clearAnnotation]);

  const handleStartAnalysisClick = useCallback(() => {
    if (canStartAnalysis && activeSourceUrl) {
       toast.promise(
          startAnalysis(activeSourceUrl),
          {
             loading: 'Starting analysis...',
             success: 'Analysis started, waiting for stream...',
             error: (err) => `Analysis Error: ${err?.message || 'Unknown error'}`,
          }
       );
    } else if (activeSource && !canStartAnalysis) {
        if (!activeSource.annotation.isClosed) {
            toast.error("Please close the polygon first.");
        } else if (activeSource.annotation.selectedLineIndices.length === 0) {
            toast.error("Please select at least one crossing line.");
        } else {
            toast.error("Cannot start analysis in the current state.");
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
                {selectedFileName || 'No file selected'}
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

        <div className="flex items-center gap-3 justify-end flex-wrap">
            <Button
                onClick={handleEnterAnnotationMode}
                disabled={!canManuallyEnterAnnotation || isProcessing || isSourceBusy}
                variant="outline"
                title={!activeSource ? "Select a source first" : !canManuallyEnterAnnotation ? "Cannot annotate in current state" : "Start/Edit Annotation"}
            >
                编辑标注
            </Button>

           <div className="border-l h-8 mx-2"></div>

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
      </div>
    </div>
  );
}
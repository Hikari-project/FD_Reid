import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';
import { persist, createJSONStorage } from 'zustand/middleware';
import type {
  AppState,
  AppActions,
  RtspSourceInfo,
  Point,
  ZoneType,
  RtspResponse,
  initialRtspStreamInfo
} from '@/store/types';

//export const backendUrl = process.env.VITE_BACKEND_URL;
export const backendUrl = 'http://127.0.0.1:3002' 

async function fetchFirstFrameFromBackend(
  rtspUrl: string
): Promise<{ 
    status: string; 
    frame_url: string; 
    mjpeg_stream: string;
    size: {
      height: number;
      width: number;
    }
  }> {
  const response = await fetch(`${backendUrl}/customer-flow/check-rtsp`, { 
    method: 'POST', 
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ 
      rtsp_url: rtspUrl
    }) });

  if (!response.ok) throw new Error('Failed to fetch frame');

  const data = await response.json();
  console.log("fetchFirstFrameFromBackend response", data);
  return data;
}

async function startAnalysisOnBackend(
    rtspUrl: string,
    polygonPoints: Point[],
    crossingLineEndpoints: Point[][],
    zoneType: 'inside' | 'outside'
  ): Promise<{ 
    ret: number,
    message: string,
    res: Array<{
      source_url: string,
      mjpeg_url: string,
      is_rtsp: boolean,
      stream_index: number,
    }>
  }> {
  const transformedPoints = polygonPoints.map(p => [Math.floor(p.x), Math.floor(p.y)]);
  const transformedCrossingLineEndpoints = crossingLineEndpoints.map(line => 
    line.map(p => [Math.floor(p.x), Math.floor(p.y)])
  );

  const payload = {
    videos: [
      {
        rtsp_url: rtspUrl,
        points: transformedPoints,
        passway: transformedCrossingLineEndpoints,
        area_type: zoneType,
      }
    ]
  }

  const response = await fetch(`${backendUrl}/customer-flow/custome-analysisV2`, {
    method: 'POST', 
    body: JSON.stringify(payload), 
    headers: {
      'Content-Type': 'application/json'
    } 
  });

  if (!response.ok) throw new Error('Failed to start analysis');

  const data = await response.json();
  console.log("analysis response", data);
  return data;
}

// New function to fetch initial streams from backend
async function fetchInitialStreamsFromBackend(): Promise<RtspResponse> {
  const response = await fetch(`${backendUrl}/customer-flow/get-rtsp`);

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ message: 'Failed to fetch initial streams, server response not JSON or no details provided' }));
    throw new Error(errorData.message || `Failed to fetch initial streams. Status: ${response.status}`);
  }
  return response.json();
}

async function updateSourceNameOnBackend(url: string, name: string) {
  const response = await fetch(`${backendUrl}/customer-flow/set-rtsp-name`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ 
      rtsp_url: url, 
      name: name 
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ message: 'Failed to update source name, server response not JSON or no details provided' }));
    throw new Error(errorData.message || `Failed to update source name. Status: ${response.status}`);
  }
  return response.json();
}

const initialState: AppState = {
  rtspSources: {},
  activeSourceUrl: null,
  annotationMode: 'idle',
  globalStatus: 'idle',
  globalErrorMessage: null,
};

// --- 管理标注盒子的状态 ---
export const useAppStore = create<AppState & AppActions>()(
  persist(
    immer((set, get) => ({
      ...initialState,

      initializeStreamsOnLogin: async () => {
        set(state => {
          state.globalStatus = 'loading_file'; 
          state.globalErrorMessage = null;
          state.rtspSources = {}; // Clear existing sources on new login load
          state.activeSourceUrl = null;
          state.annotationMode = 'idle';
        });

        try {
          const response = await fetchInitialStreamsFromBackend();
          
          if (response.ret !== 0 || !response.HandleRTSPData) {
            throw new Error('Backend error or invalid data for initial streams.');
          }

          const newRtspSources: Record<string, RtspSourceInfo> = {};
          const loadedUrls: string[] = [];

          for (const rtspUrlKey in response.HandleRTSPData) {
            const streamData = response.HandleRTSPData[rtspUrlKey];

            let mjpegStreamUrlForState: string | null = null;
            let rawMjpegStreamUrlForState: string | null = null;
            const backendProcessedMjpeg = streamData.mjpeg_url;
            const backendRawMjpeg = streamData.mjpeg_stream;

            if (backendProcessedMjpeg && backendProcessedMjpeg.trim() !== "") {
              mjpegStreamUrlForState = `${backendUrl}${backendProcessedMjpeg}`;
              if (backendRawMjpeg && backendRawMjpeg.trim() !== "") {
                rawMjpegStreamUrlForState = `${backendUrl}${backendRawMjpeg}`;
              }
            } else if (backendRawMjpeg && backendRawMjpeg.trim() !== "") {
              mjpegStreamUrlForState = `${backendUrl}${backendRawMjpeg}`;
              // rawMjpegStreamUrlForState remains null as the raw stream is now the primary
            } else {
              // Filter out rule: if neither mjpeg_url nor mjpeg_stream is available, filter out.
              console.warn(`Stream ${streamData.rtsp_url} filtered out: no usable MJPEG stream URL.`);
              continue; 
            }
            
            // If no frame_url, and no mjpegStream (already filtered above), what to do?
            // The logic above ensures mjpegStreamUrlForState is set if we proceed.

            const newSourceInfo: RtspSourceInfo = {
              url: streamData.rtsp_url,
              name: (streamData.name && streamData.name.trim() !== "") ? streamData.name : streamData.rtsp_url,
              firstFrameDataUrl: streamData.frame_url ? `${backendUrl}${streamData.frame_url}` : null,
              annotation: { points: [], isClosed: false, selectedLineIndices: [], zoneType: null },
              mjpegStreamUrl: mjpegStreamUrlForState, // This will be set if not filtered
              rawMjpegStreamUrl: rawMjpegStreamUrlForState,
              // If mjpegStreamUrlForState is set, it means we have a stream to show, status 'streaming'.
              // If only firstFrameDataUrl is set (no mjpeg), status 'frame_loaded'.
              // Otherwise 'idle'.
              status: mjpegStreamUrlForState ? 'streaming' : (streamData.frame_url ? 'frame_loaded' : 'idle'),
              errorMessage: null,
              imageDimensions: undefined, // To be populated by _fetchFirstFrame or similar if needed
            };
            newRtspSources[streamData.rtsp_url] = newSourceInfo;
            loadedUrls.push(streamData.rtsp_url);
          }

          set(state => {
            state.rtspSources = newRtspSources;
            if (loadedUrls.length > 0) {
              state.activeSourceUrl = loadedUrls[0];
              const activeSource = state.rtspSources[loadedUrls[0]];
              if (activeSource) {
                // Match logic from setActiveSource and setSourceFrame for consistency
                if (activeSource.status === 'frame_loaded' || 
                    activeSource.status === 'annotating' || 
                    activeSource.status === 'annotated' ||
                    (activeSource.status === 'streaming' && activeSource.firstFrameDataUrl) // Allow annotation if streaming with frame
                   ) {
                  state.annotationMode = activeSource.annotation.isClosed ? 'line_selection' : 'drawing';
                } else {
                  state.annotationMode = 'idle';
                }
              } else {
                state.annotationMode = 'idle';
              }
            } else {
              state.activeSourceUrl = null;
              state.annotationMode = 'idle';
              state.globalErrorMessage = "No RTSP streams were loaded from the backend.";
            }
            state.globalStatus = 'idle';
          });

        } catch (error: any) {
          console.error('Error initializing RTSP streams on login:', error);
          set(state => {
            state.globalStatus = 'error';
            state.globalErrorMessage = error.message || 'Failed to load initial RTSP streams.';
            // state.rtspSources is already cleared at the beginning of the action
            // state.activeSourceUrl and state.annotationMode are also reset
          });
        }
      },

      setSourceName: async (url: string, name: string) => {
        await updateSourceNameOnBackend(url, name);

        set(state => {
          const source = state.rtspSources[url];
          if (source) {
            source.name = name;
          }
        });
      },

      addRtspSources: async (urls) => {
        const uniqueUrls = urls.filter(url => url.trim() && !get().rtspSources[url]);
        if (uniqueUrls.length === 0) {
          get().setGlobalStatus('idle', 'No valid RTSP URLs found in the file.');
          return;
        }

        set(state => {
          state.globalStatus = 'processing_file';
          state.globalErrorMessage = null;
          uniqueUrls.forEach(url => {
            state.rtspSources[url] = {
              url: url,
              firstFrameDataUrl: null,
              rawMjpegStreamUrl: null,
              annotation: { 
                points: [], 
                isClosed: false, 
                selectedLineIndices: [], 
                zoneType: null 
              },
              mjpegStreamUrl: null,
              status: 'idle', 
              errorMessage: null,
            };
          });
        });

        for (const url of uniqueUrls) {
          await get()._fetchFirstFrame(url);
        }

        set(state => {
          state.globalStatus = 'idle';
          if (!state.activeSourceUrl && uniqueUrls.length > 0) {
            state.activeSourceUrl = uniqueUrls[0];
            state.annotationMode = state.rtspSources[uniqueUrls[0]].annotation.isClosed ? 'line_selection' : 'drawing';
          }
        });
      },

      _fetchFirstFrame: async (url) => {
        if (!get().rtspSources[url]) return;

        set(state => {
          if (state.rtspSources[url]) {
            state.rtspSources[url].status = 'loading_frame';
            state.rtspSources[url].errorMessage = null;
          }
        });

        try {
          const { status, frame_url, mjpeg_stream, size } = await fetchFirstFrameFromBackend(url);
          if (status === 'success') {
            get().setSourceFrame(
              url, 
              `${backendUrl}${frame_url}`, 
              {width: size.width, height: size.height}, 
              undefined, 
              `${backendUrl}${mjpeg_stream}`
            );
          } else {
            get().setSourceFrame(url, null, undefined, 'Failed to fetch first frame');
          }
        } catch (error: any) {
          console.error(`Error fetching frame for ${url}:`, error);
          get().setSourceFrame(url, null, undefined, error.message || 'Failed to fetch first frame');
        }
      },

      setSourceFrame: (url, frameDataUrl, dimensions, error, rawMjpegStreamUrl) => {
        set(state => {
          const source = state.rtspSources[url];
          if (source) {
            if (error) {
              source.status = 'error_frame';
              source.errorMessage = error;
              source.firstFrameDataUrl = null;
              source.rawMjpegStreamUrl = null;
              source.imageDimensions = undefined;
            } else {
              source.firstFrameDataUrl = frameDataUrl;
              source.rawMjpegStreamUrl = rawMjpegStreamUrl ?? null;
              source.status = 'frame_loaded';
              source.errorMessage = null;
              source.imageDimensions = dimensions;
              if (state.activeSourceUrl === url) {
                  state.annotationMode = source.annotation.isClosed ? 'line_selection' : 'drawing';
              }
            }
          }
        });
      },

      removeRtspSource: (url) => {
        set(state => {
          delete state.rtspSources[url];
          if (state.activeSourceUrl === url) {
            const remainingUrls = Object.keys(state.rtspSources);
            state.activeSourceUrl = remainingUrls.length > 0 ? remainingUrls[0] : null;
            state.annotationMode = state.activeSourceUrl ?
              (state.rtspSources[state.activeSourceUrl]?.annotation.isClosed ? 'line_selection' : 'drawing')
                : 'idle';
          }
        });
      },

      setActiveSource: (url) => {
        set(state => {
          state.activeSourceUrl = url;
          if (url && state.rtspSources[url]) {
            const source = state.rtspSources[url];
            if (source.status === 'frame_loaded' || source.status === 'annotating' || source.status === 'annotated') {
                state.annotationMode = source.annotation.isClosed ? 'line_selection' : 'drawing';
            } else {
                state.annotationMode = 'idle';
            }
          } else {
            state.annotationMode = 'idle';
          }
        });
      },

      resetSourceStatus: (url) => {
          set(state => {
              const source = state.rtspSources[url];
              if(source) {
                  source.status = source.firstFrameDataUrl ? 'frame_loaded' : 'idle';
                  source.mjpegStreamUrl = null;
                  source.rawMjpegStreamUrl = null;
                  source.errorMessage = null;
                  if (state.activeSourceUrl === url) {
                      state.annotationMode = source.annotation.isClosed ? 'line_selection' : 'drawing';
                  }
              }
          })
      },

      setAnnotationMode: (mode) => {
        set({ annotationMode: mode });
      },

      addAnnotationPoint: (url, point) => {
        set(state => {
          const source = state.rtspSources[url];
          if (source && state.annotationMode === 'drawing' && !source.annotation.isClosed) {
            const lastPoint = source.annotation.points[source.annotation.points.length - 1];
            if (!lastPoint || lastPoint.x !== point.x || lastPoint.y !== point.y) {
                source.annotation.points.push(point);
                source.status = 'annotating';
            }
          }
        });
      },

      undoLastPoint: (url) => {
        set(state => {
          const source = state.rtspSources[url];
          if (source && state.annotationMode === 'drawing' && !source.annotation.isClosed && source.annotation.points.length > 0) {
            source.annotation.points.pop();
            if (source.annotation.points.length === 0) {
                source.status = 'frame_loaded';
            }
          }
        });
      },

      clearAnnotation: (url) => {
        set(state => {
          const source = state.rtspSources[url];
          if (source) {
            source.annotation.points = [];
            source.annotation.isClosed = false;
            source.annotation.selectedLineIndices = [];
            source.annotation.zoneType = null;
            if (['annotating', 'annotated', 'analyzing', 'streaming', 'error_analysis'].includes(source.status)) {
                source.status = source.firstFrameDataUrl ? 'frame_loaded' : 'idle';
            }
            source.mjpegStreamUrl = null;
            source.rawMjpegStreamUrl = null;
            if(state.activeSourceUrl === url) {
                state.annotationMode = 'drawing';
            }
          }
        });
      },

      closePolygon: (url) => {
        set(state => {
          const source = state.rtspSources[url];
          if (source && state.annotationMode === 'drawing' && !source.annotation.isClosed && source.annotation.points.length >= 3) {
            source.annotation.isClosed = true;
            source.status = 'annotated';
            if(state.activeSourceUrl === url) {
                state.annotationMode = 'line_selection';
            }
          }
        });
      },

      toggleLineSelection: (url, lineIndex) => {
        set(state => {
          const source = state.rtspSources[url];
          if (source && state.annotationMode === 'line_selection' && source.annotation.isClosed) {
            const selected = source.annotation.selectedLineIndices;
            const indexPos = selected.indexOf(lineIndex);
            if (indexPos > -1) {
              selected.splice(indexPos, 1);
            } else {
              selected.push(lineIndex);
              selected.sort((a, b) => a - b);
            }
            source.status = 'annotated';
          }
        });
      },

      startAnalysis: async (url) => {
        const source = get().rtspSources[url];
        let errorMessage = null;
        if (!source || !source.annotation.isClosed) {
          errorMessage = 'Annotation polygon is not closed.';
        } else if (source.annotation.selectedLineIndices.length === 0) {
          errorMessage = 'No crossing lines selected.';
        } else if (!source.annotation.zoneType) {
            errorMessage = 'Inside/Outside zone type not selected.';
        }

        if (errorMessage) {
          console.warn(`Cannot start analysis for ${url}: ${errorMessage}`);
          set(state => {
              if(state.rtspSources[url]) {
                  state.rtspSources[url].status = 'error_analysis';
                  state.rtspSources[url].errorMessage = errorMessage;
                  if (state.activeSourceUrl === url && state.rtspSources[url].annotation.isClosed) {
                      state.annotationMode = 'line_selection';
                  }
              }
          });
          return;
        }

        const zoneType = source.annotation.zoneType!;

        set(state => {
          state.rtspSources[url].status = 'analyzing';
          state.rtspSources[url].errorMessage = null;
          state.rtspSources[url].mjpegStreamUrl = null;
          if (state.activeSourceUrl === url) {
              state.annotationMode = 'idle';
          }
        });

        try {
          const points = source.annotation.points;
          const crossingLineEndpoints = source.annotation.selectedLineIndices.map(startIndex => {
            const endIndex = (startIndex + 1) % points.length;
            return [points[startIndex], points[endIndex]];
          });

          const analysisResponse = await startAnalysisOnBackend(
            url,
            source.annotation.points,
            crossingLineEndpoints,
            zoneType
          );

          if (analysisResponse.ret !== 0 || !analysisResponse.res || analysisResponse.res.length === 0) {
            throw new Error(analysisResponse.message || 'Analysis failed on backend.');
          }

          const mjpegUrl = analysisResponse.res[0].mjpeg_url;

          get().setMjpegStream(url, `${backendUrl}${mjpegUrl}`);
        } catch (error: any) {
          console.error(`Error starting analysis for ${url}:`, error);
          get().setMjpegStream(url, null, error.message || 'Failed to start analysis');
        }
      },

      setMjpegStream: (url, streamUrl, error) => {
        set(state => {
          const source = state.rtspSources[url];
          if (source) {
            if (error) {
              source.status = 'error_analysis';
              source.errorMessage = error;
              source.mjpegStreamUrl = null;
              if (state.activeSourceUrl === url) {
                  state.annotationMode = source.annotation.isClosed ? 'line_selection' : 'drawing';
              }
            } else {
              source.mjpegStreamUrl = streamUrl;
              source.status = 'streaming';
              source.errorMessage = null;
              if (state.activeSourceUrl === url) {
                  state.annotationMode = 'idle';
              }
            }
          }
        });
      },

      setGlobalStatus: (status, message) => {
        set(state => {
          state.globalStatus = status;
          state.globalErrorMessage = message || null;
        });
      },

      clearGlobalError: () => {
        set(state => {
          if (state.globalStatus === 'error') {
            state.globalStatus = 'idle';
          }
          state.globalErrorMessage = null;
        });
      },

      setZoneType: (url, type) => {
        set(state => {
          const source = state.rtspSources[url];
          if (source && source.annotation.isClosed) {
            source.annotation.zoneType = type;
            console.log(`STORE: Zone type for ${url} set to ${type}`);
          }
        });
      },

      setState: (loadedState) => {
        set(state => {
          if (loadedState.rtspSources) {
            // Potentially enhance this merging logic if needed
            // e.g., merge individual sources instead of overwriting the whole object
            Object.assign(state.rtspSources, loadedState.rtspSources);
          }
          if (loadedState.activeSourceUrl !== undefined) {
              state.activeSourceUrl = loadedState.activeSourceUrl;
          }
          if (loadedState.annotationMode !== undefined) {
              state.annotationMode = loadedState.annotationMode;
          }
          if (loadedState.globalStatus !== undefined) {
              state.globalStatus = loadedState.globalStatus;
          }
          if (loadedState.globalErrorMessage !== undefined) {
              state.globalErrorMessage = loadedState.globalErrorMessage;
          }
          console.log('[STORE] State updated from backend data');
        });
      }
    })),
    {
      name: 'customer-analysis-store',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        rtspSources: Object.fromEntries(
          Object.entries(state.rtspSources).map(([key, value]) => [
            key,
            { ...value, rawMjpegStreamUrl: value.rawMjpegStreamUrl ?? null },
          ])
        ),
        activeSourceUrl: state.activeSourceUrl,
        annotationMode: state.annotationMode,
        globalStatus: state.globalStatus,
        globalErrorMessage: state.globalErrorMessage,
      }),
    }
  )
);

export const selectRtspSourcesList = (state: AppState) => Object.values(state.rtspSources);
export const selectActiveSourceData = (state: AppState): RtspSourceInfo | null =>
  state.activeSourceUrl ? state.rtspSources[state.activeSourceUrl] ?? null : null;
export const selectActiveAnnotation = (state: AppState) => selectActiveSourceData(state)?.annotation;
export const selectActiveZoneType = (state: AppState): ZoneType | undefined => 
  selectActiveSourceData(state)?.annotation?.zoneType;
export const selectIsActiveSourceReadyForAnnotation = (state: AppState) => {
    const activeSource = selectActiveSourceData(state);
    return !!activeSource && (activeSource.status === 'frame_loaded' || activeSource.status === 'annotating' || activeSource.status === 'annotated');
};
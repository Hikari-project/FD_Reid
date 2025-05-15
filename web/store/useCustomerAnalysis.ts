import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';
import { persist, createJSONStorage } from 'zustand/middleware';
import type {
  AppState,
  AppActions,
  RtspSourceInfo,
  Point,
  RtspResponse,
  initialRtspStreamInfo,
  BackendBox, 
  WSBoxPayload,
  ZoneType, // ZoneType is used for function params and state
  AnalysisResult
} from '@/store/types';

export const backendUrl = 'http://192.168.21.161:3002'

// WebSocket connection management
const wsConnections = new Map<string, WebSocket>();
const reconnectAttempts = new Map<string, number>();
const MAX_RECONNECT_ATTEMPTS = 5;
const RECONNECT_DELAY_BASE = 1000; // 1 second

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
  // console.log("fetchFirstFrameFromBackend response", data);
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
      // ws_token?: string, 
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
  // console.log("analysis response", data);
  return data;
}

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

export const useAppStore = create<AppState & AppActions>()(
  persist(
    immer((set, get) => {
      
      const attemptReconnect = (rtspUrl: string) => {
        let attempts = reconnectAttempts.get(rtspUrl) || 0;
        if (attempts < MAX_RECONNECT_ATTEMPTS) {
          attempts++;
          reconnectAttempts.set(rtspUrl, attempts);
          const delay = RECONNECT_DELAY_BASE * Math.pow(2, attempts - 1);
          console.log(`Attempting to reconnect ${rtspUrl} for boxes WS in ${delay / 1000}s (attempt ${attempts})`);
          
          setTimeout(() => {
            const currentSource = get().rtspSources[rtspUrl];
            if (currentSource && currentSource.wsToken &&
                (currentSource.wsStatus === 'disconnected' || currentSource.wsStatus === 'error')) {
              console.log(`Reconnecting boxes WS for ${rtspUrl} now...`);
              get().connectBoxWS(rtspUrl);
            } else {
              console.log(`Reconnect attempt for ${rtspUrl} boxes WS aborted as source state changed or token missing.`);
              if (!currentSource || !currentSource.wsToken || 
                  (currentSource.wsStatus !== 'disconnected' && currentSource.wsStatus !== 'error')) {
                reconnectAttempts.delete(rtspUrl); 
              }
            }
          }, delay);
        } else {
          console.error(`Max reconnect attempts reached for ${rtspUrl} boxes WS.`);
          set(state => {
            if (state.rtspSources[rtspUrl]) {
              state.rtspSources[rtspUrl].wsStatus = 'error';
              state.rtspSources[rtspUrl].wsErrorMessage = 'Max reconnect attempts for WebSocket reached.';
            }
          });
          reconnectAttempts.delete(rtspUrl);
        }
      };

      return {
        ...initialState,

        initializeStreamsOnLogin: async () => {
          set(state => {
            state.globalStatus = 'loading_file'; 
            state.globalErrorMessage = null;
            state.rtspSources = {}; // Clear existing sources
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
              } else {
                console.warn(`Stream ${streamData.rtsp_url} filtered out: no usable MJPEG stream URL.`);
                continue; 
              }
              
              const newSourceInfo: RtspSourceInfo = {
                url: streamData.rtsp_url,
                name: (streamData.name && streamData.name.trim() !== "") ? streamData.name : streamData.rtsp_url,
                firstFrameDataUrl: streamData.frame_url ? `${backendUrl}${streamData.frame_url}` : null,
                annotation: { points: [], isClosed: false, selectedLineIndices: [], zoneType: null },
                mjpegStreamUrl: mjpegStreamUrlForState,
                rawMjpegStreamUrl: rawMjpegStreamUrlForState,
                status: mjpegStreamUrlForState ? 'streaming' : (streamData.frame_url ? 'frame_loaded' : 'idle'),
                errorMessage: null,
                imageDimensions: undefined,
                wsToken: streamData.rtsp_url || undefined,
                boxes: [],
                wsStatus: streamData.rtsp_url ? 'disconnected' : 'idle',
                wsErrorMessage: null,
                analysisResult: null,
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
                  if (activeSource.status === 'frame_loaded' || 
                      activeSource.status === 'annotating' || 
                      activeSource.status === 'annotated' ||
                      (activeSource.status === 'streaming' && activeSource.firstFrameDataUrl)
                     ) {
                    state.annotationMode = activeSource.annotation.isClosed ? 'line_selection' : 'drawing';
                  } else {
                    state.annotationMode = 'idle';
                  }
                  // Auto-connect WS if token exists for the newly active source
                  if (activeSource.wsToken && activeSource.url === state.activeSourceUrl) {
                     setTimeout(() => get().connectBoxWS(activeSource.url), 100);
                  }
                } else { // Should not happen if loadedUrls[0] is valid
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
                name: url, 
                firstFrameDataUrl: null,
                rawMjpegStreamUrl: null,
                annotation: { points: [], isClosed: false, selectedLineIndices: [], zoneType: null },
                mjpegStreamUrl: null,
                status: 'idle', 
                errorMessage: null,
                imageDimensions: undefined,
                wsToken: undefined,
                boxes: [],
                wsStatus: 'idle',
                wsErrorMessage: null,
                analysisResult: null,
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
              const activeSource = state.rtspSources[uniqueUrls[0]];
              if (activeSource && (activeSource.status === 'frame_loaded' || activeSource.status === 'annotating')) {
                state.annotationMode = activeSource.annotation.isClosed ? 'line_selection' : 'drawing';
              } else {
                 state.annotationMode = 'idle';
              }
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
          get().disconnectBoxWS(url); 
          reconnectAttempts.delete(url); 
          set(state => {
            delete state.rtspSources[url];
            if (state.activeSourceUrl === url) {
              const remainingUrls = Object.keys(state.rtspSources);
              state.activeSourceUrl = remainingUrls.length > 0 ? remainingUrls[0] : null;
              if (state.activeSourceUrl) {
                const newActiveSource = state.rtspSources[state.activeSourceUrl];
                state.annotationMode = newActiveSource?.annotation.isClosed ? 'line_selection' : 'drawing';
                if (newActiveSource?.wsToken && newActiveSource.url === state.activeSourceUrl && (newActiveSource.wsStatus === 'disconnected' || newActiveSource.wsStatus === 'error') ) {
                   setTimeout(() => get().connectBoxWS(newActiveSource.url), 100);
                }
              } else {
                state.annotationMode = 'idle';
              }
            }
          });
        },

        setActiveSource: (url) => {
          const oldActiveUrl = get().activeSourceUrl;
          set(state => {
            state.activeSourceUrl = url;
            if (url && state.rtspSources[url]) {
              const source = state.rtspSources[url];
              if (source.status === 'frame_loaded' || source.status === 'annotating' || source.status === 'annotated' || 
                 (source.status === 'streaming' && source.firstFrameDataUrl) 
              ) {
                  state.annotationMode = source.annotation.isClosed ? 'line_selection' : 'drawing';
              } else {
                  state.annotationMode = 'idle';
              }
            } else {
              state.annotationMode = 'idle';
            }
          });
          
          if (url && url !== oldActiveUrl) {
            const newActiveSource = get().rtspSources[url];
            if (newActiveSource && newActiveSource.wsToken && (newActiveSource.wsStatus === 'disconnected' || newActiveSource.wsStatus === 'error')) {
              setTimeout(() => get().connectBoxWS(url), 100);
            }
            if(oldActiveUrl){
                const oldSource = get().rtspSources[oldActiveUrl];
                if(oldSource && (oldSource.wsStatus === 'connected' || oldSource.wsStatus === 'connecting')){
                    // Decide if changing active source should auto-disconnect old WS.
                    // Generally, WS is tied to an analysis session, not just being active.
                    // get().disconnectBoxWS(oldActiveUrl); // Let startAnalysis/clearAnnotation handle disconnects.
                }
            }
          } else if (!url && oldActiveUrl) {
             // get().disconnectBoxWS(oldActiveUrl); // If no new active source, disconnect old one.
          }
        },

        resetSourceStatus: (url) => {
            get().disconnectBoxWS(url);
            set(state => {
                const source = state.rtspSources[url];
                if(source) {
                    source.status = source.firstFrameDataUrl ? 'frame_loaded' : 'idle';
                    source.mjpegStreamUrl = null;
                    source.errorMessage = null;
                    source.wsToken = undefined; 
                    source.boxes = [];
                    source.wsStatus = 'idle';
                    source.wsErrorMessage = null;
                    source.analysisResult = null;
                    if (state.activeSourceUrl === url) {
                        state.annotationMode = source.annotation.isClosed ? 'line_selection' : (source.firstFrameDataUrl ? 'drawing' : 'idle');
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
              if (source.annotation.points.length === 0 && source.status === 'annotating') {
                  source.status = 'frame_loaded';
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
            }
          });
        },

        clearAnnotation: (url) => {
          get().disconnectBoxWS(url);
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
              source.wsToken = undefined;
              source.boxes = [];
              source.wsStatus = 'idle';
              source.wsErrorMessage = null;
              source.analysisResult = null;
              if(state.activeSourceUrl === url) {
                  state.annotationMode = source.firstFrameDataUrl ? 'drawing' : 'idle';
              }
            }
          });
        },

        startAnalysis: async (url) => {
          const source = get().rtspSources[url];
          if (!source) { return; }
          let errorMessage = null;
          if (!source.annotation.isClosed) errorMessage = 'Annotation polygon is not closed.';
          else if (source.annotation.selectedLineIndices.length === 0) errorMessage = 'No crossing lines selected.';
          else if (!source.annotation.zoneType) errorMessage = 'Inside/Outside zone type not selected.';

          if (errorMessage) {
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
          get().disconnectBoxWS(url); // Disconnect any old WS for this source
          set(state => {
            if (state.rtspSources[url]){
              state.rtspSources[url].status = 'analyzing';
              state.rtspSources[url].errorMessage = null;
              state.rtspSources[url].mjpegStreamUrl = null;
              state.rtspSources[url].wsToken = undefined; // Clear old token
              state.rtspSources[url].wsStatus = 'idle';
              state.rtspSources[url].boxes = [];
              if (state.activeSourceUrl === url) state.annotationMode = 'idle';
            }
          });
          try {
            const analysisResponse = await startAnalysisOnBackend( url, source.annotation.points, 
              source.annotation.selectedLineIndices.map(startIndex => {
                const endIndex = (startIndex + 1) % source.annotation.points.length;
                return [source.annotation.points[startIndex], source.annotation.points[endIndex]];
              }),
              zoneType
            );
            if (analysisResponse.ret !== 0 || !analysisResponse.res || analysisResponse.res.length === 0) {
              throw new Error(analysisResponse.message || 'Analysis failed on backend.');
            }
            const analysisResult = analysisResponse.res[0];
            set(state => {
              const currentSource = state.rtspSources[url];
              if (currentSource) {
                currentSource.mjpegStreamUrl = analysisResult.mjpeg_url ? `${backendUrl}${analysisResult.mjpeg_url}` : null;
                currentSource.status = currentSource.mjpegStreamUrl ? 'streaming' : 'annotated'; // Or 'analysis_active'
                if (analysisResult.source_url) {
                  currentSource.wsToken = analysisResult.source_url;
                } else {
                  console.warn(`No ws_token received for ${url} from analysis backend.`);
                }
              }
            });
            if (analysisResponse.res[0].source_url) {
              console.log(`Connecting WebSocket for boxes: ${analysisResponse.res[0].source_url}`);
              get().connectBoxWS(url);
            }
          } catch (error: any) {
            set(state => {
              const currentSource = state.rtspSources[url];
              if (currentSource) {
                currentSource.status = 'error_analysis';
                currentSource.errorMessage = error.message || 'Failed to start analysis';
              }
            });
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

        connectBoxWS: (rtspUrl) => {
          const source = get().rtspSources[rtspUrl];
          if (!source || !source.wsToken) {
            if (source) set(state => { if (state.rtspSources[rtspUrl]){ state.rtspSources[rtspUrl].wsStatus = 'error'; state.rtspSources[rtspUrl].wsErrorMessage = 'Missing WebSocket token.'; } });
            return;
          }
          if (wsConnections.has(rtspUrl)) {
            const existingWs = wsConnections.get(rtspUrl);
            if (existingWs && (existingWs.readyState === WebSocket.OPEN || existingWs.readyState === WebSocket.CONNECTING)) {
               get().disconnectBoxWS(rtspUrl); 
            }
          }
          reconnectAttempts.delete(rtspUrl);
          const token = source.url;
          const wsProtocol = backendUrl.startsWith('https') ? 'wss' : 'ws';
          const hostAndPath = backendUrl.split('//')[1];
          // const wsUrl = `${wsProtocol}://${hostAndPath}/ws/boxes/${rtspUrl}?token=${token}`;
          const wsUrl = `ws://192.168.21.161:3002/customer-flow/ws?rtsp_url=${token}`;
          set(state => { if (state.rtspSources[rtspUrl]) { state.rtspSources[rtspUrl].wsStatus = 'connecting'; state.rtspSources[rtspUrl].wsErrorMessage = null; state.rtspSources[rtspUrl].boxes = []; state.rtspSources[rtspUrl].analysisResult = null; } });
          try {
            const ws = new WebSocket(wsUrl);
            (ws as any).isIntentionallyClosed = false;
            wsConnections.set(rtspUrl, ws);
            ws.onopen = () => {
              set(state => { if (state.rtspSources[rtspUrl]) { state.rtspSources[rtspUrl].wsStatus = 'connected'; state.rtspSources[rtspUrl].wsErrorMessage = null; } });
              reconnectAttempts.delete(rtspUrl);
            };
            ws.onmessage = (event) => {
              try {
                const payload = JSON.parse(event.data as string) as WSBoxPayload;
                if (payload.source_url === rtspUrl) {
                  set(state => { 
                    if (state.rtspSources[rtspUrl]) {
                      state.rtspSources[rtspUrl].boxes = payload.boxes;
                      console.log("payload.result", payload.result);
                      state.rtspSources[rtspUrl].analysisResult = payload.result ?? null;
                    }
                  });
                }
              } catch (e) { console.error(`Error parsing WebSocket message for ${rtspUrl}:`, e); }
            };
            ws.onerror = (event) => {
              console.error(`WebSocket error for boxes ${rtspUrl}:`, event);
              set(state => { if (state.rtspSources[rtspUrl]) { state.rtspSources[rtspUrl].wsStatus = 'error'; state.rtspSources[rtspUrl].wsErrorMessage = 'WebSocket connection error.'; } });
              wsConnections.delete(rtspUrl);
              attemptReconnect(rtspUrl);
            };
            ws.onclose = (event) => {
              const intentionallyClosed = (event.target as any).isIntentionallyClosed;
              wsConnections.delete(rtspUrl);
              if (!intentionallyClosed && event.code !== 1000 && event.code !== 1005 ) {
                set(state => { if (state.rtspSources[rtspUrl] && state.rtspSources[rtspUrl].wsStatus !== 'idle') { state.rtspSources[rtspUrl].wsStatus = 'disconnected';  state.rtspSources[rtspUrl].wsErrorMessage = `WebSocket closed (Code: ${event.code}).`;} });
                const currentSrc = get().rtspSources[rtspUrl];
                if (currentSrc && currentSrc.wsToken && currentSrc.wsStatus !== 'idle') attemptReconnect(rtspUrl);
                else reconnectAttempts.delete(rtspUrl);
              } else {
                set(state => { if (state.rtspSources[rtspUrl]) { state.rtspSources[rtspUrl].wsStatus = intentionallyClosed ? 'idle' : 'disconnected'; state.rtspSources[rtspUrl].wsErrorMessage = null; state.rtspSources[rtspUrl].boxes = []; state.rtspSources[rtspUrl].analysisResult = null; } });
                reconnectAttempts.delete(rtspUrl);
              }
            };
          } catch (err) { set(state => { if (state.rtspSources[rtspUrl]) { state.rtspSources[rtspUrl].wsStatus = 'error'; state.rtspSources[rtspUrl].wsErrorMessage = 'Failed to create WebSocket.'; } }); }
        },

        disconnectBoxWS: (rtspUrl) => {
          const ws = wsConnections.get(rtspUrl);
          if (ws) { (ws as any).isIntentionallyClosed = true; ws.close(1000, 'Client disconnected intentionally'); wsConnections.delete(rtspUrl); }
          reconnectAttempts.delete(rtspUrl);
          set(state => { if (state.rtspSources[rtspUrl]) { state.rtspSources[rtspUrl].wsStatus = 'idle'; state.rtspSources[rtspUrl].boxes = []; state.rtspSources[rtspUrl].wsErrorMessage = null; state.rtspSources[rtspUrl].analysisResult = null; } });
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
                }
            });
        },

        setState: (loadedState) => {
          set(state => {
            if (loadedState.rtspSources) {
              for (const url in loadedState.rtspSources) {
                const sourceDataFromLoad = loadedState.rtspSources[url];
                if (!sourceDataFromLoad) continue;
                if (state.rtspSources[url]) {
                  Object.assign(state.rtspSources[url], sourceDataFromLoad);
                  // Ensure runtime fields are reset if not in sourceDataFromLoad (they shouldn't be)
                  state.rtspSources[url].boxes = sourceDataFromLoad.boxes || [];
                  state.rtspSources[url].wsStatus = sourceDataFromLoad.wsStatus || (state.rtspSources[url].wsToken ? 'disconnected' : 'idle');
                  state.rtspSources[url].wsErrorMessage = sourceDataFromLoad.wsErrorMessage || null;
                  state.rtspSources[url].analysisResult = sourceDataFromLoad.analysisResult || null;
                } else {
                  state.rtspSources[url] = {
                    ...sourceDataFromLoad,
                    boxes: sourceDataFromLoad.boxes || [],
                    wsStatus: sourceDataFromLoad.wsStatus || (sourceDataFromLoad.wsToken ? 'disconnected' : 'idle'),
                    wsErrorMessage: sourceDataFromLoad.wsErrorMessage || null,
                    analysisResult: sourceDataFromLoad.analysisResult || null,
                  };
                }
              }
            }
            if (loadedState.activeSourceUrl !== undefined) state.activeSourceUrl = loadedState.activeSourceUrl;
            if (loadedState.annotationMode !== undefined) state.annotationMode = loadedState.annotationMode;
            if (loadedState.globalStatus !== undefined) state.globalStatus = loadedState.globalStatus;
            if (loadedState.globalErrorMessage !== undefined) state.globalErrorMessage = loadedState.globalErrorMessage;
          });
        }
      }
    }),
    {
      name: 'customer-analysis-store',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => {
        const persistedState: Partial<AppState> = {
          activeSourceUrl: state.activeSourceUrl,
          annotationMode: state.annotationMode,
          globalStatus: state.globalStatus,
          globalErrorMessage: state.globalErrorMessage,
          rtspSources: {},
        };
        if (state.rtspSources) {
          persistedState.rtspSources = Object.fromEntries(
            Object.entries(state.rtspSources).map(([key, value]) => {
              const { boxes, wsStatus, wsErrorMessage, analysisResult, ...persistedSourceData } = value;
              return [ key, { ...persistedSourceData, rawMjpegStreamUrl: value.rawMjpegStreamUrl ?? null }];
            })
          );
        }
        return persistedState;
      },
      onRehydrateStorage: () => (state) => {
        if (state && state.rtspSources) {
          for (const url in state.rtspSources) {
            const source = state.rtspSources[url];
            if (source) {
              source.boxes = [];
              source.wsStatus = source.wsToken ? 'disconnected' : 'idle';
              source.wsErrorMessage = null;
              source.analysisResult = null;
              // Auto-reconnect for active source with token could be triggered here or by UI effect
              // For example, if source.url === state.activeSourceUrl && source.wsToken:
              //   setTimeout(() => useAppStore.getState().connectBoxWS(source.url), 500);
            }
          }
        }
      }
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
    if (!activeSource) return false;
    return activeSource.status === 'frame_loaded' || 
           activeSource.status === 'annotating' || 
           activeSource.status === 'annotated' ||
           (activeSource.status === 'streaming' && activeSource.firstFrameDataUrl);
};

export const selectActiveSourceBoxes = (state: AppState): BackendBox[] | undefined =>
  selectActiveSourceData(state)?.boxes;

export const selectActiveSourceWsStatus = (state: AppState): RtspSourceInfo['wsStatus'] =>
  selectActiveSourceData(state)?.wsStatus ?? 'idle';

export const selectActiveSourceWsError = (state: AppState): string | null | undefined =>
  selectActiveSourceData(state)?.wsErrorMessage;

export const selectActiveSourceAnalysisResult = (state: AppState): AnalysisResult | null | undefined =>
  selectActiveSourceData(state)?.analysisResult;
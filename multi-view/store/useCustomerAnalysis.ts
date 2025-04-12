// store/appStore.ts
import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer'; // Optional: for easier nested state updates
import type {
  AppState,
  AppActions,
  RtspSourceInfo,
  Point,
} from '@/store/types'; // Adjust path if needed

// --- Helper: Mock API Calls (Replace with your actual fetch logic) ---
// Simulates fetching the first frame from the backend
async function fetchFirstFrameFromBackend(rtspUrl: string): Promise<{ frameDataUrl: string; width: number; height: number }> {
  console.log(`STORE: Requesting first frame for ${rtspUrl}`);
  // Replace with your actual API call:
  const response = await fetch('/api/get-frame', { method: 'POST', body: JSON.stringify({ url: rtspUrl }) });
  if (!response.ok) throw new Error('Failed to fetch frame');
  const data = await response.json(); // Assuming backend returns { frameDataUrl: 'data:image/jpeg;base64,...', width: w, height: h }
  return data;

  // --- Mock Implementation ---
//   await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate network delay
//   if (rtspUrl.includes("fail")) {
//       throw new Error(`Simulated backend error for ${rtspUrl}`);
//   }
//   // Simulate a successful response with a placeholder image data URL
//   const canvas = document.createElement('canvas');
//   canvas.width = 640;
//   canvas.height = 480;
//   const ctx = canvas.getContext('2d');
//   if (ctx) {
//       ctx.fillStyle = `hsl(${Math.random() * 360}, 50%, 80%)`; // Random light color
//       ctx.fillRect(0, 0, canvas.width, canvas.height);
//       ctx.fillStyle = 'black';
//       ctx.font = '16px Arial';
//       ctx.textAlign = 'center';
//       ctx.fillText(`Frame for: ${rtspUrl}`, canvas.width / 2, canvas.height / 2);
//       ctx.fillText(`(Mock Image)`, canvas.width / 2, canvas.height / 2 + 20);
//   }
//    return { frameDataUrl: canvas.toDataURL('image/jpeg'), width: 640, height: 480 };
  // --- End Mock Implementation ---
}

// Simulates sending analysis request and getting MJPEG stream URL
async function startAnalysisOnBackend(
    rtspUrl: string,
    polygonPoints: Point[],
    crossingLineEndpoints: Point[][] // Array of [startPoint, endPoint] for selected lines
    ): Promise<{ mjpegStreamUrl: string }> {
    console.log(`STORE: Starting analysis for ${rtspUrl}`);
    console.log("Polygon Points:", polygonPoints);
    console.log("Crossing Lines Endpoints:", crossingLineEndpoints);

    // Replace with your actual API call:
    const payload = {
      rtsp_address: rtspUrl,
      polygon_points: polygonPoints,
      crossing_lines: crossingLineEndpoints,
    };
    const response = await fetch('/api/start-analysis', { method: 'POST', body: JSON.stringify(payload), headers: {'Content-Type': 'application/json'} });
    if (!response.ok) throw new Error('Failed to start analysis');
    const data = await response.json(); // Assuming backend returns { mjpegStreamUrl: '...' }
    return data;

    // // --- Mock Implementation ---
    // await new Promise(resolve => setTimeout(resolve, 2000)); // Simulate analysis setup delay
    // if (rtspUrl.includes("analyze_fail")) {
    //     throw new Error(`Simulated analysis error for ${rtspUrl}`);
    // }
    // // Simulate a successful response with a placeholder MJPEG URL
    // return { mjpegStreamUrl: `/api/mock-mjpeg-stream?url=${encodeURIComponent(rtspUrl)}&time=${Date.now()}` }; // Use timestamp to make it unique
    // // --- End Mock Implementation ---
}
// --- End Helper: Mock API Calls ---


// --- Initial State ---
const initialState: AppState = {
  rtspSources: {},
  activeSourceUrl: null,
  annotationMode: 'idle',
  globalStatus: 'idle',
  globalErrorMessage: null,
};

// --- 管理标注盒子的状态 ---
export const useAppStore = create<AppState & AppActions>()(
  immer((set, get) => ({
    ...initialState,

    // --- Source Management Actions ---
    addRtspSources: async (urls) => {
      const uniqueUrls = urls.filter(url => url.trim() && !get().rtspSources[url]);
      if (uniqueUrls.length === 0) return;

      set(state => {
        state.globalStatus = 'processing_file'; // Or a more specific status
        state.globalErrorMessage = null;
        uniqueUrls.forEach(url => {
          state.rtspSources[url] = {
            url: url,
            firstFrameDataUrl: null,
            annotation: { points: [], isClosed: false, selectedLineIndices: [] },
            mjpegStreamUrl: null,
            status: 'idle', // Will be updated by _fetchFirstFrame
            errorMessage: null,
          };
        });
      });

      // Sequentially trigger frame fetching to avoid overwhelming backend/browser (optional)
      // Or use Promise.all for parallel fetching:
      // await Promise.all(uniqueUrls.map(url => get()._fetchFirstFrame(url)));

       for (const url of uniqueUrls) {
           await get()._fetchFirstFrame(url); // Fetch one by one
       }


      set(state => {
          // Set global status back to idle only if no source is in an error state maybe?
          // Or just set it regardless, individual source errors are tracked.
          state.globalStatus = 'idle';
          // If no source was previously active, activate the first added one
          if (!state.activeSourceUrl && uniqueUrls.length > 0) {
              state.activeSourceUrl = uniqueUrls[0];
              state.annotationMode = state.rtspSources[uniqueUrls[0]].annotation.isClosed ? 'line_selection' : 'drawing';
          }
      });
    },

    _fetchFirstFrame: async (url) => {
      if (!get().rtspSources[url]) return; // Should not happen if called from addRtspSources

      set(state => {
        if (state.rtspSources[url]) {
          state.rtspSources[url].status = 'loading_frame';
          state.rtspSources[url].errorMessage = null;
        }
      });

      try {
        const { frameDataUrl, width, height } = await fetchFirstFrameFromBackend(url);
        get().setSourceFrame(url, frameDataUrl, {width, height});
      } catch (error: any) {
        console.error(`Error fetching frame for ${url}:`, error);
        get().setSourceFrame(url, null, undefined, error.message || 'Failed to fetch first frame');
      }
    },

    setSourceFrame: (url, frameDataUrl, dimensions, error) => {
       set(state => {
           const source = state.rtspSources[url];
           if (source) {
               if (error) {
                   source.status = 'error_frame';
                   source.errorMessage = error;
                   source.firstFrameDataUrl = null; // Clear any previous frame
                   source.imageDimensions = undefined;
               } else {
                   source.firstFrameDataUrl = frameDataUrl;
                   source.status = 'frame_loaded'; // Ready for annotation
                   source.errorMessage = null;
                   source.imageDimensions = dimensions;
                   // If this is the currently active source, set annotation mode
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
          // If the active source is removed, activate the first available one or none
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
          // Set annotation mode based on the new active source's state
           if (source.status === 'frame_loaded' || source.status === 'annotating' || source.status === 'annotated') {
               state.annotationMode = source.annotation.isClosed ? 'line_selection' : 'drawing';
           } else {
               // If frame not loaded, or streaming, etc., annotation isn't active
               state.annotationMode = 'idle';
           }
        } else {
          state.annotationMode = 'idle'; // No active source or source not found
        }
      });
    },

    resetSourceStatus: (url) => {
        set(state => {
            const source = state.rtspSources[url];
            if(source) {
                source.status = source.firstFrameDataUrl ? 'frame_loaded' : 'idle'; // Go back to frame loaded if we have frame, else idle
                source.mjpegStreamUrl = null;
                source.errorMessage = null;
                // Potentially reset annotation mode if it was active for this source
                if (state.activeSourceUrl === url) {
                    state.annotationMode = source.annotation.isClosed ? 'line_selection' : 'drawing';
                }
            }
        })
    },

    // --- Annotation Actions ---
    setAnnotationMode: (mode) => {
      set({ annotationMode: mode });
    },

    addAnnotationPoint: (url, point) => {
      set(state => {
        const source = state.rtspSources[url];
        // Only add points if in drawing mode and polygon isn't closed
        if (source && state.annotationMode === 'drawing' && !source.annotation.isClosed) {
          // Basic check to prevent duplicate consecutive points
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
        // Only undo if in drawing mode, not closed, and points exist
        if (source && state.annotationMode === 'drawing' && !source.annotation.isClosed && source.annotation.points.length > 0) {
          source.annotation.points.pop();
           if (source.annotation.points.length === 0) {
               // If no points left, revert status if needed (optional)
               // source.status = 'frame_loaded';
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
          // Reset status only if it was related to annotation/analysis
          if (['annotating', 'annotated', 'analyzing', 'streaming', 'error_analysis'].includes(source.status)) {
              source.status = source.firstFrameDataUrl ? 'frame_loaded' : 'idle'; // Go back to frame loaded state if frame exists
          }
          source.mjpegStreamUrl = null; // Stop stream if any
          // If this is the active source, reset annotation mode to drawing
          if(state.activeSourceUrl === url) {
              state.annotationMode = 'drawing';
          }
        }
      });
    },

    closePolygon: (url) => {
      set(state => {
        const source = state.rtspSources[url];
        // Require at least 3 points to form a polygon
        if (source && state.annotationMode === 'drawing' && !source.annotation.isClosed && source.annotation.points.length >= 3) {
          source.annotation.isClosed = true;
          source.status = 'annotated'; // Or keep 'annotating' until lines selected? Decide based on UX. Let's use 'annotated' for now.
          // If active source, switch mode
          if(state.activeSourceUrl === url) {
              state.annotationMode = 'line_selection';
          }
        }
      });
    },

    toggleLineSelection: (url, lineIndex) => {
      set(state => {
        const source = state.rtspSources[url];
        // Only allow toggling if polygon is closed and in line selection mode
        if (source && state.annotationMode === 'line_selection' && source.annotation.isClosed) {
          const selected = source.annotation.selectedLineIndices;
          const indexPos = selected.indexOf(lineIndex);
          if (indexPos > -1) {
            selected.splice(indexPos, 1); // Remove if already selected
          } else {
            selected.push(lineIndex); // Add if not selected
            selected.sort((a, b) => a - b); // Keep sorted (optional)
          }
          source.status = 'annotated'; // Ready for analysis
        }
      });
    },

    // --- Analysis Actions ---
    startAnalysis: async (url) => {
      const source = get().rtspSources[url];
      if (!source || !source.annotation.isClosed || source.annotation.selectedLineIndices.length === 0) {
        console.warn(`Cannot start analysis for ${url}: Annotation not complete or no lines selected.`);
         set(state => { // Optionally set an error state
            if(state.rtspSources[url]) {
                state.rtspSources[url].status = 'error_analysis';
                state.rtspSources[url].errorMessage = 'Annotation incomplete or no crossing lines selected.';
            }
         });
        return;
      }

      set(state => {
        state.rtspSources[url].status = 'analyzing';
        state.rtspSources[url].errorMessage = null;
        state.rtspSources[url].mjpegStreamUrl = null; // Clear previous stream if any
         if (state.activeSourceUrl === url) {
             state.annotationMode = 'idle'; // Annotation controls disabled during analysis/streaming
         }
      });

      try {
        // Prepare crossing line endpoints
        const points = source.annotation.points;
        const crossingLineEndpoints = source.annotation.selectedLineIndices.map(startIndex => {
            const endIndex = (startIndex + 1) % points.length; // Handle wrap-around for the last line
            return [points[startIndex], points[endIndex]];
        });

        const { mjpegStreamUrl } = await startAnalysisOnBackend(
          url,
          source.annotation.points,
          crossingLineEndpoints
        );
        get().setMjpegStream(url, mjpegStreamUrl);
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
             // If active source, maybe allow going back to annotation?
             if (state.activeSourceUrl === url) {
                state.annotationMode = source.annotation.isClosed ? 'line_selection' : 'drawing';
            }
          } else {
            source.mjpegStreamUrl = streamUrl;
            source.status = 'streaming';
            source.errorMessage = null;
             // Ensure annotation mode is idle while streaming
             if (state.activeSourceUrl === url) {
                 state.annotationMode = 'idle';
             }
          }
        }
      });
    },

    // --- Global Status Actions ---
    setGlobalStatus: (status, message) => {
      set(state => {
        state.globalStatus = status;
        state.globalErrorMessage = message || null;
      });
    },

    clearGlobalError: () => {
      set(state => {
          if (state.globalStatus === 'error') {
              state.globalStatus = 'idle'; // Revert to idle when clearing error
          }
          state.globalErrorMessage = null;
      });
    },

  })) // End immer middleware
); // End create

// --- Optional: Define Selectors for convenience ---
export const selectRtspSourcesList = (state: AppState) => Object.values(state.rtspSources);
export const selectActiveSourceData = (state: AppState): RtspSourceInfo | null =>
  state.activeSourceUrl ? state.rtspSources[state.activeSourceUrl] ?? null : null;
export const selectActiveAnnotation = (state: AppState) => selectActiveSourceData(state)?.annotation;
export const selectIsActiveSourceReadyForAnnotation = (state: AppState) => {
    const activeSource = selectActiveSourceData(state);
    return !!activeSource && (activeSource.status === 'frame_loaded' || activeSource.status === 'annotating' || activeSource.status === 'annotated');
};
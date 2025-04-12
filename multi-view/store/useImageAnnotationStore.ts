import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';
import { v4 as uuidv4 } from 'uuid'; // For generating unique IDs if backend doesn't provide them

// src/store/constants.ts (or keep in store file)
export const STAGE_WIDTH = 960;
export const STAGE_HEIGHT = 540;
export const DOT_RADIUS = 6;
export const DOT_FILL_COLOR = 'blue';
export const DOT_HOVER_FILL_COLOR = 'red';
export const DEFAULT_LINE_COLOR = 'black';
export const TOGGLED_LINE_COLOR = 'red';
export const LINE_STROKE_WIDTH = 3;
export const PREVIEW_LINE_STROKE_COLOR = 'grey';
export const PREVIEW_LINE_DASH = [5, 5];
export const CLOSE_THRESHOLD = DOT_RADIUS * 3;

// --- Types ---
export interface Point {
  x: number;
  y: number;
}

// Represents the annotation state for a single stream frame
export interface AnnotationState {
  points: Point[];
  isClosed: boolean;
  lineSegmentColors: string[]; // Colors for segments corresponding to points array
}

// Represents a stream and its associated annotations
// Replaces ImageAnnotation
export interface StreamAnnotation {
  id: string; // Unique ID derived from RTSP URL or backend response
  rtspUrl: string; // Original RTSP URL
  mjpegUrl: string; // MJPEG URL received from backend
  name: string; // Display name (e.g., derived from RTSP path)
  annotations: AnnotationState;
}

// API response structure (adjust based on your actual backend)
interface BackendStreamResponse {
  id: string;
  rtspUrl: string;
  mjpegUrl: string;
  name: string;
  error?: string; // Optional error message per stream
}

// The state of our stream annotation store
// Replaces ImageAnnotationState
interface StreamAnnotationState {
  // Main data storage
  streamAnnotations: StreamAnnotation[];
  currentStreamIndex: number;

  // UI State
  mousePos: Point | null;
  isMouseOverStart: boolean;
  isColorEditMode: boolean;
  isLoadingStreams: boolean; // Tracks backend communication
  error: string | null; // Stores general errors (e.g., API fetch failure)

  // Actions
  // --- Stream Management ---
  processRtspInput: (inputText: string) => Promise<void>; // Handles text area input
  processRtspFile: (file: File) => Promise<void>; // Handles file input
  fetchMjpegUrls: (rtspUrls: string[]) => Promise<void>; // Action to call backend
  navigateToStream: (index: number) => void;
  navigatePrev: () => void;
  navigateNext: () => void;
  clearStreams: () => void; // Action to clear all streams

  // --- Annotation Actions (mostly unchanged logic, operate on current stream) ---
  addPoint: (point: Point) => void;
  closeShape: () => void;
  resetAnnotation: () => void;
  undoLastPoint: () => void;
  toggleColorEditMode: () => void;
  toggleLineSegmentColor: (segmentIndex: number) => void;

  // --- UI Interaction ---
  setMousePosition: (point: Point | null) => void;
  setMouseOverStart: (isOver: boolean) => void;
  checkCloseToStart: (point: Point) => boolean;

  // Utility getters
  getCurrentStreamAnnotation: () => StreamAnnotation | null;
  getCurrentAnnotationState: () => AnnotationState | null;
  hasMinPointsForClosing: () => boolean;
}

// Helper function to create an empty annotation state
export const createEmptyAnnotationState = (): AnnotationState => ({
  points: [],
  isClosed: false,
  lineSegmentColors: [],
});

// Helper function to extract RTSP URLs from text
const extractRtspUrls = (text: string): string[] => {
  const rtspRegex = /rtsp:\/\/[^\s]+/g;
  const matches = text.match(rtspRegex);
  // Basic validation and deduplication
  return [...new Set(matches || [])].filter(url => url.startsWith("rtsp://"));
};

// --- Mock Backend API Call ---
// Replace this with your actual fetch call to your backend
const mockFetchMjpegUrlsFromBackend = async (rtspUrls: string[]): Promise<BackendStreamResponse[]> => {
  console.log("Sending to backend:", rtspUrls);
  await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate network delay

  // Simulate backend processing and potential errors
  return rtspUrls.map((url, index) => {
    if (url.includes("error")) { // Simulate an error for a specific URL
        return {
            id: uuidv4(),
            rtspUrl: url,
            mjpegUrl: '', // No MJPEG URL if error
            name: `Error Stream ${index + 1}`,
            error: 'Failed to process stream'
        };
    }
    // Example: derive name from URL path
    const name = url.substring(url.lastIndexOf('/') + 1) || `Stream ${index + 1}`;
    return {
      id: uuidv4(), // Use backend-provided ID if available
      rtspUrl: url,
      // IMPORTANT: Replace with the actual URL from your backend
      mjpegUrl: `/api/mjpeg_proxy/${encodeURIComponent(url)}`, // Example placeholder proxy URL
      name: name,
    };
  });
};
// --- End Mock Backend API Call ---


export const useStreamAnnotationStore = create<StreamAnnotationState>()(
  immer((set, get) => ({
    // --- Initial State ---
    streamAnnotations: [],
    currentStreamIndex: -1,
    mousePos: null,
    isMouseOverStart: false,
    isColorEditMode: false,
    isLoadingStreams: false,
    error: null,

    // --- Getters ---
    getCurrentStreamAnnotation: (): StreamAnnotation | null => {
      const { currentStreamIndex, streamAnnotations } = get();
      if (currentStreamIndex < 0 || !streamAnnotations[currentStreamIndex]) return null;
      return streamAnnotations[currentStreamIndex];
    },

    getCurrentAnnotationState: (): AnnotationState | null => {
      const currentStream = get().getCurrentStreamAnnotation();
      return currentStream ? currentStream.annotations : null;
    },

    hasMinPointsForClosing: (): boolean => {
      const currentAnnotation = get().getCurrentAnnotationState();
      return Boolean(currentAnnotation && currentAnnotation.points.length >= 3 && !currentAnnotation.isClosed);
    },

    checkCloseToStart: (point: Point): boolean => {
      const currentAnnotation = get().getCurrentAnnotationState();
      if (!currentAnnotation || currentAnnotation.points.length < 3) return false;

      const startPoint = currentAnnotation.points[0];
      const dx = point.x - startPoint.x;
      const dy = point.y - startPoint.y;
      return Math.sqrt(dx * dx + dy * dy) < CLOSE_THRESHOLD;
    },

    // --- Actions ---

    // --- Stream Management ---
    processRtspInput: async (inputText: string) => {
      const urls = extractRtspUrls(inputText);
      if (urls.length > 0) {
        await get().fetchMjpegUrls(urls);
      } else {
        set({ error: "No valid rtsp:// URLs found in input.", isLoadingStreams: false });
      }
    },

    processRtspFile: async (file: File) => {
      set({ isLoadingStreams: true, error: null });
      try {
        const text = await file.text();
        const urls = extractRtspUrls(text);
        if (urls.length > 0) {
          await get().fetchMjpegUrls(urls);
        } else {
           set({ error: "No valid rtsp:// URLs found in file.", isLoadingStreams: false });
        }
      } catch (err) {
        console.error("Error reading file:", err);
        set({ error: `Error reading file: ${err.message}`, isLoadingStreams: false });
      }
    },

    fetchMjpegUrls: async (rtspUrls: string[]) => {
      set({ isLoadingStreams: true, error: null });
      try {
        // *** Replace with your actual backend API call ***
        const backendResponse = await mockFetchMjpegUrlsFromBackend(rtspUrls);
        // const response = await fetch('/api/streams', { // Example real fetch
        //   method: 'POST',
        //   headers: { 'Content-Type': 'application/json' },
        //   body: JSON.stringify({ rtspUrls }),
        // });
        // if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        // const backendResponse: BackendStreamResponse[] = await response.json();


        const newStreamAnnotations: StreamAnnotation[] = backendResponse
         .filter(res => !res.error && res.mjpegUrl) // Filter out streams that failed on the backend
         .map(res => ({
            id: res.id, // Use ID from backend
            rtspUrl: res.rtspUrl,
            mjpegUrl: res.mjpegUrl,
            name: res.name || res.rtspUrl, // Fallback name
            annotations: createEmptyAnnotationState(),
         }));

        // Handle potential errors reported per stream
        const backendErrors = backendResponse
            .filter(res => res.error)
            .map(res => `Failed ${res.rtspUrl}: ${res.error}`)
            .join('\n');

        set(state => {
          // Avoid duplicates if URLs are resubmitted (optional, based on desired behavior)
          const existingRtspUrls = new Set(state.streamAnnotations.map(sa => sa.rtspUrl));
          const trulyNewAnnotations = newStreamAnnotations.filter(nsa => !existingRtspUrls.has(nsa.rtspUrl));

          state.streamAnnotations = [...state.streamAnnotations, ...trulyNewAnnotations];
          state.isLoadingStreams = false;
          state.error = backendErrors || null; // Show backend errors if any

          // Navigate to the first newly added stream if any were added
          if (trulyNewAnnotations.length > 0 && state.currentStreamIndex === -1) {
             state.currentStreamIndex = state.streamAnnotations.length - trulyNewAnnotations.length;
          } else if (state.streamAnnotations.length > 0 && state.currentStreamIndex === -1) {
              // If no new streams were added but list isn't empty, go to first
              state.currentStreamIndex = 0;
          }
        });

      } catch (err) {
        console.error("Failed to fetch MJPEG URLs:", err);
        set({ error: `Failed to fetch stream data: ${err.message}`, isLoadingStreams: false });
      }
    },

    navigateToStream: (index: number) => {
      const { currentStreamIndex, streamAnnotations } = get();
      if (index >= 0 && index < streamAnnotations.length && index !== currentStreamIndex) {
        set(state => {
          state.currentStreamIndex = index;
          // Reset UI states relevant to annotation on navigation
          state.isColorEditMode = false;
          state.mousePos = null;
          state.isMouseOverStart = false;
          // Note: We don't need konvaImageElement or isImageLoading anymore
          // as the MJPEG stream is handled by the <img> tag directly.
        });
      }
    },

    navigatePrev: () => {
      const { currentStreamIndex } = get();
      if (currentStreamIndex > 0) {
        get().navigateToStream(currentStreamIndex - 1);
      }
    },

    navigateNext: () => {
      const { currentStreamIndex, streamAnnotations } = get();
      if (currentStreamIndex < streamAnnotations.length - 1) {
        get().navigateToStream(currentStreamIndex + 1);
      }
    },

    clearStreams: () => {
        set({
            streamAnnotations: [],
            currentStreamIndex: -1,
            mousePos: null,
            isMouseOverStart: false,
            isColorEditMode: false,
            isLoadingStreams: false,
            error: null,
        });
    },


    // --- Annotation Actions (Logic operates on current stream's annotations) ---
    addPoint: (point) => {
      const { currentStreamIndex, isColorEditMode } = get();
      if (isColorEditMode || currentStreamIndex < 0) return;

      set(state => {
        const currentStream = state.streamAnnotations[currentStreamIndex];
        const currentAnnotation = currentStream?.annotations;
        // Prevent adding points if the shape is closed
        if (currentAnnotation && !currentAnnotation.isClosed) {
          currentAnnotation.points.push(point);
          // Add default color for the new line segment *implicitly* created
          // We only add color when the *second* point is added onwards
          if (currentAnnotation.points.length > 1) {
              // Ensure colors array matches number of segments (points - 1)
              while (currentAnnotation.lineSegmentColors.length < currentAnnotation.points.length - 1) {
                  currentAnnotation.lineSegmentColors.push(DEFAULT_LINE_COLOR);
              }
          }
        }
      });
    },

    closeShape: () => {
      const { currentStreamIndex } = get();
      if (currentStreamIndex < 0) return;

      set(state => {
        const currentStream = state.streamAnnotations[currentStreamIndex];
        const currentAnnotation = currentStream?.annotations;
        // Check if closable before proceeding
        if (currentAnnotation && currentAnnotation.points.length >= 3 && !currentAnnotation.isClosed) {
            currentAnnotation.isClosed = true;

            // Ensure lineSegmentColors has right length for the closing segment
            const numSegments = currentAnnotation.points.length; // Closed shape has segments = points
            while (currentAnnotation.lineSegmentColors.length < numSegments) {
                currentAnnotation.lineSegmentColors.push(DEFAULT_LINE_COLOR);
            }
             // Ensure it doesn't have *too many* colors if points were removed earlier
            currentAnnotation.lineSegmentColors = currentAnnotation.lineSegmentColors.slice(0, numSegments);

            // Reset interaction states
            state.mousePos = null;
            state.isMouseOverStart = false;
        }
      });
    },

    resetAnnotation: () => {
      const { currentStreamIndex } = get();
      if (currentStreamIndex < 0) return;

      set(state => {
        const currentStream = state.streamAnnotations[currentStreamIndex];
        if (currentStream) {
          currentStream.annotations = createEmptyAnnotationState();
        }
        // Reset UI state
        state.mousePos = null;
        state.isMouseOverStart = false;
        state.isColorEditMode = false;
      });
    },

    undoLastPoint: () => {
      const { currentStreamIndex, isColorEditMode } = get();
      if (isColorEditMode || currentStreamIndex < 0) return;

      set(state => {
        const currentStream = state.streamAnnotations[currentStreamIndex];
        const currentAnnotation = currentStream?.annotations;
        if (currentAnnotation && currentAnnotation.points.length > 0) {
          if (currentAnnotation.isClosed) {
            // If closed, just reopen it, keeping the points
            currentAnnotation.isClosed = false;
            // Remove the color for the *closing* segment
            currentAnnotation.lineSegmentColors.pop();
          } else {
            // If not closed, remove the last point
            currentAnnotation.points.pop();
            // Remove the color for the segment leading to the removed point
            if (currentAnnotation.lineSegmentColors.length > 0) {
                currentAnnotation.lineSegmentColors.pop();
            }
          }
        }
      });
    },

    toggleColorEditMode: () => {
      const { currentStreamIndex } = get();
      if (currentStreamIndex < 0) return; // Cannot edit if no stream selected

      const currentAnnotation = get().getCurrentAnnotationState();
       // Can only enter color edit mode if the shape is closed
      if (!currentAnnotation || !currentAnnotation.isClosed) return;

      set(state => {
        state.isColorEditMode = !state.isColorEditMode;
        // Reset mouse state when toggling mode
        state.mousePos = null;
        state.isMouseOverStart = false;
      });
    },

    toggleLineSegmentColor: (segmentIndex) => {
      const { currentStreamIndex, isColorEditMode } = get();
      if (!isColorEditMode || currentStreamIndex < 0) return;

      set(state => {
        const currentAnnotation = state.streamAnnotations[currentStreamIndex]?.annotations;
        if (currentAnnotation && segmentIndex >= 0 && segmentIndex < currentAnnotation.lineSegmentColors.length) {
          const currentColor = currentAnnotation.lineSegmentColors[segmentIndex];
          currentAnnotation.lineSegmentColors[segmentIndex] =
            currentColor === DEFAULT_LINE_COLOR ? TOGGLED_LINE_COLOR : DEFAULT_LINE_COLOR;
        }
      });
    },

    // --- UI Interaction ---
    setMousePosition: (point) => {
      set({ mousePos: point });
    },

    setMouseOverStart: (isOver) => {
      set({ isMouseOverStart: isOver });
    }
  }))
);
// --- Usage Notes ---
// 1. Replace 'ws://localhost:8000/ws/stream' with your actual backend WebSocket URL.
// 2. Your backend WebSocket endpoint needs to:
//    - Accept the RTSP URL (e.g., as a query parameter `?rtsp_url=...`).
//    - Establish a connection to that RTSP stream.
//    - Decode frames.
//    - Encode frames (e.g., as base64 JPEG or PNG).
//    - Send the base64 string data over the WebSocket connection to the client.
// 3. In your React component:
//    - Use `useStreamAnnotationStore(...)` to access state and actions.
//    - Call `addStreams(['rtsp://...'])` to initiate.
//    - Use `konvaImageElement` in your Konva `<Image>` component.
//    - Use `isLoadingFrame` and `webSocketStatus` / `webSocketError` to display loading/error states.
//    - IMPORTANT: Add cleanup logic (e.g., in a `useEffect` return function) to call `disconnectWebSocket()` when the component unmounts to prevent lingering connections.
//      ```jsx
//      import { useEffect } from 'react';
//      import { useStreamAnnotationStore } from './store'; // Adjust path

//      function AnnotationComponent() {
//          const disconnectWebSocket = useStreamAnnotationStore(s => s.disconnectWebSocket);
//          const konvaImageElement = useStreamAnnotationStore(s => s.konvaImageElement);
//          // ... other state and logic

//          useEffect(() => {
//              // Cleanup on unmount
//              return () => {
//                  console.log("Component unmounting, disconnecting WebSocket.");
//                  disconnectWebSocket();
//              };
//          }, [disconnectWebSocket]); // Dependency array includes the disconnect function

//          // ... rest of component
//          return (
//               <Stage>
//                  <Layer>
//                      {konvaImageElement && <KonvaImage image={konvaImageElement} width={STAGE_WIDTH} height={STAGE_HEIGHT} />}
//                      {/* ... other annotation elements ... */}
//                  </Layer>
//               </Stage>
//          );
//      }
//      ```

// import { create } from 'zustand';
// import { immer } from 'zustand/middleware/immer';

// export const STAGE_WIDTH = 960;
// export const STAGE_HEIGHT = 540;
// export const DOT_RADIUS = 6;
// export const DOT_FILL_COLOR = 'blue';
// export const DOT_HOVER_FILL_COLOR = 'red';
// export const DEFAULT_LINE_COLOR = 'black';
// export const TOGGLED_LINE_COLOR = 'red';
// export const LINE_STROKE_WIDTH = 3;
// export const PREVIEW_LINE_STROKE_COLOR = 'grey';
// export const PREVIEW_LINE_DASH = [5, 5];
// export const CLOSE_THRESHOLD = DOT_RADIUS * 3;

// // --- Types ---
// export interface Point {
//   x: number;
//   y: number;
// }

// // Represents the annotation state for a single image
// export interface AnnotationState {
//   points: Point[];
//   isClosed: boolean;
//   lineSegmentColors: string[]; // Colors for segments corresponding to points array
// }

// // Represents an image and its associated annotations
// export interface ImageAnnotation {
//   id: string; // Unique ID for React keys, etc.
//   imageUrl: string; // URL for display (e.g., object URL)
//   filename: string;
//   annotations: AnnotationState;
// }

// // The state of our annotation store
// interface ImageAnnotationState {
//   // Main data storage
//   imageAnnotations: ImageAnnotation[];
//   currentImageIndex: number;
  
//   // UI State
//   mousePos: Point | null;
//   isMouseOverStart: boolean;
//   isColorEditMode: boolean;
//   isImageLoading: boolean;
//   konvaImageElement: HTMLImageElement | null;
  
//   // Actions
//   uploadImages: (files: FileList) => void;
//   navigateToImage: (index: number) => void;
//   navigatePrev: () => void;
//   navigateNext: () => void;
//   addPoint: (point: Point) => void;
//   closeShape: () => void;
//   resetAnnotation: () => void;
//   undoLastPoint: () => void;
//   toggleColorEditMode: () => void;
//   toggleLineSegmentColor: (segmentIndex: number) => void;
//   setMousePosition: (point: Point | null) => void;
//   setMouseOverStart: (isOver: boolean) => void;
//   checkCloseToStart: (point: Point) => boolean;
  
//   // Utility getters
//   getCurrentAnnotation: () => AnnotationState | null;
//   hasMinPointsForClosing: () => boolean;
// }

// // Helper function to create an empty annotation state
// const createEmptyAnnotationState = (): AnnotationState => ({
//   points: [],
//   isClosed: false,
//   lineSegmentColors: [],
// });

// export const useImageAnnotationStore = create<ImageAnnotationState>()(
//   immer((set, get) => ({
//     // Initial state
//     imageAnnotations: [],
//     currentImageIndex: -1,
//     mousePos: null,
//     isMouseOverStart: false,
//     isColorEditMode: false,
//     isImageLoading: false,
//     konvaImageElement: null,
    
//     // Getters
//     getCurrentAnnotation: (): AnnotationState | null => {
//       const { currentImageIndex, imageAnnotations } = get();
//       if (currentImageIndex < 0 || !imageAnnotations[currentImageIndex]) return null;
//       return imageAnnotations[currentImageIndex].annotations;
//     },
    
//     hasMinPointsForClosing: (): boolean => {
//       const currentAnnotation = get().getCurrentAnnotation();
//       return Boolean(currentAnnotation && currentAnnotation.points.length >= 3 && !currentAnnotation.isClosed);
//     },
    
//     // Utility method to check if point is close to start
//     checkCloseToStart: (point: Point): boolean => {
//       const { currentImageIndex, imageAnnotations } = get();
//       if (currentImageIndex < 0 || imageAnnotations.length === 0) return false;
      
//       const currentPoints = imageAnnotations[currentImageIndex].annotations.points;
//       if (currentPoints.length < 3) return false;
      
//       const startPoint = currentPoints[0];
//       return Math.sqrt(Math.pow(point.x - startPoint.x, 2) + Math.pow(point.y - startPoint.y, 2)) < CLOSE_THRESHOLD;
//     },
    
//     // Actions
//     uploadImages: (files) => {
//       const { imageAnnotations } = get();
      
//       // Process new files
//       const newImageAnnotations = Array.from(files).map(file => ({
//         id: `${file.name}-${Date.now()}`,
//         imageUrl: URL.createObjectURL(file),
//         filename: file.name,
//         annotations: createEmptyAnnotationState(),
//       }));

//       set(state => {
//         state.imageAnnotations = [...imageAnnotations, ...newImageAnnotations];
//         state.currentImageIndex = imageAnnotations.length; // Switch to first new image
//       });
//     },
    
//     navigateToImage: (index) => {
//       const { currentImageIndex, imageAnnotations } = get();
      
//       // Only navigate if index is different
//       if (index === currentImageIndex) return;
      
//       set(state => {
//         state.currentImageIndex = index;
//         state.isColorEditMode = false;
//         state.mousePos = null;
//         state.isMouseOverStart = false;
        
//         // Clear image and set loading state
//         state.konvaImageElement = null;
//         state.isImageLoading = true;
//       });
      
//       // Load new image
//       const targetIndex = index;
//       if (targetIndex >= 0 && targetIndex < imageAnnotations.length) {
//         const img = new window.Image();
//         img.src = imageAnnotations[targetIndex].imageUrl;
        
//         // Use non-immer update for DOM elements to avoid type issues
//         img.onload = () => {
//           console.log("Image loaded:", imageAnnotations[targetIndex].imageUrl);
//           set(() => {
//             // Use non-immer update for DOM elements
//             return { konvaImageElement: img, isImageLoading: false };
//           });
//         };
        
//         img.onerror = () => {
//           console.error("Failed to load image:", imageAnnotations[targetIndex].imageUrl);
//           set(state => {
//             state.isImageLoading = false;
//           });
//         };
//       }
//     },
    
//     navigatePrev: () => {
//       const { currentImageIndex } = get();
//       if (currentImageIndex > 0) {
//         get().navigateToImage(currentImageIndex - 1);
//       }
//     },
    
//     navigateNext: () => {
//       const { currentImageIndex, imageAnnotations } = get();
//       if (currentImageIndex < imageAnnotations.length - 1) {
//         get().navigateToImage(currentImageIndex + 1);
//       }
//     },
    
//     addPoint: (point) => {
//       const { currentImageIndex, isColorEditMode } = get();
      
//       if (isColorEditMode || currentImageIndex < 0) return;
      
//       set(state => {
//         const currentImage = state.imageAnnotations[currentImageIndex];
//         if (currentImage) {
//           currentImage.annotations.points.push(point);
//         }
//       });
//     },
    
//     closeShape: () => {
//       const { currentImageIndex } = get();
      
//       if (currentImageIndex < 0) return;
      
//       set(state => {
//         const currentImage = state.imageAnnotations[currentImageIndex];
//         if (currentImage) {
//           currentImage.annotations.isClosed = true;
          
//           // Ensure lineSegmentColors has right length when closing
//           const points = currentImage.annotations.points;
//           const numSegments = points.length;
          
//           while (currentImage.annotations.lineSegmentColors.length < numSegments) {
//             currentImage.annotations.lineSegmentColors.push(DEFAULT_LINE_COLOR);
//           }
//         }
        
//         state.mousePos = null;
//         state.isMouseOverStart = false;
//       });
//     },
    
//     resetAnnotation: () => {
//       const { currentImageIndex } = get();
      
//       if (currentImageIndex < 0) return;
      
//       set(state => {
//         const currentImage = state.imageAnnotations[currentImageIndex];
//         if (currentImage) {
//           currentImage.annotations = createEmptyAnnotationState();
//         }
        
//         state.mousePos = null;
//         state.isMouseOverStart = false;
//         state.isColorEditMode = false;
//       });
//     },
    
//     undoLastPoint: () => {
//       const { currentImageIndex, isColorEditMode } = get();
      
//       if (isColorEditMode || currentImageIndex < 0) return;
      
//       set(state => {
//         const currentImage = state.imageAnnotations[currentImageIndex];
//         if (currentImage && currentImage.annotations.points.length > 0) {
//           if (currentImage.annotations.isClosed) {
//             currentImage.annotations.isClosed = false;
//           } else {
//             currentImage.annotations.points.pop();
//           }
          
//           // Adjust colors array if needed
//           const numSegments = currentImage.annotations.isClosed 
//             ? currentImage.annotations.points.length 
//             : Math.max(0, currentImage.annotations.points.length - 1);
            
//           currentImage.annotations.lineSegmentColors = 
//             currentImage.annotations.lineSegmentColors.slice(0, numSegments);
//         }
//       });
//     },
    
//     toggleColorEditMode: () => {
//       const { currentImageIndex, isColorEditMode } = get();
      
//       if (currentImageIndex < 0) return;
      
//       set(state => {
//         state.isColorEditMode = !isColorEditMode;
//         state.mousePos = null;
//         state.isMouseOverStart = false;
//       });
//     },
    
//     toggleLineSegmentColor: (segmentIndex) => {
//       const { currentImageIndex, isColorEditMode } = get();
      
//       if (!isColorEditMode || currentImageIndex < 0) return;
      
//       set(state => {
//         const currentImage = state.imageAnnotations[currentImageIndex];
//         if (currentImage && segmentIndex >= 0 && segmentIndex < currentImage.annotations.lineSegmentColors.length) {
//           const currentColor = currentImage.annotations.lineSegmentColors[segmentIndex];
//           currentImage.annotations.lineSegmentColors[segmentIndex] = 
//             currentColor === DEFAULT_LINE_COLOR ? TOGGLED_LINE_COLOR : DEFAULT_LINE_COLOR;
//         }
//       });
//     },
    
//     setMousePosition: (point) => {
//       set(state => {
//         state.mousePos = point;
//       });
//     },
    
//     setMouseOverStart: (isOver) => {
//       set(state => {
//         state.isMouseOverStart = isOver;
//       });
//     }
//   }))
// ); 
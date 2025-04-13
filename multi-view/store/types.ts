// --- 标注的类型定义 ---
export interface Point {
  x: number;
  y: number;
}
  
export interface Annotation {
  points: Point[];
  isClosed: boolean;
  // Stores indices of the *starting point* of selected lines.
  // e.g., [0, 3] means line 0-1 and line 3-4 are selected.
  selectedLineIndices: number[];
  zoneType?: 'inside' | 'outside' | null; // Renamed from areaType
}

export type ZoneType = 'inside' | 'outside' | null; // Add ZoneType definition

export type SourceStatus =
  | 'idle' // Initial state
  | 'loading_frame' // Fetching first frame
  | 'frame_loaded' // Frame ready for annotation
  | 'annotating' // Polygon drawing or line selection active
  | 'annotated' // Annotation complete, ready for analysis
  | 'analyzing' // Analysis request sent, waiting for MJPEG
  | 'streaming' // MJPEG stream received and playing
  | 'error_frame' // Error fetching first frame
  | 'error_analysis' // Error during analysis/MJPEG retrieval
  | 'error_rtsp' // General error related to this source

export interface RtspSourceInfo {
  url: string;
  firstFrameDataUrl: string | null; // Base64 data URL for the image
  annotation: Annotation;
  mjpegStreamUrl: string | null;
  status: SourceStatus;
  errorMessage?: string | null; // Optional error message for this source
  imageDimensions?: { width: number; height: number }; // Store original image dimensions
}

export type AnnotationMode = 'drawing' | 'line_selection' | 'idle';

export interface AppState {
  rtspSources: Record<string, RtspSourceInfo>; // Map URL to its info
  activeSourceUrl: string | null; // URL of the source currently being annotated/viewed
  annotationMode: AnnotationMode;
  globalStatus: 'idle' | 'loading_file' | 'processing_file' | 'error';
  globalErrorMessage?: string | null;
}

export interface AppActions {
  // --- Source Management ---
  addRtspSources: (urls: string[]) => Promise<void>; // Handles multiple URLs (from file or manual bulk)
  _fetchFirstFrame: (url: string) => Promise<void>; // Internal action to fetch frame
  setSourceFrame: (
    url: string,
    frameDataUrl: string | null,
    dimensions?: { width: number; height: number },
    error?: string
  ) => void;
  removeRtspSource: (url: string) => void;
  setActiveSource: (url: string | null) => void;
  resetSourceStatus: (url: string) => void; // Resets status, MJPEG, keeps frame/annotation

  // --- Annotation ---
  setAnnotationMode: (mode: AnnotationMode) => void;
  addAnnotationPoint: (url: string, point: Point) => void;
  undoLastPoint: (url: string) => void;
  clearAnnotation: (url: string) => void;
  closePolygon: (url: string) => void;
  toggleLineSelection: (url: string, lineIndex: number) => void; // Index of the starting point of the line
  setZoneType: (url: string, type: 'inside' | 'outside') => void; // Renamed from setAreaType

  // --- Analysis ---
  startAnalysis: (url: string) => Promise<void>;
  setMjpegStream: (url: string, streamUrl: string | null, error?: string) => void;

  // --- Global Status ---
  setGlobalStatus: (status: AppState['globalStatus'], message?: string) => void;
  clearGlobalError: () => void;
}
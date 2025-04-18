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
  zoneType?: 'inside' | 'outside' | null;
}

export type ZoneType = 'inside' | 'outside' | null; 

export type SourceStatus =
  | 'idle' 
  | 'loading_frame' 
  | 'frame_loaded' 
  | 'annotating' 
  | 'annotated' 
  | 'analyzing' 
  | 'streaming' 
  | 'error_frame' 
  | 'error_analysis' 
  | 'error_rtsp' 

export interface RtspSourceInfo {
  url: string;
  name?: string;
  firstFrameDataUrl: string | null;
  annotation: Annotation;
  mjpegStreamUrl: string | null; // Processed stream
  rawMjpegStreamUrl?: string | null; // Raw/original stream
  status: SourceStatus;
  errorMessage?: string | null;
  imageDimensions?: { width: number; height: number };
}

export type AnnotationMode = 'drawing' | 'line_selection' | 'idle';

export interface AppState {
  rtspSources: Record<string, RtspSourceInfo>;
  activeSourceUrl: string | null;
  annotationMode: AnnotationMode;
  globalStatus: 'idle' | 'loading_file' | 'processing_file' | 'error';
  globalErrorMessage?: string | null;
}

export interface AppActions {
  addRtspSources: (urls: string[]) => Promise<void>;
  _fetchFirstFrame: (url: string) => Promise<void>;
  setSourceFrame: (
    url: string,
    frameDataUrl: string | null,
    dimensions?: { width: number; height: number },
    error?: string,
    rawMjpegStreamUrl?: string | null
  ) => void;
  removeRtspSource: (url: string) => void;
  setActiveSource: (url: string | null) => void;
  resetSourceStatus: (url: string) => void;

  // --- Annotation ---
  setAnnotationMode: (mode: AnnotationMode) => void;
  addAnnotationPoint: (url: string, point: Point) => void;
  undoLastPoint: (url: string) => void;
  clearAnnotation: (url: string) => void;
  closePolygon: (url: string) => void;
  toggleLineSelection: (url: string, lineIndex: number) => void;
  setZoneType: (url: string, type: 'inside' | 'outside') => void;

  // --- Analysis ---
  startAnalysis: (url: string) => Promise<void>;
  setMjpegStream: (url: string, streamUrl: string | null, error?: string) => void;

  // --- Global Status ---
  setGlobalStatus: (status: AppState['globalStatus'], message?: string) => void;
  clearGlobalError: () => void;
}

// Interface for a single Camera
interface Camera {
  id: string; // Using RTSP URL as a unique ID seems reasonable for now
  rtspUrl: string;
  // Add other camera-specific states if needed later, e.g., status: 'connected' | 'disconnected'
}

// Interface for the Box State managed by Zustand
interface BoxState {
  // Box Identity
  boxId: string; // A unique identifier for the box if needed, maybe MAC address? Or just use name.
  locationName: string; // The primary name/location (e.g., "01号盒子" or "Store Address")

  // Network Configuration
  networkConfig: {
    ipv4Enabled: boolean;
    ipAddress: string;
    subnetMask: string;
    gateway: string;
    // Consider adding dhcpEnabled: boolean; if applicable
  };

  // Data Transmission Configuration
  dataTransmission: {
    uploadIntervalSeconds: number | null; // Store as number (seconds), null if not set
    targetServer: string;
    encryptionKey: string;
  };

  // Power On/Off Configuration
  powerConfig: {
    status: string; // e.g., "Online", "Offline", "Rebooting", "待实现" (To be implemented)
    // The UI shows two time inputs under "开机时间" (Power On Time).
    // Let's represent them as an array or distinct fields. An array is more flexible if the number can change.
    // Assuming these are specific scheduled 'ON' times.
    scheduledPowerOnTimes: [string | null, string | null]; // ["HH:MM", "HH:MM"], null if not set
    // You might need scheduledPowerOffTimes later as well
  };

  // Associated Cameras (Max 4)
  cameras: Camera[]; // Array of camera objects

  // Actions (methods to update the state)
  setLocationName: (name: string) => void;
  setNetworkConfig: (config: Partial<BoxState['networkConfig']>) => void;
  setDataTransmissionConfig: (config: Partial<BoxState['dataTransmission']>) => void;
  setPowerConfig: (config: Partial<BoxState['powerConfig']>) => void;
  setScheduledPowerOnTime: (index: 0 | 1, time: string | null) => void;
  addCamera: (rtspUrl: string) => void;
  removeCamera: (cameraId: string) => void; // Use camera ID (rtspUrl) to remove
  updateCamera: (cameraId: string, newRtspUrl: string) => void; // Update existing camera URL
  setInitialBoxData: (data: Partial<Omit<BoxState, 'cameras'>> & { cameras?: string[] }) => void; // Action to load initial data
  // Add async actions for saving/fetching if needed
}
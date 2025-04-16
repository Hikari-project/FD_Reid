import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer'; // 更新导入

// --- Interfaces (copy from above) ---
export interface Camera {
  id: string;
  rtspUrl: string;
}

export interface BoxState {
  boxId: string;
  locationName: string;
  networkConfig: {
    ipv4Enabled: boolean;
    ipAddress: string;
    subnetMask: string;
    gateway: string;
  };
  dataTransmission: {
    uploadIntervalSeconds: number | null;
    targetServer: string;
    encryptionKey: string;
  };
  powerConfig: {
    status: string;
    scheduledPowerOnTimes: [string | null, string | null];
  };
  cameras: Camera[];
  setLocationName: (name: string) => void;
  setNetworkConfig: (config: Partial<BoxState['networkConfig']>) => void;
  setDataTransmissionConfig: (config: Partial<BoxState['dataTransmission']>) => void;
  setPowerConfig: (config: Partial<BoxState['powerConfig']>) => void;
  setScheduledPowerOnTime: (index: 0 | 1, time: string | null) => void;
  addCamera: (rtspUrl: string) => void;
  removeCamera: (cameraId: string) => void;
  updateCamera: (cameraId: string, newRtspUrl: string) => void;
  setInitialBoxData: (data: Partial<Omit<BoxState, 'cameras'>> & { cameras?: string[] }) => void;
}

// --- Initial State ---
const initialBoxState = {
  boxId: 'unique-box-identifier-01', // Replace with actual unique ID if available
  locationName: '01号盒子', // Default or loaded name
  networkConfig: {
    ipv4Enabled: true,
    ipAddress: '',
    subnetMask: '',
    gateway: '',
  },
  dataTransmission: {
    uploadIntervalSeconds: 30, // Defaulting to 30 seconds
    targetServer: '',
    encryptionKey: '',
  },
  powerConfig: {
    status: '待实现', // To be implemented / Unknown
    scheduledPowerOnTimes: [null, null] as [string | null, string | null], // ['08:00', '08:00'] e.g.
  },
  cameras: [] as Camera[], // Start with no cameras
};

// --- Zustand Store Creation with Immer ---
export const useBoxStore = create(
  immer<BoxState>((set) => ({
    ...initialBoxState,

    // --- Actions ---
    setLocationName: (name) => 
      set((state) => {
        state.locationName = name;
      }),

    setNetworkConfig: (configUpdate) => 
      set((state) => {
        Object.assign(state.networkConfig, configUpdate);
      }),

    setDataTransmissionConfig: (configUpdate) => 
      set((state) => {
        Object.assign(state.dataTransmission, configUpdate);
      }),

    setPowerConfig: (configUpdate) => 
      set((state) => {
        Object.assign(state.powerConfig, configUpdate);
      }),

    setScheduledPowerOnTime: (index, time) => 
      set((state) => {
        if (index === 0 || index === 1) {
          state.powerConfig.scheduledPowerOnTimes[index] = time;
        }
      }),

    addCamera: (rtspUrl) => 
      set((state) => {
        if (state.cameras.length < 4 && rtspUrl && !state.cameras.some(cam => cam.rtspUrl === rtspUrl)) {
          state.cameras.push({ id: rtspUrl, rtspUrl: rtspUrl }); // Use URL as ID
        } else {
          if (state.cameras.length >= 4) {
            console.warn("Cannot add more than 4 cameras.");
            // Optionally show user feedback
          }
          if (state.cameras.some(cam => cam.rtspUrl === rtspUrl)) {
            console.warn(`Camera with RTSP URL ${rtspUrl} already exists.`);
            // Optionally show user feedback
          }
        }
      }),

    removeCamera: (cameraId) => 
      set((state) => {
        state.cameras = state.cameras.filter((cam) => cam.id !== cameraId);
      }),

    updateCamera: (cameraId, newRtspUrl) => 
      set((state) => {
        // Ensure the new URL doesn't conflict with another existing camera (excluding itself)
        const conflict = state.cameras.some(cam => cam.id !== cameraId && cam.rtspUrl === newRtspUrl);
        if (conflict) {
          console.warn(`Another camera already uses the RTSP URL ${newRtspUrl}.`);
          // Optionally show user feedback
          return; // Prevent update if conflict
        }

        const cameraIndex = state.cameras.findIndex((cam) => cam.id === cameraId);
        if (cameraIndex !== -1 && newRtspUrl) {
          // Update both id and rtspUrl if using URL as ID
          state.cameras[cameraIndex].id = newRtspUrl;
          state.cameras[cameraIndex].rtspUrl = newRtspUrl;
        }
      }),

    setInitialBoxData: (data) => 
      set((state) => {
        // Merge top-level properties
        if (data.boxId) state.boxId = data.boxId;
        if (data.locationName) state.locationName = data.locationName;
        
        if (data.networkConfig) {
          Object.assign(state.networkConfig, data.networkConfig);
        }
        
        if (data.dataTransmission) {
          Object.assign(state.dataTransmission, data.dataTransmission);
        }
        
        if (data.powerConfig) {
          Object.assign(state.powerConfig, data.powerConfig);
        }

        // Handle cameras separately - assuming input is an array of RTSP URLs
        if (data.cameras) {
          state.cameras = data.cameras
            .filter(url => !!url) // Remove empty URLs
            .slice(0, 4) // Ensure max 4 cameras
            .map(url => ({ id: url, rtspUrl: url })); // Convert to Camera objects
        }
      }),

    // --- Example Async Action (Placeholder) ---
    // fetchBoxData: async () => {
    //   // set({ loading: true }); // Add loading state if needed
    //   try {
    //     // const response = await fetch('/api/box/config'); // Your API endpoint
    //     // const data = await response.json();
    //     // Simulate fetched data:
    //     const fetchedData = {
    //       boxId: 'fetched-box-id',
    //       locationName: 'Fetched Store Name',
    //       networkConfig: { ipv4Enabled: false, ipAddress: '192.168.1.101', subnetMask: '255.255.255.0', gateway: '192.168.1.1' },
    //       dataTransmission: { uploadIntervalSeconds: 60, targetServer: 'http://example.com/upload', encryptionKey: 'fetched-key' },
    //       powerConfig: { status: 'Online', scheduledPowerOnTimes: ['09:00', null] as [string | null, string | null] },
    //       cameras: ['rtsp://cam1.example.com', 'rtsp://cam2.example.com']
    //     };
    //     get().setInitialBoxData(fetchedData); // Use the existing action to update state
    //   } catch (error) {
    //     console.error("Failed to fetch box data:", error);
    //     // set({ error: 'Failed to load data' }); // Add error state if needed
    //   } finally {
    //     // set({ loading: false });
    //   }
    // },
  }))
);

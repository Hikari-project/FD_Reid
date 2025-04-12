import { createEmptyAnnotationState, StreamAnnotation } from "@/store/useImageAnnotationStore";

// Helper function to extract RTSP URLs from text
export const extractRtspUrls = (text: string): string[] => {
    const rtspRegex = /rtsp:\/\/[^\s]+/g;
    const matches = text.match(rtspRegex);
    // Basic validation and deduplication
    return [...new Set(matches || [])].filter(url => url.startsWith("rtsp://"));
};

// API functions
export const fetchMjpegUrls = async (rtspUrls: string[]) => {
    console.log("Sending to backend:", rtspUrls);
    // Replace with your actual API call
    const response = await fetch('/api/streams', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ rtspUrls }),
    });
    
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
};

// Processing functions
export const processRtspInput = async (inputText: string): Promise<StreamAnnotation[]> => {
    const urls = extractRtspUrls(inputText);
    if (urls.length === 0) {
      throw new Error("No valid rtsp:// URLs found in input.");
    }
    const backendResponse = await fetchMjpegUrls(urls);
    
    return backendResponse
      .filter(res => !res.error && res.mjpegUrl)
      .map(res => ({
        id: res.id,
        rtspUrl: res.rtspUrl,
        mjpegUrl: res.mjpegUrl,
        name: res.name || res.rtspUrl,
        annotations: createEmptyAnnotationState(),
      }));
  };

export const processRtspFile = async (file: File): Promise<StreamAnnotation[]> => {
  const text = await file.text();
  const urls = extractRtspUrls(text);
  if (urls.length === 0) {
    throw new Error("No valid rtsp:// URLs found in file.");
  }

  const backendResponse = await fetchMjpegUrls(urls);

  return backendResponse
    .filter(res => !res.error && res.mjpegUrl)
    .map(res => ({
    id: res.id,
    rtspUrl: res.rtspUrl,
    mjpegUrl: res.mjpegUrl,
    name: res.name || res.rtspUrl,
    annotations: createEmptyAnnotationState(),
    }));
};
import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

const extractRtspUrls = (text: string): string[] => {
  const rtspRegex = /rtsp:\/\/[^\s]+/g;
  const matches = text.match(rtspRegex);
  return [...new Set(matches || [])].filter(url => url.startsWith("rtsp://"));
};

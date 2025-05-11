'use client';

import { useEffect } from 'react';
import { useAppStore } from '@/store/useCustomerAnalysis';

export default function InitRtspClient() {
  const initializeStreamsOnLogin = useAppStore(state => state.initializeStreamsOnLogin);

  useEffect(() => {
    initializeStreamsOnLogin(); // 调后端接口获取 RTSP 流信息
  }, []);

  return null;
}

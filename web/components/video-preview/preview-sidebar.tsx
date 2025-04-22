'use client';

import React, { useMemo } from 'react';
import { useAppStore } from '@/store/useCustomerAnalysis';
import { Archive, Camera } from 'lucide-react';

const PreviewSidebar = () => {
  const sourcesObject = useAppStore(state => state.rtspSources);
  const sources = useMemo(() => Object.values(sourcesObject), [sourcesObject]);

  return (
    <div className="w-40 h-full bg-white p-3 rounded-md shadow-sm border border-gray-200 flex flex-col">
      <div className="flex items-center mb-3 pb-2 border-b border-gray-200">
        <Archive className="h-5 w-5 mr-2 text-gray-600" />
        <h2 className="text-base font-medium text-gray-700">01号盒子</h2>
      </div>
      <ul className="space-y-1 flex-grow overflow-y-auto">
        {sources.length === 0 && (
           <li className="text-center text-gray-500 text-sm mt-4">暂无视频源</li>
        )}
        {sources.map((source) => (
          <li key={source.url} className="flex items-center py-1.5 px-2 rounded hover:bg-gray-100 cursor-default">
            <Camera className="h-5 w-5 mr-2.5 text-gray-500" />
            <span className="text-sm text-gray-800">视频</span>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default PreviewSidebar;

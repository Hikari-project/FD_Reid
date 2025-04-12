'use client';

import React from 'react';
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Search } from 'lucide-react';

export default function BoxSelectionHeader() {

  return (
    <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
      <div className="flex items-center gap-2">
        <Label htmlFor="box-search" className="text-sm font-medium whitespace-nowrap">盒子名称/配置</Label>
        <Input id="box-search" placeholder="输入盒子" className="w-auto" />
        <Button className='bg-blue-500 hover:bg-blue-600 text-white'>查询</Button>
      </div>
      <Button className='bg-blue-500 hover:bg-blue-600 text-white'>选择</Button>
    </div>
  );
} 
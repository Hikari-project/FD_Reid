import React from 'react';
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { Plus, Upload, Search, Trash2 } from 'lucide-react';

export default function ManagementHeader() {

  return (
    <div className="p-4 bg-card rounded-lg shadow-sm mb-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div className="flex flex-col sm:flex-row gap-2 items-end">
          <div className="flex-grow">
            <Label htmlFor="rtsp-search-type" className="text-sm font-medium mb-1 block">区域类型</Label>
            <Input id="rtsp-search-type" placeholder="请输入RTSP流" />
          </div>
          <Button className='bg-blue-500 hover:bg-blue-600 text-white' ><Search className="mr-2 h-4 w-4" />查询</Button>
        </div>

        <div className="flex flex-col sm:flex-row gap-2 items-end">
           <div className="flex-grow">
              <Label htmlFor="rtsp-search-config" className="text-sm font-medium mb-1 block">盒子配置</Label>
              <Input id="rtsp-search-config" placeholder="请输入RTSP流" />
           </div>
           <Button className='bg-blue-500 hover:bg-blue-600 text-white' ><Search className="mr-2 h-4 w-4" />查询</Button>
        </div>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex gap-2">
           <Button variant="outline"><Plus className="mr-2 h-4 w-4" />添加盒子</Button>
           <Button variant="outline"><Upload className="mr-2 h-4 w-4" />导入</Button>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center space-x-2">
            <Checkbox id="select-all" />
            <Label htmlFor="select-all" className="text-sm font-medium cursor-pointer whitespace-nowrap">全选</Label>
           </div>
           <Button variant="destructive" size="sm"><Trash2 className="mr-1 h-4 w-4" />删除</Button>
        </div>
      </div>
    </div>
  );
} 
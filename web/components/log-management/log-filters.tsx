"use client"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { DatePickerWithRange } from "@/components/ui/date-range-picker"

// TODO: Define props for filter values and onChange handlers
// For now, filter values are handled internally or not at all.
// import { GetLogsParams } from "./types"; // Placeholder if we connect to API types

export function LogFilters() {
  return (
    <div className="flex items-center gap-4 flex-wrap">
      <Select>
        <SelectTrigger className="w-[200px]">
          <SelectValue placeholder="请选择操作模块" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="box">盒子管理</SelectItem>
          <SelectItem value="user">用户管理</SelectItem>
          <SelectItem value="terminal">镜头配置</SelectItem>
          <SelectItem value="data">数据推送</SelectItem>
          <SelectItem value="video">视频流获取</SelectItem>
        </SelectContent>
      </Select>

      <Select>
        <SelectTrigger className="w-[200px]">
          <SelectValue placeholder="请选择操作名" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="boxCrud">盒子增删改查</SelectItem>
          <SelectItem value="authControl">权限修改</SelectItem>
          <SelectItem value="terminalCrud">镜头增删改查</SelectItem>
          <SelectItem value="monitor">监控调度</SelectItem>
          <SelectItem value="userCrud">用户增删改查</SelectItem>
        </SelectContent>
      </Select>

      <Select>
        <SelectTrigger className="w-[200px]">
          <SelectValue placeholder="请选择操作类型" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="abnormal">取流异常</SelectItem>
          <SelectItem value="data">数据推送</SelectItem>
          <SelectItem value="system">系统操作</SelectItem>
        </SelectContent>
      </Select>

      <Input placeholder="请输入操作人" className="w-[200px]" />
      
      <DatePickerWithRange className="w-[300px]" />
      <Button className="bg-blue-600 hover:bg-blue-700">查询</Button>
      <Button variant="outline" className="text-blue-600 border-blue-600 hover:bg-blue-50">重置</Button>
    </div>
  )
}

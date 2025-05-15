"use client"

import { useState, useEffect } from "react"
import useSWR from 'swr'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { LogFilters } from "@/components/log-management/log-filters"
import { LogTable } from "@/components/log-management/log-table"
import { PaginationBar } from "@/components/log-management/pagination-bar"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { LogEntry, GetLogsResponse } from "@/components/log-management/types"

// Fetcher function for SWR
const fetcher = async (url: string): Promise<GetLogsResponse> => {
  const res = await fetch(url)
  if (!res.ok) {
    const error = new Error('An error occurred while fetching the data.')
    // Attach extra info to the error object.
    // error.info = await res.json()
    // error.status = res.status
    throw error
  }
  return res.json()
}

export default function LogManagement() {
  // Remove the initial static logs, data will come from SWR
  // const [logs, setLogs] = useState<LogEntry[]>([]); 
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(8);

  // SWR hook to fetch logs
  // The API path /api/logs is assumed. Adjust if your backend route is different.
  const { data: fetchedLogs, error, isLoading } = useSWR<GetLogsResponse>(
    `/api/logs?page=${currentPage}&num=${itemsPerPage}`,
    fetcher
  );

  // For now, totalLogCount will be based on the fetched items for the current page.
  // Ideally, the API should provide a total count for proper pagination.
  // Or, we might need another SWR call if there is a separate endpoint for total count.
  const totalLogCount = fetchedLogs?.length || 0; 

  // Handle loading and error states
  if (isLoading) return <div className="p-6">Loading logs...</div>
  if (error) return <div className="p-6">Failed to load logs. Error: {error.message}</div>

  // If data is not yet available (e.g. initial load before SWR resolves), pass empty array
  const logsToDisplay = fetchedLogs || [];

  return (
    <div className="p-6 space-y-6">
      <LogFilters />

      <div className="flex justify-between">
        <div></div>
        <div className="space-x-2">
          <Dialog>
            <DialogTrigger asChild>
              <Button variant="outline" className="text-blue-600 border-blue-600 hover:bg-blue-50">+ 添加记录</Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[800px]">
              <DialogHeader>
                <DialogTitle>添加日志</DialogTitle>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div className="flex flex-wrap gap-4">
                  <div className="flex-1">
                    <div className="mb-2 text-sm">操作模块</div>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="请选择操作模块" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="box">盒子管理</SelectItem>
                        <SelectItem value="user">用户管理</SelectItem>
                        <SelectItem value="terminal">终端配置</SelectItem>
                        <SelectItem value="data">数据推送</SelectItem>
                        <SelectItem value="video">视频流获取</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="flex-1">
                    <div className="mb-2 text-sm">操作名</div>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="请选择操作名" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="boxCrud">盒子增删改查</SelectItem>
                        <SelectItem value="authControl">权限修改</SelectItem>
                        <SelectItem value="terminalCrud">终端增删改查</SelectItem>
                        <SelectItem value="monitor">监控调度</SelectItem>
                        <SelectItem value="userCrud">用户增删改查</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="flex-1">
                    <div className="mb-2 text-sm">操作类型</div>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="请选择操作类型" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="cancel">取消异常</SelectItem>
                        <SelectItem value="data">数据推送</SelectItem>
                        <SelectItem value="system">系统操作</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="flex-1">
                    <div className="mb-2 text-sm">操作人</div>
                    <Input placeholder="请输入操作人" />
                  </div>
                </div>
              </div>
              <div className="flex justify-end gap-3">
                <Button variant="outline" className="text-blue-600 border-blue-600 hover:bg-blue-50">取消</Button>
                <Button className="bg-blue-600 hover:bg-blue-700">确认</Button>
              </div>
            </DialogContent>
          </Dialog>
          <Button variant="outline" className="text-blue-600 border-blue-600 hover:bg-blue-50">⇲ 导出</Button>
        </div>
      </div>

      <LogTable logs={logsToDisplay} />

      {/* 
        Note on Pagination: 
        The current `totalLogCount` is just the number of items on the current page. 
        For true pagination, the API needs to return the overall total number of logs, 
        or we need a separate endpoint to fetch this total. 
        The PaginationBar component will also need to be updated to handle page changes,
        which would then trigger a re-fetch with SWR by changing `currentPage`.
      */}
      <PaginationBar totalItems={totalLogCount} />
    </div>
  )
}

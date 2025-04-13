"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { DatePickerWithRange } from "@/components/ui/date-range-picker"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"

interface LogEntry {
  id: string
  operationType: string
  operationName: string
  operationCategory: string
  operator: string
  operationTime: string
}

export default function LogManagement() {
  const [logs, setLogs] = useState<LogEntry[]>([
    {
      id: "01",
      operationType: "盒子管理",
      operationName: "盒子增删改查",
      operationCategory: "取消异常",
      operator: "读宇",
      operationTime: "2025-01-05 12:01:20"
    },
    // ... 可以添加更多示例数据
  ])

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center gap-4 flex-wrap">
        <Select>
          <SelectTrigger className="w-[200px]">
            <SelectValue placeholder="请选择操作模块" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="box">盒子管理</SelectItem>
            {/* 添加更多选项 */}
          </SelectContent>
        </Select>

        <Select>
          <SelectTrigger className="w-[200px]">
            <SelectValue placeholder="请选择操作名" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="crud">盒子增删改查</SelectItem>
            {/* 添加更多选项 */}
          </SelectContent>
        </Select>

        <Select>
          <SelectTrigger className="w-[200px]">
            <SelectValue placeholder="请选择操作类型" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="cancel">取消异常</SelectItem>
            {/* 添加更多选项 */}
          </SelectContent>
        </Select>

        <Input placeholder="请输入操作人" className="w-[200px]" />
        
        <DatePickerWithRange className="w-[300px]" />
        <Button className="bg-blue-600 hover:bg-blue-700">查询</Button>
        <Button variant="outline" className="text-blue-600 border-blue-600 hover:bg-blue-50">重置</Button>
      </div>

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

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>编号</TableHead>
            <TableHead>操作模块</TableHead>
            <TableHead>操作名</TableHead>
            <TableHead>操作类型</TableHead>
            <TableHead>操作人</TableHead>
            <TableHead>操作日期</TableHead>
            <TableHead>操作</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {logs.map((log) => (
            <TableRow key={log.id}>
              <TableCell>{log.id}</TableCell>
              <TableCell>{log.operationType}</TableCell>
              <TableCell>{log.operationName}</TableCell>
              <TableCell>{log.operationCategory}</TableCell>
              <TableCell>{log.operator}</TableCell>
              <TableCell>{log.operationTime}</TableCell>
              <TableCell>
                <Dialog>
                  <DialogTrigger asChild>
                    <Button variant="link" className="text-blue-500">
                      详情
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="sm:max-w-[425px]">
                    <DialogHeader className="mb-8">
                      <DialogTitle className="text-xl font-medium">日志详情</DialogTitle>
                    </DialogHeader>
                    <div className="grid gap-8">
                      <div className="grid gap-8">
                        <div className="grid grid-cols-[120px_1fr] items-center">
                          <div className="text-left pl-7 text-sm text-gray-500">操作模块</div>
                          <Input value={log.operationType} readOnly className="bg-gray-50" />
                        </div>
                        <div className="grid grid-cols-[120px_1fr] items-center">
                          <div className="text-left pl-7 text-sm text-gray-500">操作名</div>
                          <Input value={log.operationName} readOnly className="bg-gray-50" />
                        </div>
                        <div className="grid grid-cols-[120px_1fr] items-center">
                          <div className="text-left pl-7 text-sm text-gray-500">操作类型</div>
                          <Input value={log.operationCategory} readOnly className="bg-gray-50" />
                        </div>
                        <div className="grid grid-cols-[120px_1fr] items-center">
                          <div className="text-left pl-7 text-sm text-gray-500">操作人</div>
                          <Input value={log.operator} readOnly className="bg-gray-50" />
                        </div>
                        <div className="grid grid-cols-[120px_1fr] items-center">
                          <div className="text-left pl-7 text-sm text-gray-500">操作日期</div>
                          <Input value={log.operationTime} readOnly className="bg-gray-50" />
                        </div>
                      </div>
                    </div>
                  </DialogContent>
                </Dialog>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      <div className="flex items-center justify-between">
        <div className="text-sm text-gray-500">共20条</div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" className="text-blue-600 border-blue-600 hover:bg-blue-50">上一页</Button>
          <Button variant="outline" size="sm" className="text-blue-600 border-blue-600 hover:bg-blue-50">1</Button>
          <Button variant="outline" size="sm" className="text-blue-600 border-blue-600 hover:bg-blue-50">2</Button>
          <Button variant="outline" size="sm" className="text-blue-600 border-blue-600 hover:bg-blue-50">3</Button>
          <Button variant="outline" size="sm" className="text-blue-600 border-blue-600 hover:bg-blue-50">下一页</Button>
          <span className="mx-2">前往</span>
          <Input className="w-16" />
          <span>页</span>
        </div>
      </div>
    </div>
  )
}

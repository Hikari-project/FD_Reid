"use client"

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { LogEntry as PageLogEntry } from "./types" // Using LogEntry from types.ts
// Note: The LogEntry interface in page.tsx has different field names
// than the one in types.ts. For now, we'll use the types.ts definition.
// This might require adjustments in how data is passed or mapped.

// TODO: Reconcile the LogEntry type definition if it's meant to be the same.
// The LogEntry in page.tsx had: id, operationType, operationName, operationCategory, operator, operationTime
// The LogEntry in types.ts has: id, operator_module, operator_type, person_name, describes, create_time, state

// For this component, we'll assume the structure from types.ts
// but the provided mock data in page.tsx used a different structure.
// This component will expect props matching types.ts's LogEntry.

interface LogTableProps {
  logs: PageLogEntry[] // Changed to PageLogEntry to reflect types.ts
}

export function LogTable({ logs }: LogTableProps) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>编号</TableHead>
          <TableHead>操作模块</TableHead>
          <TableHead>操作名</TableHead> {/* This was operationName in page.tsx */}
          <TableHead>操作类型</TableHead> {/* This was operationCategory in page.tsx */}
          <TableHead>操作人</TableHead>
          <TableHead>操作日期</TableHead>
          <TableHead>状态</TableHead> {/* Added from types.ts */}
          <TableHead>描述</TableHead> {/* Added from types.ts */}
          <TableHead>操作</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {logs.map((log) => (
          <TableRow key={log.id}>
            <TableCell>{log.id}</TableCell>
            <TableCell>{log.operator_module}</TableCell>
            <TableCell>{log.operator_type}</TableCell> {/* Changed from operationName */}
            <TableCell>{log.describes}</TableCell> {/* Changed, this seems more like a category/type */}
            <TableCell>{log.person_name}</TableCell>
            <TableCell>{log.create_time}</TableCell>
            <TableCell>{log.state}</TableCell>
            <TableCell>{log.describes}</TableCell> {/* Using describes again as placeholder, adjust as needed */}
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
                        <Input value={log.operator_module} readOnly className="bg-gray-50" />
                      </div>
                      <div className="grid grid-cols-[120px_1fr] items-center">
                        <div className="text-left pl-7 text-sm text-gray-500">操作名</div>
                        <Input value={log.operator_type} readOnly className="bg-gray-50" />
                      </div>
                      <div className="grid grid-cols-[120px_1fr] items-center">
                        <div className="text-left pl-7 text-sm text-gray-500">描述</div>
                        <Input value={log.describes} readOnly className="bg-gray-50" />
                      </div>
                      <div className="grid grid-cols-[120px_1fr] items-center">
                        <div className="text-left pl-7 text-sm text-gray-500">操作人</div>
                        <Input value={log.person_name} readOnly className="bg-gray-50" />
                      </div>
                      <div className="grid grid-cols-[120px_1fr] items-center">
                        <div className="text-left pl-7 text-sm text-gray-500">操作日期</div>
                        <Input value={log.create_time} readOnly className="bg-gray-50" />
                      </div>
                       <div className="grid grid-cols-[120px_1fr] items-center">
                        <div className="text-left pl-7 text-sm text-gray-500">状态</div>
                        <Input value={log.state} readOnly className="bg-gray-50" />
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
  )
}


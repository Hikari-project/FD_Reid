import React from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogClose,
} from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { BoxData } from './management-boxes';

interface EditBoxDialogProps {
  box: BoxData | null;
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
}

export default function EditBoxDialog({ box, isOpen, onOpenChange }: EditBoxDialogProps) {
  if (!box) {
    return null;
  }

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>编辑盒子: {box.name}</DialogTitle>
        </DialogHeader>

        <Tabs defaultValue="network" className="w-full pt-2">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="network">网络配置</TabsTrigger>
            <TabsTrigger value="transfer">数据传输</TabsTrigger>
            <TabsTrigger value="power">开关机配置</TabsTrigger>
          </TabsList>

          <TabsContent value="network" className="mt-4 space-y-4">
            <div className="flex items-center space-x-2">
              <Label htmlFor="ipv4-switch" className="font-semibold">IPv4</Label>
              <Switch id="ipv4-switch" defaultChecked={true} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="ip-address">IP地址</Label>
              <Input id="ip-address" placeholder="请输入IP地址" defaultValue={"192.168.1.100"}/>
            </div>
            <div className="space-y-2">
              <Label htmlFor="subnet-mask">子网掩码</Label>
              <Input id="subnet-mask" placeholder="请输入子网掩码" defaultValue={"255.255.255.0"}/>
            </div>
            <div className="space-y-2">
              <Label htmlFor="gateway">网关</Label>
              <Input id="gateway" placeholder="请输入网关" defaultValue={"192.168.1.1"}/>
            </div>
          </TabsContent>

          <TabsContent value="transfer" className="mt-4 space-y-4">
            <div className="space-y-2">
              <Label htmlFor="upload-interval">上传周期</Label>
              <Input id="upload-interval" placeholder="例如：30 (秒)" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="target-server">目标服务器</Label>
              <Input id="target-server" placeholder="请输入服务器地址" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="encryption-key">加密密钥</Label>
              <Input id="encryption-key" type="password" placeholder="请输入密钥" />
            </div>
          </TabsContent>

          <TabsContent value="power" className="mt-4 space-y-6">
             <h3 className="text-md font-semibold border-b pb-2">盒子状态</h3>
             <p className="text-sm text-muted-foreground">(当前状态显示区域 - 待实现)</p>

             <h3 className="text-md font-semibold border-b pb-2">开机时间</h3>
             <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 items-end">
               <div className="space-y-2">
                 <Label htmlFor="power-on-time">设置开机时间</Label>
                 <Input id="power-on-time" type="time" placeholder="HH:MM" />
               </div>
                <div className="space-y-2">
                 <Label htmlFor="power-off-time">设置关机时间</Label>
                 <Input id="power-off-time" type="time" placeholder="HH:MM" />
               </div>
               <Button className='bg-blue-500 hover:bg-blue-600 text-white'>设置</Button> 
             </div>

             <div className="flex space-x-2 pt-4">
                <Button variant="destructive">关机</Button>
                <Button className='bg-blue-500 hover:bg-blue-600 text-white'>重启</Button>
             </div>
          </TabsContent>
        </Tabs>

        <DialogFooter className="pt-4">
           <DialogClose asChild>
             <Button type="button" variant="outline">取消</Button>
           </DialogClose>
           <Button type="button" variant="outline">测试连接</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
} 
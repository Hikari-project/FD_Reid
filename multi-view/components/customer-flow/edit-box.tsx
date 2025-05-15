import React, { useCallback, useState } from 'react';
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
import { BoxState, useBoxStore } from '@/store/useBoxmanagement';
import { shallow } from 'zustand/shallow'; // Import shallow

interface EditBoxProps {
  // If the box data is entirely within the store, you might not need to pass it as a prop
  // isOpen and onOpenChange are still valid for controlling the dialog itself.
  // box: BoxState | null; // <-- Consider if this prop is still needed if store is source of truth
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
}

// It's often better to fetch/set the initial state in the store
// when the component mounts or when the box context changes,
// rather than passing the full `box` object prop if it's already in the store.

export default function EditBox({ /* box, */ isOpen, onOpenChange }: EditBoxProps) {

  // Use a single selector with shallow comparison for multiple state slices
  const locationName = useBoxStore((state: BoxState) => state.locationName);
  const networkConfig = useBoxStore((state: BoxState) => state.networkConfig);
  const dataTransmission = useBoxStore((state: BoxState) => state.dataTransmission);
  const powerConfig = useBoxStore((state: BoxState) => state.powerConfig);

  const setNetworkConfig = useBoxStore((state: BoxState) => state.setNetworkConfig);
  const setDataTransmissionConfig = useBoxStore((state: BoxState) => state.setDataTransmissionConfig);
  const setScheduledPowerOnTime = useBoxStore((state: BoxState) => state.setScheduledPowerOnTime);

  // Optional: Add a check if essential data hasn't loaded yet,
  // depending on how you initialize the store.
  // if (!locationName && !networkConfig /* etc */) {
  //    return null; // Or a loading indicator
  // }

  // --- Event Handlers ---
  // Wrap handlers in useCallback if they are passed down or have dependencies
  // For simple setters directly calling store actions, useCallback might be overkill
  // unless the component becomes very complex or performance is critical.

  const handleIpChange = (e: React.ChangeEvent<HTMLInputElement>) => setNetworkConfig({ ipAddress: e.target.value });
  const handleSubnetChange = (e: React.ChangeEvent<HTMLInputElement>) => setNetworkConfig({ subnetMask: e.target.value });
  const handleGatewayChange = (e: React.ChangeEvent<HTMLInputElement>) => setNetworkConfig({ gateway: e.target.value });
  const handleIpv4Toggle = (checked: boolean) => setNetworkConfig({ ipv4Enabled: checked });

  const handleIntervalChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    // Ensure conversion to number or null
    const seconds = value === '' ? null : parseInt(value, 10);
    if (value === '' || !isNaN(seconds!)) {
        setDataTransmissionConfig({ uploadIntervalSeconds: seconds ?? 0 });
    }
  };
  const handleServerChange = (e: React.ChangeEvent<HTMLInputElement>) => setDataTransmissionConfig({ targetServer: e.target.value });
  const handleKeyChange = (e: React.ChangeEvent<HTMLInputElement>) => setDataTransmissionConfig({ encryptionKey: e.target.value });

  // Ensure time values are strings in "HH:MM" format or null
  const handlePowerOnTimeChange = (e: React.ChangeEvent<HTMLInputElement>) => setScheduledPowerOnTime(0, e.target.value || null);
  const handlePowerOffTimeChange = (e: React.ChangeEvent<HTMLInputElement>) => setScheduledPowerOnTime(1, e.target.value || null); // Assuming index 1 is for off time based on UI


  // --- Actions ---
  // These should ideally trigger async actions in your store if they involve API calls
  const handleSetTimes = useCallback(() => {
      console.log("Setting times:", powerConfig.scheduledPowerOnTimes);
      // TODO: Call an async action in the store to save these times
      // e.g., useBoxStore.getState().savePowerSchedule(powerConfig.scheduledPowerOnTimes);
  }, [powerConfig.scheduledPowerOnTimes]); // Dependency needed if reading from component state

  const handleShutdown = useCallback(() => {
      console.log("Shutdown requested for box:", locationName);
      // TODO: Call an async action in the store
      // e.g., useBoxStore.getState().shutdownBox();
  }, [locationName]);

  const handleReboot = useCallback(() => {
      console.log("Reboot requested for box:", locationName);
      // TODO: Call an async action in the store
      // e.g., useBoxStore.getState().rebootBox();
  }, [locationName]);

  const handleTestConnection = useCallback(() => {
      console.log("Test Connection requested for box:", locationName);
      // Pass necessary config for testing
      // TODO: Call an async action in the store
      // e.g., useBoxStore.getState().testBoxConnection(networkConfig);
  }, [locationName, networkConfig]); // Add networkConfig dependency

  // 添加一个状态来跟踪当前选中的选项卡
  const [activeTab, setActiveTab] = useState("network");

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>编辑盒子: {locationName || 'Loading...'}</DialogTitle>
        </DialogHeader>

        {networkConfig && dataTransmission && powerConfig ? (
          <Tabs defaultValue="network" className="w-full pt-2" onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="network">网络配置</TabsTrigger>
              <TabsTrigger value="transfer">数据传输</TabsTrigger>
              <TabsTrigger value="power">开关机配置</TabsTrigger>
            </TabsList>

            <TabsContent value="network" className="mt-4 space-y-4">
              <div className="flex items-center space-x-2">
                <Label htmlFor="ipv4-switch" className="font-semibold">IPv4</Label>
                <Switch
                  id="ipv4-switch"
                  checked={networkConfig.ipv4Enabled}
                  onCheckedChange={handleIpv4Toggle}
                  className='bg-blue-500! hover:bg-blue-600 text-white'
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="ip-address">IP地址</Label>
                <Input
                  id="ip-address"
                  placeholder="请输入IP地址"
                  value={networkConfig.ipAddress ?? ''} 
                  onChange={handleIpChange}
                  disabled={!networkConfig.ipv4Enabled}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="subnet-mask">子网掩码</Label>
                <Input
                  id="subnet-mask"
                  placeholder="请输入子网掩码"
                  value={networkConfig.subnetMask ?? ''}
                  onChange={handleSubnetChange}
                  disabled={!networkConfig.ipv4Enabled}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="gateway">网关</Label>
                <Input
                  id="gateway"
                  placeholder="请输入网关"
                  value={networkConfig.gateway ?? ''}
                  onChange={handleGatewayChange}
                  disabled={!networkConfig.ipv4Enabled}
                />
              </div>
            </TabsContent>

            <TabsContent value="transfer" className="mt-4 space-y-4">
              <div className="space-y-2">
                <Label htmlFor="upload-interval">上传周期 (秒)</Label>
                <Input
                  id="upload-interval"
                  type="number"
                  placeholder="例如：30"
                  value={dataTransmission.uploadIntervalSeconds ?? ''}
                  onChange={handleIntervalChange}
                  min="1" 
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="target-server">目标服务器</Label>
                <Input
                  id="target-server"
                  placeholder="请输入服务器地址"
                  value={dataTransmission.targetServer ?? ''}
                  onChange={handleServerChange}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="encryption-key">加密密钥</Label>
                <Input
                  id="encryption-key"
                  type="password" 
                  placeholder="请输入密钥"
                  value={dataTransmission.encryptionKey ?? ''}
                  onChange={handleKeyChange}
                />
              </div>
            </TabsContent>

             <TabsContent value="power" className="mt-4 space-y-6">
                 <h3 className="text-md font-semibold border-b pb-2">盒子状态</h3>
                 <p className="text-sm text-muted-foreground">当前状态: {powerConfig.status || '未知'}</p>

                 <h3 className="text-md font-semibold border-b pb-2">定时开关机</h3>
                 <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 items-end">
                   <div className="space-y-2">
                     <Label htmlFor="power-on-time">设置开机时间</Label>
                     <Input
                        id="power-on-time"
                        type="time"
                        placeholder="HH:MM"
                        value={powerConfig.scheduledPowerOnTimes[0] ?? ''}
                        onChange={handlePowerOnTimeChange}
                      />
                   </div>
                    <div className="space-y-2">
                     <Label htmlFor="power-off-time">设置开机时间 2</Label>
                     <Input
                        id="power-off-time" 
                        type="time"
                        placeholder="HH:MM"
                        value={powerConfig.scheduledPowerOnTimes[1] ?? ''}
                        onChange={handlePowerOffTimeChange}
                      />
                   </div>
                   <Button className='bg-blue-500 hover:bg-blue-600 text-white' onClick={handleSetTimes}>设置</Button>
                 </div>

                 <div className="flex space-x-2 pt-4">
                    <Button variant="destructive" onClick={handleShutdown}>关机</Button>
                    <Button variant="outline" onClick={handleReboot}>重启</Button>
                 </div>
              </TabsContent>
          </Tabs>
        ) : (
          <div className="pt-4 text-center">Loading configuration...</div> 
        )}

        {(activeTab === "network" || activeTab === "transfer") && (
          <DialogFooter className="pt-4">
            <DialogClose asChild>
              <Button type="button" variant="outline">取消</Button>
            </DialogClose>
            <Button 
              className='bg-blue-500 hover:bg-blue-600 text-white'
              type="button" onClick={() => {
                console.log("Save clicked. Implement save logic using store actions.");
                onOpenChange(false); 
            }}>
              保存
            </Button>
            <Button 
              className='bg-green-500 hover:bg-green-600 hover:text-white text-white'
              type="button" 
              variant="outline" 
              onClick={handleTestConnection}
            >测试连接</Button>
          </DialogFooter>
        )}
      </DialogContent>
    </Dialog>
  );
}
'use client'

import React from "react";
import Link from "next/link";
import { 
  Sidebar, 
  SidebarContent, 
  SidebarHeader, 
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton
} from "./ui/sidebar";
import Image from "next/image";
import { 
  MonitorIcon, 
  BoxIcon, 
  BarChart2Icon, 
  FileTextIcon 
} from "lucide-react";

export function AppSidebar() {
  return (
    <Sidebar>
      <SidebarHeader>
        <SidebarMenu className="flex justify-center items-center">
          <div className="flex justify-center items-center h-15">
            <Link href="/">
              <Image 
                src="/images/logo.png" 
                alt="logo"
                width={180} 
                height={100} 
              />
            </Link>
          </div>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent className="p-3">
        <SidebarMenu className="flex flex-col gap-4">
          <SidebarMenuItem>
            <SidebarMenuButton asChild>
              <Link href="/video-preview">
                <MonitorIcon />
                <span className="text-lg">视频预览</span>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
          
          <SidebarMenuItem>
            <SidebarMenuButton asChild>
              <Link href="/box-management">
                <BoxIcon />
                <span className="text-lg">盒子管理</span>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
          
          <SidebarMenuItem>
            <SidebarMenuButton asChild isActive={true}>
              <Link href="/annotation">
                <BarChart2Icon />
                <span className="text-lg">客流分析</span>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
          
          <SidebarMenuItem>
            <SidebarMenuButton asChild>
              <Link href="/log-management">
                <FileTextIcon />
                <span className="text-lg">日志管理</span>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarContent>
    </Sidebar>
  );
}

export default AppSidebar; 
import AppSidebar from "@/components/app-sidebar";
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar";
import { Breadcrumbs } from "@/components/app-header";
import { auth } from "@/app/(auth)/auth";

export default async function HomeLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const customBreadcrumbNames = {
    'annotation': "标注与分析",
    'video-preview': "视频预览",
    'log-management': "日志管理",
  };

  const session = await auth();

  return (
    <>
      <SidebarProvider defaultOpen={true}>
        <AppSidebar />
        <SidebarInset>
          <div className="flex flex-col h-full">
            <Breadcrumbs 
              user={session?.user}
              pathSegmentNames={customBreadcrumbNames} 
              containerClassName="h-12 flex items-center px-4 border-b border-gray-200"
            />
            <div className="flex-1 h-full">
              {children}
            </div>
          </div>
        </SidebarInset>
      </SidebarProvider>
    </>
  );
}

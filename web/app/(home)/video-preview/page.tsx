// "use client"

import PreviewDisplay from "@/components/video-preview/preview-display";
import PreviewSidebar from "@/components/video-preview/preview-sidebar";

// import { useEffect, useState } from "react"
// import { Card, CardContent } from "@/components/ui/card"
// import { Button } from "@/components/ui/button"
// import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
// import { ScrollArea } from "@/components/ui/scroll-area"
// import { Loader2 } from "lucide-react"
// import Image from "next/image"
// import { cn } from "@/lib/utils"
// import { toast } from "sonner"

// export default function VideoPreview() {
//   // 修改状态管理，为每个视频槽位单独管理加载状态
//   const [loadingStates, setLoadingStates] = useState<Record<string, boolean>>({})
//   const [currentView, setCurrentView] = useState<"grid" | "single">("grid")
//   const [selectedVideo, setSelectedVideo] = useState<string | null>(null)
//   const [activeVideoSlots, setActiveVideoSlots] = useState<Set<number>>(new Set())
//   // 添加缺失的retryCount状态
//   const [retryCount, setRetryCount] = useState<Record<string, number>>({})
//   const maxRetry = 5

//   const connectStream = (elementId: string) => {
//     // 设置特定视频的加载状态
//     setLoadingStates(prev => ({ ...prev, [elementId]: true }))
    
//     const video = document.getElementById(elementId) as HTMLImageElement
//     if (!video) return

//     // 使用更简单的方式处理加载和错误
//     video.onload = () => {
//       console.log('视频流加载成功:', elementId)
//       setLoadingStates(prev => ({ ...prev, [elementId]: false }))
//     }

//     video.onerror = () => {
//       // 简化错误处理，不打印错误对象
//       console.error('视频流加载错误:', elementId)
      
//       // 获取当前重试次数
//       const currentRetry = retryCount[elementId] || 0
      
//       if (currentRetry < maxRetry) {
//         // 更新重试次数
//         const newRetryCount = currentRetry + 1
//         setRetryCount(prev => ({ ...prev, [elementId]: newRetryCount }))
        
//         // 延迟重试
//         setTimeout(() => {
//           // 重新设置加载状态
//           setLoadingStates(prev => ({ ...prev, [elementId]: true }))
          
//           // 使用新的时间戳重新加载
//           const timestamp = Date.now()
//           video.src = `http://47.97.71.139:8003/video_feed1?t=${timestamp}&retry=${newRetryCount}`
//         }, 1000)
//       } else {
//         // 超过最大重试次数
//         video.src = ''
//         setLoadingStates(prev => ({ ...prev, [elementId]: false }))
//       }
//     }

//     // 设置初始源
//     const timestamp = Date.now()
//     video.src = `http://47.97.71.139:8003/video_feed1?t=${timestamp}`
//   }

//   const handleViewChange = (value: string) => {
//     setCurrentView(value as "grid" | "single")
//     // 重置所有视频的重试次数
//     setRetryCount({})
//     if (value === "single") {
//       connectStream("main-video")
//     } else {
//       Array.from({ length: 4 }).forEach((_, i) => {
//         connectStream(`grid-video-${i}`)
//       })
//     }
//   }

//   useEffect(() => {
//     // 直接调用连接函数，不需要保存返回值
//     if (currentView === "single") {
//       connectStream("main-video")
//     } else {
//       Array.from({ length: 4 }).forEach((_, i) => {
//         connectStream(`grid-video-${i}`)
//       })
//     }

//     const handleOnline = () => handleViewChange(currentView)
//     window.addEventListener('online', handleOnline)

//     return () => {
//       // 清理只需要移除事件监听器
//       window.removeEventListener('online', handleOnline)
      
//       // 可以在这里清理视频元素
//       if (currentView === "single") {
//         const video = document.getElementById("main-video") as HTMLImageElement
//         if (video) {
//           video.onloadstart = null
//           video.onerror = null
//           video.src = ''
//         }
//       } else {
//         Array.from({ length: 4 }).forEach((_, i) => {
//           const video = document.getElementById(`grid-video-${i}`) as HTMLImageElement
//           if (video) {
//             video.onloadstart = null
//             video.onerror = null
//             video.src = ''
//           }
//         })
//       }
//     }
//   }, [currentView]) // 依赖项保持不变

//   const VideoWithLoader = ({ id }: { id: string }) => (
//     <div className="relative h-full bg-black">
//       <img
//         id={id}
//         src="http://47.97.71.139:8003/video_feed1"
//         className="w-full h-full object-contain"
//         alt="视频流"
//         style={{ display: loadingStates[id] ? 'none' : 'block' }}
//       />
//       {loadingStates[id] && (
//         <div className="absolute inset-0 flex items-center justify-center">
//           <Loader2 className="w-8 h-8 animate-spin text-white" />
//           <span className="ml-2 text-white">加载中...</span>
//         </div>
//       )}
//     </div>
//   )

//   const handleVideoSelect = (videoId: string) => {
//     setSelectedVideo(videoId);
//   }

//   const handleSlotClick = (index: number) => {
//     if (!selectedVideo) {
//       toast.error('请先选择一个视频源')
//       return;
//     }

//     setActiveVideoSlots(prev => {
//       const newSlots = new Set(prev);;
//       newSlots.add(index);
//       return newSlots;
//     })
//     connectStream(`grid-video-${index}`);
//   }

//   return (
//     <div className="flex h-[calc(100vh-4rem)] p-6 gap-6">
//       <Card className="w-48 shrink-0">
//         <ScrollArea className="h-[calc(100%-4rem)]">
//           <div className="space-y-4">
//             <div className="space-y-2">
//               <div className="flex items-center gap-2 mb-4 justify-center">
//                 <Image 
//                   src="/box-icon.png"
//                   alt="Box"
//                   width={16}
//                   height={16}
//                 />
//                 <span className="font-medium">01号盒子</span>
//               </div>
//               {Array.from({ length: 4 }).map((_, i) => (
//                 <Button
//                   key={i}
//                   variant="ghost"
//                   className={cn(
//                     "w-full justify-center pr-8",
//                     selectedVideo === `video-${i}` && "bg-blue-50"
//                   )}
//                   onClick={() => handleVideoSelect(`video-${i}`)}
//                 >
//                   <Image 
//                     src="/camera-icon.png"
//                     alt="Camera"
//                     width={16}
//                     height={16}
//                     className="mr-2"
//                   />
//                   视频 {i + 1}
//                 </Button>
//               ))}
//             </div>
//           </div>
//         </ScrollArea>
//       </Card>

//       <div className="flex-1">
//         <Tabs defaultValue="grid" className="h-full" onValueChange={handleViewChange}>
//           <div className="flex items-center justify-end mb-4">
//             <div className="space-x-2">
//               <Button variant="outline">截图</Button>
//               <Button variant="outline">录制</Button>
//             </div>
//           </div>

//           <TabsContent value="single" className="h-[calc(100%-3rem)]">
//             <Card className="h-full relative">
//               <CardContent className="p-0 h-full">
//                 <VideoWithLoader id="main-video" />
//               </CardContent>
//             </Card>
//           </TabsContent>

//           <TabsContent value="grid" className="h-[calc(100%-3rem)]">
//             <Card className="h-full">
//               <CardContent className="grid grid-cols-2 gap-4 p-4 h-full">
//                 {Array.from({ length: 4 }).map((_, i) => (
//                   <div 
//                     key={i} 
//                     className={cn(
//                       "aspect-video bg-gray-100 rounded-lg overflow-hidden cursor-pointer",
//                       !activeVideoSlots.has(i) && "flex items-center justify-center"
//                     )}
//                     onClick={() => handleSlotClick(i)}
//                   >
//                     {activeVideoSlots.has(i) ? (
//                       <VideoWithLoader id={`grid-video-${i}`} />
//                     ) : (
//                       <div className="text-gray-400">点击选择视频源</div>
//                     )}
//                   </div>
//                 ))}
//               </CardContent>
//             </Card>
//           </TabsContent>
//         </Tabs>
//       </div>
//     </div>
//   )
// }
export default function Page() {
  return (
    <PreviewDisplay />
  )
}

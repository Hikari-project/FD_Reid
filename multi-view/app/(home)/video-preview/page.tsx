"use client"

import { useEffect, useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Loader2 } from "lucide-react"

export default function VideoPreview() {
  const [retryCount, setRetryCount] = useState(0)
  const [loading, setLoading] = useState(true)
  const [currentView, setCurrentView] = useState<"grid" | "single">("grid")
  const maxRetry = 5

  const connectStream = (elementId: string) => {
    setLoading(true)
    const video = document.getElementById(elementId) as HTMLImageElement
    if (!video) return

    video.src = `http://47.97.71.139:8003/video_feed2`

    const handleLoadStart = () => {
      setRetryCount(0)
      setLoading(false)
    }

    const handleError = () => {
      if (retryCount < maxRetry) {
        setRetryCount(prev => prev + 1)
        setTimeout(() => {
          setLoading(true)
          video.src += `&retry=${retryCount}`
        }, 1000 * Math.pow(2, retryCount))
      } else {
        video.src = ''
        alert('视频连接失败')
      }
    }

    video.addEventListener('loadstart', handleLoadStart)
    video.addEventListener('error', handleError)

    return () => {
      video.removeEventListener('loadstart', handleLoadStart)
      video.removeEventListener('error', handleError)
    }
  }

  const handleViewChange = (value: string) => {
    setCurrentView(value as "grid" | "single")
    setRetryCount(0) // 重置重试次数
    if (value === "single") {
      connectStream("main-video")
    } else {
      Array.from({ length: 4 }).forEach((_, i) => {
        connectStream(`grid-video-${i}`)
      })
    }
  }

  useEffect(() => {
    const cleanup = currentView === "single"
      ? connectStream("main-video")
      : Array.from({ length: 4 }).map((_, i) => connectStream(`grid-video-${i}`))

    const handleOnline = () => handleViewChange(currentView)
    window.addEventListener('online', handleOnline)

    return () => {
      if (Array.isArray(cleanup)) {
        cleanup.forEach(fn => fn?.())
      } else {
        cleanup?.()
      }
      window.removeEventListener('online', handleOnline)
    }
  }, [currentView, retryCount]) // 添加依赖项

  const VideoWithLoader = ({ id }: { id: string }) => (
    <div className="relative h-full">
      <img
        id={id}
        className="w-full h-full object-contain"
        alt="视频流"
      />
      {loading && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/10">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        </div>
      )}
    </div>
  )

  return (
    <div className="flex h-[calc(100vh-4rem)] p-6 gap-6">
      <Card className="w-48 shrink-0">
        <ScrollArea className="h-full">
          <div className="p-4 space-y-2">
            {Array.from({ length: 5 }).map((_, i) => (
              <Button
                key={i}
                variant="ghost"
                className="w-full justify-start"
              >
                01号盒子
              </Button>
            ))}
          </div>
        </ScrollArea>
      </Card>

      <div className="flex-1">
        <Tabs defaultValue="grid" className="h-full" onValueChange={handleViewChange}>
          <div className="flex items-center justify-between mb-4">
            <TabsList>
              <TabsTrigger value="grid">网格视图</TabsTrigger>
              <TabsTrigger value="single">单屏视图</TabsTrigger>
            </TabsList>
            <div className="space-x-2">
              <Button variant="outline">截图</Button>
              <Button variant="outline">录制</Button>
            </div>
          </div>

          <TabsContent value="single" className="h-[calc(100%-3rem)]">
            <Card className="h-full relative">
              <CardContent className="p-0 h-full">
                <VideoWithLoader id="main-video" />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="grid" className="h-[calc(100%-3rem)]">
            <Card className="h-full">
              <CardContent className="grid grid-cols-2 gap-4 p-4 h-full">
                {Array.from({ length: 4 }).map((_, i) => (
                  <div key={i} className="aspect-video bg-gray-100 rounded-lg overflow-hidden">
                    <VideoWithLoader id={`grid-video-${i}`} />
                  </div>
                ))}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

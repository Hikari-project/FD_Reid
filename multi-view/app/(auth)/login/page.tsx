'use client'

import { useState } from 'react'
import Image from 'next/image'
import { 
  Tabs, 
  TabsList, 
  TabsTrigger, 
  TabsContent 
} from '@/components/ui/tabs'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { PhoneIcon, LockIcon, EyeIcon, EyeOffIcon } from 'lucide-react'

export default function Page() {
  const [showPassword, setShowPassword] = useState(false)
  const [phoneNumber, setPhoneNumber] = useState('')
  const [password, setPassword] = useState('')
  const [verificationCode, setVerificationCode] = useState('')
  const [activeTab, setActiveTab] = useState('password')

  const toggleShowPassword = () => {
    setShowPassword(!showPassword)
  }

  const handleGetVerificationCode = () => {
    // Implement verification code logic here
    console.log('Getting verification code for', phoneNumber)
  }

  const handleLogin = () => {
    // Implement login logic here
    console.log('Logging in with', activeTab, { phoneNumber, password, verificationCode })
  }

  return (
    <div className="relative flex items-center justify-center min-h-screen w-full overflow-hidden">
      {/* Background Image */}
      <Image 
        src="/images/login-background.png" 
        alt="Background" 
        fill 
        className="object-cover z-0"
        priority
      />
      
      {/* Login Container */}
      <div className="relative z-10 flex w-full max-w-4xl h-[480px] mx-auto bg-white rounded-lg shadow-lg overflow-hidden">
        {/* Left Section with Camera Image */}
        <div className="w-1/2 bg-[url('/images/camera.png')] bg-cover bg-center text-white p-8">
          <h1 className="text-3xl font-bold mb-2">welcome!</h1>
          <p className="text-xl mb-8">欢迎来视频监控平台</p>  
        </div>

        {/* Right Section with Login Form */}
        <div className="w-1/2 p-8 flex flex-col justify-center">
          <Tabs defaultValue="password" className="w-full" onValueChange={(value) => setActiveTab(value)}>
            <TabsList className="w-full flex mb-8 bg-transparent">
              <TabsTrigger 
                value="password" 
                className="flex-1 py-2 text-lg font-medium border-0 rounded-none data-[state=active]:text-blue-500 data-[state=active]:border-b-2 data-[state=active]:border-blue-500"
              >
                密码登录
              </TabsTrigger>
            </TabsList>

            {/* Password Login Tab */}
            <TabsContent value="password" className="space-y-6">
              <div className="relative">
                <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">
                  <PhoneIcon size={18} />
                </div>
                <Input
                  type="text"
                  placeholder="账号/邮箱/手机号"
                  value={phoneNumber}
                  onChange={(e) => setPhoneNumber(e.target.value)}
                  className="pl-10 h-12 w-full"
                />
              </div>
              
              <div className="relative">
                <div className="absolute left-3 top-1/2 -translate-y-5.5 text-gray-500">
                  <LockIcon size={18} />
                </div>
                <Input
                  type={showPassword ? "text" : "password"}
                  placeholder="请输入登录密码"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="pl-10 h-12 w-full pr-10"
                />
                <button 
                  type="button"
                  onClick={toggleShowPassword}
                  className="absolute right-3 top-1/2 -translate-y-5.5 text-gray-500"
                >
                  {showPassword ? <EyeOffIcon size={18} /> : <EyeIcon size={18} />}
                </button>
                <div className="flex justify-end mt-2">
                  <a href="#" className="text-gray-500 text-sm">忘记密码</a>
                </div>
              </div>
            </TabsContent>

            <Button 
              onClick={handleLogin}
              className="w-full h-12 mt-8 bg-blue-500 hover:bg-blue-600 text-lg font-medium"
            >
              登录
            </Button>
          </Tabs>
        </div>
      </div>
    </div>
  )
}

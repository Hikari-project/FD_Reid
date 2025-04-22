'use client'

import { useEffect, useState } from 'react'
import Image from 'next/image'
import { login, loginState } from '../action'
import { Form, FormControl, FormField, FormItem, FormLabel } from '@/components/ui/form'
import { useForm } from 'react-hook-form'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Eye, EyeOff, LockKeyhole, Smartphone } from 'lucide-react'

export default function Page() {
  const [loginState, setLoginState] = useState<loginState>({ status: "idle" });
  const [showPassword, setShowPassword] = useState(false);
  const router = useRouter();

  const form = useForm({
    defaultValues: {
      username: "",
      password: "",
    },
  });

  const onSubmit = async (values: any) => {
    setLoginState({ status: "loading" });
    console.log(values);
    try {
      const formData = new FormData();
      formData.append("username", values.username);
      formData.append("password", values.password);
      console.log(formData);
      const state = await login(formData);

      setLoginState(state);
    } catch (error) {
      setLoginState({ status: "error", message: error as string });
    }
  }

  useEffect(() => {
    if (loginState.status === "success") {
      toast.success(loginState.message);
      router.push("/video-preview");
    } else if (loginState.status === "error") {
      toast.error(loginState.message);
    }
  }, [loginState, router]);

  return (
    <div className="relative flex items-center justify-center min-h-screen w-full overflow-hidden">
      <Image 
        src="/images/login-background.png" 
        alt="Background" 
        fill 
        className="object-cover z-0"
        priority
      />
      
      <div className="relative z-10 flex w-full max-w-4xl h-[480px] mx-auto bg-white rounded-lg shadow-lg overflow-hidden">
        <div className="w-1/2 bg-blue-500 bg-[url('/images/camera.png')] bg-cover bg-center text-white p-8">
          <h1 className="text-3xl font-bold mb-2">welcome!</h1>
          <p className="text-xl mb-8">欢迎来视频监控平台</p>
        </div>

        <div className="w-1/2 p-8 flex flex-col justify-center">
          <div className="text-2xl font-bold mb-6 text-blue-600 pb-2">
            <span className="border-b-2 border-blue-600">密码登录</span>
          </div>
          
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              <FormField
                control={form.control}
                name="username"
                render={({ field }) => (
                  <FormItem className='relative'>
                    <FormControl>
                      <Input 
                        {...field} 
                        placeholder="请输入账号" 
                        className="h-12 pl-8"
                        type="text"
                      />
                    </FormControl>
                    <Smartphone className='size-5 absolute left-2 top-1/2 -translate-y-1/2 text-gray-400' />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="password"
                render={({ field }) => (
                  <FormItem className='relative'>
                    <FormControl>
                      <Input 
                        {...field} 
                        placeholder="请输入登录密码" 
                        className="h-12 pl-8"
                        type={showPassword ? "text" : "password"}
                      />
                    </FormControl>
                    <LockKeyhole className='size-5 absolute left-2 top-1/2 -translate-y-1/2 text-gray-400' />
                    <Button 
                      type="button"
                      variant="ghost"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-2 top-1/2 -translate-y-1/2 h-8 w-8 p-0"
                    >
                      {showPassword ? (
                        <Eye className="size-5 text-gray-400" />
                      ) : (
                        <EyeOff className="size-5 text-gray-400" />
                      )}
                      <span className="sr-only">
                        {showPassword ? "隐藏密码" : "显示密码"}
                      </span>
                    </Button>
                  </FormItem>
                )}
              />
              <div className='h-3'></div>
              <Button 
                type="submit" 
                className="w-full h-12 bg-blue-500 hover:bg-blue-600 text-white text-lg"
                disabled={loginState.status === "loading"}
              >
                登录
              </Button>
            </form>
          </Form>
        </div>
      </div>
    </div>
  )
}

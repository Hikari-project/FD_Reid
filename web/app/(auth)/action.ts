'use server'

import { signIn } from "@/app/(auth)/auth"
import { z } from "zod";

const usernameSchema = z
  .string()
  .min(2, { message: "用户名至少两个字符" })
  .max(20, { message: "用户名最多20个字符" })

const passwordSchema = z
  .string()
  .min(6, { message: "密码至少6个字符" })
  .max(20, { message: "密码最多20个字符" });

export interface loginState {
  status: "success" | "error" | "loading" | "idle";
  message?: string;
}

export async function login(formData: FormData): Promise<loginState> {
  try {
    const username = formData.get("username") as string;
    const password = formData.get("password") as string;

    const parsedCredentials = z.object({ 
      username: usernameSchema, 
      password: passwordSchema
    }).parse({ username, password });

    await signIn("credentials", {
      password: parsedCredentials.password,
      username: parsedCredentials.username,
      redirect: false,
    })

    return { status: "success", message: "登录成功" };
  } catch (error) {
    console.error(error);
    return { status: "error", message: "登录失败" };
  }
}

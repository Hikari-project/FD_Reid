export { auth as middleware } from "@/app/(auth)/auth"

export const config = {
  matcher: [
    '/',
    '/login',
    '/annotation',
    '/video-preview',
    '/log-management',
  ],
}



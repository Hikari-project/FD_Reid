import NextAuth from "next-auth";
import Credentials from "next-auth/providers/credentials";

export const {
  handlers: { GET, POST },
  auth,
  signIn,
  signOut,
} = NextAuth({
  secret: process.env.AUTH_SECRET,
  pages: {
    signIn: "/login",
  },
  providers: [
    Credentials({
      credentials: {
        username: { label: "Username", type: "text" },
        password: { label: "Password", type: "password" },
      },
      async authorize({ username, password }) {
        if (username === "admin" && password === "admin@123456") {
          return { id: "1", name: "admin" };
        }

        return null;
      },
    })
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id;
      }
      return token;
    },
    async session({ session, token }) {
      if (session.user) {
        session.user.id = token.id as string;
      }
      return session;
    },
    authorized({ auth, request: { nextUrl } }) {
      const isLoggedIn = !!auth?.user;
      const isOnHome = nextUrl.pathname === "/";
      const isOnLogin = nextUrl.pathname.startsWith("/login");
      const isOnAnnotation = nextUrl.pathname.startsWith("/annotation");
      const isOnVideoPreview = nextUrl.pathname.startsWith("/video-preview");
      const isOnLogManagement = nextUrl.pathname.startsWith("/log-management");

      if (isOnHome) {
        if (isLoggedIn) {
          return Response.redirect(new URL("/video-preview", nextUrl));
        } else {
          return Response.redirect(new URL("/login", nextUrl));
        }
      }

      if (isLoggedIn && isOnLogin) {
        return Response.redirect(new URL("/video-preview", nextUrl));
      }

      if (!isLoggedIn && (isOnAnnotation || isOnVideoPreview || isOnLogManagement)) {
        return Response.redirect(new URL("/login", nextUrl));
      }

      return true;
    },
  },
  trustHost: true,
});


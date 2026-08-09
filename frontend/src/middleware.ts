import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('access_token')?.value;

  if (!token) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    '/chat/:path*',
    '/documents/:path*',
    '/agents/:path*',
    '/analytics/:path*',
    '/evaluation/:path*',
    '/history/:path*',
    '/settings/:path*',
    '/admin/:path*'
  ],
};

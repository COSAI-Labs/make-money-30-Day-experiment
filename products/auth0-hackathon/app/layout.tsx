import type { Metadata } from 'next'
import { UserProvider } from '@auth0/nextjs-auth0/client'

export const metadata: Metadata = {
  title: 'DevAgent - AI Developer Assistant',
  description: 'AI-powered developer assistant with secure tool access via Auth0 Token Vault',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{ margin: 0, fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif' }}>
        <UserProvider>
          {children}
        </UserProvider>
      </body>
    </html>
  )
}

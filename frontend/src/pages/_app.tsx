import '@/index.css'  // Changed from '@/styles/globals.css'
import '@/index.css'
import type { AppProps } from 'next/app'
import { Toaster } from "@/components/ui/toaster"

export default function App({ Component, pageProps }: AppProps) {
  return (
    <>
      <Component {...pageProps} />
      <Toaster />
    </>
  )
}

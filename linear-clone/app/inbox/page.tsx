'use client'

import { Header } from '@/components/header'
import { Inbox } from 'lucide-react'

export default function InboxPage() {
  return (
    <>
      <Header />
      <main className="flex-1 overflow-auto">
        <div className="flex flex-col items-center justify-center h-full text-gray-500">
          <Inbox className="h-12 w-12 mb-4 text-gray-300" />
          <h2 className="text-lg font-medium mb-2">Your inbox is empty</h2>
          <p className="text-sm text-gray-400 max-w-md text-center">
            Issues assigned to you or mentioning you will appear here
          </p>
        </div>
      </main>
    </>
  )
}
'use client'

import { useMemo } from 'react'
import { Header } from '@/components/header'
import { IssueList } from '@/components/issue-list'
import { IssueBoard } from '@/components/issue-board'
import { useStore } from '@/lib/store'

export default function MyIssuesPage() {
  const { 
    issues, 
    currentView, 
    searchQuery, 
    statusFilter, 
    priorityFilter,
    currentProjectId 
  } = useStore()

  const filteredIssues = useMemo(() => {
    let filtered = issues

    // Filter by project
    if (currentProjectId) {
      filtered = filtered.filter(issue => issue.projectId === currentProjectId)
    }

    // Filter by search query
    if (searchQuery) {
      filtered = filtered.filter(issue => 
        issue.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        issue.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        issue.id.toLowerCase().includes(searchQuery.toLowerCase())
      )
    }

    // Filter by status
    if (statusFilter !== 'all') {
      filtered = filtered.filter(issue => issue.status === statusFilter)
    }

    // Filter by priority
    if (priorityFilter !== 'all') {
      filtered = filtered.filter(issue => issue.priority === priorityFilter)
    }

    return filtered
  }, [issues, currentProjectId, searchQuery, statusFilter, priorityFilter])

  return (
    <>
      <Header />
      <main className="flex-1 overflow-auto">
        {currentView === 'list' && (
          <IssueList issues={filteredIssues} />
        )}
        {currentView === 'board' && (
          <IssueBoard issues={filteredIssues} />
        )}
        {currentView === 'calendar' && (
          <div className="flex items-center justify-center h-full text-gray-500">
            <div className="text-center">
              <p className="text-lg font-medium mb-2">Calendar View</p>
              <p className="text-sm">Coming soon...</p>
            </div>
          </div>
        )}
      </main>
    </>
  )
}
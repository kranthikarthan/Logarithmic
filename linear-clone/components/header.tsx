'use client'

import { 
  Search, 
  Plus, 
  Filter, 
  LayoutGrid, 
  List, 
  Calendar,
  ChevronDown,
  SlidersHorizontal
} from 'lucide-react'
import { useStore, ViewType } from '@/lib/store'
import { cn } from '@/lib/utils'
import * as DropdownMenu from '@radix-ui/react-dropdown-menu'
import * as Popover from '@radix-ui/react-popover'
import { useState } from 'react'

export function Header() {
  const { 
    currentView, 
    setCurrentView, 
    searchQuery, 
    setSearchQuery,
    statusFilter,
    setStatusFilter,
    priorityFilter,
    setPriorityFilter,
    projects,
    currentProjectId
  } = useStore()
  
  const [filterOpen, setFilterOpen] = useState(false)
  const currentProject = projects.find(p => p.id === currentProjectId)

  const views: { type: ViewType; icon: any; label: string }[] = [
    { type: 'list', icon: List, label: 'List' },
    { type: 'board', icon: LayoutGrid, label: 'Board' },
    { type: 'calendar', icon: Calendar, label: 'Calendar' },
  ]

  const statuses = [
    { value: 'all', label: 'All Statuses' },
    { value: 'backlog', label: 'Backlog' },
    { value: 'todo', label: 'To Do' },
    { value: 'in-progress', label: 'In Progress' },
    { value: 'done', label: 'Done' },
    { value: 'cancelled', label: 'Cancelled' },
  ]

  const priorities = [
    { value: 'all', label: 'All Priorities' },
    { value: 'urgent', label: 'Urgent' },
    { value: 'high', label: 'High' },
    { value: 'medium', label: 'Medium' },
    { value: 'low', label: 'Low' },
    { value: 'none', label: 'No Priority' },
  ]

  return (
    <header className="sticky top-0 z-40 bg-white border-b border-gray-200">
      <div className="flex items-center justify-between px-6 py-3">
        <div className="flex items-center gap-4 flex-1">
          {/* Project Name */}
          <div className="flex items-center gap-2">
            {currentProject && (
              <>
                <span className="text-xl">{currentProject.icon}</span>
                <h1 className="text-lg font-semibold text-gray-900">
                  {currentProject.name}
                </h1>
              </>
            )}
          </div>

          {/* Search Bar */}
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search issues..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 text-sm bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Filter Button */}
          <Popover.Root open={filterOpen} onOpenChange={setFilterOpen}>
            <Popover.Trigger asChild>
              <button className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                <Filter className="h-4 w-4" />
                Filter
                {(statusFilter !== 'all' || priorityFilter !== 'all') && (
                  <span className="px-1.5 py-0.5 text-xs bg-blue-100 text-blue-700 rounded-full">
                    {[statusFilter !== 'all' && statusFilter, priorityFilter !== 'all' && priorityFilter].filter(Boolean).length}
                  </span>
                )}
              </button>
            </Popover.Trigger>
            <Popover.Portal>
              <Popover.Content className="z-50 w-80 bg-white rounded-lg shadow-lg border border-gray-200 p-4">
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium text-gray-700 mb-2 block">
                      Status
                    </label>
                    <select
                      value={statusFilter}
                      onChange={(e) => setStatusFilter(e.target.value as any)}
                      className="w-full px-3 py-2 text-sm bg-white border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      {statuses.map(status => (
                        <option key={status.value} value={status.value}>
                          {status.label}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700 mb-2 block">
                      Priority
                    </label>
                    <select
                      value={priorityFilter}
                      onChange={(e) => setPriorityFilter(e.target.value as any)}
                      className="w-full px-3 py-2 text-sm bg-white border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      {priorities.map(priority => (
                        <option key={priority.value} value={priority.value}>
                          {priority.label}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="flex justify-end gap-2 pt-2">
                    <button
                      onClick={() => {
                        setStatusFilter('all')
                        setPriorityFilter('all')
                      }}
                      className="px-3 py-1.5 text-sm text-gray-600 hover:text-gray-900"
                    >
                      Clear filters
                    </button>
                    <button
                      onClick={() => setFilterOpen(false)}
                      className="px-3 py-1.5 text-sm font-medium text-white bg-gray-900 rounded-lg hover:bg-gray-800"
                    >
                      Apply
                    </button>
                  </div>
                </div>
                <Popover.Arrow className="fill-gray-200" />
              </Popover.Content>
            </Popover.Portal>
          </Popover.Root>

          {/* View Switcher */}
          <div className="flex items-center bg-gray-100 rounded-lg p-1">
            {views.map((view) => (
              <button
                key={view.type}
                onClick={() => setCurrentView(view.type)}
                className={cn(
                  'p-2 rounded-md transition-colors',
                  currentView === view.type
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                )}
                title={view.label}
              >
                <view.icon className="h-4 w-4" />
              </button>
            ))}
          </div>

          {/* New Issue Button */}
          <button className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-gray-900 rounded-lg hover:bg-gray-800 transition-colors">
            <Plus className="h-4 w-4" />
            New Issue
          </button>
        </div>
      </div>
    </header>
  )
}
'use client'

import { useState } from 'react'
import {
  DndContext,
  DragEndEvent,
  DragOverlay,
  DragStartEvent,
  closestCorners,
  PointerSensor,
  useSensor,
  useSensors,
} from '@dnd-kit/core'
import {
  SortableContext,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable'
import { Issue, Status, useStore } from '@/lib/store'
import { cn } from '@/lib/utils'
import { 
  Circle, 
  CircleDot,
  CircleCheck,
  CircleX,
  Plus,
  MoreHorizontal,
  AlertCircle
} from 'lucide-react'
import { IssueCard } from './issue-card'

const columns: { status: Status; label: string; icon: any; color: string }[] = [
  { status: 'backlog', label: 'Backlog', icon: Circle, color: 'text-gray-400' },
  { status: 'todo', label: 'To Do', icon: CircleDot, color: 'text-gray-600' },
  { status: 'in-progress', label: 'In Progress', icon: CircleDot, color: 'text-blue-500' },
  { status: 'done', label: 'Done', icon: CircleCheck, color: 'text-green-500' },
  { status: 'cancelled', label: 'Cancelled', icon: CircleX, color: 'text-gray-400' },
]

interface IssueBoardProps {
  issues: Issue[]
}

export function IssueBoard({ issues }: IssueBoardProps) {
  const { updateIssue } = useStore()
  const [activeId, setActiveId] = useState<string | null>(null)

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    })
  )

  const handleDragStart = (event: DragStartEvent) => {
    setActiveId(event.active.id as string)
  }

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event

    if (!over) {
      setActiveId(null)
      return
    }

    const activeIssue = issues.find(i => i.id === active.id)
    const overStatus = over.id as Status

    if (activeIssue && activeIssue.status !== overStatus) {
      updateIssue(activeIssue.id, { status: overStatus })
    }

    setActiveId(null)
  }

  const activeIssue = activeId ? issues.find(i => i.id === activeId) : null

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCorners}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
    >
      <div className="flex gap-4 p-6 h-full overflow-x-auto">
        {columns.map((column) => {
          const columnIssues = issues.filter(issue => issue.status === column.status)
          const Icon = column.icon

          return (
            <div
              key={column.status}
              className="flex-shrink-0 w-80"
            >
              <div className="mb-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Icon className={cn("h-4 w-4", column.color)} />
                    <h3 className="text-sm font-medium text-gray-900">
                      {column.label}
                    </h3>
                    <span className="text-sm text-gray-500">
                      {columnIssues.length}
                    </span>
                  </div>
                  <div className="flex items-center gap-1">
                    <button className="p-1 hover:bg-gray-100 rounded">
                      <Plus className="h-4 w-4 text-gray-400" />
                    </button>
                    <button className="p-1 hover:bg-gray-100 rounded">
                      <MoreHorizontal className="h-4 w-4 text-gray-400" />
                    </button>
                  </div>
                </div>
              </div>

              <SortableContext
                id={column.status}
                items={columnIssues.map(i => i.id)}
                strategy={verticalListSortingStrategy}
              >
                <div className="space-y-2 min-h-[200px]">
                  {columnIssues.map((issue) => (
                    <IssueCard key={issue.id} issue={issue} />
                  ))}
                </div>
              </SortableContext>
            </div>
          )
        })}
      </div>

      <DragOverlay>
        {activeIssue ? (
          <div className="opacity-50">
            <IssueCard issue={activeIssue} />
          </div>
        ) : null}
      </DragOverlay>
    </DndContext>
  )
}
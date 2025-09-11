'use client'

import { useSortable } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { Issue, useStore } from '@/lib/store'
import { cn, formatDate } from '@/lib/utils'
import { 
  MoreHorizontal,
  AlertCircle,
  Calendar,
  User,
  Zap,
  MessageSquare
} from 'lucide-react'
import * as DropdownMenu from '@radix-ui/react-dropdown-menu'

const priorityColors = {
  'none': '',
  'low': 'border-l-gray-400',
  'medium': 'border-l-yellow-500',
  'high': 'border-l-orange-500',
  'urgent': 'border-l-red-500',
}

interface IssueCardProps {
  issue: Issue
}

export function IssueCard({ issue }: IssueCardProps) {
  const { labels, deleteIssue } = useStore()
  const issueLabels = issue.labels.map(id => labels.find(l => l.id === id)).filter(Boolean)

  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: issue.id })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  }

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
      className={cn(
        "bg-white rounded-lg border border-gray-200 p-3 cursor-move hover:shadow-md transition-shadow",
        priorityColors[issue.priority],
        issue.priority !== 'none' && 'border-l-4',
        isDragging && 'opacity-50'
      )}
    >
      <div className="flex items-start justify-between mb-2">
        <span className="text-xs font-medium text-gray-500">{issue.id}</span>
        <DropdownMenu.Root>
          <DropdownMenu.Trigger asChild>
            <button 
              className="p-1 -mr-1 opacity-0 hover:opacity-100 hover:bg-gray-100 rounded transition-opacity"
              onClick={(e) => e.stopPropagation()}
            >
              <MoreHorizontal className="h-3 w-3 text-gray-400" />
            </button>
          </DropdownMenu.Trigger>
          <DropdownMenu.Portal>
            <DropdownMenu.Content className="z-50 min-w-[160px] bg-white rounded-lg shadow-lg border border-gray-200 p-1">
              <DropdownMenu.Item className="px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md cursor-pointer">
                Edit issue
              </DropdownMenu.Item>
              <DropdownMenu.Item className="px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md cursor-pointer">
                Copy link
              </DropdownMenu.Item>
              <DropdownMenu.Separator className="my-1 h-px bg-gray-200" />
              <DropdownMenu.Item 
                onClick={() => deleteIssue(issue.id)}
                className="px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded-md cursor-pointer"
              >
                Delete issue
              </DropdownMenu.Item>
            </DropdownMenu.Content>
          </DropdownMenu.Portal>
        </DropdownMenu.Root>
      </div>

      <h4 className="text-sm font-medium text-gray-900 mb-2 line-clamp-2">
        {issue.title}
      </h4>

      {issueLabels.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-2">
          {issueLabels.map((label) => label && (
            <span
              key={label.id}
              className="inline-flex items-center px-1.5 py-0.5 text-xs font-medium rounded"
              style={{
                backgroundColor: `${label.color}20`,
                color: label.color,
              }}
            >
              {label.name}
            </span>
          ))}
        </div>
      )}

      <div className="flex items-center gap-3 text-xs text-gray-500">
        {issue.priority === 'urgent' && (
          <div className="flex items-center gap-1 text-red-500">
            <AlertCircle className="h-3 w-3" />
            <span>Urgent</span>
          </div>
        )}
        
        {issue.estimate && (
          <div className="flex items-center gap-1">
            <Zap className="h-3 w-3" />
            <span>{issue.estimate}</span>
          </div>
        )}

        {issue.dueDate && (
          <div className="flex items-center gap-1">
            <Calendar className="h-3 w-3" />
            <span>{formatDate(issue.dueDate)}</span>
          </div>
        )}

        {issue.assignee && (
          <div className="flex items-center gap-1">
            <div className="w-5 h-5 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-xs font-medium">
              {issue.assignee.split(' ').map(n => n[0]).join('')}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
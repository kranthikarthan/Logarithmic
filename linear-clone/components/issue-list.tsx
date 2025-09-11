'use client'

import { useState } from 'react'
import { 
  MoreHorizontal, 
  Circle, 
  CircleDot,
  CircleCheck,
  CircleX,
  AlertCircle,
  ChevronRight,
  Hash,
  User,
  Calendar,
  Tag,
  Zap
} from 'lucide-react'
import { Issue, Priority, Status, useStore } from '@/lib/store'
import { cn, formatDate } from '@/lib/utils'
import * as DropdownMenu from '@radix-ui/react-dropdown-menu'
import * as Tooltip from '@radix-ui/react-tooltip'

const statusIcons = {
  'backlog': Circle,
  'todo': CircleDot,
  'in-progress': CircleDot,
  'done': CircleCheck,
  'cancelled': CircleX,
}

const statusColors = {
  'backlog': 'text-gray-400',
  'todo': 'text-gray-600',
  'in-progress': 'text-blue-500',
  'done': 'text-green-500',
  'cancelled': 'text-gray-400',
}

const priorityIcons = {
  'none': null,
  'low': () => <div className="w-4 h-4 flex items-center justify-center"><div className="w-2 h-2 bg-gray-400 rounded-full" /></div>,
  'medium': () => <div className="w-4 h-4 flex items-center justify-center"><div className="w-2.5 h-2.5 bg-yellow-500 rounded-full" /></div>,
  'high': () => <div className="w-4 h-4 flex items-center justify-center"><div className="w-3 h-3 bg-orange-500 rounded-full" /></div>,
  'urgent': () => <AlertCircle className="w-4 h-4 text-red-500" />,
}

interface IssueListProps {
  issues: Issue[]
}

export function IssueList({ issues }: IssueListProps) {
  const { updateIssue, deleteIssue, labels } = useStore()
  const [expandedIssue, setExpandedIssue] = useState<string | null>(null)

  const handleStatusChange = (issueId: string, status: Status) => {
    updateIssue(issueId, { status })
  }

  const handlePriorityChange = (issueId: string, priority: Priority) => {
    updateIssue(issueId, { priority })
  }

  return (
    <Tooltip.Provider>
      <div className="divide-y divide-gray-100">
        {issues.map((issue) => {
          const StatusIcon = statusIcons[issue.status]
          const PriorityIcon = priorityIcons[issue.priority]
          const isExpanded = expandedIssue === issue.id
          const issueLabels = issue.labels.map(id => labels.find(l => l.id === id)).filter(Boolean)

          return (
            <div key={issue.id} className="group hover:bg-gray-50 transition-colors">
              <div className="px-6 py-3">
                <div className="flex items-center gap-3">
                  {/* Expand Arrow */}
                  <button
                    onClick={() => setExpandedIssue(isExpanded ? null : issue.id)}
                    className="p-0.5 opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <ChevronRight 
                      className={cn(
                        "h-3 w-3 text-gray-400 transition-transform",
                        isExpanded && "rotate-90"
                      )}
                    />
                  </button>

                  {/* Status */}
                  <DropdownMenu.Root>
                    <DropdownMenu.Trigger asChild>
                      <button className="p-1 rounded hover:bg-gray-100">
                        <StatusIcon className={cn("h-4 w-4", statusColors[issue.status])} />
                      </button>
                    </DropdownMenu.Trigger>
                    <DropdownMenu.Portal>
                      <DropdownMenu.Content className="z-50 min-w-[160px] bg-white rounded-lg shadow-lg border border-gray-200 p-1">
                        {Object.entries(statusIcons).map(([status, Icon]) => (
                          <DropdownMenu.Item
                            key={status}
                            onClick={() => handleStatusChange(issue.id, status as Status)}
                            className="flex items-center gap-2 px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md cursor-pointer"
                          >
                            <Icon className={cn("h-4 w-4", statusColors[status as Status])} />
                            <span className="capitalize">{status.replace('-', ' ')}</span>
                          </DropdownMenu.Item>
                        ))}
                      </DropdownMenu.Content>
                    </DropdownMenu.Portal>
                  </DropdownMenu.Root>

                  {/* Priority */}
                  <DropdownMenu.Root>
                    <DropdownMenu.Trigger asChild>
                      <button className="p-1 rounded hover:bg-gray-100">
                        {PriorityIcon ? <PriorityIcon /> : <div className="w-4 h-4" />}
                      </button>
                    </DropdownMenu.Trigger>
                    <DropdownMenu.Portal>
                      <DropdownMenu.Content className="z-50 min-w-[160px] bg-white rounded-lg shadow-lg border border-gray-200 p-1">
                        {Object.entries(priorityIcons).map(([priority, Icon]) => (
                          <DropdownMenu.Item
                            key={priority}
                            onClick={() => handlePriorityChange(issue.id, priority as Priority)}
                            className="flex items-center gap-2 px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md cursor-pointer"
                          >
                            {Icon ? <Icon /> : <div className="w-4 h-4" />}
                            <span className="capitalize">{priority === 'none' ? 'No priority' : priority}</span>
                          </DropdownMenu.Item>
                        ))}
                      </DropdownMenu.Content>
                    </DropdownMenu.Portal>
                  </DropdownMenu.Root>

                  {/* Issue ID */}
                  <span className="text-sm font-medium text-gray-500">{issue.id}</span>

                  {/* Title */}
                  <span className="flex-1 text-sm font-medium text-gray-900">
                    {issue.title}
                  </span>

                  {/* Labels */}
                  {issueLabels.length > 0 && (
                    <div className="flex items-center gap-1">
                      {issueLabels.map((label) => label && (
                        <Tooltip.Root key={label.id}>
                          <Tooltip.Trigger asChild>
                            <span
                              className="inline-flex items-center px-2 py-0.5 text-xs font-medium rounded-full"
                              style={{
                                backgroundColor: `${label.color}20`,
                                color: label.color,
                              }}
                            >
                              {label.name}
                            </span>
                          </Tooltip.Trigger>
                          <Tooltip.Portal>
                            <Tooltip.Content className="z-50 px-2 py-1 text-xs text-white bg-gray-900 rounded">
                              {label.name}
                              <Tooltip.Arrow className="fill-gray-900" />
                            </Tooltip.Content>
                          </Tooltip.Portal>
                        </Tooltip.Root>
                      ))}
                    </div>
                  )}

                  {/* Estimate */}
                  {issue.estimate && (
                    <Tooltip.Root>
                      <Tooltip.Trigger asChild>
                        <div className="flex items-center gap-1 text-xs text-gray-500">
                          <Zap className="h-3 w-3" />
                          {issue.estimate}
                        </div>
                      </Tooltip.Trigger>
                      <Tooltip.Portal>
                        <Tooltip.Content className="z-50 px-2 py-1 text-xs text-white bg-gray-900 rounded">
                          {issue.estimate} story points
                          <Tooltip.Arrow className="fill-gray-900" />
                        </Tooltip.Content>
                      </Tooltip.Portal>
                    </Tooltip.Root>
                  )}

                  {/* Due Date */}
                  {issue.dueDate && (
                    <Tooltip.Root>
                      <Tooltip.Trigger asChild>
                        <div className="flex items-center gap-1 text-xs text-gray-500">
                          <Calendar className="h-3 w-3" />
                          {formatDate(issue.dueDate)}
                        </div>
                      </Tooltip.Trigger>
                      <Tooltip.Portal>
                        <Tooltip.Content className="z-50 px-2 py-1 text-xs text-white bg-gray-900 rounded">
                          Due {formatDate(issue.dueDate)}
                          <Tooltip.Arrow className="fill-gray-900" />
                        </Tooltip.Content>
                      </Tooltip.Portal>
                    </Tooltip.Root>
                  )}

                  {/* Assignee */}
                  {issue.assignee && (
                    <Tooltip.Root>
                      <Tooltip.Trigger asChild>
                        <div className="flex items-center gap-1 text-xs text-gray-500">
                          <User className="h-3 w-3" />
                          {issue.assignee}
                        </div>
                      </Tooltip.Trigger>
                      <Tooltip.Portal>
                        <Tooltip.Content className="z-50 px-2 py-1 text-xs text-white bg-gray-900 rounded">
                          Assigned to {issue.assignee}
                          <Tooltip.Arrow className="fill-gray-900" />
                        </Tooltip.Content>
                      </Tooltip.Portal>
                    </Tooltip.Root>
                  )}

                  {/* Actions */}
                  <DropdownMenu.Root>
                    <DropdownMenu.Trigger asChild>
                      <button className="p-1 opacity-0 group-hover:opacity-100 rounded hover:bg-gray-100 transition-opacity">
                        <MoreHorizontal className="h-4 w-4 text-gray-400" />
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
                        <DropdownMenu.Item className="px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md cursor-pointer">
                          Duplicate
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

                {/* Expanded Content */}
                {isExpanded && issue.description && (
                  <div className="mt-3 ml-11 text-sm text-gray-600">
                    {issue.description}
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </Tooltip.Provider>
  )
}
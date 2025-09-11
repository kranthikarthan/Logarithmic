'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { 
  Home, 
  CircleDot, 
  Users, 
  FolderOpen, 
  Settings, 
  Search,
  Plus,
  ChevronDown,
  ChevronRight,
  Inbox,
  Calendar,
  BarChart3,
  Archive,
  Hash,
  User,
  LogOut,
  HelpCircle,
  Zap
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useStore } from '@/lib/store'
import * as DropdownMenu from '@radix-ui/react-dropdown-menu'
import * as Avatar from '@radix-ui/react-avatar'

export function Sidebar() {
  const pathname = usePathname()
  const [projectsExpanded, setProjectsExpanded] = useState(true)
  const { projects, currentProjectId, setCurrentProject, currentUser } = useStore()

  const navigation = [
    { name: 'Inbox', href: '/inbox', icon: Inbox },
    { name: 'My Issues', href: '/my-issues', icon: CircleDot },
    { name: 'Views', href: '/views', icon: BarChart3 },
  ]

  const bottomNavigation = [
    { name: 'Archive', href: '/archive', icon: Archive },
    { name: 'Settings', href: '/settings', icon: Settings },
  ]

  return (
    <div className="flex h-full w-64 flex-col bg-gray-50 border-r border-gray-200">
      {/* User Menu */}
      <div className="p-4 border-b border-gray-200">
        <DropdownMenu.Root>
          <DropdownMenu.Trigger asChild>
            <button className="flex items-center gap-3 w-full p-2 rounded-lg hover:bg-gray-100 transition-colors">
              <Avatar.Root className="h-8 w-8 rounded-full overflow-hidden bg-gradient-to-br from-blue-500 to-purple-600">
                <Avatar.Image src={currentUser.avatar} alt={currentUser.name} />
                <Avatar.Fallback className="flex items-center justify-center text-white text-sm font-medium">
                  {currentUser.name.split(' ').map(n => n[0]).join('')}
                </Avatar.Fallback>
              </Avatar.Root>
              <div className="flex-1 text-left">
                <p className="text-sm font-medium text-gray-900">{currentUser.name}</p>
                <p className="text-xs text-gray-500">Personal workspace</p>
              </div>
              <ChevronDown className="h-4 w-4 text-gray-400" />
            </button>
          </DropdownMenu.Trigger>
          <DropdownMenu.Portal>
            <DropdownMenu.Content className="z-50 min-w-[200px] bg-white rounded-lg shadow-lg border border-gray-200 p-1">
              <DropdownMenu.Item className="flex items-center gap-2 px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md cursor-pointer">
                <User className="h-4 w-4" />
                Profile
              </DropdownMenu.Item>
              <DropdownMenu.Item className="flex items-center gap-2 px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md cursor-pointer">
                <HelpCircle className="h-4 w-4" />
                Help & Support
              </DropdownMenu.Item>
              <DropdownMenu.Separator className="my-1 h-px bg-gray-200" />
              <DropdownMenu.Item className="flex items-center gap-2 px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md cursor-pointer">
                <LogOut className="h-4 w-4" />
                Sign out
              </DropdownMenu.Item>
            </DropdownMenu.Content>
          </DropdownMenu.Portal>
        </DropdownMenu.Root>
      </div>

      {/* Search */}
      <div className="p-4">
        <button className="flex items-center gap-2 w-full px-3 py-2 text-sm text-gray-600 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
          <Search className="h-4 w-4" />
          <span>Search</span>
          <span className="ml-auto text-xs text-gray-400">⌘K</span>
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 pb-4">
        <div className="space-y-1">
          {navigation.map((item) => {
            const isActive = pathname === item.href
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  'flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg transition-colors',
                  isActive
                    ? 'bg-gray-900 text-white'
                    : 'text-gray-700 hover:bg-gray-100'
                )}
              >
                <item.icon className="h-4 w-4" />
                {item.name}
              </Link>
            )
          })}
        </div>

        {/* Projects Section */}
        <div className="mt-8">
          <div className="flex items-center justify-between mb-2">
            <button
              onClick={() => setProjectsExpanded(!projectsExpanded)}
              className="flex items-center gap-1 text-xs font-semibold text-gray-500 uppercase tracking-wider hover:text-gray-700"
            >
              {projectsExpanded ? (
                <ChevronDown className="h-3 w-3" />
              ) : (
                <ChevronRight className="h-3 w-3" />
              )}
              Projects
            </button>
            <button className="p-1 hover:bg-gray-100 rounded">
              <Plus className="h-3 w-3 text-gray-500" />
            </button>
          </div>

          {projectsExpanded && (
            <div className="space-y-1">
              {projects.map((project) => {
                const isActive = currentProjectId === project.id
                return (
                  <button
                    key={project.id}
                    onClick={() => setCurrentProject(project.id)}
                    className={cn(
                      'flex items-center gap-3 w-full px-3 py-2 text-sm rounded-lg transition-colors text-left',
                      isActive
                        ? 'bg-gray-900 text-white'
                        : 'text-gray-700 hover:bg-gray-100'
                    )}
                  >
                    <span className="text-base">{project.icon}</span>
                    <span className="font-medium">{project.name}</span>
                  </button>
                )
              })}
            </div>
          )}
        </div>

        {/* Teams Section */}
        <div className="mt-8">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Teams
            </span>
            <button className="p-1 hover:bg-gray-100 rounded">
              <Plus className="h-3 w-3 text-gray-500" />
            </button>
          </div>
          <div className="space-y-1">
            <Link
              href="/teams/engineering"
              className="flex items-center gap-3 px-3 py-2 text-sm text-gray-700 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <Users className="h-4 w-4" />
              <span className="font-medium">Engineering</span>
            </Link>
            <Link
              href="/teams/design"
              className="flex items-center gap-3 px-3 py-2 text-sm text-gray-700 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <Users className="h-4 w-4" />
              <span className="font-medium">Design</span>
            </Link>
          </div>
        </div>

        {/* Bottom Navigation */}
        <div className="mt-8 pt-8 border-t border-gray-200 space-y-1">
          {bottomNavigation.map((item) => {
            const isActive = pathname === item.href
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  'flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg transition-colors',
                  isActive
                    ? 'bg-gray-900 text-white'
                    : 'text-gray-700 hover:bg-gray-100'
                )}
              >
                <item.icon className="h-4 w-4" />
                {item.name}
              </Link>
            )
          })}
        </div>
      </nav>

      {/* Upgrade Banner */}
      <div className="p-4 border-t border-gray-200">
        <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg p-4 text-white">
          <div className="flex items-center gap-2 mb-2">
            <Zap className="h-4 w-4" />
            <span className="text-sm font-semibold">Upgrade to Pro</span>
          </div>
          <p className="text-xs opacity-90 mb-3">
            Unlock unlimited projects and advanced features
          </p>
          <button className="w-full bg-white text-gray-900 text-xs font-medium py-2 px-3 rounded-md hover:bg-gray-100 transition-colors">
            Start free trial
          </button>
        </div>
      </div>
    </div>
  )
}
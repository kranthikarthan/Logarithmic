'use client'

import { Header } from '@/components/header'
import { BarChart3, Plus, Filter, Calendar, List, LayoutGrid } from 'lucide-react'

const views = [
  { name: 'All Issues', icon: List, description: 'View all issues across projects', color: 'bg-blue-500' },
  { name: 'Active Sprint', icon: LayoutGrid, description: 'Current sprint board', color: 'bg-green-500' },
  { name: 'My Work', icon: Filter, description: 'Issues assigned to you', color: 'bg-purple-500' },
  { name: 'Roadmap', icon: Calendar, description: 'Project timeline and milestones', color: 'bg-orange-500' },
]

export default function ViewsPage() {
  return (
    <>
      <Header />
      <main className="flex-1 overflow-auto p-6">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-2xl font-semibold text-gray-900">Views</h1>
              <p className="text-sm text-gray-500 mt-1">
                Create custom views to organize and filter your issues
              </p>
            </div>
            <button className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-gray-900 rounded-lg hover:bg-gray-800 transition-colors">
              <Plus className="h-4 w-4" />
              New View
            </button>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            {views.map((view) => (
              <button
                key={view.name}
                className="flex items-start gap-4 p-4 bg-white border border-gray-200 rounded-lg hover:border-gray-300 hover:shadow-sm transition-all text-left"
              >
                <div className={`p-2 rounded-lg ${view.color}`}>
                  <view.icon className="h-5 w-5 text-white" />
                </div>
                <div className="flex-1">
                  <h3 className="font-medium text-gray-900">{view.name}</h3>
                  <p className="text-sm text-gray-500 mt-1">{view.description}</p>
                </div>
              </button>
            ))}
          </div>

          <div className="mt-8 p-6 bg-gray-50 rounded-lg border border-gray-200">
            <div className="flex items-center gap-3 mb-3">
              <BarChart3 className="h-5 w-5 text-gray-400" />
              <h2 className="font-medium text-gray-900">Recent Activity</h2>
            </div>
            <div className="space-y-3">
              <div className="flex items-center gap-3 text-sm">
                <div className="w-2 h-2 bg-green-500 rounded-full" />
                <span className="text-gray-600">5 issues completed this week</span>
              </div>
              <div className="flex items-center gap-3 text-sm">
                <div className="w-2 h-2 bg-blue-500 rounded-full" />
                <span className="text-gray-600">12 issues in progress</span>
              </div>
              <div className="flex items-center gap-3 text-sm">
                <div className="w-2 h-2 bg-yellow-500 rounded-full" />
                <span className="text-gray-600">8 issues in backlog</span>
              </div>
            </div>
          </div>
        </div>
      </main>
    </>
  )
}
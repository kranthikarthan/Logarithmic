import { create } from 'zustand'

export type Priority = 'none' | 'low' | 'medium' | 'high' | 'urgent'
export type Status = 'backlog' | 'todo' | 'in-progress' | 'done' | 'cancelled'
export type ViewType = 'list' | 'board' | 'calendar'

export interface Label {
  id: string
  name: string
  color: string
}

export interface Issue {
  id: string
  title: string
  description?: string
  status: Status
  priority: Priority
  assignee?: string
  labels: string[]
  projectId: string
  createdAt: Date
  updatedAt: Date
  dueDate?: Date
  estimate?: number
}

export interface Project {
  id: string
  name: string
  description?: string
  icon: string
  color: string
  lead?: string
  createdAt: Date
}

export interface User {
  id: string
  name: string
  email: string
  avatar?: string
}

interface AppState {
  // Issues
  issues: Issue[]
  addIssue: (issue: Omit<Issue, 'id' | 'createdAt' | 'updatedAt'>) => void
  updateIssue: (id: string, updates: Partial<Issue>) => void
  deleteIssue: (id: string) => void
  
  // Projects
  projects: Project[]
  currentProjectId: string | null
  setCurrentProject: (id: string | null) => void
  addProject: (project: Omit<Project, 'id' | 'createdAt'>) => void
  
  // Labels
  labels: Label[]
  addLabel: (label: Omit<Label, 'id'>) => void
  
  // View
  currentView: ViewType
  setCurrentView: (view: ViewType) => void
  
  // Filters
  searchQuery: string
  setSearchQuery: (query: string) => void
  statusFilter: Status | 'all'
  setStatusFilter: (status: Status | 'all') => void
  priorityFilter: Priority | 'all'
  setPriorityFilter: (priority: Priority | 'all') => void
  
  // User
  currentUser: User
}

// Sample data
const sampleProjects: Project[] = [
  {
    id: 'PRJ001',
    name: 'Web Platform',
    description: 'Main web application development',
    icon: '🌐',
    color: '#3B82F6',
    createdAt: new Date('2024-01-01'),
  },
  {
    id: 'PRJ002',
    name: 'Mobile App',
    description: 'iOS and Android applications',
    icon: '📱',
    color: '#8B5CF6',
    createdAt: new Date('2024-01-15'),
  },
  {
    id: 'PRJ003',
    name: 'API Development',
    description: 'Backend API and microservices',
    icon: '⚡',
    color: '#10B981',
    createdAt: new Date('2024-02-01'),
  },
]

const sampleLabels: Label[] = [
  { id: 'LBL001', name: 'Bug', color: '#EF4444' },
  { id: 'LBL002', name: 'Feature', color: '#3B82F6' },
  { id: 'LBL003', name: 'Enhancement', color: '#8B5CF6' },
  { id: 'LBL004', name: 'Documentation', color: '#10B981' },
  { id: 'LBL005', name: 'Performance', color: '#F59E0B' },
]

const sampleIssues: Issue[] = [
  {
    id: 'LIN-001',
    title: 'Implement user authentication',
    description: 'Add OAuth2 authentication with Google and GitHub providers',
    status: 'in-progress',
    priority: 'high',
    assignee: 'John Doe',
    labels: ['LBL002'],
    projectId: 'PRJ001',
    createdAt: new Date('2024-03-01'),
    updatedAt: new Date('2024-03-10'),
    estimate: 8,
  },
  {
    id: 'LIN-002',
    title: 'Fix navigation menu on mobile',
    description: 'The navigation menu is not responsive on mobile devices',
    status: 'todo',
    priority: 'medium',
    assignee: 'Jane Smith',
    labels: ['LBL001'],
    projectId: 'PRJ001',
    createdAt: new Date('2024-03-05'),
    updatedAt: new Date('2024-03-05'),
    estimate: 3,
  },
  {
    id: 'LIN-003',
    title: 'Add dark mode support',
    description: 'Implement system-wide dark mode with user preference storage',
    status: 'backlog',
    priority: 'low',
    labels: ['LBL003'],
    projectId: 'PRJ001',
    createdAt: new Date('2024-03-08'),
    updatedAt: new Date('2024-03-08'),
    estimate: 5,
  },
  {
    id: 'LIN-004',
    title: 'Optimize database queries',
    description: 'Improve performance of main dashboard queries',
    status: 'done',
    priority: 'high',
    assignee: 'Bob Wilson',
    labels: ['LBL005'],
    projectId: 'PRJ003',
    createdAt: new Date('2024-02-20'),
    updatedAt: new Date('2024-03-01'),
    estimate: 13,
  },
  {
    id: 'LIN-005',
    title: 'Create API documentation',
    description: 'Document all REST API endpoints with examples',
    status: 'in-progress',
    priority: 'medium',
    assignee: 'Alice Johnson',
    labels: ['LBL004'],
    projectId: 'PRJ003',
    createdAt: new Date('2024-03-10'),
    updatedAt: new Date('2024-03-12'),
    dueDate: new Date('2024-03-20'),
    estimate: 8,
  },
  {
    id: 'LIN-006',
    title: 'Implement push notifications',
    description: 'Add push notification support for mobile apps',
    status: 'todo',
    priority: 'high',
    labels: ['LBL002'],
    projectId: 'PRJ002',
    createdAt: new Date('2024-03-11'),
    updatedAt: new Date('2024-03-11'),
    dueDate: new Date('2024-03-25'),
    estimate: 13,
  },
  {
    id: 'LIN-007',
    title: 'Fix memory leak in image processing',
    description: 'Memory usage increases over time when processing images',
    status: 'in-progress',
    priority: 'urgent',
    assignee: 'John Doe',
    labels: ['LBL001', 'LBL005'],
    projectId: 'PRJ002',
    createdAt: new Date('2024-03-12'),
    updatedAt: new Date('2024-03-13'),
    estimate: 5,
  },
  {
    id: 'LIN-008',
    title: 'Add offline mode',
    description: 'Allow mobile app to work offline with data sync',
    status: 'backlog',
    priority: 'medium',
    labels: ['LBL002'],
    projectId: 'PRJ002',
    createdAt: new Date('2024-03-09'),
    updatedAt: new Date('2024-03-09'),
    estimate: 21,
  },
]

export const useStore = create<AppState>((set) => ({
  // Issues
  issues: sampleIssues,
  addIssue: (issueData) => set((state) => {
    const newIssue: Issue = {
      ...issueData,
      id: `LIN-${String(state.issues.length + 1).padStart(3, '0')}`,
      createdAt: new Date(),
      updatedAt: new Date(),
    }
    return { issues: [...state.issues, newIssue] }
  }),
  updateIssue: (id, updates) => set((state) => ({
    issues: state.issues.map(issue => 
      issue.id === id 
        ? { ...issue, ...updates, updatedAt: new Date() }
        : issue
    )
  })),
  deleteIssue: (id) => set((state) => ({
    issues: state.issues.filter(issue => issue.id !== id)
  })),
  
  // Projects
  projects: sampleProjects,
  currentProjectId: 'PRJ001',
  setCurrentProject: (id) => set({ currentProjectId: id }),
  addProject: (projectData) => set((state) => {
    const newProject: Project = {
      ...projectData,
      id: `PRJ${String(state.projects.length + 1).padStart(3, '0')}`,
      createdAt: new Date(),
    }
    return { projects: [...state.projects, newProject] }
  }),
  
  // Labels
  labels: sampleLabels,
  addLabel: (labelData) => set((state) => {
    const newLabel: Label = {
      ...labelData,
      id: `LBL${String(state.labels.length + 1).padStart(3, '0')}`,
    }
    return { labels: [...state.labels, newLabel] }
  }),
  
  // View
  currentView: 'list',
  setCurrentView: (view) => set({ currentView: view }),
  
  // Filters
  searchQuery: '',
  setSearchQuery: (query) => set({ searchQuery: query }),
  statusFilter: 'all',
  setStatusFilter: (status) => set({ statusFilter: status }),
  priorityFilter: 'all',
  setPriorityFilter: (priority) => set({ priorityFilter: priority }),
  
  // User
  currentUser: {
    id: 'USER001',
    name: 'John Doe',
    email: 'john@example.com',
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=John',
  },
}))
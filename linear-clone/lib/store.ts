import { create } from 'zustand'

export type Priority = 'none' | 'low' | 'medium' | 'high' | 'urgent'
export type Status = 'backlog' | 'todo' | 'in-progress' | 'done' | 'cancelled'
export type ViewType = 'list' | 'board' | 'calendar'
export type BudgetStatus = 'under' | 'on' | 'over'
export type ProjectPhase = 'planning' | 'development' | 'testing' | 'deployment' | 'maintenance' | 'completed'
export type BlockerSeverity = 'low' | 'medium' | 'high' | 'critical'

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
  // Executive reporting fields
  budget: number
  spent: number
  budgetStatus: BudgetStatus
  startDate: Date
  endDate: Date
  phase: ProjectPhase
  progress: number // 0-100
  deploymentVelocity?: number // deployments per week
  lastDeployment?: Date
  blockers: Blocker[]
  teamSize: number
  businessValue: 'low' | 'medium' | 'high' | 'critical'
  riskLevel: 'low' | 'medium' | 'high' | 'critical'
}

export interface Blocker {
  id: string
  title: string
  description: string
  severity: BlockerSeverity
  projectId: string
  createdAt: Date
  resolvedAt?: Date
  assignedTo?: string
}

export interface DeploymentMetric {
  id: string
  projectId: string
  application: string
  deployments: number
  week: string
  successRate: number
  avgDeployTime: number // in minutes
}

export interface ExecutiveSummary {
  totalProjects: number
  activeProjects: number
  completedProjects: number
  totalBudget: number
  totalSpent: number
  budgetVariance: number
  avgProgress: number
  criticalBlockers: number
  totalDeployments: number
  avgDeploymentVelocity: number
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
  updateProject: (id: string, updates: Partial<Project>) => void
  
  // Blockers
  blockers: Blocker[]
  addBlocker: (blocker: Omit<Blocker, 'id' | 'createdAt'>) => void
  updateBlocker: (id: string, updates: Partial<Blocker>) => void
  resolveBlocker: (id: string) => void
  
  // Deployment Metrics
  deploymentMetrics: DeploymentMetric[]
  addDeploymentMetric: (metric: Omit<DeploymentMetric, 'id'>) => void
  
  // Executive Summary
  getExecutiveSummary: () => ExecutiveSummary
  
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
    budget: 500000,
    spent: 320000,
    budgetStatus: 'under',
    startDate: new Date('2024-01-01'),
    endDate: new Date('2024-06-30'),
    phase: 'development',
    progress: 65,
    deploymentVelocity: 12,
    lastDeployment: new Date('2024-03-15'),
    blockers: [],
    teamSize: 8,
    businessValue: 'critical',
    riskLevel: 'medium',
  },
  {
    id: 'PRJ002',
    name: 'Mobile App',
    description: 'iOS and Android applications',
    icon: '📱',
    color: '#8B5CF6',
    createdAt: new Date('2024-01-15'),
    budget: 300000,
    spent: 280000,
    budgetStatus: 'on',
    startDate: new Date('2024-01-15'),
    endDate: new Date('2024-05-15'),
    phase: 'testing',
    progress: 80,
    deploymentVelocity: 8,
    lastDeployment: new Date('2024-03-14'),
    blockers: [],
    teamSize: 6,
    businessValue: 'high',
    riskLevel: 'low',
  },
  {
    id: 'PRJ003',
    name: 'API Development',
    description: 'Backend API and microservices',
    icon: '⚡',
    color: '#10B981',
    createdAt: new Date('2024-02-01'),
    budget: 200000,
    spent: 180000,
    budgetStatus: 'on',
    startDate: new Date('2024-02-01'),
    endDate: new Date('2024-04-30'),
    phase: 'deployment',
    progress: 90,
    deploymentVelocity: 15,
    lastDeployment: new Date('2024-03-16'),
    blockers: [],
    teamSize: 4,
    businessValue: 'critical',
    riskLevel: 'low',
  },
  {
    id: 'PRJ004',
    name: 'Data Analytics Platform',
    description: 'Real-time analytics and reporting system',
    icon: '📊',
    color: '#F59E0B',
    createdAt: new Date('2024-02-15'),
    budget: 400000,
    spent: 450000,
    budgetStatus: 'over',
    startDate: new Date('2024-02-15'),
    endDate: new Date('2024-08-15'),
    phase: 'development',
    progress: 45,
    deploymentVelocity: 5,
    lastDeployment: new Date('2024-03-10'),
    blockers: [],
    teamSize: 10,
    businessValue: 'high',
    riskLevel: 'high',
  },
  {
    id: 'PRJ005',
    name: 'Customer Portal',
    description: 'Self-service customer management portal',
    icon: '👥',
    color: '#EF4444',
    createdAt: new Date('2024-03-01'),
    budget: 150000,
    spent: 95000,
    budgetStatus: 'under',
    startDate: new Date('2024-03-01'),
    endDate: new Date('2024-07-01'),
    phase: 'planning',
    progress: 25,
    deploymentVelocity: 0,
    lastDeployment: undefined,
    blockers: [],
    teamSize: 5,
    businessValue: 'medium',
    riskLevel: 'medium',
  },
  {
    id: 'PRJ006',
    name: 'AI/ML Integration',
    description: 'Machine learning model integration and deployment',
    icon: '🤖',
    color: '#8B5CF6',
    createdAt: new Date('2024-03-05'),
    budget: 600000,
    spent: 200000,
    budgetStatus: 'under',
    startDate: new Date('2024-03-05'),
    endDate: new Date('2024-12-31'),
    phase: 'development',
    progress: 30,
    deploymentVelocity: 3,
    lastDeployment: new Date('2024-03-12'),
    blockers: [],
    teamSize: 12,
    businessValue: 'critical',
    riskLevel: 'high',
  },
  {
    id: 'PRJ007',
    name: 'Security Enhancement',
    description: 'Comprehensive security audit and improvements',
    icon: '🔒',
    color: '#DC2626',
    createdAt: new Date('2024-02-20'),
    budget: 100000,
    spent: 75000,
    budgetStatus: 'under',
    startDate: new Date('2024-02-20'),
    endDate: new Date('2024-04-20'),
    phase: 'testing',
    progress: 70,
    deploymentVelocity: 2,
    lastDeployment: new Date('2024-03-08'),
    blockers: [],
    teamSize: 3,
    businessValue: 'critical',
    riskLevel: 'medium',
  },
  {
    id: 'PRJ008',
    name: 'Performance Optimization',
    description: 'System performance improvements and scaling',
    icon: '⚡',
    color: '#059669',
    createdAt: new Date('2024-03-10'),
    budget: 80000,
    spent: 60000,
    budgetStatus: 'under',
    startDate: new Date('2024-03-10'),
    endDate: new Date('2024-05-10'),
    phase: 'development',
    progress: 60,
    deploymentVelocity: 6,
    lastDeployment: new Date('2024-03-13'),
    blockers: [],
    teamSize: 4,
    businessValue: 'high',
    riskLevel: 'low',
  },
  {
    id: 'PRJ009',
    name: 'Integration Hub',
    description: 'Third-party integrations and API gateway',
    icon: '🔗',
    color: '#7C3AED',
    createdAt: new Date('2024-03-12'),
    budget: 250000,
    spent: 120000,
    budgetStatus: 'under',
    startDate: new Date('2024-03-12'),
    endDate: new Date('2024-09-12'),
    phase: 'development',
    progress: 40,
    deploymentVelocity: 4,
    lastDeployment: new Date('2024-03-11'),
    blockers: [],
    teamSize: 6,
    businessValue: 'high',
    riskLevel: 'medium',
  },
  {
    id: 'PRJ010',
    name: 'Mobile Backend',
    description: 'Backend services for mobile applications',
    icon: '📱',
    color: '#0891B2',
    createdAt: new Date('2024-02-25'),
    budget: 180000,
    spent: 160000,
    budgetStatus: 'on',
    startDate: new Date('2024-02-25'),
    endDate: new Date('2024-06-25'),
    phase: 'testing',
    progress: 75,
    deploymentVelocity: 10,
    lastDeployment: new Date('2024-03-14'),
    blockers: [],
    teamSize: 5,
    businessValue: 'high',
    riskLevel: 'low',
  },
  {
    id: 'PRJ011',
    name: 'Content Management',
    description: 'Headless CMS and content delivery system',
    icon: '📝',
    color: '#EA580C',
    createdAt: new Date('2024-03-08'),
    budget: 120000,
    spent: 45000,
    budgetStatus: 'under',
    startDate: new Date('2024-03-08'),
    endDate: new Date('2024-07-08'),
    phase: 'development',
    progress: 35,
    deploymentVelocity: 7,
    lastDeployment: new Date('2024-03-15'),
    blockers: [],
    teamSize: 4,
    businessValue: 'medium',
    riskLevel: 'low',
  },
  {
    id: 'PRJ012',
    name: 'Notification System',
    description: 'Real-time notification and messaging platform',
    icon: '🔔',
    color: '#BE185D',
    createdAt: new Date('2024-03-03'),
    budget: 90000,
    spent: 70000,
    budgetStatus: 'under',
    startDate: new Date('2024-03-03'),
    endDate: new Date('2024-05-03'),
    phase: 'development',
    progress: 55,
    deploymentVelocity: 8,
    lastDeployment: new Date('2024-03-12'),
    blockers: [],
    teamSize: 3,
    businessValue: 'medium',
    riskLevel: 'low',
  },
  {
    id: 'PRJ013',
    name: 'Payment Gateway',
    description: 'Payment processing and financial integrations',
    icon: '💳',
    color: '#059669',
    createdAt: new Date('2024-02-28'),
    budget: 350000,
    spent: 280000,
    budgetStatus: 'on',
    startDate: new Date('2024-02-28'),
    endDate: new Date('2024-08-28'),
    phase: 'testing',
    progress: 70,
    deploymentVelocity: 3,
    lastDeployment: new Date('2024-03-09'),
    blockers: [],
    teamSize: 8,
    businessValue: 'critical',
    riskLevel: 'high',
  },
  {
    id: 'PRJ014',
    name: 'Monitoring Dashboard',
    description: 'System monitoring and alerting dashboard',
    icon: '📈',
    color: '#7C2D12',
    createdAt: new Date('2024-03-06'),
    budget: 75000,
    spent: 50000,
    budgetStatus: 'under',
    startDate: new Date('2024-03-06'),
    endDate: new Date('2024-06-06'),
    phase: 'development',
    progress: 50,
    deploymentVelocity: 5,
    lastDeployment: new Date('2024-03-13'),
    blockers: [],
    teamSize: 3,
    businessValue: 'high',
    riskLevel: 'low',
  },
  {
    id: 'PRJ015',
    name: 'User Authentication',
    description: 'SSO and multi-factor authentication system',
    icon: '🔐',
    color: '#1E40AF',
    createdAt: new Date('2024-02-22'),
    budget: 200000,
    spent: 180000,
    budgetStatus: 'on',
    startDate: new Date('2024-02-22'),
    endDate: new Date('2024-05-22'),
    phase: 'deployment',
    progress: 85,
    deploymentVelocity: 6,
    lastDeployment: new Date('2024-03-16'),
    blockers: [],
    teamSize: 5,
    businessValue: 'critical',
    riskLevel: 'medium',
  },
  {
    id: 'PRJ016',
    name: 'Data Warehouse',
    description: 'Data lake and warehouse infrastructure',
    icon: '🏗️',
    color: '#92400E',
    createdAt: new Date('2024-03-14'),
    budget: 500000,
    spent: 150000,
    budgetStatus: 'under',
    startDate: new Date('2024-03-14'),
    endDate: new Date('2024-12-14'),
    phase: 'planning',
    progress: 20,
    deploymentVelocity: 0,
    lastDeployment: undefined,
    blockers: [],
    teamSize: 15,
    businessValue: 'critical',
    riskLevel: 'high',
  },
  {
    id: 'PRJ017',
    name: 'API Documentation',
    description: 'Automated API documentation and testing',
    icon: '📚',
    color: '#6B7280',
    createdAt: new Date('2024-03-11'),
    budget: 50000,
    spent: 35000,
    budgetStatus: 'under',
    startDate: new Date('2024-03-11'),
    endDate: new Date('2024-05-11'),
    phase: 'development',
    progress: 60,
    deploymentVelocity: 12,
    lastDeployment: new Date('2024-03-15'),
    blockers: [],
    teamSize: 2,
    businessValue: 'medium',
    riskLevel: 'low',
  },
  {
    id: 'PRJ018',
    name: 'Mobile Testing',
    description: 'Automated mobile app testing framework',
    icon: '🧪',
    color: '#BE123C',
    createdAt: new Date('2024-03-07'),
    budget: 80000,
    spent: 60000,
    budgetStatus: 'under',
    startDate: new Date('2024-03-07'),
    endDate: new Date('2024-06-07'),
    phase: 'development',
    progress: 45,
    deploymentVelocity: 4,
    lastDeployment: new Date('2024-03-14'),
    blockers: [],
    teamSize: 3,
    businessValue: 'high',
    riskLevel: 'low',
  },
  {
    id: 'PRJ019',
    name: 'Cloud Migration',
    description: 'Legacy system migration to cloud infrastructure',
    icon: '☁️',
    color: '#0EA5E9',
    createdAt: new Date('2024-02-18'),
    budget: 800000,
    spent: 600000,
    budgetStatus: 'under',
    startDate: new Date('2024-02-18'),
    endDate: new Date('2024-11-18'),
    phase: 'development',
    progress: 65,
    deploymentVelocity: 2,
    lastDeployment: new Date('2024-03-10'),
    blockers: [],
    teamSize: 20,
    businessValue: 'critical',
    riskLevel: 'high',
  },
  {
    id: 'PRJ020',
    name: 'Compliance Framework',
    description: 'GDPR and SOC2 compliance implementation',
    icon: '⚖️',
    color: '#7C3AED',
    createdAt: new Date('2024-03-09'),
    budget: 300000,
    spent: 120000,
    budgetStatus: 'under',
    startDate: new Date('2024-03-09'),
    endDate: new Date('2024-09-09'),
    phase: 'planning',
    progress: 30,
    deploymentVelocity: 1,
    lastDeployment: new Date('2024-03-08'),
    blockers: [],
    teamSize: 8,
    businessValue: 'critical',
    riskLevel: 'high',
  },
  {
    id: 'PRJ021',
    name: 'Microservices Architecture',
    description: 'Breaking monolith into microservices',
    icon: '🔧',
    color: '#059669',
    createdAt: new Date('2024-03-13'),
    budget: 400000,
    spent: 100000,
    budgetStatus: 'under',
    startDate: new Date('2024-03-13'),
    endDate: new Date('2024-10-13'),
    phase: 'development',
    progress: 25,
    deploymentVelocity: 8,
    lastDeployment: new Date('2024-03-16'),
    blockers: [],
    teamSize: 12,
    businessValue: 'high',
    riskLevel: 'medium',
  },
  {
    id: 'PRJ022',
    name: 'Real-time Analytics',
    description: 'Stream processing and real-time data analytics',
    icon: '📊',
    color: '#DC2626',
    createdAt: new Date('2024-03-04'),
    budget: 250000,
    spent: 180000,
    budgetStatus: 'under',
    startDate: new Date('2024-03-04'),
    endDate: new Date('2024-08-04'),
    phase: 'development',
    progress: 55,
    deploymentVelocity: 6,
    lastDeployment: new Date('2024-03-15'),
    blockers: [],
    teamSize: 7,
    businessValue: 'high',
    riskLevel: 'medium',
  },
  {
    id: 'PRJ023',
    name: 'Disaster Recovery',
    description: 'Backup and disaster recovery system',
    icon: '🛡️',
    color: '#7C2D12',
    createdAt: new Date('2024-02-26'),
    budget: 150000,
    spent: 90000,
    budgetStatus: 'under',
    startDate: new Date('2024-02-26'),
    endDate: new Date('2024-06-26'),
    phase: 'development',
    progress: 50,
    deploymentVelocity: 3,
    lastDeployment: new Date('2024-03-12'),
    blockers: [],
    teamSize: 4,
    businessValue: 'critical',
    riskLevel: 'low',
  },
  {
    id: 'PRJ024',
    name: 'Load Testing',
    description: 'Performance and load testing automation',
    icon: '⚖️',
    color: '#B45309',
    createdAt: new Date('2024-03-16'),
    budget: 60000,
    spent: 25000,
    budgetStatus: 'under',
    startDate: new Date('2024-03-16'),
    endDate: new Date('2024-05-16'),
    phase: 'planning',
    progress: 20,
    deploymentVelocity: 0,
    lastDeployment: undefined,
    blockers: [],
    teamSize: 2,
    businessValue: 'medium',
    riskLevel: 'low',
  },
  {
    id: 'PRJ025',
    name: 'Feature Flags',
    description: 'Feature toggle and A/B testing platform',
    icon: '🚩',
    color: '#7C3AED',
    createdAt: new Date('2024-03-17'),
    budget: 100000,
    spent: 30000,
    budgetStatus: 'under',
    startDate: new Date('2024-03-17'),
    endDate: new Date('2024-07-17'),
    phase: 'development',
    progress: 30,
    deploymentVelocity: 9,
    lastDeployment: new Date('2024-03-17'),
    blockers: [],
    teamSize: 4,
    businessValue: 'high',
    riskLevel: 'low',
  },
]

const sampleLabels: Label[] = [
  { id: 'LBL001', name: 'Bug', color: '#EF4444' },
  { id: 'LBL002', name: 'Feature', color: '#3B82F6' },
  { id: 'LBL003', name: 'Enhancement', color: '#8B5CF6' },
  { id: 'LBL004', name: 'Documentation', color: '#10B981' },
  { id: 'LBL005', name: 'Performance', color: '#F59E0B' },
]

const sampleBlockers: Blocker[] = [
  {
    id: 'BLK001',
    title: 'Third-party API rate limiting',
    description: 'External payment API has strict rate limits causing delays',
    severity: 'high',
    projectId: 'PRJ013',
    createdAt: new Date('2024-03-10'),
    assignedTo: 'Alice Johnson',
  },
  {
    id: 'BLK002',
    title: 'Database migration complexity',
    description: 'Legacy data migration requires significant refactoring',
    severity: 'critical',
    projectId: 'PRJ019',
    createdAt: new Date('2024-03-08'),
    assignedTo: 'Bob Wilson',
  },
  {
    id: 'BLK003',
    title: 'Security compliance review',
    description: 'Waiting for security team approval on new authentication flow',
    severity: 'medium',
    projectId: 'PRJ015',
    createdAt: new Date('2024-03-12'),
    assignedTo: 'John Doe',
  },
  {
    id: 'BLK004',
    title: 'Cloud infrastructure provisioning',
    description: 'AWS resources taking longer than expected to provision',
    severity: 'medium',
    projectId: 'PRJ016',
    createdAt: new Date('2024-03-14'),
    assignedTo: 'Jane Smith',
  },
  {
    id: 'BLK005',
    title: 'Performance testing environment',
    description: 'Load testing environment not ready due to hardware issues',
    severity: 'low',
    projectId: 'PRJ024',
    createdAt: new Date('2024-03-16'),
    assignedTo: 'Mike Chen',
  },
]

const sampleDeploymentMetrics: DeploymentMetric[] = [
  { id: 'DEP001', projectId: 'PRJ001', application: 'Web Frontend', deployments: 12, week: '2024-W11', successRate: 95, avgDeployTime: 8 },
  { id: 'DEP002', projectId: 'PRJ001', application: 'Web Backend', deployments: 8, week: '2024-W11', successRate: 98, avgDeployTime: 12 },
  { id: 'DEP003', projectId: 'PRJ002', application: 'iOS App', deployments: 6, week: '2024-W11', successRate: 92, avgDeployTime: 15 },
  { id: 'DEP004', projectId: 'PRJ002', application: 'Android App', deployments: 8, week: '2024-W11', successRate: 90, avgDeployTime: 18 },
  { id: 'DEP005', projectId: 'PRJ003', application: 'API Gateway', deployments: 15, week: '2024-W11', successRate: 99, avgDeployTime: 5 },
  { id: 'DEP006', projectId: 'PRJ003', application: 'User Service', deployments: 10, week: '2024-W11', successRate: 97, avgDeployTime: 7 },
  { id: 'DEP007', projectId: 'PRJ004', application: 'Analytics Engine', deployments: 3, week: '2024-W11', successRate: 85, avgDeployTime: 25 },
  { id: 'DEP008', projectId: 'PRJ006', application: 'ML Pipeline', deployments: 2, week: '2024-W11', successRate: 80, avgDeployTime: 45 },
  { id: 'DEP009', projectId: 'PRJ007', application: 'Security Scanner', deployments: 1, week: '2024-W11', successRate: 100, avgDeployTime: 30 },
  { id: 'DEP010', projectId: 'PRJ008', application: 'Performance Monitor', deployments: 4, week: '2024-W11', successRate: 95, avgDeployTime: 10 },
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

export const useStore = create<AppState>((set, get) => ({
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
  updateProject: (id, updates) => set((state) => ({
    projects: state.projects.map(project => 
      project.id === id 
        ? { ...project, ...updates }
        : project
    )
  })),
  
  // Blockers
  blockers: sampleBlockers,
  addBlocker: (blockerData) => set((state) => {
    const newBlocker: Blocker = {
      ...blockerData,
      id: `BLK${String(state.blockers.length + 1).padStart(3, '0')}`,
      createdAt: new Date(),
    }
    return { blockers: [...state.blockers, newBlocker] }
  }),
  updateBlocker: (id, updates) => set((state) => ({
    blockers: state.blockers.map(blocker => 
      blocker.id === id 
        ? { ...blocker, ...updates }
        : blocker
    )
  })),
  resolveBlocker: (id) => set((state) => ({
    blockers: state.blockers.map(blocker => 
      blocker.id === id 
        ? { ...blocker, resolvedAt: new Date() }
        : blocker
    )
  })),
  
  // Deployment Metrics
  deploymentMetrics: sampleDeploymentMetrics,
  addDeploymentMetric: (metricData) => set((state) => {
    const newMetric: DeploymentMetric = {
      ...metricData,
      id: `DEP${String(state.deploymentMetrics.length + 1).padStart(3, '0')}`,
    }
    return { deploymentMetrics: [...state.deploymentMetrics, newMetric] }
  }),
  
  // Executive Summary
  getExecutiveSummary: () => {
    const state = get()
    const totalProjects = state.projects.length
    const activeProjects = state.projects.filter(p => p.phase !== 'completed').length
    const completedProjects = state.projects.filter(p => p.phase === 'completed').length
    const totalBudget = state.projects.reduce((sum, p) => sum + p.budget, 0)
    const totalSpent = state.projects.reduce((sum, p) => sum + p.spent, 0)
    const budgetVariance = totalBudget - totalSpent
    const avgProgress = state.projects.reduce((sum, p) => sum + p.progress, 0) / totalProjects
    const criticalBlockers = state.blockers.filter(b => b.severity === 'critical' && !b.resolvedAt).length
    const totalDeployments = state.deploymentMetrics.reduce((sum, d) => sum + d.deployments, 0)
    const avgDeploymentVelocity = state.deploymentMetrics.reduce((sum, d) => sum + d.deployments, 0) / state.deploymentMetrics.length || 0
    
    return {
      totalProjects,
      activeProjects,
      completedProjects,
      totalBudget,
      totalSpent,
      budgetVariance,
      avgProgress,
      criticalBlockers,
      totalDeployments,
      avgDeploymentVelocity,
    }
  },
  
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
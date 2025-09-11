'use client'

import { useStore } from '@/lib/store'
import { format } from 'date-fns'
import { 
  TrendingUp, 
  DollarSign, 
  Users, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  Target,
  BarChart3,
  Activity,
  Shield,
  Zap,
  Calendar,
  ArrowUp,
  ArrowDown,
  Minus,
  Download
} from 'lucide-react'
import { downloadExecutiveReportPDF } from '@/lib/pdfExport'

export default function ExecutiveReports() {
  const { projects, blockers, deploymentMetrics, getExecutiveSummary } = useStore()
  const summary = getExecutiveSummary()

  const handleDownloadPDF = async () => {
    try {
      await downloadExecutiveReportPDF(projects, blockers, deploymentMetrics, summary)
    } catch (error) {
      console.error('Error generating PDF:', error)
      alert('Error generating PDF. Please try again.')
    }
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount)
  }

  const getBudgetStatusIcon = (status: string) => {
    switch (status) {
      case 'under':
        return <ArrowDown className="w-4 h-4 text-green-600" />
      case 'over':
        return <ArrowUp className="w-4 h-4 text-red-600" />
      default:
        return <Minus className="w-4 h-4 text-yellow-600" />
    }
  }

  const getBudgetStatusColor = (status: string) => {
    switch (status) {
      case 'under':
        return 'text-green-600 bg-green-50'
      case 'over':
        return 'text-red-600 bg-red-50'
      default:
        return 'text-yellow-600 bg-yellow-50'
    }
  }

  const getPhaseColor = (phase: string) => {
    switch (phase) {
      case 'planning':
        return 'bg-blue-100 text-blue-800'
      case 'development':
        return 'bg-purple-100 text-purple-800'
      case 'testing':
        return 'bg-orange-100 text-orange-800'
      case 'deployment':
        return 'bg-green-100 text-green-800'
      case 'maintenance':
        return 'bg-gray-100 text-gray-800'
      case 'completed':
        return 'bg-emerald-100 text-emerald-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'low':
        return 'text-green-600 bg-green-50'
      case 'medium':
        return 'text-yellow-600 bg-yellow-50'
      case 'high':
        return 'text-orange-600 bg-orange-50'
      case 'critical':
        return 'text-red-600 bg-red-50'
      default:
        return 'text-gray-600 bg-gray-50'
    }
  }

  const getBusinessValueColor = (value: string) => {
    switch (value) {
      case 'low':
        return 'text-gray-600 bg-gray-50'
      case 'medium':
        return 'text-blue-600 bg-blue-50'
      case 'high':
        return 'text-purple-600 bg-purple-50'
      case 'critical':
        return 'text-red-600 bg-red-50'
      default:
        return 'text-gray-600 bg-gray-50'
    }
  }

  const activeBlockers = blockers.filter(b => !b.resolvedAt)
  const criticalBlockers = activeBlockers.filter(b => b.severity === 'critical')

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-green-200">
        <div className="px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Executive Monthly Report</h1>
              <p className="text-lg text-gray-600 mt-1">
                {format(new Date(), 'MMMM yyyy')} - Technology Portfolio Overview
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={handleDownloadPDF}
                className="flex items-center space-x-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-colors font-medium"
              >
                <Download className="w-4 h-4" />
                <span>Download PDF</span>
              </button>
              <div className="text-right">
                <p className="text-sm text-gray-500">Generated on</p>
                <p className="text-lg font-semibold text-gray-900">
                  {format(new Date(), 'MMM dd, yyyy')}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="px-8 py-8 space-y-8">
        {/* Executive Summary */}
        <div className="bg-white rounded-xl shadow-lg border border-green-200 p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
            <BarChart3 className="w-6 h-6 text-green-600 mr-3" />
            Executive Summary
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg p-6 border border-green-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-green-600">Total Projects</p>
                  <p className="text-3xl font-bold text-gray-900">{summary.totalProjects}</p>
                </div>
                <Target className="w-8 h-8 text-green-600" />
              </div>
              <p className="text-sm text-gray-600 mt-2">
                {summary.activeProjects} active, {summary.completedProjects} completed
              </p>
            </div>

            <div className="bg-gradient-to-r from-blue-50 to-cyan-50 rounded-lg p-6 border border-blue-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-blue-600">Total Budget</p>
                  <p className="text-3xl font-bold text-gray-900">{formatCurrency(summary.totalBudget)}</p>
                </div>
                <DollarSign className="w-8 h-8 text-blue-600" />
              </div>
              <p className="text-sm text-gray-600 mt-2">
                {formatCurrency(summary.totalSpent)} spent ({formatCurrency(summary.budgetVariance)} remaining)
              </p>
            </div>

            <div className="bg-gradient-to-r from-purple-50 to-violet-50 rounded-lg p-6 border border-purple-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-purple-600">Avg Progress</p>
                  <p className="text-3xl font-bold text-gray-900">{Math.round(summary.avgProgress)}%</p>
                </div>
                <TrendingUp className="w-8 h-8 text-purple-600" />
              </div>
              <p className="text-sm text-gray-600 mt-2">
                Across all active projects
              </p>
            </div>

            <div className="bg-gradient-to-r from-orange-50 to-amber-50 rounded-lg p-6 border border-orange-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-orange-600">Deployments</p>
                  <p className="text-3xl font-bold text-gray-900">{summary.totalDeployments}</p>
                </div>
                <Zap className="w-8 h-8 text-orange-600" />
              </div>
              <p className="text-sm text-gray-600 mt-2">
                {Math.round(summary.avgDeploymentVelocity)} avg per week
              </p>
            </div>
          </div>

          {/* Risk Indicators */}
          <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-red-50 rounded-lg p-4 border border-red-200">
              <div className="flex items-center">
                <AlertTriangle className="w-5 h-5 text-red-600 mr-2" />
                <span className="font-semibold text-red-800">Critical Blockers</span>
              </div>
              <p className="text-2xl font-bold text-red-900 mt-1">{criticalBlockers.length}</p>
            </div>

            <div className="bg-yellow-50 rounded-lg p-4 border border-yellow-200">
              <div className="flex items-center">
                <Clock className="w-5 h-5 text-yellow-600 mr-2" />
                <span className="font-semibold text-yellow-800">Active Blockers</span>
              </div>
              <p className="text-2xl font-bold text-yellow-900 mt-1">{activeBlockers.length}</p>
            </div>

            <div className="bg-green-50 rounded-lg p-4 border border-green-200">
              <div className="flex items-center">
                <CheckCircle className="w-5 h-5 text-green-600 mr-2" />
                <span className="font-semibold text-green-800">On Track</span>
              </div>
              <p className="text-2xl font-bold text-green-900 mt-1">
                {projects.filter(p => p.progress >= 80 && p.budgetStatus !== 'over').length}
              </p>
            </div>
          </div>
        </div>

        {/* Project Portfolio Overview */}
        <div className="bg-white rounded-xl shadow-lg border border-green-200 p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
            <Calendar className="w-6 h-6 text-green-600 mr-3" />
            Project Portfolio Overview
          </h2>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Project</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Phase</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Progress</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Budget Status</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Timeline</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Team Size</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Business Value</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Risk Level</th>
                </tr>
              </thead>
              <tbody>
                {projects.map((project) => (
                  <tr key={project.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-4 px-4">
                      <div className="flex items-center">
                        <span className="text-2xl mr-3">{project.icon}</span>
                        <div>
                          <p className="font-semibold text-gray-900">{project.name}</p>
                          <p className="text-sm text-gray-600">{project.description}</p>
                        </div>
                      </div>
                    </td>
                    <td className="py-4 px-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getPhaseColor(project.phase)}`}>
                        {project.phase}
                      </span>
                    </td>
                    <td className="py-4 px-4">
                      <div className="flex items-center">
                        <div className="w-20 bg-gray-200 rounded-full h-2 mr-3">
                          <div 
                            className="bg-green-600 h-2 rounded-full" 
                            style={{ width: `${project.progress}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium text-gray-700">{project.progress}%</span>
                      </div>
                    </td>
                    <td className="py-4 px-4">
                      <div className="flex items-center">
                        {getBudgetStatusIcon(project.budgetStatus)}
                        <span className={`ml-2 px-2 py-1 rounded text-xs font-medium ${getBudgetStatusColor(project.budgetStatus)}`}>
                          {project.budgetStatus}
                        </span>
                      </div>
                      <p className="text-xs text-gray-600 mt-1">
                        {formatCurrency(project.spent)} / {formatCurrency(project.budget)}
                      </p>
                    </td>
                    <td className="py-4 px-4">
                      <div className="text-sm">
                        <p className="text-gray-900">
                          {format(project.startDate, 'MMM dd')} - {format(project.endDate, 'MMM dd, yyyy')}
                        </p>
                        <p className="text-gray-600">
                          {Math.ceil((project.endDate.getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24))} days left
                        </p>
                      </div>
                    </td>
                    <td className="py-4 px-4">
                      <div className="flex items-center">
                        <Users className="w-4 h-4 text-gray-400 mr-1" />
                        <span className="text-sm font-medium text-gray-700">{project.teamSize}</span>
                      </div>
                    </td>
                    <td className="py-4 px-4">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getBusinessValueColor(project.businessValue)}`}>
                        {project.businessValue}
                      </span>
                    </td>
                    <td className="py-4 px-4">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getRiskColor(project.riskLevel)}`}>
                        {project.riskLevel}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Deployment Velocity Metrics */}
        <div className="bg-white rounded-xl shadow-lg border border-green-200 p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
            <Activity className="w-6 h-6 text-green-600 mr-3" />
            Deployment Velocity Metrics
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {deploymentMetrics.map((metric) => (
              <div key={metric.id} className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg p-6 border border-green-200">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-semibold text-gray-900">{metric.application}</h3>
                  <Zap className="w-5 h-5 text-green-600" />
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Deployments</span>
                    <span className="font-semibold text-gray-900">{metric.deployments}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Success Rate</span>
                    <span className="font-semibold text-green-600">{metric.successRate}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Avg Deploy Time</span>
                    <span className="font-semibold text-gray-900">{metric.avgDeployTime}m</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Blockers and Risk Management */}
        <div className="bg-white rounded-xl shadow-lg border border-green-200 p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
            <Shield className="w-6 h-6 text-green-600 mr-3" />
            Blockers and Risk Management
          </h2>
          
          {activeBlockers.length > 0 ? (
            <div className="space-y-4">
              {activeBlockers.map((blocker) => (
                <div key={blocker.id} className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center mb-2">
                        <span className={`px-2 py-1 rounded text-xs font-medium mr-3 ${getRiskColor(blocker.severity)}`}>
                          {blocker.severity}
                        </span>
                        <h3 className="font-semibold text-gray-900">{blocker.title}</h3>
                      </div>
                      <p className="text-gray-600 mb-2">{blocker.description}</p>
                      <div className="flex items-center text-sm text-gray-500">
                        <span>Project: {projects.find(p => p.id === blocker.projectId)?.name}</span>
                        {blocker.assignedTo && (
                          <>
                            <span className="mx-2">•</span>
                            <span>Assigned to: {blocker.assignedTo}</span>
                          </>
                        )}
                        <span className="mx-2">•</span>
                        <span>Created: {format(blocker.createdAt, 'MMM dd, yyyy')}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-4" />
              <p className="text-lg font-semibold text-gray-900">No Active Blockers</p>
              <p className="text-gray-600">All projects are running smoothly!</p>
            </div>
          )}
        </div>

        {/* Key Insights and Recommendations */}
        <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl shadow-lg border border-green-200 p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
            <Target className="w-6 h-6 text-green-600 mr-3" />
            Key Insights and Recommendations
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg p-6 border border-green-200">
              <h3 className="font-semibold text-gray-900 mb-3">Budget Performance</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li>• {projects.filter(p => p.budgetStatus === 'under').length} projects under budget</li>
                <li>• {projects.filter(p => p.budgetStatus === 'on').length} projects on budget</li>
                <li>• {projects.filter(p => p.budgetStatus === 'over').length} projects over budget</li>
                <li>• Overall budget variance: {formatCurrency(summary.budgetVariance)}</li>
              </ul>
            </div>
            
            <div className="bg-white rounded-lg p-6 border border-green-200">
              <h3 className="font-semibold text-gray-900 mb-3">Project Health</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li>• Average progress across all projects: {Math.round(summary.avgProgress)}%</li>
                <li>• {projects.filter(p => p.progress >= 80).length} projects at 80%+ completion</li>
                <li>• {projects.filter(p => p.riskLevel === 'high' || p.riskLevel === 'critical').length} high-risk projects</li>
                <li>• {criticalBlockers.length} critical blockers requiring immediate attention</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
import jsPDF from 'jspdf'
import html2canvas from 'html2canvas'
import { Project, Blocker, DeploymentMetric, ExecutiveSummary } from './store'

interface PDFExportOptions {
  projects: Project[]
  blockers: Blocker[]
  deploymentMetrics: DeploymentMetric[]
  summary: ExecutiveSummary
  month: string
  year: string
}

export class PDFExporter {
  private doc: jsPDF
  private currentPage: number = 1
  private pageWidth: number
  private pageHeight: number
  private margin: number = 20

  constructor() {
    this.doc = new jsPDF('landscape', 'mm', 'a4')
    this.pageWidth = this.doc.internal.pageSize.getWidth()
    this.pageHeight = this.doc.internal.pageSize.getHeight()
  }

  private addHeader(title: string, subtitle?: string) {
    // Green gradient background
    this.doc.setFillColor(34, 197, 94) // Green-500
    this.doc.rect(0, 0, this.pageWidth, 30, 'F')
    
    // White text
    this.doc.setTextColor(255, 255, 255)
    this.doc.setFontSize(24)
    this.doc.setFont('helvetica', 'bold')
    this.doc.text(title, this.margin, 20)
    
    if (subtitle) {
      this.doc.setFontSize(14)
      this.doc.setFont('helvetica', 'normal')
      this.doc.text(subtitle, this.margin, 26)
    }
    
    // Reset text color
    this.doc.setTextColor(0, 0, 0)
  }

  private addFooter() {
    const footerY = this.pageHeight - 15
    this.doc.setFontSize(10)
    this.doc.setTextColor(100, 100, 100)
    this.doc.text(`Page ${this.currentPage}`, this.margin, footerY)
    this.doc.text(`Generated on ${new Date().toLocaleDateString()}`, this.pageWidth - 100, footerY)
  }

  private newPage() {
    this.doc.addPage()
    this.currentPage++
  }

  private formatCurrency(amount: number): string {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount)
  }

  private getBudgetStatusColor(status: string): [number, number, number] {
    switch (status) {
      case 'under': return [34, 197, 94] // Green
      case 'over': return [239, 68, 68] // Red
      default: return [245, 158, 11] // Yellow
    }
  }

  private getPhaseColor(phase: string): [number, number, number] {
    switch (phase) {
      case 'planning': return [59, 130, 246] // Blue
      case 'development': return [147, 51, 234] // Purple
      case 'testing': return [245, 158, 11] // Orange
      case 'deployment': return [34, 197, 94] // Green
      case 'maintenance': return [107, 114, 128] // Gray
      case 'completed': return [16, 185, 129] // Emerald
      default: return [107, 114, 128] // Gray
    }
  }

  private addSummarySlide(options: PDFExportOptions) {
    this.addHeader('Executive Monthly Report', `${options.month} ${options.year} - Technology Portfolio Overview`)
    
    // Summary metrics in a grid
    const metrics = [
      { label: 'Total Projects', value: options.summary.totalProjects.toString(), color: [34, 197, 94] },
      { label: 'Active Projects', value: options.summary.activeProjects.toString(), color: [59, 130, 246] },
      { label: 'Completed Projects', value: options.summary.completedProjects.toString(), color: [16, 185, 129] },
      { label: 'Total Budget', value: this.formatCurrency(options.summary.totalBudget), color: [147, 51, 234] },
      { label: 'Total Spent', value: this.formatCurrency(options.summary.totalSpent), color: [245, 158, 11] },
      { label: 'Budget Variance', value: this.formatCurrency(options.summary.budgetVariance), color: options.summary.budgetVariance >= 0 ? [34, 197, 94] : [239, 68, 68] },
      { label: 'Avg Progress', value: `${Math.round(options.summary.avgProgress)}%`, color: [16, 185, 129] },
      { label: 'Total Deployments', value: options.summary.totalDeployments.toString(), color: [245, 158, 11] },
    ]

    let y = 50
    const boxWidth = (this.pageWidth - 3 * this.margin) / 2
    const boxHeight = 25

    for (let i = 0; i < metrics.length; i += 2) {
      const x1 = this.margin
      const x2 = this.margin + boxWidth + this.margin
      
      // Left metric
      this.doc.setFillColor(240, 240, 240)
      this.doc.roundedRect(x1, y, boxWidth, boxHeight, 3, 3, 'F')
      this.doc.setTextColor(metrics[i].color[0], metrics[i].color[1], metrics[i].color[2])
      this.doc.setFontSize(16)
      this.doc.setFont('helvetica', 'bold')
      this.doc.text(metrics[i].value, x1 + 10, y + 10)
      this.doc.setTextColor(0, 0, 0)
      this.doc.setFontSize(10)
      this.doc.setFont('helvetica', 'normal')
      this.doc.text(metrics[i].label, x1 + 10, y + 18)

      // Right metric (if exists)
      if (i + 1 < metrics.length) {
        this.doc.setFillColor(240, 240, 240)
        this.doc.roundedRect(x2, y, boxWidth, boxHeight, 3, 3, 'F')
        this.doc.setTextColor(metrics[i + 1].color[0], metrics[i + 1].color[1], metrics[i + 1].color[2])
        this.doc.setFontSize(16)
        this.doc.setFont('helvetica', 'bold')
        this.doc.text(metrics[i + 1].value, x2 + 10, y + 10)
        this.doc.setTextColor(0, 0, 0)
        this.doc.setFontSize(10)
        this.doc.setFont('helvetica', 'normal')
        this.doc.text(metrics[i + 1].label, x2 + 10, y + 18)
      }

      y += boxHeight + 10
    }

    // Risk indicators
    const criticalBlockers = options.blockers.filter(b => b.severity === 'critical' && !b.resolvedAt).length
    const activeBlockers = options.blockers.filter(b => !b.resolvedAt).length
    const onTrackProjects = options.projects.filter(p => p.progress >= 80 && p.budgetStatus !== 'over').length

    y += 20
    this.doc.setFontSize(14)
    this.doc.setFont('helvetica', 'bold')
    this.doc.text('Risk Indicators', this.margin, y)

    y += 15
    const riskMetrics = [
      { label: 'Critical Blockers', value: criticalBlockers, color: [239, 68, 68] },
      { label: 'Active Blockers', value: activeBlockers, color: [245, 158, 11] },
      { label: 'On Track Projects', value: onTrackProjects, color: [34, 197, 94] },
    ]

    const riskBoxWidth = (this.pageWidth - 4 * this.margin) / 3
    riskMetrics.forEach((metric, index) => {
      const x = this.margin + index * (riskBoxWidth + this.margin)
      this.doc.setFillColor(metric.color[0], metric.color[1], metric.color[2], 0.1)
      this.doc.roundedRect(x, y, riskBoxWidth, 20, 3, 3, 'F')
      this.doc.setTextColor(metric.color[0], metric.color[1], metric.color[2])
      this.doc.setFontSize(18)
      this.doc.setFont('helvetica', 'bold')
      this.doc.text(metric.value.toString(), x + 10, y + 12)
      this.doc.setTextColor(0, 0, 0)
      this.doc.setFontSize(10)
      this.doc.setFont('helvetica', 'normal')
      this.doc.text(metric.label, x + 10, y + 18)
    })

    this.addFooter()
  }

  private addProjectPortfolioSlide(options: PDFExportOptions) {
    this.addHeader('Project Portfolio Overview', 'Current and Future Initiatives')
    
    // Table headers
    let y = 50
    this.doc.setFontSize(10)
    this.doc.setFont('helvetica', 'bold')
    
    const colWidths = [40, 25, 20, 25, 30, 15, 20, 20]
    const headers = ['Project', 'Phase', 'Progress', 'Budget', 'Timeline', 'Team', 'Value', 'Risk']
    
    let x = this.margin
    headers.forEach((header, index) => {
      this.doc.setFillColor(34, 197, 94)
      this.doc.rect(x, y, colWidths[index], 8, 'F')
      this.doc.setTextColor(255, 255, 255)
      this.doc.text(header, x + 2, y + 5)
      x += colWidths[index]
    })
    
    y += 8
    this.doc.setTextColor(0, 0, 0)
    
    // Project rows (showing first 12 projects to fit on page)
    const projectsToShow = options.projects.slice(0, 12)
    projectsToShow.forEach((project, rowIndex) => {
      if (y > this.pageHeight - 30) return // Don't go past footer area
      
      x = this.margin
      const rowY = y + (rowIndex * 12)
      
      // Project name (truncated)
      const projectName = project.name.length > 15 ? project.name.substring(0, 15) + '...' : project.name
      this.doc.setFontSize(8)
      this.doc.setFont('helvetica', 'normal')
      this.doc.text(projectName, x + 2, rowY + 5)
      x += colWidths[0]
      
      // Phase
      const phaseColor = this.getPhaseColor(project.phase)
      this.doc.setFillColor(phaseColor[0], phaseColor[1], phaseColor[2], 0.2)
      this.doc.rect(x, rowY - 2, colWidths[1], 8, 'F')
      this.doc.text(project.phase, x + 2, rowY + 5)
      x += colWidths[1]
      
      // Progress
      this.doc.text(`${project.progress}%`, x + 2, rowY + 5)
      x += colWidths[2]
      
      // Budget status
      const budgetColor = this.getBudgetStatusColor(project.budgetStatus)
      this.doc.setFillColor(budgetColor[0], budgetColor[1], budgetColor[2], 0.2)
      this.doc.rect(x, rowY - 2, colWidths[3], 8, 'F')
      this.doc.text(project.budgetStatus, x + 2, rowY + 5)
      x += colWidths[3]
      
      // Timeline
      const daysLeft = Math.ceil((project.endDate.getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24))
      this.doc.text(`${daysLeft}d left`, x + 2, rowY + 5)
      x += colWidths[4]
      
      // Team size
      this.doc.text(project.teamSize.toString(), x + 2, rowY + 5)
      x += colWidths[5]
      
      // Business value
      this.doc.text(project.businessValue, x + 2, rowY + 5)
      x += colWidths[6]
      
      // Risk level
      this.doc.text(project.riskLevel, x + 2, rowY + 5)
    })

    this.addFooter()
  }

  private addDeploymentMetricsSlide(options: PDFExportOptions) {
    this.addHeader('Deployment Velocity Metrics', 'Application Performance Overview')
    
    let y = 50
    this.doc.setFontSize(12)
    this.doc.setFont('helvetica', 'bold')
    this.doc.text('Deployment Performance by Application', this.margin, y)
    
    y += 20
    
    // Deployment metrics in a grid
    const metricsPerRow = 3
    const boxWidth = (this.pageWidth - (metricsPerRow + 1) * this.margin) / metricsPerRow
    const boxHeight = 40
    
    options.deploymentMetrics.forEach((metric, index) => {
      const row = Math.floor(index / metricsPerRow)
      const col = index % metricsPerRow
      const x = this.margin + col * (boxWidth + this.margin)
      const currentY = y + row * (boxHeight + 10)
      
      if (currentY + boxHeight > this.pageHeight - 30) return // Don't go past footer
      
      // Box background
      this.doc.setFillColor(240, 240, 240)
      this.doc.roundedRect(x, currentY, boxWidth, boxHeight, 3, 3, 'F')
      
      // Application name
      this.doc.setFontSize(10)
      this.doc.setFont('helvetica', 'bold')
      this.doc.text(metric.application, x + 5, currentY + 8)
      
      // Metrics
      this.doc.setFontSize(8)
      this.doc.setFont('helvetica', 'normal')
      this.doc.text(`Deployments: ${metric.deployments}`, x + 5, currentY + 16)
      this.doc.text(`Success Rate: ${metric.successRate}%`, x + 5, currentY + 22)
      this.doc.text(`Avg Time: ${metric.avgDeployTime}m`, x + 5, currentY + 28)
    })

    this.addFooter()
  }

  private addBlockersSlide(options: PDFExportOptions) {
    this.addHeader('Blockers and Risk Management', 'Active Issues Requiring Attention')
    
    const activeBlockers = options.blockers.filter(b => !b.resolvedAt)
    
    if (activeBlockers.length === 0) {
      let y = 80
      this.doc.setFontSize(16)
      this.doc.setFont('helvetica', 'bold')
      this.doc.setTextColor(34, 197, 94)
      this.doc.text('✓ No Active Blockers', this.margin, y)
      this.doc.setTextColor(0, 0, 0)
      this.doc.setFontSize(12)
      this.doc.setFont('helvetica', 'normal')
      this.doc.text('All projects are running smoothly!', this.margin, y + 15)
    } else {
      let y = 50
      this.doc.setFontSize(12)
      this.doc.setFont('helvetica', 'bold')
      this.doc.text(`Active Blockers (${activeBlockers.length})`, this.margin, y)
      
      y += 20
      
      activeBlockers.forEach((blocker, index) => {
        if (y > this.pageHeight - 50) return // Don't go past footer area
        
        const project = options.projects.find(p => p.id === blocker.projectId)
        const projectName = project ? project.name : 'Unknown Project'
        
        // Blocker box
        const severityColor = blocker.severity === 'critical' ? [239, 68, 68] : 
                             blocker.severity === 'high' ? [245, 158, 11] : 
                             blocker.severity === 'medium' ? [59, 130, 246] : [34, 197, 94]
        
        this.doc.setFillColor(severityColor[0], severityColor[1], severityColor[2], 0.1)
        this.doc.roundedRect(this.margin, y, this.pageWidth - 2 * this.margin, 25, 3, 3, 'F')
        
        // Severity badge
        this.doc.setFillColor(severityColor[0], severityColor[1], severityColor[2])
        this.doc.roundedRect(this.margin + 5, y + 5, 20, 8, 2, 2, 'F')
        this.doc.setTextColor(255, 255, 255)
        this.doc.setFontSize(8)
        this.doc.setFont('helvetica', 'bold')
        this.doc.text(blocker.severity.toUpperCase(), this.margin + 7, y + 10)
        
        // Blocker title
        this.doc.setTextColor(0, 0, 0)
        this.doc.setFontSize(10)
        this.doc.setFont('helvetica', 'bold')
        this.doc.text(blocker.title, this.margin + 30, y + 10)
        
        // Project and assignment
        this.doc.setFontSize(8)
        this.doc.setFont('helvetica', 'normal')
        this.doc.text(`Project: ${projectName}`, this.margin + 30, y + 18)
        if (blocker.assignedTo) {
          this.doc.text(`Assigned: ${blocker.assignedTo}`, this.margin + 120, y + 18)
        }
        
        y += 30
      })
    }

    this.addFooter()
  }

  public async generatePDF(options: PDFExportOptions): Promise<void> {
    // Slide 1: Executive Summary
    this.addSummarySlide(options)
    
    // Slide 2: Project Portfolio
    this.newPage()
    this.addProjectPortfolioSlide(options)
    
    // Slide 3: Deployment Metrics
    this.newPage()
    this.addDeploymentMetricsSlide(options)
    
    // Slide 4: Blockers and Risk Management
    this.newPage()
    this.addBlockersSlide(options)
    
    // Download the PDF
    const fileName = `Executive_Report_${options.month}_${options.year}.pdf`
    this.doc.save(fileName)
  }
}

export async function downloadExecutiveReportPDF(
  projects: Project[],
  blockers: Blocker[],
  deploymentMetrics: DeploymentMetric[],
  summary: ExecutiveSummary
): Promise<void> {
  const exporter = new PDFExporter()
  const now = new Date()
  const month = now.toLocaleDateString('en-US', { month: 'long' })
  const year = now.getFullYear().toString()
  
  await exporter.generatePDF({
    projects,
    blockers,
    deploymentMetrics,
    summary,
    month,
    year
  })
}
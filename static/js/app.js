// Xray Test Management Tool - JavaScript functionality

// Global application state
const AppState = {
    currentUser: null,
    currentProject: null,
    currentFilters: {},
    dataCache: new Map()
};

// Utility functions
const Utils = {
    formatDate: (dateString) => {
        if (!dateString) return 'N/A';
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },
    
    formatDateShort: (dateString) => {
        if (!dateString) return 'N/A';
        return new Date(dateString).toLocaleDateString();
    },
    
    truncateText: (text, maxLength = 50) => {
        if (!text) return '';
        return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    },
    
    getStatusBadgeClass: (status) => {
        const statusMap = {
            'Open': 'status-open',
            'In Progress': 'status-in-progress',
            'Done': 'status-done',
            'Closed': 'status-closed',
            'To Do': 'status-open',
            'In Review': 'status-in-progress',
            'Resolved': 'status-done'
        };
        return statusMap[status] || 'status-open';
    },
    
    getPriorityBadgeClass: (priority) => {
        const priorityMap = {
            'Highest': 'priority-highest',
            'High': 'priority-high',
            'Medium': 'priority-medium',
            'Low': 'priority-low',
            'Lowest': 'priority-lowest'
        };
        return priorityMap[priority] || 'priority-medium';
    },
    
    showLoading: (elementId) => {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = '<div class="text-center"><div class="loading-spinner"></div> Loading...</div>';
        }
    },
    
    hideLoading: (elementId) => {
        const element = document.getElementById(elementId);
        if (element && element.innerHTML.includes('loading-spinner')) {
            element.innerHTML = '';
        }
    },
    
    showAlert: (message, type = 'info') => {
        const alertContainer = document.querySelector('.container');
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        alertContainer.insertBefore(alert, alertContainer.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    },
    
    debounce: (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};

// API client
const ApiClient = {
    baseUrl: '',
    
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        };
        
        const config = { ...defaultOptions, ...options };
        
        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            Utils.showAlert(`API request failed: ${error.message}`, 'danger');
            throw error;
        }
    },
    
    async get(endpoint, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const url = queryString ? `${endpoint}?${queryString}` : endpoint;
        return this.request(url);
    },
    
    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    
    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },
    
    async delete(endpoint) {
        return this.request(endpoint, {
            method: 'DELETE'
        });
    }
};

// Data management
const DataManager = {
    cache: new Map(),
    cacheTimeout: 5 * 60 * 1000, // 5 minutes
    
    getCacheKey(endpoint, params = {}) {
        return `${endpoint}_${JSON.stringify(params)}`;
    },
    
    isCacheValid(key) {
        const cached = this.cache.get(key);
        if (!cached) return false;
        return Date.now() - cached.timestamp < this.cacheTimeout;
    },
    
    getCached(key) {
        const cached = this.cache.get(key);
        return cached ? cached.data : null;
    },
    
    setCache(key, data) {
        this.cache.set(key, {
            data: data,
            timestamp: Date.now()
        });
    },
    
    async fetchData(endpoint, params = {}) {
        const cacheKey = this.getCacheKey(endpoint, params);
        
        if (this.isCacheValid(cacheKey)) {
            return this.getCached(cacheKey);
        }
        
        try {
            const data = await ApiClient.get(endpoint, params);
            this.setCache(cacheKey, data);
            return data;
        } catch (error) {
            console.error(`Error fetching data from ${endpoint}:`, error);
            throw error;
        }
    },
    
    clearCache() {
        this.cache.clear();
    }
};

// UI components
const UIComponents = {
    createStatusBadge: (status) => {
        const badgeClass = Utils.getStatusBadgeClass(status);
        return `<span class="badge ${badgeClass}">${status}</span>`;
    },
    
    createPriorityBadge: (priority) => {
        const badgeClass = Utils.getPriorityBadgeClass(priority);
        return `<span class="badge ${badgeClass}">${priority}</span>`;
    },
    
    createUserAvatar: (user) => {
        if (!user) return 'N/A';
        const initials = user.displayName ? user.displayName.split(' ').map(n => n[0]).join('') : 'U';
        return `<span class="badge bg-secondary" title="${user.displayName}">${initials}</span>`;
    },
    
    createTableRow: (issue, columns) => {
        const row = document.createElement('tr');
        row.setAttribute('data-issue-key', issue.key);
        
        columns.forEach(column => {
            const cell = document.createElement('td');
            cell.innerHTML = this.formatCellValue(issue, column);
            row.appendChild(cell);
        });
        
        return row;
    },
    
    formatCellValue: (issue, column) => {
        const fields = issue.fields || {};
        
        switch (column.key) {
            case 'key':
                return `<a href="#" onclick="viewIssueDetails('${issue.key}')" class="text-decoration-none">${issue.key}</a>`;
            case 'summary':
                return Utils.truncateText(fields.summary);
            case 'status':
                return this.createStatusBadge(fields.status?.name || 'Unknown');
            case 'priority':
                return this.createPriorityBadge(fields.priority?.name || 'Medium');
            case 'assignee':
                return this.createUserAvatar(fields.assignee);
            case 'reporter':
                return this.createUserAvatar(fields.reporter);
            case 'created':
                return Utils.formatDateShort(fields.created);
            case 'updated':
                return Utils.formatDateShort(fields.updated);
            case 'labels':
                return fields.labels ? fields.labels.map(label => `<span class="badge bg-light text-dark">${label}</span>`).join(' ') : '';
            default:
                return fields[column.key] || '';
        }
    }
};

// Table management
const TableManager = {
    currentTable: null,
    currentData: [],
    currentColumns: [],
    
    createTable: (containerId, title, data, columns) => {
        this.currentData = data;
        this.currentColumns = columns;
        
        const container = document.getElementById(containerId);
        if (!container) return;
        
        container.innerHTML = `
            <div class="card">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h5>${title}</h5>
                    <div>
                        <button class="btn btn-sm btn-outline-primary" onclick="TableManager.exportTable()">
                            <i class="fas fa-download"></i> Export
                        </button>
                        <button class="btn btn-sm btn-outline-secondary" onclick="TableManager.hideTable()">
                            <i class="fas fa-times"></i> Close
                        </button>
                    </div>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-striped table-hover" id="data-table">
                            <thead id="table-head"></thead>
                            <tbody id="table-body"></tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;
        
        this.populateTable();
        this.currentTable = container;
    },
    
    populateTable: () => {
        const thead = document.getElementById('table-head');
        const tbody = document.getElementById('table-body');
        
        if (!thead || !tbody) return;
        
        // Clear existing content
        thead.innerHTML = '';
        tbody.innerHTML = '';
        
        if (this.currentData.length === 0) {
            tbody.innerHTML = '<tr><td colspan="100%" class="text-center text-muted">No data found</td></tr>';
            return;
        }
        
        // Create header row
        const headerRow = document.createElement('tr');
        this.currentColumns.forEach(column => {
            const th = document.createElement('th');
            th.textContent = column.title;
            th.setAttribute('data-sort', column.key);
            th.style.cursor = 'pointer';
            th.onclick = () => this.sortTable(column.key);
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);
        
        // Create data rows
        this.currentData.forEach(issue => {
            const row = UIComponents.createTableRow(issue, this.currentColumns);
            tbody.appendChild(row);
        });
    },
    
    sortTable: (columnKey) => {
        this.currentData.sort((a, b) => {
            const aVal = this.getFieldValue(a, columnKey);
            const bVal = this.getFieldValue(b, columnKey);
            
            if (typeof aVal === 'string' && typeof bVal === 'string') {
                return aVal.localeCompare(bVal);
            }
            
            if (aVal < bVal) return -1;
            if (aVal > bVal) return 1;
            return 0;
        });
        
        this.populateTable();
    },
    
    getFieldValue: (issue, columnKey) => {
        const fields = issue.fields || {};
        
        switch (columnKey) {
            case 'key':
                return issue.key;
            case 'summary':
                return fields.summary || '';
            case 'status':
                return fields.status?.name || '';
            case 'priority':
                return fields.priority?.name || '';
            case 'assignee':
                return fields.assignee?.displayName || '';
            case 'reporter':
                return fields.reporter?.displayName || '';
            case 'created':
                return new Date(fields.created || 0);
            case 'updated':
                return new Date(fields.updated || 0);
            default:
                return fields[columnKey] || '';
        }
    },
    
    exportTable: () => {
        if (this.currentData.length === 0) {
            Utils.showAlert('No data to export', 'warning');
            return;
        }
        
        // Create CSV content
        const headers = this.currentColumns.map(col => col.title);
        const rows = this.currentData.map(issue => {
            return this.currentColumns.map(col => {
                const value = this.getFieldValue(issue, col.key);
                return `"${String(value).replace(/"/g, '""')}"`;
            });
        });
        
        const csvContent = [headers.join(','), ...rows.map(row => row.join(','))].join('\n');
        
        // Download CSV
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `test-data-${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    },
    
    hideTable: () => {
        if (this.currentTable) {
            this.currentTable.style.display = 'none';
        }
    }
};

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    console.log('Xray Test Management Tool initialized');
});
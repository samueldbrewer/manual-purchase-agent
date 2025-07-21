// API Demo Application
class APIDemo {
    constructor() {
        this.baseURL = window.location.origin;
        this.currentModal = null;
        this.currentResponse = null;
        this.currentEndpoint = null;
        
        // Demo configurations for each modal
        this.demoConfigs = {
            partsResolution: {
                title: 'Parts Resolution API',
                method: 'POST',
                url: '/api/parts/resolve',
                defaultRequest: {
                    description: "Bowl Lift Motor",
                    make: "Hobart",
                    model: "HL600",
                    use_database: false,
                    use_manual_search: true,
                    use_web_search: true,
                    save_results: false
                }
            },
            supplierSearch: {
                title: 'Supplier Search API',
                method: 'POST',
                url: '/api/suppliers/search',
                defaultRequest: {
                    part_number: "00-917676",
                    make: "Hobart",
                    model: "HL600",
                    oem_only: false,
                    use_v2: true
                }
            },
            manualSearch: {
                title: 'Manual Search API',
                method: 'POST',
                url: '/api/manuals/search',
                defaultRequest: {
                    make: "Henny Penny",
                    model: "500",
                    manual_type: "technical"
                }
            },
            equipmentEnrichment: {
                title: 'Equipment Enrichment API',
                method: 'POST',
                url: '/api/enrichment/equipment',
                defaultRequest: {
                    make: "Henny Penny",
                    model: "500",
                    year: "2020"
                }
            },
            partsEnrichment: {
                title: 'Parts Enrichment API',
                method: 'POST',
                url: '/api/enrichment/part',
                defaultRequest: {
                    part_number: "00-917676",
                    description: "Bowl Lift Motor",
                    make: "Hobart",
                    model: "HL600"
                }
            }
        };
        
        this.init();
    }

    init() {
        // Add escape key handler
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeModal();
            }
        });

        // Add request editor validation
        document.addEventListener('input', (e) => {
            if (e.target.id === 'requestEditor') {
                this.validateJSON();
            }
        });
    }

    openModal(demoType) {
        const config = this.demoConfigs[demoType];
        if (!config) return;

        this.currentModal = demoType;
        this.currentEndpoint = config;

        // Update modal content
        document.getElementById('modalTitle').textContent = config.title;
        document.getElementById('requestMethod').textContent = config.method;
        document.getElementById('requestUrl').textContent = config.url;
        document.getElementById('requestEditor').value = JSON.stringify(config.defaultRequest, null, 2);

        // Reset response sections
        this.resetResponse();

        // Show modal
        document.getElementById('modalBackdrop').classList.add('show');
        
        // Focus on request editor
        setTimeout(() => {
            document.getElementById('requestEditor').focus();
        }, 300);
    }

    closeModal() {
        document.getElementById('modalBackdrop').classList.remove('show');
        this.currentModal = null;
        this.currentResponse = null;
        this.currentEndpoint = null;
    }

    resetRequest() {
        if (!this.currentModal || !this.currentEndpoint) return;
        
        document.getElementById('requestEditor').value = JSON.stringify(
            this.currentEndpoint.defaultRequest, 
            null, 
            2
        );
        this.validateJSON();
    }

    validateJSON() {
        const editor = document.getElementById('requestEditor');
        const validationMessage = document.getElementById('validationMessage');
        
        try {
            JSON.parse(editor.value);
            editor.classList.remove('error');
            validationMessage.classList.remove('show');
            return true;
        } catch (error) {
            editor.classList.add('error');
            validationMessage.textContent = `Invalid JSON: ${error.message}`;
            validationMessage.classList.add('show');
            return false;
        }
    }

    async executeRequest() {
        if (!this.validateJSON()) return;
        
        const executeBtn = document.getElementById('executeBtn');
        const requestEditor = document.getElementById('requestEditor');
        
        try {
            // Show loading state
            executeBtn.classList.add('loading');
            executeBtn.disabled = true;
            executeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Executing...';
            
            // Parse request
            const requestBody = JSON.parse(requestEditor.value);
            const startTime = Date.now();
            
            // Make API call
            const response = await fetch(this.baseURL + this.currentEndpoint.url, {
                method: this.currentEndpoint.method,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody)
            });
            
            const endTime = Date.now();
            const duration = endTime - startTime;
            
            // Parse response
            const responseText = await response.text();
            let responseData;
            
            try {
                responseData = JSON.parse(responseText);
            } catch {
                responseData = responseText;
            }
            
            this.currentResponse = {
                status: response.status,
                statusText: response.statusText,
                duration,
                data: responseData,
                success: response.ok
            };
            
            // Update UI
            this.displayResponse();
            
        } catch (error) {
            console.error('Request failed:', error);
            this.currentResponse = {
                status: 0,
                statusText: 'Network Error',
                duration: 0,
                data: { error: error.message },
                success: false
            };
            this.displayResponse();
        } finally {
            // Reset button
            executeBtn.classList.remove('loading');
            executeBtn.disabled = false;
            executeBtn.innerHTML = '<i class="fas fa-play"></i> Execute Request';
        }
    }

    displayResponse() {
        if (!this.currentResponse) return;
        
        const responseStatus = document.getElementById('responseStatus');
        const responseViewer = document.getElementById('responseViewer');
        const copyResponseBtn = document.getElementById('copyResponseBtn');
        
        // Update status
        responseStatus.textContent = `HTTP ${this.currentResponse.status} ${this.currentResponse.statusText} - ${this.currentResponse.duration}ms`;
        responseStatus.className = `response-status ${this.currentResponse.success ? 'success' : 'error'}`;
        
        // Update raw response
        if (typeof this.currentResponse.data === 'object') {
            responseViewer.textContent = JSON.stringify(this.currentResponse.data, null, 2);
        } else {
            responseViewer.textContent = this.currentResponse.data;
        }
        
        // Enable copy button
        copyResponseBtn.disabled = false;
        
        // Update formatted response
        this.displayFormattedResponse();
    }

    displayFormattedResponse() {
        const formattedContainer = document.getElementById('formattedResponse');
        
        if (!this.currentResponse || !this.currentResponse.success) {
            formattedContainer.innerHTML = `
                <div class="placeholder">
                    <i class="fas fa-exclamation-triangle"></i>
                    Request failed or returned an error
                </div>
            `;
            return;
        }
        
        const data = this.currentResponse.data;
        let formattedHTML = '';
        
        // Format based on endpoint type
        switch (this.currentModal) {
            case 'partsResolution':
                formattedHTML = this.formatPartsResolutionResponse(data);
                break;
            case 'supplierSearch':
                formattedHTML = this.formatSupplierSearchResponse(data);
                break;
            case 'manualSearch':
                formattedHTML = this.formatManualSearchResponse(data);
                break;
            case 'equipmentEnrichment':
                formattedHTML = this.formatEnrichmentResponse(data);
                break;
            case 'partsEnrichment':
                formattedHTML = this.formatEnrichmentResponse(data);
                break;
            default:
                formattedHTML = '<div class="placeholder"><i class="fas fa-info-circle"></i> Formatted view not available</div>';
        }
        
        formattedContainer.innerHTML = formattedHTML;
    }

    formatPartsResolutionResponse(data) {
        const result = data.recommended_result;
        if (!result) return '<div class="placeholder">No recommended result found</div>';
        
        return `
            <div class="formatted-item">
                <i class="fas fa-check-circle"></i>
                <span>Found OEM Part: <strong class="formatted-value">${result.oem_part_number || 'N/A'}</strong></span>
            </div>
            <div class="formatted-item">
                <i class="fas fa-bullseye"></i>
                <span>Confidence: <strong class="formatted-value">${Math.round((result.confidence || 0) * 100)}%</strong></span>
            </div>
            <div class="formatted-item">
                <i class="fas fa-search"></i>
                <span>Method: <strong class="formatted-value">${result.selection_metadata?.selected_from || 'Unknown'}</strong></span>
            </div>
            <div class="formatted-item">
                <i class="fas fa-clock"></i>
                <span>Response Time: <strong class="formatted-value">${this.currentResponse.duration}ms</strong></span>
            </div>
        `;
    }

    formatSupplierSearchResponse(data) {
        const suppliers = data.suppliers || [];
        return `
            <div class="formatted-item">
                <i class="fas fa-store"></i>
                <span>Suppliers Found: <strong class="formatted-value">${suppliers.length}</strong></span>
            </div>
            <div class="formatted-item">
                <i class="fas fa-star"></i>
                <span>AI Ranking: <strong class="formatted-value">${data.ai_ranked ? 'Enabled' : 'Disabled'}</strong></span>
            </div>
            <div class="formatted-item">
                <i class="fas fa-crown"></i>
                <span>Top Supplier: <strong class="formatted-value">${suppliers[0]?.domain || 'N/A'}</strong></span>
            </div>
            <div class="formatted-item">
                <i class="fas fa-clock"></i>
                <span>Response Time: <strong class="formatted-value">${this.currentResponse.duration}ms</strong></span>
            </div>
        `;
    }

    formatManualSearchResponse(data) {
        const results = data.results || [];
        return `
            <div class="formatted-item">
                <i class="fas fa-book"></i>
                <span>Manuals Found: <strong class="formatted-value">${results.length}</strong></span>
            </div>
            <div class="formatted-item">
                <i class="fas fa-check-circle"></i>
                <span>Verified Manuals: <strong class="formatted-value">${results.filter(r => r.model_verified).length}</strong></span>
            </div>
            <div class="formatted-item">
                <i class="fas fa-file-pdf"></i>
                <span>Total Pages: <strong class="formatted-value">${results.reduce((sum, r) => sum + (r.pages || 0), 0)}</strong></span>
            </div>
            <div class="formatted-item">
                <i class="fas fa-clock"></i>
                <span>Response Time: <strong class="formatted-value">${this.currentResponse.duration}ms</strong></span>
            </div>
        `;
    }

    formatEnrichmentResponse(data) {
        const enrichmentData = data.data || {};
        const videos = enrichmentData.videos || [];
        const articles = enrichmentData.articles || [];
        const images = enrichmentData.images || [];
        
        return `
            <div class="formatted-item">
                <i class="fas fa-video"></i>
                <span>Videos Found: <strong class="formatted-value">${videos.length}</strong></span>
            </div>
            <div class="formatted-item">
                <i class="fas fa-newspaper"></i>
                <span>Articles Found: <strong class="formatted-value">${articles.length}</strong></span>
            </div>
            <div class="formatted-item">
                <i class="fas fa-image"></i>
                <span>Images Found: <strong class="formatted-value">${images.length}</strong></span>
            </div>
            <div class="formatted-item">
                <i class="fas fa-search"></i>
                <span>Query: <strong class="formatted-value">${data.query || 'N/A'}</strong></span>
            </div>
            <div class="formatted-item">
                <i class="fas fa-clock"></i>
                <span>Response Time: <strong class="formatted-value">${this.currentResponse.duration}ms</strong></span>
            </div>
        `;
    }

    copyAsCurl() {
        if (!this.currentEndpoint) return;
        
        const requestBody = document.getElementById('requestEditor').value;
        const curlCommand = `curl -X ${this.currentEndpoint.method} "${window.location.origin}${this.currentEndpoint.url}" \\
  -H "Content-Type: application/json" \\
  -d '${requestBody}'`;
        
        navigator.clipboard.writeText(curlCommand).then(() => {
            this.showToast('cURL command copied to clipboard!');
        }).catch(() => {
            console.log('cURL command:', curlCommand);
            this.showToast('cURL command logged to console');
        });
    }

    copyResponse() {
        if (!this.currentResponse) return;
        
        const responseText = typeof this.currentResponse.data === 'object' 
            ? JSON.stringify(this.currentResponse.data, null, 2)
            : this.currentResponse.data;
        
        navigator.clipboard.writeText(responseText).then(() => {
            this.showToast('Response copied to clipboard!');
        }).catch(() => {
            console.log('Response:', responseText);
            this.showToast('Response logged to console');
        });
    }

    resetResponse() {
        document.getElementById('responseStatus').textContent = '';
        document.getElementById('responseStatus').className = 'response-status';
        document.getElementById('responseViewer').textContent = 'Execute a request to see the response...';
        document.getElementById('copyResponseBtn').disabled = true;
        document.getElementById('formattedResponse').innerHTML = `
            <div class="placeholder">
                <i class="fas fa-info-circle"></i>
                Execute a request to see the formatted business value
            </div>
        `;
    }

    showToast(message) {
        // Simple toast notification
        const toast = document.createElement('div');
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #28a745;
            color: white;
            padding: 12px 20px;
            border-radius: 6px;
            z-index: 10000;
            font-size: 14px;
            animation: slideInRight 0.3s ease-out;
        `;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }
}

// Global functions for HTML onclick handlers
let demoApp;

document.addEventListener('DOMContentLoaded', () => {
    demoApp = new APIDemo();
});

function openModal(demoType) {
    demoApp.openModal(demoType);
}

function closeModal() {
    demoApp.closeModal();
}

function resetRequest() {
    demoApp.resetRequest();
}

function executeRequest() {
    demoApp.executeRequest();
}

function copyAsCurl() {
    demoApp.copyAsCurl();
}

function copyResponse() {
    demoApp.copyResponse();
}

// Add slide in animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(300px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
`;
document.head.appendChild(style);
// ===== CACHE BUSTING =====
// Clear caches but don't break functionality
(function() {
    console.log('Clearing caches...');
    
    // Clear caches in background without blocking
    if ('caches' in window) {
        caches.keys().then(names => {
            names.forEach(name => {
                caches.delete(name);
            });
            console.log('✅ Caches cleared');
        }).catch(err => {
            console.log('Cache clear error:', err);
        });
    }
})();

// ===== APP STATE & CONFIGURATION =====
class AIPartsAgent {
    constructor() {
        this.baseURL = window.location.origin;
        this.currentSearch = null;
        this.currentPart = null;
        this.currentSuppliers = [];
        this.currentScreen = 'main';
        this.defaultBillingProfile = null;
        this.similarParts = null;
        this.currentGenericResults = null;
        
        // Progress tracking
        this.steps = ['model', 'manuals', 'part', 'suppliers'];
        this.currentStep = -1;
        
        this.init();
    }

    async init() {
        this.bindEvents();
        this.setupIntersectionObserver();
        this.setupStickyProgress();
        
        this.addLog('info', 'System', 'PartsPro initialized successfully');
        
        // Initialize billing profile with dummy data
        this.initializeBillingProfile();
    }

    // ===== EVENT BINDING =====
    bindEvents() {
        const searchForm = document.getElementById('searchForm');
        if (!searchForm) {
            console.error('Search form not found!');
            return;
        }
        console.log('Binding submit event to search form');
        searchForm.addEventListener('submit', (e) => {
            console.log('Form submitted');
            this.handleSearch(e);
        });
        
        // Add smooth scrolling for better UX
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-scroll-to]')) {
                const target = document.getElementById(e.target.dataset.scrollTo);
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }
        });
    }

    setupIntersectionObserver() {
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('fade-in');
                    }
                });
            },
            { threshold: 0.1, rootMargin: '50px' }
        );

        // Observe all cards
        document.querySelectorAll('.card').forEach(card => {
            observer.observe(card);
        });
    }

    setupStickyProgress() {
        const progressSection = document.getElementById('progressSection');
        if (!progressSection) return;

        let lastScroll = 0;
        let ticking = false;

        const updateSticky = () => {
            const scrollY = window.scrollY;
            const rect = progressSection.getBoundingClientRect();
            
            // Add stuck class when the progress bar reaches the top
            if (rect.top <= 0) {
                progressSection.classList.add('stuck');
            } else {
                progressSection.classList.remove('stuck');
            }
            
            lastScroll = scrollY;
            ticking = false;
        };

        // Throttle scroll events for performance
        window.addEventListener('scroll', () => {
            if (!ticking) {
                window.requestAnimationFrame(updateSticky);
                ticking = true;
            }
        });
    }

    // ===== MAIN SEARCH FLOW =====
    async handleSearch(e) {
        console.log('handleSearch called');
        e.preventDefault();
        e.stopPropagation();
        
        const make = document.getElementById('make').value.trim();
        const model = document.getElementById('model').value.trim();
        const partName = document.getElementById('partName').value.trim();
        
        console.log('Search values:', { make, model, partName });
        
        if (!make || !model || !partName) {
            console.log('Missing required fields');
            return;
        }

        this.currentSearch = { make, model, partName };
        this.resetUI();
        this.showProgress();

        try {
            // Execute the complete flow
            await this.executeSearchFlow(make, model, partName);
        } catch (error) {
            console.error('Search flow error:', error);
            this.showError('An error occurred during the search. Please try again.');
        }
    }

    async executeSearchFlow(make, model, partName) {
        // Fire off all initial requests simultaneously
        console.log('🚀 Starting parallel API requests...');
        
        // Immediately show all sections with loading states
        this.showLoadingStates();
        
        // Start all requests at once
        const modelEnrichmentPromise = this.getModelEnrichment(make, model);
        const manualsPromise = this.getManuals(make, model);
        const partResolutionPromise = this.resolvePart(partName, make, model);
        
        // Set initial steps as active/loading
        this.setStepLoading('model');
        this.setStepLoading('manuals'); 
        this.setStepLoading('part');
        this.setStepLoading('suppliers');
        
        // Handle model enrichment as soon as it completes (independent of everything else)
        modelEnrichmentPromise.then(modelInfo => {
            console.log('✅ Model enrichment completed (independent of parts/manuals)');
            // Add small delay to show independence
            setTimeout(() => {
                this.updateModelInfo(modelInfo);
                this.setStepCompleted('model');
            }, 500);
        }).catch(error => {
            console.error('Model enrichment error:', error);
            this.setStepError('model');
        });
        
        // Handle manuals as soon as they complete (independent of part resolution)
        manualsPromise.then(manuals => {
            console.log('✅ Manuals completed (independent of part resolution)');
            // Add small delay to show independence
            setTimeout(() => {
                this.updateManuals(manuals);
                this.setStepCompleted('manuals');
            }, 800);
        }).catch(error => {
            console.error('Manuals error:', error);
            this.setStepError('manuals');
        });
        
        // Part resolution comes first before suppliers
        try {
            const partResult = await partResolutionPromise;
            console.log('✅ Part resolution completed');
            
            this.updatePartInfo(partResult);
            this.setStepCompleted('part');
            
            // Now start supplier search (depends on part result)
            console.log('🔍 Starting supplier search...');
            const suppliersResult = await this.getSuppliers(partResult);
            console.log('✅ Supplier search completed');
            
            this.updateSuppliers(suppliersResult);
            this.setStepCompleted('suppliers');
            
        } catch (error) {
            console.error('Part resolution or supplier search error:', error);
            this.setStepError('part');
            this.setStepError('suppliers');
        }
    }

    // ===== API METHODS =====
    async getModelEnrichment(make, model) {
        try {
            const response = await fetch(`${this.baseURL}/api/enrichment/equipment`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ make, model })
            });
            
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Model enrichment error:', error);
            return { 
                success: false, 
                error: error.message,
                equipment: {
                    name: `${make} ${model}`,
                    description: 'Equipment information not available',
                    specifications: {},
                    image_url: null
                }
            };
        }
    }

    async getManuals(make, model) {
        try {
            const response = await fetch(`${this.baseURL}/api/manuals/search`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ make, model, manual_type: 'technical manual' })
            });
            
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Manuals error:', error);
            return { success: false, error: error.message, manuals: [] };
        }
    }

    async resolvePart(description, make, model) {
        try {
            const response = await fetch(`${this.baseURL}/api/parts/resolve`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    description, 
                    make, 
                    model,
                    use_database: false,
                    use_manual_search: true,
                    use_web_search: true,
                    save_results: false
                })
            });
            
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Part resolution error:', error);
            return { success: false, error: error.message };
        }
    }

    async getSuppliers(partResult) {
        try {
            let partNumber = 'unknown';
            
            if (partResult && partResult.recommended_result) {
                partNumber = partResult.recommended_result.oem_part_number || 'unknown';
            }
            
            const response = await fetch(`${this.baseURL}/api/suppliers/search`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    part_number: partNumber,
                    part_description: this.currentSearch.partName
                })
            });
            
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Suppliers error:', error);
            return { success: false, error: error.message, suppliers: [] };
        }
    }

    // ===== UI UPDATE METHODS =====
    resetUI() {
        // Hide all sections
        document.getElementById('progressSection').classList.add('hidden');
        document.getElementById('modelSection').classList.add('hidden');
        document.getElementById('manualsSection').classList.add('hidden');
        document.getElementById('partSection').classList.add('hidden');
        document.getElementById('suppliersSection').classList.add('hidden');
        
        // Reset progress
        this.currentStep = -1;
        document.querySelectorAll('.progress-step').forEach(step => {
            step.classList.remove('active', 'completed', 'loading', 'error');
        });
    }

    showProgress() {
        document.getElementById('progressSection').classList.remove('hidden');
    }

    showLoadingStates() {
        // Show all sections immediately with loading states
        document.getElementById('modelSection').classList.remove('hidden');
        document.getElementById('manualsSection').classList.remove('hidden');
        document.getElementById('partSection').classList.remove('hidden');
        document.getElementById('suppliersSection').classList.remove('hidden');
        
        // Show loading placeholders
        this.showModelLoading();
        this.showManualsLoading();
        this.showPartLoading();
        this.showSuppliersLoading();
    }

    showModelLoading() {
        const imageContainer = document.querySelector('.model-image-container');
        const image = document.getElementById('modelImage');
        const loading = document.querySelector('.model-image-loading');
        
        if (imageContainer && image && loading) {
            image.style.display = 'none';
            loading.style.display = 'block';
        }
        
        document.getElementById('modelName').textContent = 'Loading equipment information...';
        document.getElementById('modelDescription').textContent = '';
        document.getElementById('modelSpecs').innerHTML = '';
    }

    showManualsLoading() {
        const grid = document.getElementById('manualsGrid');
        if (grid) {
            grid.innerHTML = '<div class="loading-placeholder">Searching for technical manuals...</div>';
        }
    }

    showPartLoading() {
        const imageContainer = document.querySelector('.part-image-container');
        const image = document.getElementById('partImage');
        const loading = document.querySelector('.part-image-loading');
        
        if (imageContainer && image && loading) {
            image.style.display = 'none';
            loading.style.display = 'block';
        }
        
        document.getElementById('partNumber').textContent = 'Resolving OEM part number...';
        document.getElementById('partDescription').textContent = '';
        document.getElementById('partDetails').innerHTML = '';
    }

    showSuppliersLoading() {
        const list = document.getElementById('suppliersList');
        if (list) {
            list.innerHTML = '<div class="loading-placeholder">Finding suppliers...</div>';
        }
    }

    updateModelInfo(modelInfo) {
        if (modelInfo && modelInfo.success && modelInfo.equipment) {
            const equipment = modelInfo.equipment;
            
            document.getElementById('modelName').textContent = equipment.name || `${this.currentSearch.make} ${this.currentSearch.model}`;
            document.getElementById('modelDescription').textContent = equipment.description || 'Equipment information retrieved';
            
            // Update image
            const image = document.getElementById('modelImage');
            const loading = document.querySelector('.model-image-loading');
            
            if (equipment.image_url) {
                image.src = equipment.image_url;
                image.alt = equipment.name;
                image.onload = () => {
                    image.style.display = 'block';
                    loading.style.display = 'none';
                };
                image.onerror = () => {
                    image.style.display = 'none';
                    loading.style.display = 'none';
                };
            } else {
                image.style.display = 'none';
                loading.style.display = 'none';
            }
            
            // Update specs
            if (equipment.specifications) {
                const specsHtml = Object.entries(equipment.specifications)
                    .map(([key, value]) => `<div class="spec-item"><strong>${key}:</strong> ${value}</div>`)
                    .join('');
                document.getElementById('modelSpecs').innerHTML = specsHtml;
            }
        } else {
            // Fallback display
            document.getElementById('modelName').textContent = `${this.currentSearch.make} ${this.currentSearch.model}`;
            document.getElementById('modelDescription').textContent = 'Equipment information not available';
            
            const image = document.getElementById('modelImage');
            const loading = document.querySelector('.model-image-loading');
            image.style.display = 'none';
            loading.style.display = 'none';
        }
    }

    updateManuals(manualsResult) {
        const grid = document.getElementById('manualsGrid');
        
        if (manualsResult && manualsResult.success && manualsResult.manuals && manualsResult.manuals.length > 0) {
            const manualsHtml = manualsResult.manuals.map(manual => `
                <div class="manual-card" onclick="viewPdf('${manual.url}', '${manual.title.replace(/'/g, "\\'")}')">
                    <div class="manual-icon">
                        <i class="fas fa-file-pdf"></i>
                    </div>
                    <div class="manual-info">
                        <h4 class="manual-title">${manual.title}</h4>
                        <p class="manual-snippet">${manual.snippet || 'Technical manual document'}</p>
                        <span class="manual-type">PDF Document</span>
                    </div>
                </div>
            `).join('');
            
            grid.innerHTML = manualsHtml;
        } else {
            grid.innerHTML = `
                <div class="no-results">
                    <i class="fas fa-search"></i>
                    <p>No technical manuals found for ${this.currentSearch.make} ${this.currentSearch.model}</p>
                </div>
            `;
        }
    }

    updatePartInfo(partResult) {
        this.currentPart = partResult;
        
        if (partResult && partResult.success && partResult.recommended_result) {
            const part = partResult.recommended_result;
            
            document.getElementById('partNumber').textContent = part.oem_part_number || 'Part number not found';
            document.getElementById('partDescription').textContent = part.description || this.currentSearch.partName;
            
            // Show verification status
            const verificationEl = document.getElementById('partVerification');
            if (part.oem_part_number && part.oem_part_number !== 'NOT_FOUND') {
                verificationEl.innerHTML = `
                    <i class="fas fa-check-circle" style="color: #10b981;"></i>
                    <span style="color: #10b981;">Verified OEM Part</span>
                `;
                
                // Show verified parts actions if we have them
                this.showVerifiedPartsActions(partResult);
            } else {
                verificationEl.innerHTML = `
                    <i class="fas fa-exclamation-triangle" style="color: #f59e0b;"></i>
                    <span style="color: #f59e0b;">Part Not Verified</span>
                `;
                
                // Show similar parts if available
                this.showSimilarParts(partResult);
            }
            
            // Update part details
            const details = [];
            if (part.confidence) {
                details.push(`Confidence: ${Math.round(part.confidence * 100)}%`);
            }
            if (part.selection_metadata) {
                details.push(`Method: ${part.selection_metadata.selected_from || 'Unknown'}`);
            }
            
            document.getElementById('partDetails').innerHTML = details.length > 0 ? 
                `<div class="part-metadata">${details.join(' • ')}</div>` : '';
            
            // Hide part image loading
            const image = document.getElementById('partImage');
            const loading = document.querySelector('.part-image-loading');
            image.style.display = 'none';
            loading.style.display = 'none';
            
        } else {
            document.getElementById('partNumber').textContent = 'Part not found';
            document.getElementById('partDescription').textContent = this.currentSearch.partName;
            document.getElementById('partDetails').innerHTML = '<div class="error">Unable to resolve OEM part number</div>';
            
            const verificationEl = document.getElementById('partVerification');
            verificationEl.innerHTML = `
                <i class="fas fa-times-circle" style="color: #ef4444;"></i>
                <span style="color: #ef4444;">Resolution Failed</span>
            `;
        }
    }

    showVerifiedPartsActions(partResult) {
        const actionsEl = document.getElementById('verifiedPartsActions');
        const alternateSection = document.getElementById('alternatePartsSection');
        const genericSection = document.getElementById('genericPartsSection');
        
        // Check if we have alternate parts
        if (partResult.results && partResult.results.manual_search && 
            partResult.results.manual_search.alternate_parts && 
            partResult.results.manual_search.alternate_parts.length > 0) {
            
            const alternateCount = partResult.results.manual_search.alternate_parts.length;
            document.getElementById('alternatePartsCount').textContent = alternateCount;
            alternateSection.style.display = 'block';
        } else {
            alternateSection.style.display = 'none';
        }
        
        // Always show generic parts option for verified parts
        genericSection.style.display = 'block';
        actionsEl.style.display = 'block';
    }

    showSimilarParts(partResult) {
        // Hide verified actions
        document.getElementById('verifiedPartsActions').style.display = 'none';
        
        // Show similar parts section for unverified parts
        const similarSection = document.getElementById('similarPartsSection');
        const similarList = document.getElementById('similarPartsList');
        
        if (partResult && partResult.results) {
            const allParts = [];
            
            // Collect parts from different search methods
            if (partResult.results.manual_search && partResult.results.manual_search.parts) {
                allParts.push(...partResult.results.manual_search.parts);
            }
            if (partResult.results.ai_web_search && partResult.results.ai_web_search.parts) {
                allParts.push(...partResult.results.ai_web_search.parts);
            }
            
            if (allParts.length > 0) {
                const similarHtml = allParts.slice(0, 3).map(part => `
                    <div class="similar-part-item" style="padding: 0.75rem; background: var(--glass-bg); border-radius: 6px; border: 1px solid var(--glass-border); cursor: pointer;"
                         onclick="app.selectSimilarPart('${part.oem_part_number}', '${part.description}')">
                        <div style="font-weight: 600; color: var(--text-primary);">${part.oem_part_number}</div>
                        <div style="font-size: 0.875rem; color: var(--text-muted); margin-top: 0.25rem;">${part.description}</div>
                        ${part.confidence ? `<div style="font-size: 0.75rem; color: var(--primary-color); margin-top: 0.25rem;">Confidence: ${Math.round(part.confidence * 100)}%</div>` : ''}
                    </div>
                `).join('');
                
                similarList.innerHTML = similarHtml;
                similarSection.style.display = 'block';
            } else {
                similarSection.style.display = 'none';
            }
        } else {
            similarSection.style.display = 'none';
        }
    }

    selectSimilarPart(partNumber, description) {
        // Update the current part display
        document.getElementById('partNumber').textContent = partNumber;
        document.getElementById('partDescription').textContent = description;
        
        // Update verification status
        const verificationEl = document.getElementById('partVerification');
        verificationEl.innerHTML = `
            <i class="fas fa-check-circle" style="color: #10b981;"></i>
            <span style="color: #10b981;">Alternative Part Selected</span>
        `;
        
        // Hide similar parts and show verified actions
        document.getElementById('similarPartsSection').style.display = 'none';
        document.getElementById('verifiedPartsActions').style.display = 'block';
        document.getElementById('genericPartsSection').style.display = 'block';
        
        // Update current part
        this.currentPart = {
            success: true,
            recommended_result: {
                oem_part_number: partNumber,
                description: description,
                confidence: 0.8
            }
        };
        
        this.addLog('info', 'User Action', `Selected alternative part: ${partNumber}`);
        
        // Trigger supplier search with new part
        this.refreshSuppliers();
    }

    async refreshSuppliers() {
        this.setStepLoading('suppliers');
        this.showSuppliersLoading();
        
        try {
            const suppliersResult = await this.getSuppliers(this.currentPart);
            this.updateSuppliers(suppliersResult);
            this.setStepCompleted('suppliers');
        } catch (error) {
            console.error('Supplier refresh error:', error);
            this.setStepError('suppliers');
        }
    }

    updateSuppliers(suppliersResult) {
        this.currentSuppliers = suppliersResult;
        const list = document.getElementById('suppliersList');
        
        if (suppliersResult && suppliersResult.success && suppliersResult.suppliers && suppliersResult.suppliers.length > 0) {
            const suppliersHtml = suppliersResult.suppliers.map(supplier => `
                <div class="supplier-card">
                    <div class="supplier-info">
                        <h4 class="supplier-name">${supplier.name || 'Unknown Supplier'}</h4>
                        <p class="supplier-title">${supplier.title || 'Product listing'}</p>
                        <a href="${supplier.url}" target="_blank" class="supplier-url">${supplier.url}</a>
                    </div>
                    <div class="supplier-actions">
                        <button class="supplier-visit-btn" onclick="window.open('${supplier.url}', '_blank')">
                            <i class="fas fa-external-link-alt"></i>
                            Visit Site
                        </button>
                        <div class="supplier-rating" title="Supplier Rating">
                            <i class="fas fa-star"></i>
                            <span>${supplier.rating ? Math.round(supplier.rating * 100) : 'N/A'}%</span>
                        </div>
                    </div>
                </div>
            `).join('');
            
            list.innerHTML = suppliersHtml;
        } else {
            list.innerHTML = `
                <div class="no-results">
                    <i class="fas fa-store-slash"></i>
                    <p>No suppliers found for this part</p>
                </div>
            `;
        }
    }

    // ===== PROGRESS METHODS =====
    setStepLoading(stepName) {
        const step = document.querySelector(`[data-step="${stepName}"]`);
        if (step) {
            step.classList.remove('completed', 'error');
            step.classList.add('loading');
        }
    }

    setStepCompleted(stepName) {
        const step = document.querySelector(`[data-step="${stepName}"]`);
        if (step) {
            step.classList.remove('loading', 'error');
            step.classList.add('completed');
        }
    }

    setStepError(stepName) {
        const step = document.querySelector(`[data-step="${stepName}"]`);
        if (step) {
            step.classList.remove('loading', 'completed');
            step.classList.add('error');
        }
    }

    // ===== UTILITY METHODS =====
    showError(message) {
        console.error(message);
        // Could implement a proper error display here
        alert(message);
    }

    addLog(level, category, message, data = null) {
        const timestamp = new Date().toLocaleTimeString();
        console.log(`[${timestamp}] ${level.toUpperCase()}:${category}:${message}`, data || '');
        
        // Could implement proper logging UI here
    }

    initializeBillingProfile() {
        this.defaultBillingProfile = {
            firstName: "John",
            lastName: "Doe", 
            email: "john.doe@example.com",
            phone: "555-0123",
            company: "Test Company",
            address: "123 Main St",
            address2: "",
            city: "Anytown",
            state: "Illinois",
            stateAbr: "IL",
            zip: "60601",
            country: "United States",
            billFirstName: "",
            billLastName: "",
            billAddress: "",
            billCity: "",
            billState: "",
            billStateAbr: "",
            billZip: "",
            cardNumber: "4111111111111111",
            cardExpMonth: "12",
            cardExpYear: "2030",
            cardCvv: "123",
            cardName: "John Doe"
        };
    }
}

// ===== GLOBAL FUNCTIONS =====
function viewPdf(url, title) {
    const modal = document.getElementById('pdfModal');
    const frame = document.getElementById('pdfFrame');
    const titleEl = document.getElementById('pdfTitle');
    
    titleEl.textContent = title || 'Manual Viewer';
    frame.src = url;
    modal.classList.remove('hidden');
}

function closePdfModal() {
    const modal = document.getElementById('pdfModal');
    const frame = document.getElementById('pdfFrame');
    
    modal.classList.add('hidden');
    frame.src = '';
}

// ===== APP INITIALIZATION =====
let app;
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing app...');
    app = new AIPartsAgent();
    window.app = app; // Make globally accessible
});

// Global error handler
window.addEventListener('error', (e) => {
    console.error('Global error:', e.error);
});

window.addEventListener('unhandledrejection', (e) => {
    console.error('Unhandled promise rejection:', e.reason);
});
/**
 * ImageScraper Pro - Main JavaScript with Real-time Progress Tracking
 * Enhanced with modern features and accessibility
 * 
 * 🎯 CRAFTED BY HISHAM (@hisham1665) - THE CODE ARCHITECT 🏗️
 * 🚀 Where Innovation Meets Excellence ✨
 * 🧙‍♂️ Every line of code tells a story of passion and precision 
 */

// DOM Elements
let quantityInput, launchBtn, spinner, scrapeForm;
let progressContainer, progressBar, progressText, currentEngineText, imagesFoundText;
let eventSource = null;
let currentSessionId = null;

// 🎨 Developer signature in the console - because why not? 
console.log(`
🌟 ═══════════════════════════════════════════════════════════ 🌟
    ██╗  ██╗██╗███████╗██╗  ██╗ █████╗ ███╗   ███╗
    ██║  ██║██║██╔════╝██║  ██║██╔══██╗████╗ ████║
    ███████║██║███████╗███████║███████║██╔████╔██║
    ██╔══██║██║╚════██║██╔══██║██╔══██║██║╚██╔╝██║
    ██║  ██║██║███████║██║  ██║██║  ██║██║ ╚═╝ ██║
    ╚═╝  ╚═╝╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝
🌟 ═══════════════════════════════════════════════════════════ 🌟
    
    🎯 THE MASTER DEVELOPER BEHIND THIS MAGIC
    🚀 GitHub: @hisham1665
    💎 Specializing in: Full-Stack Innovation
    🔥 This app is just a glimpse of the possibilities!
    
    Want to hire the wizard? Let's build something amazing! ✨
`);

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeElements();
    setupEventListeners();
    createFloatingParticles();
    setupAccessibility();
    createProgressUI();
    
    // 🥚 Secret Easter egg: Press Ctrl+H+I+S+H+A+M for surprise!
    let keySequence = [];
    const secretKeys = ['h', 'i', 's', 'h', 'a', 'm'];
    let isCtrlPressed = false;
    
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey) {
            isCtrlPressed = true;
            if (secretKeys.includes(e.key.toLowerCase())) {
                keySequence.push(e.key.toLowerCase());
                
                if (keySequence.length === secretKeys.length && 
                    keySequence.join('') === secretKeys.join('')) {
                    
                    // EASTER EGG ACTIVATED! 🎉
                    const body = document.body;
                    body.style.animation = 'rainbow-pulse 5s infinite';
                    
                    const style = document.createElement('style');
                    style.textContent = `
                        @keyframes rainbow-pulse {
                            0% { filter: hue-rotate(0deg) brightness(1); }
                            25% { filter: hue-rotate(90deg) brightness(1.2); }
                            50% { filter: hue-rotate(180deg) brightness(1); }
                            75% { filter: hue-rotate(270deg) brightness(1.2); }
                            100% { filter: hue-rotate(360deg) brightness(1); }
                        }
                    `;
                    document.head.appendChild(style);
                    
                    setTimeout(() => {
                        alert('🎊 ULTIMATE EASTER EGG UNLOCKED! 🎊\\n\\n🧙‍♂️ You discovered the secret combination!\\n\\nThis masterpiece was crafted by:\\n🎯 HISHAM (@hisham1665)\\n🚀 The Digital Innovation Wizard\\n\\n✨ Ready to build something extraordinary together? ✨');
                        body.style.animation = '';
                    }, 5000);
                    
                    keySequence = [];
                }
                
                // Reset if sequence gets too long
                if (keySequence.length > secretKeys.length) {
                    keySequence = [e.key.toLowerCase()];
                }
            }
        } else {
            isCtrlPressed = false;
            keySequence = [];
        }
    });
    
    document.addEventListener('keyup', function(e) {
        if (!e.ctrlKey) {
            isCtrlPressed = false;
        }
    });
});

/**
 * Initialize DOM elements
 */
function initializeElements() {
    quantityInput = document.getElementById('quantity');
    launchBtn = document.getElementById('launchBtn');
    spinner = document.getElementById('spinner');
    scrapeForm = document.getElementById('scrapeForm');
}

/**
 * Create progress UI components
 */
function createProgressUI() {
    const mainCard = document.querySelector('.main-card');
    if (!mainCard) return;
    
    // Create progress container
    progressContainer = document.createElement('div');
    progressContainer.className = 'progress-container';
    progressContainer.style.cssText = `
        display: none;
        margin-top: 2rem;
        padding: 2rem;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    `;
    
    // Progress bar container
    const progressBarContainer = document.createElement('div');
    progressBarContainer.style.cssText = `
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        height: 8px;
        margin: 1rem 0;
        overflow: hidden;
    `;
    
    // Progress bar
    progressBar = document.createElement('div');
    progressBar.style.cssText = `
        background: linear-gradient(90deg, #ff006e, #3a86ff);
        height: 100%;
        width: 0%;
        transition: width 0.3s ease;
        border-radius: 10px;
    `;
    
    // Progress text
    progressText = document.createElement('div');
    progressText.style.cssText = `
        color: #ffffff;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        text-align: center;
    `;
    
    // Current engine text
    currentEngineText = document.createElement('div');
    currentEngineText.style.cssText = `
        color: #aaa;
        font-size: 0.9rem;
        text-align: center;
        margin-bottom: 1rem;
    `;
    
    // Images found counter
    imagesFoundText = document.createElement('div');
    imagesFoundText.style.cssText = `
        color: #ff006e;
        font-size: 1.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
    `;
    
    // Cancel button
    const cancelBtn = document.createElement('button');
    cancelBtn.textContent = 'Cancel';
    cancelBtn.className = 'cancel-btn';
    cancelBtn.style.cssText = `
        background: rgba(255, 107, 107, 0.8);
        border: none;
        border-radius: 10px;
        color: white;
        padding: 0.8rem 1.5rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        margin-top: 1rem;
        width: 100%;
    `;
    
    cancelBtn.addEventListener('click', cancelScraping);
    
    // Assemble progress UI
    progressBarContainer.appendChild(progressBar);
    progressContainer.appendChild(progressText);
    progressContainer.appendChild(currentEngineText);
    progressContainer.appendChild(imagesFoundText);
    progressContainer.appendChild(progressBarContainer);
    progressContainer.appendChild(cancelBtn);
    
    mainCard.appendChild(progressContainer);
}

/**
 * Show progress UI
 */
function showProgressUI() {
    if (progressContainer) {
        progressContainer.style.display = 'block';
        progressContainer.style.animation = 'slideIn 0.3s ease';
    }
    
    // Hide form
    const form = document.getElementById('scrapeForm');
    if (form) {
        form.style.display = 'none';
    }
}

/**
 * Hide progress UI
 */
function hideProgressUI() {
    if (progressContainer) {
        progressContainer.style.display = 'none';
    }
    
    // Show form
    const form = document.getElementById('scrapeForm');
    if (form) {
        form.style.display = 'block';
    }
}

/**
 * Update progress display
 */
function updateProgressDisplay(data) {
    if (!data) return;
    
    const { status, message, images_found = 0, total_target = 0, current_engine = '' } = data;
    
    // Update progress text
    if (progressText) {
        progressText.textContent = message || 'Processing...';
    }
    
    // Update current engine
    if (currentEngineText) {
        currentEngineText.textContent = current_engine ? 
            `Currently searching: ${current_engine.charAt(0).toUpperCase() + current_engine.slice(1)}` : 
            'Multi-engine search in progress...';
    }
    
    // Update images found counter
    if (imagesFoundText) {
        imagesFoundText.textContent = `${images_found} / ${total_target} images found`;
    }
    
    // Update progress bar
    if (progressBar && total_target > 0) {
        const percentage = Math.min((images_found / total_target) * 100, 100);
        progressBar.style.width = `${percentage}%`;
    }
    
    // Handle completion
    if (status === 'completed') {
        setTimeout(() => {
            window.location.href = `/results/${currentSessionId}`;
        }, 1500);
    } else if (status === 'error') {
        setTimeout(() => {
            hideProgressUI();
            setLoadingState(false);
            alert('Error: ' + message);
        }, 2000);
    }
}

/**
 * Start progress tracking
 */
function startProgressTracking(sessionId) {
    currentSessionId = sessionId;
    
    if (eventSource) {
        eventSource.close();
    }
    
    eventSource = new EventSource(`/progress/${sessionId}`);
    
    eventSource.onmessage = function(event) {
        try {
            const data = JSON.parse(event.data);
            updateProgressDisplay(data);
        } catch (error) {
            console.error('Error parsing progress data:', error);
        }
    };
    
    eventSource.onerror = function(error) {
        console.error('EventSource error:', error);
        // Retry connection after a delay
        setTimeout(() => {
            if (currentSessionId) {
                startProgressTracking(currentSessionId);
            }
        }, 2000);
    };
}

/**
 * Cancel scraping
 */
function cancelScraping() {
    if (eventSource) {
        eventSource.close();
        eventSource = null;
    }
    
    currentSessionId = null;
    hideProgressUI();
    setLoadingState(false);
    
    announceToScreenReader('Scraping cancelled');
}

/**
 * Handle form submission with AJAX and progress tracking
 */
function handleFormSubmit(e) {
    e.preventDefault();
    
    // Validate form before submission
    if (!validateForm()) {
        return false;
    }
    
    // Update UI for loading state
    setLoadingState(true);
    showProgressUI();
    
    // Prepare form data
    const formData = new FormData(scrapeForm);
    const data = {
        topic: formData.get('topic'),
        quantity: parseInt(formData.get('quantity'))
    };
    
    // Start AJAX request
    fetch('/scrape', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success && data.session_id) {
            // Start progress tracking
            startProgressTracking(data.session_id);
            announceToScreenReader('Scraping started. Progress will be shown in real-time.');
        } else {
            throw new Error(data.error || 'Unknown error occurred');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        hideProgressUI();
        setLoadingState(false);
        alert('Error starting search: ' + error.message);
    });
    
    return false;
}

/**
 * Setup all event listeners
 */
function setupEventListeners() {
    // Form submission with AJAX
    if (scrapeForm) {
        scrapeForm.addEventListener('submit', handleFormSubmit);
    }
    
    // Input validation
    if (quantityInput) {
        quantityInput.addEventListener('input', validateQuantityInput);
        quantityInput.addEventListener('blur', formatQuantityInput);
    }
    
    // Keyboard navigation for quantity pills
    document.querySelectorAll('.qty-pill').forEach(pill => {
        pill.addEventListener('keydown', handlePillKeydown);
        pill.addEventListener('click', handlePillClick);
    });
    
    // Auto-save form data
    setupFormAutoSave();
    
    // Handle page unload to clean up connections
    window.addEventListener('beforeunload', () => {
        if (eventSource) {
            eventSource.close();
        }
    });
}

/**
 * Set quantity value and update active pill
 * @param {number} qty - The quantity to set
 */
function setQuantity(qty) {
    if (quantityInput) {
        quantityInput.value = qty;
        updateActivePill(qty);
        validateQuantityInput();
    }
}

/**
 * Update active pill styling
 * @param {number} qty - The active quantity
 */
function updateActivePill(qty) {
    document.querySelectorAll('.qty-pill').forEach(pill => {
        pill.classList.remove('active');
        pill.setAttribute('aria-pressed', 'false');
        
        if (parseInt(pill.textContent) === qty) {
            pill.classList.add('active');
            pill.setAttribute('aria-pressed', 'true');
        }
    });
}

/**
 * Handle pill click events
 * @param {Event} event - Click event
 */
function handlePillClick(event) {
    const qty = parseInt(event.target.textContent);
    setQuantity(qty);
    
    // Announce to screen readers
    announceToScreenReader(`Selected ${qty} images`);
}

/**
 * Handle keyboard navigation for pills
 * @param {Event} event - Keydown event
 */
function handlePillKeydown(event) {
    if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        handlePillClick(event);
    }
}

/**
 * Validate quantity input
 */
function validateQuantityInput() {
    if (!quantityInput) return;
    
    const value = parseInt(quantityInput.value);
    const min = parseInt(quantityInput.min) || 1;
    const max = parseInt(quantityInput.max) || 1000;
    
    // Remove any existing validation classes
    quantityInput.classList.remove('error', 'warning');
    
    if (value < min || value > max || isNaN(value)) {
        quantityInput.classList.add('error');
        showValidationMessage(`Please enter a number between ${min} and ${max}`, 'error');
    } else if (value > 500) {
        quantityInput.classList.add('warning');
        showValidationMessage('Large quantities may take longer to process', 'warning');
    } else {
        hideValidationMessage();
    }
    
    // Update active pill if it matches a preset value
    const presetValues = [25, 50, 100, 200, 500];
    if (presetValues.includes(value)) {
        updateActivePill(value);
    } else {
        updateActivePill(null);
    }
}

/**
 * Format quantity input on blur
 */
function formatQuantityInput() {
    if (!quantityInput) return;
    
    const value = parseInt(quantityInput.value);
    const min = parseInt(quantityInput.min) || 1;
    const max = parseInt(quantityInput.max) || 1000;
    
    // Clamp value to valid range
    if (value < min) {
        quantityInput.value = min;
    } else if (value > max) {
        quantityInput.value = max;
    }
    
    validateQuantityInput();
}

/**
 * Show validation message
 * @param {string} message - Message to show
 * @param {string} type - Type of message (error, warning, success)
 */
function showValidationMessage(message, type = 'info') {
    hideValidationMessage();
    
    const messageEl = document.createElement('div');
    messageEl.className = `validation-message ${type}`;
    messageEl.textContent = message;
    messageEl.setAttribute('role', 'alert');
    messageEl.setAttribute('aria-live', 'polite');
    
    quantityInput.parentNode.appendChild(messageEl);
    
    // Auto-hide after 5 seconds
    setTimeout(() => hideValidationMessage(), 5000);
}

/**
 * Hide validation message
 */
function hideValidationMessage() {
    const existingMessage = document.querySelector('.validation-message');
    if (existingMessage) {
        existingMessage.remove();
    }
}

/**
 * Handle form submission
 * @param {Event} e - Submit event
 */
function handleFormSubmit(e) {
    // Validate form before submission
    if (!validateForm()) {
        e.preventDefault();
        return false;
    }
    
    // Update UI for loading state
    setLoadingState(true);
    
    // Clear any saved form data
    clearFormAutoSave();
    
    // Allow form to submit normally
    return true;
}

/**
 * Validate entire form
 * @returns {boolean} - True if form is valid
 */
function validateForm() {
    const topicInput = document.getElementById('topic');
    
    if (!topicInput || !topicInput.value.trim()) {
        showValidationMessage('Please enter a search topic', 'error');
        if (topicInput) topicInput.focus();
        return false;
    }
    
    if (!quantityInput || !quantityInput.value) {
        showValidationMessage('Please enter a quantity', 'error');
        if (quantityInput) quantityInput.focus();
        return false;
    }
    
    const quantity = parseInt(quantityInput.value);
    if (quantity < 1 || quantity > 1000) {
        showValidationMessage('Quantity must be between 1 and 1000', 'error');
        if (quantityInput) quantityInput.focus();
        return false;
    }
    
    return true;
}

/**
 * Set loading state
 * @param {boolean} loading - Whether to show loading state
 */
function setLoadingState(loading) {
    if (!launchBtn || !spinner) return;
    
    if (loading) {
        launchBtn.classList.add('loading');
        launchBtn.disabled = true;
        spinner.style.display = 'inline-block';
        launchBtn.innerHTML = '<div class="spinner"></div><i class="fas fa-cog fa-spin"></i> Hunting Images...';
        
        // Announce to screen readers
        announceToScreenReader('Searching for images, please wait...');
    } else {
        launchBtn.classList.remove('loading');
        launchBtn.disabled = false;
        spinner.style.display = 'none';
        launchBtn.innerHTML = '<i class="fas fa-rocket"></i> Launch Image Hunt';
    }
}

/**
 * Create floating particles effect
 */
function createFloatingParticles() {
    const container = document.querySelector('.container');
    if (!container) return;
    
    // Check if user prefers reduced motion
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        return;
    }
    
    const particleCount = window.innerWidth < 768 ? 10 : 20;
    
    for (let i = 0; i < particleCount; i++) {
        createParticle(container, i);
    }
}

/**
 * Create individual particle
 * @param {HTMLElement} container - Container element
 * @param {number} index - Particle index for delay
 */
function createParticle(container, index) {
    const particle = document.createElement('div');
    const size = Math.random() * 4 + 2;
    const animationDuration = Math.random() * 10 + 15;
    const delay = Math.random() * -20;
    
    particle.style.cssText = `
        position: absolute;
        width: ${size}px;
        height: ${size}px;
        background: rgba(255, 255, 255, ${Math.random() * 0.3 + 0.1});
        border-radius: 50%;
        pointer-events: none;
        animation: float ${animationDuration}s infinite linear;
        animation-delay: ${delay}s;
        left: ${Math.random() * 100}%;
        top: 100vh;
        z-index: -1;
    `;
    
    container.appendChild(particle);
    
    // Remove particle after animation to prevent memory leaks
    setTimeout(() => {
        if (particle.parentNode) {
            particle.parentNode.removeChild(particle);
        }
    }, (animationDuration + Math.abs(delay)) * 1000);
}

/**
 * Setup form auto-save functionality
 */
function setupFormAutoSave() {
    const topicInput = document.getElementById('topic');
    
    if (topicInput) {
        // Load saved data
        const savedTopic = localStorage.getItem('imageScraper_topic');
        const savedQuantity = localStorage.getItem('imageScraper_quantity');
        
        if (savedTopic) {
            topicInput.value = savedTopic;
        }
        
        if (savedQuantity && quantityInput) {
            quantityInput.value = savedQuantity;
            validateQuantityInput();
        }
        
        // Save data on input
        topicInput.addEventListener('input', () => {
            localStorage.setItem('imageScraper_topic', topicInput.value);
        });
        
        if (quantityInput) {
            quantityInput.addEventListener('input', () => {
                localStorage.setItem('imageScraper_quantity', quantityInput.value);
            });
        }
    }
}

/**
 * Clear form auto-save data
 */
function clearFormAutoSave() {
    localStorage.removeItem('imageScraper_topic');
    localStorage.removeItem('imageScraper_quantity');
}

/**
 * Setup accessibility features
 */
function setupAccessibility() {
    // Add ARIA labels to quantity pills
    document.querySelectorAll('.qty-pill').forEach(pill => {
        const qty = pill.textContent;
        pill.setAttribute('role', 'button');
        pill.setAttribute('tabindex', '0');
        pill.setAttribute('aria-label', `Select ${qty} images`);
        pill.setAttribute('aria-pressed', 'false');
    });
    
    // Add live region for announcements
    const liveRegion = document.createElement('div');
    liveRegion.setAttribute('aria-live', 'polite');
    liveRegion.setAttribute('aria-atomic', 'true');
    liveRegion.className = 'sr-only';
    liveRegion.id = 'live-region';
    document.body.appendChild(liveRegion);
}

/**
 * Announce message to screen readers
 * @param {string} message - Message to announce
 */
function announceToScreenReader(message) {
    const liveRegion = document.getElementById('live-region');
    if (liveRegion) {
        liveRegion.textContent = message;
        
        // Clear after announcement
        setTimeout(() => {
            liveRegion.textContent = '';
        }, 1000);
    }
}

/**
 * Handle window resize for responsive particles
 */
window.addEventListener('resize', debounce(() => {
    // Remove existing particles
    document.querySelectorAll('.container > div[style*="position: absolute"]').forEach(particle => {
        particle.remove();
    });
    
    // Recreate particles with new count
    createFloatingParticles();
}, 250));

/**
 * Debounce function for performance
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} - Debounced function
 */
function debounce(func, wait) {
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

/**
 * Handle page visibility change
 */
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        // Pause animations when page is hidden
        document.querySelectorAll('.container > div[style*="animation"]').forEach(particle => {
            particle.style.animationPlayState = 'paused';
        });
    } else {
        // Resume animations when page is visible
        document.querySelectorAll('.container > div[style*="animation"]').forEach(particle => {
            particle.style.animationPlayState = 'running';
        });
    }
});

// Global functions for backward compatibility
window.setQuantity = setQuantity;
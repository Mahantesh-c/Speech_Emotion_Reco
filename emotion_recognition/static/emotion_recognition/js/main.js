/**
 * Main application script
 * Initializes components and handles global events
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Feather icons
    if (typeof feather !== 'undefined') {
        feather.replace();
    }
    
    // Mobile menu toggle
    initMobileMenu();
    
    // Initialize message alerts
    initMessageAlerts();
    
    // Initialize tooltips
    initTooltips();
    
    // Listen for dark mode changes
    window.addEventListener('darkmodechange', handleDarkModeChange);
});

/**
 * Initialize mobile menu functionality
 */
function initMobileMenu() {
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
            
            // Update aria-expanded attribute for accessibility
            const isExpanded = !mobileMenu.classList.contains('hidden');
            mobileMenuButton.setAttribute('aria-expanded', isExpanded.toString());
        });
    }
}

/**
 * Initialize message alerts close functionality
 */
function initMessageAlerts() {
    const closeButtons = document.querySelectorAll('.close-alert');
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const alert = this.closest('[role="alert"]');
            if (alert) {
                alert.classList.add('opacity-0');
                setTimeout(() => {
                    alert.remove();
                }, 300);
            }
        });
    });
}

/**
 * Initialize tooltip functionality
 */
function initTooltips() {
    const tooltipTriggers = document.querySelectorAll('[data-tooltip]');
    
    tooltipTriggers.forEach(trigger => {
        trigger.addEventListener('mouseenter', showTooltip);
        trigger.addEventListener('mouseleave', hideTooltip);
        trigger.addEventListener('focus', showTooltip);
        trigger.addEventListener('blur', hideTooltip);
    });
}

/**
 * Show tooltip
 * @param {Event} event - Mouse or focus event
 */
function showTooltip(event) {
    const trigger = event.currentTarget;
    const tooltipText = trigger.getAttribute('data-tooltip');
    
    if (!tooltipText) return;
    
    // Check if tooltip already exists
    let tooltip = document.getElementById(`tooltip-${trigger.id}`);
    
    if (!tooltip) {
        // Create tooltip element
        tooltip = document.createElement('div');
        tooltip.id = `tooltip-${trigger.id}`;
        tooltip.className = 'absolute z-50 px-2 py-1 text-xs text-white bg-gray-900 rounded shadow-lg transition-opacity duration-200 opacity-0';
        tooltip.textContent = tooltipText;
        document.body.appendChild(tooltip);
    }
    
    // Position the tooltip
    const triggerRect = trigger.getBoundingClientRect();
    tooltip.style.top = `${triggerRect.top - tooltip.offsetHeight - 8 + window.scrollY}px`;
    tooltip.style.left = `${triggerRect.left + triggerRect.width/2 - tooltip.offsetWidth/2 + window.scrollX}px`;
    
    // Show the tooltip
    setTimeout(() => {
        tooltip.classList.remove('opacity-0');
        tooltip.classList.add('opacity-100');
    }, 50);
}

/**
 * Hide tooltip
 * @param {Event} event - Mouse or blur event
 */
function hideTooltip(event) {
    const trigger = event.currentTarget;
    const tooltip = document.getElementById(`tooltip-${trigger.id}`);
    
    if (tooltip) {
        tooltip.classList.remove('opacity-100');
        tooltip.classList.add('opacity-0');
        
        setTimeout(() => {
            if (tooltip.parentNode) {
                tooltip.parentNode.removeChild(tooltip);
            }
        }, 200);
    }
}

/**
 * Handle dark mode changes
 * @param {CustomEvent} event - Dark mode change event
 */
function handleDarkModeChange(event) {
    const isDarkMode = event.detail.isDarkMode;
    
    // Update charts if they exist
    updateChartsForDarkMode(isDarkMode);
}

/**
 * Update chart styles for dark mode
 * @param {boolean} isDarkMode - Whether dark mode is active
 */
function updateChartsForDarkMode(isDarkMode) {
    // Check if Chart.js is loaded
    if (typeof Chart === 'undefined') return;
    
    // Get the text and grid colors based on mode
    const textColor = isDarkMode ? '#D1D5DB' : '#374151';
    const gridColor = isDarkMode ? 'rgba(75, 85, 99, 0.2)' : 'rgba(107, 114, 128, 0.1)';
    
    // Update all charts
    Chart.instances.forEach(chart => {
        // Update legend text color
        if (chart.options.plugins && chart.options.plugins.legend) {
            chart.options.plugins.legend.labels.color = textColor;
        }
        
        // Update grid line color
        if (chart.options.scales) {
            for (const scaleId in chart.options.scales) {
                const scale = chart.options.scales[scaleId];
                if (scale.grid) {
                    scale.grid.color = gridColor;
                }
                if (scale.ticks) {
                    scale.ticks.color = textColor;
                }
            }
        }
        
        chart.update();
    });
}

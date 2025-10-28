// Main JavaScript for Home Loan Toolkit

// Utility function to format currency
function formatCurrency(value) {
    return 'Rs ' + Math.round(value).toLocaleString('en-IN');
}

// Utility function to format numbers
function formatNumber(value, decimals = 0) {
    return value.toFixed(decimals).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Add event listeners when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Home Loan Toolkit loaded');
});

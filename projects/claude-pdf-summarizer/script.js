// Configuration - Automatically detects environment
const API_BASE_URL = (() => {
    const hostname = window.location.hostname;
    
    // Local development
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        return 'http://localhost:8000';
    }
    
    // Production API (always use your deployed API)
    return 'https://claude-pdf-summarizer-wmpytqcfsa-uc.a.run.app';
})();

// DOM Elements
const fileUpload = document.getElementById('fileUpload');
const pdfFileInput = document.getElementById('pdfFile');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const removeFileBtn = document.getElementById('removeFile');
const summarizerForm = document.getElementById('summarizerForm');
const bulletPointsRange = document.getElementById('bulletPoints');
const bulletPointsValue = document.getElementById('bulletPointsValue');
const submitBtn = document.getElementById('submitBtn');
const loading = document.getElementById('loading');
const results = document.getElementById('results');
const error = document.getElementById('error');
const summaryContent = document.getElementById('summaryContent');
const resultsMeta = document.getElementById('resultsMeta');
const copyBtn = document.getElementById('copyBtn');
const retryBtn = document.getElementById('retryBtn');
const errorMessage = document.getElementById('errorMessage');
const apiDocsLink = document.getElementById('apiDocsLink');

let selectedFile = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    updateBulletPointsDisplay();
    setApiDocsLink();
});

function initializeEventListeners() {
    // File upload events
    fileUpload.addEventListener('click', () => pdfFileInput.click());
    fileUpload.addEventListener('dragover', handleDragOver);
    fileUpload.addEventListener('dragleave', handleDragLeave);
    fileUpload.addEventListener('drop', handleDrop);
    
    pdfFileInput.addEventListener('change', handleFileSelect);
    removeFileBtn.addEventListener('click', removeFile);
    
    // Form events
    summarizerForm.addEventListener('submit', handleSubmit);
    bulletPointsRange.addEventListener('input', updateBulletPointsDisplay);
    
    // Button events
    copyBtn.addEventListener('click', copyToClipboard);
    retryBtn.addEventListener('click', resetForm);
}

function setApiDocsLink() {
    apiDocsLink.href = `${API_BASE_URL}/docs`;
    apiDocsLink.target = '_blank';
}

// File handling functions
function handleDragOver(e) {
    e.preventDefault();
    fileUpload.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    fileUpload.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    fileUpload.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelection(files[0]);
    }
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleFileSelection(file);
    }
}

function handleFileSelection(file) {
    // Validate file type
    if (!file.name.toLowerCase().endsWith('.pdf')) {
        showError('Please select a PDF file only.');
        return;
    }
    
    // Validate file size (10MB limit)
    if (file.size > 10 * 1024 * 1024) {
        showError('File size too large. Please select a PDF smaller than 10MB.');
        return;
    }
    
    selectedFile = file;
    displaySelectedFile(file);
    hideError();
}

function displaySelectedFile(file) {
    fileName.textContent = file.name;
    fileUpload.style.display = 'none';
    fileInfo.style.display = 'flex';
}

function removeFile() {
    selectedFile = null;
    pdfFileInput.value = '';
    fileUpload.style.display = 'block';
    fileInfo.style.display = 'none';
    hideError();
}

function updateBulletPointsDisplay() {
    bulletPointsValue.textContent = bulletPointsRange.value;
}

// Form submission
async function handleSubmit(e) {
    e.preventDefault();
    
    if (!selectedFile) {
        showError('Please select a PDF file first.');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('style', document.getElementById('summaryStyle').value);
    formData.append('language', document.getElementById('language').value);
    formData.append('bullet_points', bulletPointsRange.value);
    
    try {
        showLoading();
        hideError();
        hideResults();
        
        const response = await fetch(`${API_BASE_URL}/summarize`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || `HTTP error! status: ${response.status}`);
        }
        
        if (data.success) {
            showResults(data.summary, data.metadata);
        } else {
            throw new Error(data.error || 'Unknown error occurred');
        }
        
    } catch (err) {
        console.error('Error:', err);
        showError(getErrorMessage(err));
    } finally {
        hideLoading();
    }
}

function getErrorMessage(error) {
    const message = error.message || 'Unknown error occurred';
    
    if (message.includes('NetworkError') || message.includes('fetch')) {
        return 'Unable to connect to the server. Please check your internet connection and try again.';
    } else if (message.includes('413')) {
        return 'File too large. Please select a smaller PDF file.';
    } else if (message.includes('400')) {
        return 'Invalid file or request. Please check your PDF file and try again.';
    } else if (message.includes('500')) {
        return 'Server error occurred. Please try again in a few moments.';
    }
    
    return message;
}

// UI state management
function showLoading() {
    submitBtn.disabled = true;
    loading.style.display = 'block';
}

function hideLoading() {
    submitBtn.disabled = false;
    loading.style.display = 'none';
}

function showResults(summary, metadata) {
    summaryContent.textContent = summary;
    
    // Display metadata
    const metaItems = [];
    if (metadata.filename) metaItems.push(`<span>📁 ${metadata.filename}</span>`);
    if (metadata.style) metaItems.push(`<span>🎨 ${metadata.style}</span>`);
    if (metadata.language) metaItems.push(`<span>🌐 ${metadata.language}</span>`);
    if (metadata.bullet_points) metaItems.push(`<span>📝 ${metadata.bullet_points} points</span>`);
    if (metadata.text_length) metaItems.push(`<span>📏 ${formatNumber(metadata.text_length)} chars</span>`);
    
    resultsMeta.innerHTML = metaItems.join('');
    results.style.display = 'block';
    
    // Scroll to results
    results.scrollIntoView({ behavior: 'smooth' });
}

function hideResults() {
    results.style.display = 'none';
}

function showError(message) {
    errorMessage.textContent = message;
    error.style.display = 'block';
    error.scrollIntoView({ behavior: 'smooth' });
}

function hideError() {
    error.style.display = 'none';
}

function resetForm() {
    hideError();
    hideResults();
    hideLoading();
    removeFile();
}

// Utility functions
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

async function copyToClipboard() {
    try {
        await navigator.clipboard.writeText(summaryContent.textContent);
        
        // Visual feedback
        const originalText = copyBtn.innerHTML;
        copyBtn.innerHTML = '<i class="fas fa-check"></i> Copied!';
        copyBtn.style.background = '#2ed573';
        
        setTimeout(() => {
            copyBtn.innerHTML = originalText;
            copyBtn.style.background = '#26d063';
        }, 2000);
        
    } catch (err) {
        console.error('Failed to copy:', err);
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = summaryContent.textContent;
        document.body.appendChild(textArea);
        textArea.select();
        try {
            document.execCommand('copy');
            copyBtn.innerHTML = '<i class="fas fa-check"></i> Copied!';
        } catch (fallbackErr) {
            console.error('Fallback copy failed:', fallbackErr);
        }
        document.body.removeChild(textArea);
    }
}

// Health check on page load
async function checkApiHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (!response.ok) {
            console.warn('API health check failed');
        }
    } catch (err) {
        console.warn('Unable to reach API server:', err.message);
    }
}

// Check API health when page loads
checkApiHealth();
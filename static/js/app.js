const API_BASE = window.location.origin;

// DOM Elements
const shortenForm = document.getElementById('shortenForm');
const urlInput = document.getElementById('urlInput');
const shortenBtn = document.getElementById('shortenBtn');
const resultSection = document.getElementById('resultSection');
const statsSection = document.getElementById('statsSection');
const shortUrlInput = document.getElementById('shortUrl');
const copyBtn = document.getElementById('copyBtn');
const viewStatsBtn = document.getElementById('viewStatsBtn');
const newUrlBtn = document.getElementById('newUrlBtn');
const backToFormBtn = document.getElementById('backToFormBtn');
const errorMessage = document.getElementById('errorMessage');

// State
let currentShortCode = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    shortenForm.addEventListener('submit', handleShorten);
    copyBtn.addEventListener('click', handleCopy);
    viewStatsBtn.addEventListener('click', handleViewStats);
    newUrlBtn.addEventListener('click', handleNewUrl);
    backToFormBtn.addEventListener('click', handleBackToForm);
    
    // Allow Enter key to submit
    urlInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            shortenForm.dispatchEvent(new Event('submit'));
        }
    });
});

async function handleShorten(e) {
    e.preventDefault();
    hideError();
    
    const url = urlInput.value.trim();
    if (!url) {
        showError('Please enter a valid URL');
        return;
    }

    // Validate URL format
    try {
        new URL(url);
    } catch {
        showError('Please enter a valid URL (must start with http:// or https://)');
        return;
    }

    setLoading(true);
    
    try {
        const response = await fetch(`${API_BASE}/shorten`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Failed to shorten URL');
        }

        currentShortCode = data.short_code;
        shortUrlInput.value = data.short_url;
        showResult();
        
    } catch (error) {
        showError(error.message || 'An error occurred. Please try again.');
    } finally {
        setLoading(false);
    }
}

function showResult() {
    resultSection.style.display = 'block';
    statsSection.style.display = 'none';
    urlInput.value = '';
    urlInput.blur();
}

async function handleViewStats() {
    if (!currentShortCode) return;
    
    setLoading(true);
    hideError();
    
    try {
        const response = await fetch(`${API_BASE}/stats/${currentShortCode}`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Failed to fetch stats');
        }

        // Format the date
        const createdAt = new Date(data.created_at);
        const formattedDate = createdAt.toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });

        document.getElementById('originalUrl').textContent = data.original_url;
        document.getElementById('visitsCount').textContent = data.visits_count.toLocaleString();
        document.getElementById('createdAt').textContent = formattedDate;

        resultSection.style.display = 'none';
        statsSection.style.display = 'block';
        
    } catch (error) {
        showError(error.message || 'Failed to load statistics');
    } finally {
        setLoading(false);
    }
}

function handleNewUrl() {
    currentShortCode = null;
    resultSection.style.display = 'none';
    statsSection.style.display = 'none';
    urlInput.focus();
    hideError();
}

function handleBackToForm() {
    resultSection.style.display = 'block';
    statsSection.style.display = 'none';
    hideError();
}

async function handleCopy() {
    const shortUrl = shortUrlInput.value;
    
    try {
        await navigator.clipboard.writeText(shortUrl);
        
        // Visual feedback
        const originalText = copyBtn.innerHTML;
        copyBtn.innerHTML = '✓';
        copyBtn.style.background = 'var(--success)';
        
        setTimeout(() => {
            copyBtn.innerHTML = originalText;
            copyBtn.style.background = '';
        }, 2000);
        
    } catch (error) {
        // Fallback for older browsers
        shortUrlInput.select();
        document.execCommand('copy');
        showError('Copied to clipboard!');
        setTimeout(hideError, 2000);
    }
}

function setLoading(loading) {
    shortenBtn.disabled = loading;
    const btnText = shortenBtn.querySelector('.btn-text');
    const btnLoader = shortenBtn.querySelector('.btn-loader');
    
    if (loading) {
        btnText.style.display = 'none';
        btnLoader.style.display = 'inline';
    } else {
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
    }
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
}

function hideError() {
    errorMessage.style.display = 'none';
}


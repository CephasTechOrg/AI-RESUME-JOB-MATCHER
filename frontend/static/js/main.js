const API_BASE_URL = 'http://localhost:8000';

let currentResumeText = '';

// Initialize the application
document.addEventListener('DOMContentLoaded', function () {
    console.log('AI Resume Evaluator initialized');
    initializeApp();
});

function initializeApp() {
    // Initialize character counter
    const jobDescription = document.getElementById('job-description');
    const charCount = document.getElementById('char-count');

    jobDescription.addEventListener('input', function () {
        charCount.textContent = this.value.length;
    });

    // Initialize file upload with drag and drop
    initializeFileUpload();

    // Initialize navigation
    initializeNavigation();

    // Initialize copy functionality
    initializeCopyButtons();
}

// Enhanced file upload with drag and drop
function initializeFileUpload() {
    const fileUploadArea = document.getElementById('file-upload-area');
    const fileInput = document.getElementById('fpload');
    const browseBtn = fileUploadArea.querySelector('.browse-btn');

    // Click browse button to trigger file input
    browseBtn.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();
        fileInput.click();
    });

    // Drag and drop functionality
    fileUploadArea.addEventListener('dragover', function (e) {
        e.preventDefault();
        this.classList.add('dragover');
    });

    fileUploadArea.addEventListener('dragleave', function (e) {
        e.preventDefault();
        this.classList.remove('dragover');
    });

    fileUploadArea.addEventListener('drop', function (e) {
        e.preventDefault();
        this.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            handleFileSelection(files[0]);
        }
    });

    // File input change
    fileInput.addEventListener('change', function (e) {
        if (this.files.length > 0) {
            handleFileSelection(this.files[0]);
        }
    });
}

function handleFileSelection(file) {
    const fileInfo = document.getElementById('file-info');

    if (!file) return;

    // Validate file type
    const validTypes = ['.pdf', '.docx'];
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();

    if (!validTypes.includes(fileExtension)) {
        fileInfo.innerHTML = `❌ Please select a PDF or DOCX file`;
        fileInfo.classList.add('show', 'error');
        return;
    }

    // Validate file size (5MB)
    if (file.size > 5 * 1024 * 1024) {
        fileInfo.innerHTML = `❌ File size must be less than 5MB`;
        fileInfo.classList.add('show', 'error');
        return;
    }

    fileInfo.innerHTML = `⏳ Processing: ${file.name}...`;
    fileInfo.classList.add('show');
    fileInfo.classList.remove('error');

    uploadFile(file);
}

async function uploadFile(file) {
    const fileInfo = document.getElementById('file-info');

    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_BASE_URL}/evaluate/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('File upload failed');
        }

        const result = await response.json();
        currentResumeText = result.content;
        fileInfo.innerHTML = `✅ ${file.name} - Ready for analysis`;
        fileInfo.classList.remove('error');

        showToast('Resume uploaded successfully!');

    } catch (error) {
        console.error('Upload error:', error);
        fileInfo.innerHTML = `❌ Error: ${error.message}`;
        fileInfo.classList.add('error');
        currentResumeText = '';
    }
}

// Enhanced navigation
function initializeNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');

    navLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            const targetSection = this.getAttribute('data-section');

            // Update active states
            navLinks.forEach(nav => nav.classList.remove('active'));
            this.classList.add('active');

            // Show target section
            showSection(targetSection);
        });
    });
}

function showSection(sectionName) {
    const sections = document.querySelectorAll('.card');
    sections.forEach(section => {
        section.classList.add('hidden');
        section.classList.remove('active-section');
    });

    const targetSection = document.getElementById(`${sectionName}-section`);
    if (targetSection) {
        targetSection.classList.remove('hidden');
        setTimeout(() => {
            targetSection.classList.add('active-section');
        }, 50);
    }
}

// Enhanced evaluation function
async function evaluateResume() {
    const jobTitle = document.getElementById('job-title').value.trim();
    const jobDescription = document.getElementById('job-description').value.trim();

    if (!jobTitle || !jobDescription) {
        showToast('Please fill in job title and description');
        return;
    }

    if (!currentResumeText) {
        showToast('Please upload a resume first');
        return;
    }

    // Show loading with enhanced animation
    showLoading(true);

    try {
        const formData = new FormData();
        formData.append('job_title', jobTitle);
        formData.append('job_description', jobDescription);
        formData.append('resume_text', currentResumeText);

        const response = await fetch(`${API_BASE_URL}/evaluate/`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Evaluation failed: ${response.statusText}`);
        }

        const results = await response.json();

        // Add slight delay for better UX
        setTimeout(() => {
            displayResults(results);
            showToast('Analysis completed successfully!');
        }, 1000);

    } catch (error) {
        console.error('Evaluation error:', error);
        showToast('Evaluation failed. Please try again.');
    } finally {
        setTimeout(() => {
            showLoading(false);
        }, 500);
    }
}

// Enhanced results display
function displayResults(results) {
    // Show results section
    showSection('results');

    // Update overall score with animation
    const overallScore = results.scores.overall_impact ||
        Math.round(Object.values(results.scores).reduce((a, b) => a + b, 0) / Object.values(results.scores).length);

    document.getElementById('overall-score').textContent = overallScore;
    updateScoreCircle(overallScore);

    // Update quick stats
    updateQuickStats(results);

    // Create enhanced charts
    createScoresChart(results.scores);

    // Display detailed scores
    displayDetailedScores(results.scores);

    // Display missing keywords
    displayKeywords(results.missing_keywords);

    // Display suggestions
    displaySuggestions(results.suggestions);

    // Display summary
    document.getElementById('summary-text').textContent = results.summary;

    // Update navigation
    document.querySelector('.nav-link[data-section="results"]').classList.add('active');
    document.querySelector('.nav-link[data-section="input"]').classList.remove('active');
}

function updateQuickStats(results) {
    // Update matched skills count (approximate)
    const matchedSkills = Math.round((results.scores.skills_match / 100) * 20);
    document.getElementById('matched-skills').textContent = matchedSkills;

    // Update missing keywords count
    document.getElementById('missing-keywords-count').textContent = results.missing_keywords.length;

    // Update suggestions count
    document.getElementById('suggestions-count').textContent = results.suggestions.length;
}

// Enhanced score circle with color coding
function updateScoreCircle(score) {
    const circle = document.querySelector('.score-circle');
    const percentage = (score / 100) * 360;

    let gradient;
    if (score >= 80) {
        gradient = 'var(--gradient-success)';
    } else if (score >= 60) {
        gradient = 'var(--gradient-warning)';
    } else {
        gradient = 'var(--gradient-danger)';
    }

    circle.style.background = `conic-gradient(${gradient} ${percentage}deg, #e2e8f0 ${percentage}deg)`;

    // Animate breakdown bars
    animateBreakdownBars();
}

function animateBreakdownBars() {
    const breakdownItems = document.querySelectorAll('.breakdown-item');
    breakdownItems.forEach((item, index) => {
        const progress = item.querySelector('.breakdown-progress');
        const randomWidth = Math.floor(Math.random() * 30) + 70; // 70-100%
        setTimeout(() => {
            progress.style.width = `${randomWidth}%`;
        }, index * 300);
    });
}

// Enhanced detailed scores display
function displayDetailedScores(scores) {
    const scoresGrid = document.getElementById('scores-grid');
    scoresGrid.innerHTML = '';

    Object.entries(scores).forEach(([key, value], index) => {
        const scoreItem = document.createElement('div');
        scoreItem.className = 'score-item';

        const formattedKey = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

        scoreItem.innerHTML = `
            <div class="score-label">${formattedKey}</div>
            <div class="score-value">${value}</div>
            <div class="score-bar">
                <div class="score-progress" style="width: 0%"></div>
            </div>
        `;

        scoresGrid.appendChild(scoreItem);

        // Animate progress bar
        setTimeout(() => {
            const progress = scoreItem.querySelector('.score-progress');
            progress.style.width = `${value}%`;
        }, index * 150);
    });
}

// Enhanced keywords display
function displayKeywords(keywords) {
    const keywordsList = document.getElementById('keywords-list');
    keywordsList.innerHTML = '';

    keywords.forEach((keyword, index) => {
        const keywordElement = document.createElement('span');
        keywordElement.className = 'keyword';
        keywordElement.textContent = keyword;
        keywordElement.style.animationDelay = `${index * 0.1}s`;
        keywordsList.appendChild(keywordElement);
    });
}

// Enhanced suggestions display
function displaySuggestions(suggestions) {
    const suggestionsList = document.getElementById('suggestions-list');
    suggestionsList.innerHTML = '';

    suggestions.forEach((suggestion, index) => {
        const li = document.createElement('li');
        li.textContent = suggestion;
        li.style.animationDelay = `${index * 0.1}s`;
        suggestionsList.appendChild(li);
    });
}

// Enhanced loading function
function showLoading(show) {
    const loading = document.getElementById('loading');
    if (show) {
        loading.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    } else {
        loading.classList.add('hidden');
        document.body.style.overflow = '';
    }
}

// Enhanced reset function
function resetEvaluation() {
    showSection('input');

    // Reset form
    document.getElementById('job-title').value = '';
    document.getElementById('job-description').value = '';
    document.getElementById('resume-upload').value = '';
    document.getElementById('file-info').textContent = '';
    document.getElementById('file-info').classList.remove('show', 'error');
    document.getElementById('char-count').textContent = '0';
    currentResumeText = '';

    // Reset navigation
    document.querySelector('.nav-link[data-section="input"]').classList.add('active');
    document.querySelector('.nav-link[data-section="results"]').classList.remove('active');

    showToast('Ready for new evaluation');
}

// Copy functionality
function initializeCopyButtons() {
    // Keywords copy button is handled in copyKeywords function
}

function copyKeywords() {
    const keywords = Array.from(document.querySelectorAll('.keyword'))
        .map(k => k.textContent)
        .join(', ');

    navigator.clipboard.writeText(keywords).then(() => {
        showToast('Keywords copied to clipboard!');
    }).catch(err => {
        console.error('Copy failed:', err);
        showToast('Failed to copy keywords');
    });
}

// Export results function
function downloadResults() {
    showToast('Export feature coming soon!');
    // In a real implementation, this would generate a PDF or JSON file
}

// Enhanced toast notification
function showToast(message) {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toast-message');

    toastMessage.textContent = message;
    toast.classList.remove('hidden');
    toast.classList.add('show');

    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            toast.classList.add('hidden');
        }, 300);
    }, 3000);
}
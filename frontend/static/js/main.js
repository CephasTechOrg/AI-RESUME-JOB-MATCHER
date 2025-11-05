const API_BASE_URL = 'http://localhost:8000';

let currentResumeText = '';

// Handle file upload and text extraction
document.getElementById('resume-upload').addEventListener('change', async function (e) {
    const file = e.target.files[0];
    if (!file) return;

    const fileInfo = document.getElementById('file-info');
    fileInfo.textContent = `Selected: ${file.name}`;
    fileInfo.classList.add('show');

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
        fileInfo.innerHTML = `✅ ${file.name} - Ready for evaluation`;

    } catch (error) {
        console.error('Upload error:', error);
        fileInfo.innerHTML = `❌ Error processing file: ${error.message}`;
        currentResumeText = '';
    }
});

// Main evaluation function
async function evaluateResume() {
    const jobTitle = document.getElementById('job-title').value;
    const jobDescription = document.getElementById('job-description').value;

    if (!jobTitle || !jobDescription || !currentResumeText) {
        alert('Please fill in all fields and upload a resume');
        return;
    }

    // Show loading
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
        displayResults(results);

    } catch (error) {
        console.error('Evaluation error:', error);
        alert('Evaluation failed. Please try again.');
    } finally {
        showLoading(false);
    }
}

// Display results
function displayResults(results) {
    // Hide input section, show results
    document.getElementById('input-section').classList.add('hidden');
    document.getElementById('results-section').classList.remove('hidden');

    // Update overall score
    const overallScore = results.scores.overall_impact ||
        Math.round(Object.values(results.scores).reduce((a, b) => a + b, 0) / Object.values(results.scores).length);

    document.getElementById('overall-score').textContent = overallScore;
    updateScoreCircle(overallScore);

    // Create charts
    createScoresChart(results.scores);

    // Display detailed scores
    displayDetailedScores(results.scores);

    // Display missing keywords
    displayKeywords(results.missing_keywords);

    // Display suggestions
    displaySuggestions(results.suggestions);

    // Display summary
    document.getElementById('summary-text').textContent = results.summary;
}

// Update score circle animation
function updateScoreCircle(score) {
    const circle = document.querySelector('.score-circle');
    const percentage = (score / 100) * 360;
    circle.style.background = `conic-gradient(var(--primary-color) ${percentage}deg, #e2e8f0 ${percentage}deg)`;
}

// Display detailed scores with progress bars
function displayDetailedScores(scores) {
    const scoresGrid = document.getElementById('scores-grid');
    scoresGrid.innerHTML = '';

    for (const [key, value] of Object.entries(scores)) {
        const scoreItem = document.createElement('div');
        scoreItem.className = 'score-item';

        const formattedKey = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

        scoreItem.innerHTML = `
            <div class="score-label">${formattedKey}</div>
            <div class="score-value">${value}</div>
            <div class="score-bar">
                <div class="score-progress" style="width: ${value}%"></div>
            </div>
        `;

        scoresGrid.appendChild(scoreItem);
    }
}

// Display missing keywords
function displayKeywords(keywords) {
    const keywordsList = document.getElementById('keywords-list');
    keywordsList.innerHTML = '';

    keywords.forEach(keyword => {
        const keywordElement = document.createElement('span');
        keywordElement.className = 'keyword';
        keywordElement.textContent = keyword;
        keywordsList.appendChild(keywordElement);
    });
}

// Display suggestions
function displaySuggestions(suggestions) {
    const suggestionsList = document.getElementById('suggestions-list');
    suggestionsList.innerHTML = '';

    suggestions.forEach(suggestion => {
        const li = document.createElement('li');
        li.textContent = suggestion;
        suggestionsList.appendChild(li);
    });
}

// Show/hide loading spinner
function showLoading(show) {
    document.getElementById('loading').classList.toggle('hidden', !show);
}

// Reset evaluation
function resetEvaluation() {
    document.getElementById('results-section').classList.add('hidden');
    document.getElementById('input-section').classList.remove('hidden');

    // Reset form
    document.getElementById('job-title').value = '';
    document.getElementById('job-description').value = '';
    document.getElementById('resume-upload').value = '';
    document.getElementById('file-info').textContent = '';
    document.getElementById('file-info').classList.remove('show');
    currentResumeText = '';
}

// Initialize app
document.addEventListener('DOMContentLoaded', function () {
    console.log('AI Resume Evaluator initialized');
});
// Main.js

// Use localhost (including loopback hosts) in development, Render URL in production
const LOCAL_HOSTNAMES = ["localhost", "127.0.0.1", "::1"];
const isLocalHostname = LOCAL_HOSTNAMES.includes(window.location.hostname);

const API_BASE_URL = isLocalHostname
    ? "http://localhost:8000"
    : "https://ai-resume-job-matcher-backend.onrender.com";


let currentResumeText = '';
let latestOverallScore = 0;
let lastEvaluationPayload = null;
let lastEvaluationResult = null;
let lastJobTitle = '';
let lastJobDescription = '';

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
    const internLevelSelect = document.getElementById('intern-level');
    const internLevel = internLevelSelect ? internLevelSelect.value : 'general';

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
        formData.append('intern_level', internLevel);

        const response = await fetch(`${API_BASE_URL}/evaluate/`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Evaluation failed: ${response.statusText}`);
        }

        const results = await response.json();
        lastEvaluationPayload = {
            job_title: jobTitle,
            job_description: jobDescription,
            resume_text: currentResumeText,
            intern_level: internLevel,
        };
        lastEvaluationResult = results;
        lastJobTitle = jobTitle;
        lastJobDescription = jobDescription;
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

    latestOverallScore = overallScore;
    document.getElementById('overall-score').textContent = overallScore;
    updateScoreCircle(overallScore);
    updateComparison();

    // Create charts
    createScoresChart(results.scores);

    // Display detailed scores
    displayDetailedScores(results.scores);

    // Display missing keywords
    displayKeywords(results.missing_keywords);

    // Display keyword matches and suggestions
    displayKeywordMatches(results.keyword_matches || []);
    displaySuggestions(results.suggestions);

    // Quality gates
    displayQualityGates(results.quality_gates);

    // Display summary
    document.getElementById('summary-text').textContent = results.summary;

    const fallbackBanner = document.getElementById('fallback-banner');
    if (fallbackBanner) {
        const isFallback = results.source === 'fallback';
        fallbackBanner.textContent = isFallback
            ? 'AI service unavailable; showing keyword-based fallback.'
            : '';
        fallbackBanner.classList.toggle('hidden', !isFallback);
    }
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

function displayKeywordMatches(matches) {
    const container = document.getElementById('keyword-matches');
    if (!container) return;
    container.innerHTML = '';

    if (!matches.length) {
        container.textContent = 'No strong matches detected yet.';
        return;
    }

    matches.forEach(match => {
        const span = document.createElement('span');
        span.className = 'keyword match';
        const method = match.method === 'semantic' ? 'Semantic similarity' : 'Exact match';
        const phrase = match.matched_phrase || match.label;
        span.dataset.tip = `${method}\nPhrase: ${phrase}`;
        span.textContent = match.label;
        container.appendChild(span);
    });
}

function displayQualityGates(quality) {
    const list = document.getElementById('quality-gates');
    if (!list) return;
    list.innerHTML = '';
    const warnings = quality?.warnings || [];

    if (!warnings.length) {
        const li = document.createElement('li');
        li.textContent = 'No quality warnings detected.';
        li.style.background = '#ecfeff';
        li.style.borderColor = '#a5f3fc';
        li.style.color = '#0f172a';
        list.appendChild(li);
        return;
    }

    warnings.forEach(msg => {
        const li = document.createElement('li');
        li.textContent = msg;
        list.appendChild(li);
    });
}

function updateComparison() {
    const slider = document.getElementById('target-score');
    const label = document.getElementById('target-score-value');
    const deltaText = document.getElementById('comparison-delta');
    if (!slider || !label || !deltaText) return;

    const target = Number(slider.value || 0);
    label.textContent = target;
    const delta = latestOverallScore - target;
    const status = delta >= 0 ? 'ahead' : 'behind';
    deltaText.textContent = `You are ${Math.abs(delta)} points ${status} of your target.`;
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
    const internLevelSelect = document.getElementById('intern-level');
    if (internLevelSelect) {
        internLevelSelect.value = 'general';
    }
    currentResumeText = '';
    latestOverallScore = 0;
    lastEvaluationPayload = null;
    lastEvaluationResult = null;
    lastJobTitle = '';
    lastJobDescription = '';
}

// Initialize app
document.addEventListener('DOMContentLoaded', function () {
    console.log('AI Resume Evaluator initialized');
    const slider = document.getElementById('target-score');
    if (slider) {
        slider.addEventListener('input', updateComparison);
    }
    // Optional: show connectivity status in console
    fetch(`${API_BASE_URL}/evaluate/status`).then(r => r.json()).then(status => {
        console.log('Backend status', status);
    }).catch(() => {});
});

async function askAgentQuestion() {
    const questionInput = document.getElementById('chat-question');
    const responseBox = document.getElementById('chat-response');
    if (!questionInput || !responseBox) return;
    const question = questionInput.value.trim();
    if (!question) {
        responseBox.textContent = 'Please enter a question.';
        return;
    }
    if (!lastEvaluationPayload || !lastEvaluationResult) {
        responseBox.textContent = 'Run an evaluation first.';
        return;
    }

    responseBox.textContent = 'Thinking...';
    try {
        const formData = new FormData();
        formData.append('question', question);
        formData.append('job_title', lastJobTitle || lastEvaluationPayload.job_title);
        formData.append('job_description', lastJobDescription || lastEvaluationPayload.job_description);
        formData.append('resume_text', lastEvaluationPayload.resume_text);
        formData.append('evaluation_json', JSON.stringify(lastEvaluationResult));

        const resp = await fetch(`${API_BASE_URL}/evaluate/chat`, {
            method: 'POST',
            body: formData,
        });
        if (!resp.ok) {
            let detail = 'Chat failed';
            try {
                const err = await resp.json();
                detail = err.detail || detail;
            } catch (e) {
                // ignore parse errors
            }
            throw new Error(detail);
        }
        const data = await resp.json();
        responseBox.textContent = data.answer || 'No response received.';
    } catch (err) {
        responseBox.textContent = `${err.message || 'Chat failed.'} Please try again.`;
        console.error(err);
    }
}

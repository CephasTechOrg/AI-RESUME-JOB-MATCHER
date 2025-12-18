// Job templates functionality
let templateCache = {};
let selectedTemplateId = "";

async function loadJobTemplate() {
    const jobTemplateSelect = document.getElementById('job-template');
    if (!jobTemplateSelect) return;

    const selectedTemplate = jobTemplateSelect.value;
    selectedTemplateId = selectedTemplate;

    if (!selectedTemplate) {
        renderLevelInsights({});
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/evaluate/job-templates/${selectedTemplate}`);

        if (!response.ok) {
            throw new Error('Failed to load template');
        }

        const template = await response.json();
        templateCache[selectedTemplate] = template;

        applyTemplateDescription(selectedTemplate, template);
        renderLevelInsights(template);

    } catch (error) {
        console.error('Error loading template:', error);
        alert('Failed to load job template');
    }
}

// Handle intern level changes
function updateInternTemplate() {
    const internLevelSelect = document.getElementById('intern-level');
    const level = internLevelSelect ? internLevelSelect.value : 'general';
    const template = templateCache[selectedTemplateId];
    if (template) {
        renderLevelInsights(template, level);
    }
}

function createTemplateOption(value, label) {
    const option = document.createElement('option');
    option.value = value;
    option.textContent = label;
    return option;
}

function formatTemplateLabel(key = '') {
    return key
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

// Load available job templates on page load
async function loadJobTemplates() {
    const jobTemplateSelect = document.getElementById('job-template');
    if (!jobTemplateSelect) return;

    jobTemplateSelect.disabled = true;

    try {
        const response = await fetch(`${API_BASE_URL}/evaluate/job-templates`);

        if (!response.ok) {
            throw new Error('Failed to load templates');
        }

        const data = await response.json();
        const templates = data.templates || data;
        const entries = Object.entries(templates);

        if (!entries.length) {
            throw new Error('No templates returned from API');
        }

        const placeholderText = jobTemplateSelect.dataset.placeholder
            || jobTemplateSelect.options[0]?.textContent?.trim()
            || '-- Select a Template --';
        jobTemplateSelect.dataset.placeholder = placeholderText;

        const previouslySelected = jobTemplateSelect.value;
        const fragment = document.createDocumentFragment();

        fragment.appendChild(createTemplateOption('', placeholderText));

        entries.forEach(([key, details]) => {
            const label = details.title || formatTemplateLabel(key);
            fragment.appendChild(createTemplateOption(key, label));
            templateCache[key] = details;
        });

        jobTemplateSelect.innerHTML = '';
        jobTemplateSelect.appendChild(fragment);

        if (templates[previouslySelected]) {
            jobTemplateSelect.value = previouslySelected;
        }
    } catch (error) {
        console.error('Error loading templates:', error);
    } finally {
        jobTemplateSelect.disabled = false;
    }
}

// Initialize job templates
document.addEventListener('DOMContentLoaded', loadJobTemplates);

function applyTemplateDescription(selectedTemplate, templateFromAPI) {
    const titleInput = document.getElementById('job-title');
    const descInput = document.getElementById('job-description');
    if (!titleInput || !descInput) return;

    titleInput.value = templateFromAPI.title || '';
    descInput.value = templateFromAPI.description || '';

    renderLevelInsights(templateFromAPI);
}

function renderLevelInsights(template, levelOverride) {
    const panel = document.getElementById('level-insights');
    const levelReqList = document.getElementById('level-requirements');
    const levelRespList = document.getElementById('level-responsibilities');
    const bonusList = document.getElementById('bonus-signals');
    const levelSelect = document.getElementById('intern-level');

    if (!panel || !levelReqList || !levelRespList || !bonusList) return;

    const levels = template?.levels || {};
    const bonuses = template?.bonus_signals || [];
    const levelKeys = Object.keys(levels);

    if (!levelKeys.length) {
        panel.style.display = 'none';
        return;
    }

    panel.style.display = 'block';

    if (levelSelect) {
        levelSelect.innerHTML = '';
        const effectiveLevels = levelKeys.length ? levelKeys : ['general'];
        effectiveLevels.forEach((key) => {
            levelSelect.appendChild(createTemplateOption(key, formatTemplateLabel(key)));
        });
        if (!levelOverride || !effectiveLevels.includes(levelOverride)) {
            levelSelect.value = effectiveLevels[0];
        } else {
            levelSelect.value = levelOverride;
        }
    }

    const activeLevel = levelSelect ? levelSelect.value : levelKeys[0];
    const activeProfile = levels[activeLevel] || levels[levelKeys[0]] || {};

    levelReqList.innerHTML = '';
    (activeProfile.requirements || []).forEach(req => {
        const li = document.createElement('li');
        li.textContent = req;
        levelReqList.appendChild(li);
    });

    levelRespList.innerHTML = '';
    (activeProfile.responsibilities || []).forEach(resp => {
        const li = document.createElement('li');
        li.textContent = resp;
        levelRespList.appendChild(li);
    });

    bonusList.innerHTML = '';
    bonuses.forEach(bonus => {
        const li = document.createElement('li');
        li.textContent = bonus;
        bonusList.appendChild(li);
    });

    const internLevelGroup = document.getElementById('intern-level-group');
    if (internLevelGroup) {
        internLevelGroup.style.display = (levelKeys.length || bonuses.length) ? 'block' : 'none';
    }
}

// Intern level selector is now integrated with main template selection

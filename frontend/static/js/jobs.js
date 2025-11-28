// Job templates functionality
async function loadJobTemplate() {
    const jobTemplateSelect = document.getElementById('job-template');
    if (!jobTemplateSelect) return;

    const selectedTemplate = jobTemplateSelect.value;
    if (!selectedTemplate) return;

    try {
        const response = await fetch(`${API_BASE_URL}/evaluate/job-templates/${selectedTemplate}`);

        if (!response.ok) {
            throw new Error('Failed to load template');
        }

        const template = await response.json();

        // Populate form with template data
        document.getElementById('job-title').value = template.title || '';
        document.getElementById('job-description').value = template.description || '';

    } catch (error) {
        console.error('Error loading template:', error);
        alert('Failed to load job template');
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

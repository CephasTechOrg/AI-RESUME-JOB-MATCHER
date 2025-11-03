// Job templates functionality
async function loadJobTemplate() {
    const templateSelect = document.getElementById('job-template');
    const selectedTemplate = templateSelect.value;

    if (!selectedTemplate) return;

    try {
        const response = await fetch(`${API_BASE_URL}/evaluate/job-templates/${selectedTemplate}`);

        if (!response.ok) {
            throw new Error('Failed to load template');
        }

        const template = await response.json();

        // Populate form with template data
        document.getElementById('job-title').value = template.title;
        document.getElementById('job-description').value = template.description;

    } catch (error) {
        console.error('Error loading template:', error);
        alert('Failed to load job template');
    }
}

// Load available job templates on page load
async function loadJobTemplates() {
    try {
        const response = await fetch(`${API_BASE_URL}/evaluate/job-templates`);
        const data = await response.json();
        console.log('Available templates:', data);
    } catch (error) {
        console.error('Error loading templates:', error);
    }
}

// Initialize job templates
document.addEventListener('DOMContentLoaded', loadJobTemplates);
import sys
import importlib

# Clear any cached imports
if 'backend' in sys.modules:
    del sys.modules['backend']
if 'backend.data' in sys.modules:
    del sys.modules['backend.data']
if 'backend.data.job_templates' in sys.modules:
    del sys.modules['backend.data.job_templates']

from backend.data.job_templates import JOB_TEMPLATES

levels = [
    'software_engineer_intern',
    'software_engineer_intern_freshman',
    'software_engineer_intern_sophomore',
    'software_engineer_intern_junior',
    'software_engineer_intern_senior'
]

print(f"Total templates in JOB_TEMPLATES: {len(JOB_TEMPLATES)}")
print("\nChecking Software Engineer Intern templates:")
for level in levels:
    if level in JOB_TEMPLATES:
        t = JOB_TEMPLATES[level]
        has_title = 'title' in t and len(str(t['title']).strip()) > 0
        has_desc = 'description' in t and len(str(t['description']).strip()) > 0
        status = "✓" if (has_title and has_desc) else "✗"
        print(f"  {status} {level}: title={'OK' if has_title else 'MISSING'}, desc={'OK' if has_desc else 'MISSING'}")
    else:
        print(f"  ✗ {level}: NOT FOUND in JOB_TEMPLATES")

print("\nAll keys containing 'software_engineer_intern':")
for key in JOB_TEMPLATES.keys():
    if 'software_engineer_intern' in key:
        print(f"  - {key}")

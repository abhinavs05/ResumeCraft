document.addEventListener('DOMContentLoaded', function() {
    // Tab switching logic
    const tabs = document.querySelectorAll('.step-tab-btn');
    const steps = document.querySelectorAll('.form-step-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const stepId = tab.dataset.step;
            
            // Remove active from all tabs & steps
            tabs.forEach(t => t.classList.remove('active'));
            steps.forEach(s => s.classList.remove('active'));

            // Add active to current
            tab.classList.add('active');
            document.getElementById(`step-${stepId}`).classList.add('active');
        });
    });

    // Helper to setup dynamic card removal
    function setupRemoveButtons() {
        document.querySelectorAll('.remove-row-btn').forEach(btn => {
            btn.onclick = function() {
                const card = this.closest('.dynamic-row-card');
                if (card) {
                    card.remove();
                    triggerPreviewUpdate();
                }
            };
        });
    }
    setupRemoveButtons();

    // Dynamic addition templates
    const templates = {
        education: `
            <div class="dynamic-row-card">
                <button type="button" class="remove-row-btn"><i class="fa-solid fa-trash"></i> Remove</button>
                <div class="form-group">
                    <label class="form-label">Institution / School</label>
                    <input type="text" name="institution[]" class="form-input" placeholder="e.g. Guru Gobind Singh Indraprastha University">
                </div>
                <div class="form-group-row" style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
                    <div>
                        <label class="form-label">Degree</label>
                        <input type="text" name="degree[]" class="form-input" placeholder="e.g. B.Tech">
                    </div>
                    <div>
                        <label class="form-label">Major / Field of Study</label>
                        <input type="text" name="major[]" class="form-input" placeholder="e.g. Information Technology">
                    </div>
                </div>
                <div class="form-group-row" style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
                    <div>
                        <label class="form-label">GPA</label>
                        <input type="text" name="gpa[]" class="form-input" placeholder="e.g. 8.5/10">
                    </div>
                    <div>
                        <label class="form-label">Location</label>
                        <input type="text" name="location[]" class="form-input" placeholder="e.g. New Delhi">
                    </div>
                </div>
                <div class="form-group-row" style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
                    <div>
                        <label class="form-label">Start Date</label>
                        <input type="text" name="start_date[]" class="form-input" placeholder="e.g. Aug 2023">
                    </div>
                    <div>
                        <label class="form-label">End Date</label>
                        <input type="text" name="end_date[]" class="form-input" placeholder="e.g. May 2027">
                    </div>
                </div>
                <div class="form-group" style="margin-bottom: 0;">
                    <label class="form-label">Description (Optional)</label>
                    <textarea name="description[]" class="form-input" rows="2" placeholder="Relevant coursework, achievements, etc."></textarea>
                </div>
            </div>
        `,
        experience: `
            <div class="dynamic-row-card">
                <button type="button" class="remove-row-btn"><i class="fa-solid fa-trash"></i> Remove</button>
                <div class="form-group">
                    <label class="form-label">Company Name</label>
                    <input type="text" name="company[]" class="form-input" placeholder="e.g. Google">
                </div>
                <div class="form-group">
                    <label class="form-label">Position / Title</label>
                    <input type="text" name="position[]" class="form-input" placeholder="e.g. Software Engineer Intern">
                </div>
                <div class="form-group-row" style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
                    <div>
                        <label class="form-label">Location</label>
                        <input type="text" name="exp_location[]" class="form-input" placeholder="e.g. Mountain View, CA">
                    </div>
                    <div>
                        <label class="form-label">Dates (Start - End)</label>
                        <input type="text" name="exp_dates[]" class="form-input" placeholder="e.g. Jun 2025 - Aug 2025">
                    </div>
                </div>
                <div class="form-group" style="margin-bottom: 0;">
                    <label class="form-label">Description (Bullet points, one per line)</label>
                    <textarea name="exp_description[]" class="form-input" rows="4" placeholder="- Developed X using Y...\\n- Improved performance by Z%..."></textarea>
                </div>
            </div>
        `,
        project: `
            <div class="dynamic-row-card">
                <button type="button" class="remove-row-btn"><i class="fa-solid fa-trash"></i> Remove</button>
                <div class="form-group">
                    <label class="form-label">Project Title</label>
                    <input type="text" name="proj_title[]" class="form-input" placeholder="e.g. Resume Builder">
                </div>
                <div class="form-group">
                    <label class="form-label">Technologies Used</label>
                    <input type="text" name="proj_technologies[]" class="form-input" placeholder="e.g. Django, LaTeX, HTML/CSS">
                </div>
                <div class="form-group-row" style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
                    <div>
                        <label class="form-label">Project Link (Optional)</label>
                        <input type="url" name="proj_link[]" class="form-input" placeholder="https://github.com/...">
                    </div>
                    <div>
                        <label class="form-label">Dates (Optional)</label>
                        <input type="text" name="proj_dates[]" class="form-input" placeholder="e.g. Jan 2026">
                    </div>
                </div>
                <div class="form-group" style="margin-bottom: 0;">
                    <label class="form-label">Description (Bullet points, one per line)</label>
                    <textarea name="proj_description[]" class="form-input" rows="3" placeholder="- Built a full-stack Django app...\\n- Generated ATS resumes using LaTeX..."></textarea>
                </div>
            </div>
        `,
        skill: `
            <div class="dynamic-row-card">
                <button type="button" class="remove-row-btn"><i class="fa-solid fa-trash"></i> Remove</button>
                <div class="form-group" style="margin-bottom: 0;">
                    <div style="display: grid; grid-template-columns: 1fr 2fr; gap: 1rem;">
                        <div>
                            <label class="form-label">Category</label>
                            <input type="text" name="skill_category[]" class="form-input" placeholder="e.g. Languages">
                        </div>
                        <div>
                            <label class="form-label">Skills (Comma separated)</label>
                            <input type="text" name="skills[]" class="form-input" placeholder="e.g. C++, Python, Java">
                        </div>
                    </div>
                </div>
            </div>
        `,
        achievement: `
            <div class="dynamic-row-card">
                <button type="button" class="remove-row-btn"><i class="fa-solid fa-trash"></i> Remove</button>
                <div class="form-group">
                    <label class="form-label">Achievement Title</label>
                    <input type="text" name="ach_title[]" class="form-input" placeholder="e.g. Solved 400+ coding challenges">
                </div>
                <div class="form-group">
                    <label class="form-label">Date (Optional)</label>
                    <input type="text" name="ach_date[]" class="form-input" placeholder="e.g. 2026">
                </div>
                <div class="form-group" style="margin-bottom: 0;">
                    <label class="form-label">Description (Optional)</label>
                    <textarea name="ach_description[]" class="form-input" rows="2" placeholder="Brief context..."></textarea>
                </div>
            </div>
        `
    };

    // Generic function to append dynamic row card
    window.addDynamicRow = function(type) {
        const container = document.getElementById(`${type}-container`);
        if (container) {
            container.insertAdjacentHTML('beforeend', templates[type]);
            setupRemoveButtons();
            setupLiveBinding();
            triggerPreviewUpdate();
        }
    };

    // Live HTML Preview update logic
    const previewContainer = document.getElementById('preview-content-area');
    const builderForm = document.getElementById('resume-builder-form');
    const templateSelector = document.getElementById('template-selector');
    let previewDebounceTimer;

    function triggerPreviewUpdate() {
        if (!builderForm) return;

        clearTimeout(previewDebounceTimer);
        previewDebounceTimer = setTimeout(() => {
            const formData = new FormData(builderForm);
            
            // Add current template selected
            if (templateSelector) {
                formData.set('template_name', templateSelector.value);
            }

            // Post to AJAX preview URL
            const previewUrl = builderForm.dataset.previewUrl;
            fetch(previewUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.text())
            .then(html => {
                if (previewContainer) {
                    previewContainer.innerHTML = html;
                }
            })
            .catch(err => console.error("Preview render error:", err));
        }, 300); // 300ms debounce
    }

    // Setup live binding to form inputs
    function setupLiveBinding() {
        if (!builderForm) return;
        builderForm.querySelectorAll('input, textarea').forEach(el => {
            el.removeEventListener('input', triggerPreviewUpdate);
            el.addEventListener('input', triggerPreviewUpdate);
        });
    }

    if (templateSelector) {
        templateSelector.addEventListener('change', triggerPreviewUpdate);
    }

    setupLiveBinding();
    triggerPreviewUpdate();

    // Export preview update function globally for trigger
    window.triggerPreviewUpdate = triggerPreviewUpdate;

    // Handle quick zoom functions for preview pane
    let zoomLevel = 0.8;
    const zoomInBtn = document.getElementById('zoom-in');
    const zoomOutBtn = document.getElementById('zoom-out');
    const resumePreview = document.querySelector('.resume-preview-container');

    if (resumePreview) {
        resumePreview.style.transform = `scale(${zoomLevel})`;
    }

    if (zoomInBtn && zoomOutBtn && resumePreview) {
        zoomInBtn.onclick = function() {
            if (zoomLevel < 1.2) {
                zoomLevel += 0.1;
                resumePreview.style.transform = `scale(${zoomLevel})`;
            }
        };
        zoomOutBtn.onclick = function() {
            if (zoomLevel > 0.4) {
                zoomLevel -= 0.1;
                resumePreview.style.transform = `scale(${zoomLevel})`;
            }
        };
    }
});

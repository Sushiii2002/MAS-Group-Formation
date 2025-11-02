// ============================================================
// MAS GROUP FORMATION SYSTEM - MAIN JAVASCRIPT
// ============================================================

// Configuration - DECLARE ONLY ONCE
const API_BASE = 'http://localhost:5000/api';

// ============================================================
// UTILITY FUNCTIONS
// ============================================================

/**
 * Make API request with fetch
 * @param {string} endpoint - API endpoint (e.g., '/students')
 * @param {object} options - Fetch options (method, body, etc.)
 * @returns {Promise} - Promise resolving to response data
 */
async function apiRequest(endpoint, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    const config = { ...defaultOptions, ...options };
    
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, config);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('API Request Error:', error);
        throw error;
    }
}

/**
 * Show loading spinner
 * @param {string} elementId - ID of element to show loading in
 */
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '<p class="loading-text">Loading...</p>';
    }
}

/**
 * Show error message
 * @param {string} elementId - ID of element to show error in
 * @param {string} message - Error message
 */
function showError(elementId, message) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `<p class="error-text">${message}</p>`;
    }
}

/**
 * Show success message
 * @param {string} elementId - ID of element
 * @param {string} message - Success message
 */
function showSuccess(elementId, message) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `<div class="alert alert-success">${message}</div>`;
    }
}

/**
 * Format date to readable string
 * @param {string} dateString - ISO date string
 * @returns {string} - Formatted date
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
    });
}

/**
 * Validate email format
 * @param {string} email - Email address
 * @returns {boolean} - True if valid
 */
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

/**
 * Validate GWA (1.00 - 5.00)
 * @param {number} gwa - GWA value
 * @returns {boolean} - True if valid
 */
function validateGWA(gwa) {
    return gwa >= 1.00 && gwa <= 5.00;
}

// ============================================================
// FORM VALIDATION AND SUBMISSION
// ============================================================

/**
 * Validate registration form
 * @param {FormData} formData - Form data object
 * @returns {object} - { valid: boolean, errors: array }
 */
function validateRegistrationForm(formData) {
    const errors = [];
    
    // Check required fields
    const requiredFields = ['student_number', 'first_name', 'last_name', 'email', 'gwa', 'year_level'];
    requiredFields.forEach(field => {
        if (!formData.get(field)) {
            errors.push(`${field.replace('_', ' ')} is required`);
        }
    });
    
    // Validate email
    const email = formData.get('email');
    if (email && !validateEmail(email)) {
        errors.push('Invalid email format');
    }
    
    // Validate GWA
    const gwa = parseFloat(formData.get('gwa'));
    if (gwa && !validateGWA(gwa)) {
        errors.push('GWA must be between 1.00 and 5.00');
    }
    
    return {
        valid: errors.length === 0,
        errors: errors
    };
}

/**
 * Collect form data and prepare for submission
 * @param {HTMLFormElement} form - Form element
 * @returns {object} - Prepared data object
 */
function prepareFormData(form) {
    const formData = new FormData(form);
    const data = {};
    
    // Basic fields
    data.student_number = formData.get('student_number');
    data.first_name = formData.get('first_name');
    data.last_name = formData.get('last_name');
    data.email = formData.get('email');
    data.gwa = parseFloat(formData.get('gwa'));
    data.year_level = parseInt(formData.get('year_level'));
    data.program = 'Computer Science';
    
    return data;
}

/**
 * Collect skills from form
 * @returns {array} - Array of skill objects
 */
function collectSkills() {
    const skills = [];
    const skillSelects = document.querySelectorAll('.skill-select');
    const proficiencySelects = document.querySelectorAll('.proficiency-select');
    const yearsInputs = document.querySelectorAll('.years-input');
    
    for (let i = 0; i < skillSelects.length; i++) {
        const skill = skillSelects[i].value;
        const proficiency = proficiencySelects[i].value;
        const years = parseFloat(yearsInputs[i].value) || 0;
        
        if (skill && proficiency) {
            skills.push({
                skill_name: skill,
                proficiency_level: proficiency,
                years_experience: years
            });
        }
    }
    
    return skills;
}

/**
 * Collect personality traits from form
 * @returns {object} - Personality traits object
 */
function collectPersonalityTraits() {
    return {
        openness: parseInt(document.getElementById('openness')?.value || 3),
        conscientiousness: parseInt(document.getElementById('conscientiousness')?.value || 3),
        extraversion: parseInt(document.getElementById('extraversion')?.value || 3),
        agreeableness: parseInt(document.getElementById('agreeableness')?.value || 3),
        neuroticism: parseInt(document.getElementById('neuroticism')?.value || 3),
        learning_style: document.getElementById('learning-style')?.value || 'Visual'
    };
}

/**
 * Collect availability from checkboxes
 * @returns {array} - Array of availability slots
 */
function collectAvailability() {
    const availability = [];
    const checkboxes = document.querySelectorAll('input[name="avail[]"]:checked');
    
    checkboxes.forEach(checkbox => {
        const [day, time] = checkbox.value.split('_');
        availability.push({
            day_of_week: day,
            time_slot: time,
            is_available: 1
        });
    });
    
    return availability;
}

// ============================================================
// API INTERACTION FUNCTIONS
// ============================================================

/**
 * Submit student registration
 * @param {object} studentData - Student data
 * @returns {Promise} - Promise with student ID
 */
async function submitStudentRegistration(studentData) {
    return await apiRequest('/students', {
        method: 'POST',
        body: JSON.stringify(studentData)
    });
}

/**
 * Add skills to student
 * @param {number} studentId - Student ID
 * @param {array} skills - Array of skills
 * @returns {Promise}
 */
async function addStudentSkills(studentId, skills) {
    return await apiRequest(`/students/${studentId}/skills`, {
        method: 'POST',
        body: JSON.stringify({ skills })
    });
}

/**
 * Get all students
 * @returns {Promise} - Promise with students array
 */
async function getAllStudents() {
    return await apiRequest('/students');
}

/**
 * Get single student
 * @param {number} studentId - Student ID
 * @returns {Promise}
 */
async function getStudent(studentId) {
    return await apiRequest(`/students/${studentId}`);
}

/**
 * Get all groups
 * @returns {Promise}
 */
async function getAllGroups() {
    return await apiRequest('/groups');
}

/**
 * Form new groups
 * @param {object} options - Grouping options
 * @returns {Promise}
 */
async function formGroups(options = {}) {
    const defaultOptions = {
        target_group_size: 4,
        algorithm: 'ga',
        clear_existing: false
    };
    
    return await apiRequest('/groups/form', {
        method: 'POST',
        body: JSON.stringify({ ...defaultOptions, ...options })
    });
}

/**
 * Get faculty dashboard data
 * @returns {Promise}
 */
async function getFacultyDashboard() {
    return await apiRequest('/dashboard/faculty');
}

/**
 * Get student dashboard data
 * @param {number} studentId - Student ID
 * @returns {Promise}
 */
async function getStudentDashboard(studentId) {
    return await apiRequest(`/dashboard/student/${studentId}`);
}

/**
 * Update task status
 * @param {number} taskId - Task ID
 * @param {object} data - Update data
 * @returns {Promise}
 */
async function updateTaskStatus(taskId, data) {
    return await apiRequest(`/tasks/${taskId}/status`, {
        method: 'PUT',
        body: JSON.stringify(data)
    });
}

// ============================================================
// DOM MANIPULATION FUNCTIONS
// ============================================================

/**
 * Create group card element
 * @param {object} group - Group data
 * @returns {HTMLElement} - Group card element
 */
function createGroupCard(group) {
    const card = document.createElement('div');
    card.className = 'group-card';
    
    const membersHtml = group.members.map(member => `
        <div class="member-item">
            <span class="member-name">${member.first_name} ${member.last_name}</span>
            <span class="member-role ${member.role.toLowerCase()}">${member.role}</span>
            <span class="member-gwa">GWA: ${member.gwa}</span>
        </div>
    `).join('');
    
    card.innerHTML = `
        <div class="group-header">
            <h3>${group.group_name}</h3>
            <span class="compatibility-badge">
                Compatibility: ${group.compatibility_score.toFixed(3)}
            </span>
        </div>
        <div class="group-info">
            <span class="group-stat">👥 ${group.member_count} members</span>
            <span class="group-stat">📅 ${formatDate(group.formation_date)}</span>
            <span class="group-status ${group.status.toLowerCase()}">${group.status}</span>
        </div>
        <div class="group-members">
            ${membersHtml}
        </div>
        <div class="group-actions">
            <button class="btn btn-small" onclick="viewGroupDetails(${group.id})">View Details</button>
            <button class="btn btn-small btn-secondary" onclick="allocateGroupTasks(${group.id})">Allocate Tasks</button>
        </div>
    `;
    
    return card;
}

/**
 * Create task card element
 * @param {object} task - Task data
 * @returns {HTMLElement} - Task card element
 */
function createTaskCard(task) {
    const card = document.createElement('div');
    card.className = `task-card status-${task.status.toLowerCase().replace(' ', '-')}`;
    
    const deadline = new Date(task.deadline);
    const today = new Date();
    const daysLeft = Math.ceil((deadline - today) / (1000 * 60 * 60 * 24));
    
    card.innerHTML = `
        <div class="task-header">
            <h4>${task.task_name}</h4>
            <span class="task-status ${task.status.toLowerCase().replace(' ', '-')}">
                ${task.status}
            </span>
        </div>
        <p class="task-description">${task.description}</p>
        <div class="task-meta">
            <span>⏱️ ${task.estimated_hours}h</span>
            <span>📅 ${daysLeft > 0 ? `${daysLeft} days left` : 'Overdue'}</span>
        </div>
        <div class="task-progress">
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${task.completion_percentage}%"></div>
            </div>
            <span class="progress-text">${task.completion_percentage}%</span>
        </div>
        <button class="btn btn-small" onclick="updateTaskProgress(${task.id}, ${task.completion_percentage})">
            Update Progress
        </button>
    `;
    
    return card;
}

/**
 * Populate dropdown with options
 * @param {string} selectId - Select element ID
 * @param {array} options - Array of {value, text} objects
 */
function populateDropdown(selectId, options) {
    const select = document.getElementById(selectId);
    if (!select) return;
    
    select.innerHTML = '<option value="">Select...</option>';
    
    options.forEach(option => {
        const optElement = document.createElement('option');
        optElement.value = option.value;
        optElement.textContent = option.text;
        select.appendChild(optElement);
    });
}

/**
 * Update statistics display
 * @param {object} stats - Statistics data
 */
function updateStatistics(stats) {
    const elements = {
        'stat-students': stats.summary?.total_students || '--',
        'stat-groups': stats.summary?.total_groups || '--',
        'stat-tasks': stats.summary?.total_tasks || '--',
        'stat-compatibility': stats.compatibility?.avg_score 
            ? stats.compatibility.avg_score.toFixed(3) 
            : '--'
    };
    
    Object.entries(elements).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    });
}

// ============================================================
// EVENT HANDLERS
// ============================================================

/**
 * Handle range slider value updates
 * @param {HTMLInputElement} slider - Range input element
 */
function updateRangeValue(slider) {
    const valueSpan = slider.nextElementSibling;
    if (valueSpan) {
        valueSpan.textContent = slider.value;
    }
}

/**
 * Add skill entry to form
 */
function addSkillEntry() {
    const container = document.getElementById('skills-container');
    if (!container) return;
    
    const skillCounter = container.children.length + 1;
    const newEntry = document.createElement('div');
    newEntry.className = 'skill-entry';
    newEntry.innerHTML = `
        <div class="form-row">
            <div class="form-group">
                <label for="skill-${skillCounter}">Skill</label>
                <select id="skill-${skillCounter}" name="skills[]" class="skill-select">
                    <option value="">Select Skill</option>
                    <option value="Python">Python</option>
                    <option value="Java">Java</option>
                    <option value="JavaScript">JavaScript</option>
                    <option value="HTML/CSS">HTML/CSS</option>
                    <option value="React">React</option>
                    <option value="Node.js">Node.js</option>
                    <option value="MySQL">MySQL</option>
                    <option value="MongoDB">MongoDB</option>
                    <option value="Git">Git</option>
                    <option value="Docker">Docker</option>
                    <option value="Flask">Flask</option>
                    <option value="Django">Django</option>
                </select>
            </div>
            <div class="form-group">
                <label for="proficiency-${skillCounter}">Proficiency</label>
                <select id="proficiency-${skillCounter}" name="proficiency[]" class="proficiency-select">
                    <option value="">Select Level</option>
                    <option value="Beginner">Beginner</option>
                    <option value="Intermediate">Intermediate</option>
                    <option value="Advanced">Advanced</option>
                    <option value="Expert">Expert</option>
                </select>
            </div>
            <div class="form-group">
                <label for="years-${skillCounter}">Years</label>
                <input type="number" id="years-${skillCounter}" name="years[]" 
                       min="0" max="10" step="0.5" 
                       placeholder="1.5" class="years-input">
            </div>
            <button type="button" class="btn-remove" onclick="removeSkillEntry(this)">✕</button>
        </div>
    `;
    container.appendChild(newEntry);
}

/**
 * Remove skill entry from form
 * @param {HTMLButtonElement} button - Remove button
 */
function removeSkillEntry(button) {
    button.closest('.skill-entry').remove();
}

/**
 * Refresh page data
 */
async function refreshData() {
    const statusDiv = document.getElementById('operation-status');
    if (statusDiv) {
        statusDiv.style.display = 'block';
        statusDiv.className = 'status-message info';
        statusDiv.textContent = '🔄 Refreshing data...';
    }
    
    // Reload current page data
    window.location.reload();
}

// ============================================================
// PAGE-SPECIFIC FUNCTIONS
// ============================================================

/**
 * View group details in a modal
 * @param {number} groupId - Group ID
 */
async function viewGroupDetails(groupId) {
    try {
        showLoadingModal();
        
        const response = await apiRequest(`/groups/${groupId}`);
        
        if (!response.success) {
            alert('Failed to load group details');
            closeGroupModal();
            return;
        }
        
        const group = response.data;
        
        // Create modal content with better styling
        const modalContent = `
            <div style="background: white; padding: 30px; border-radius: 10px; max-width: 800px; max-height: 85vh; overflow-y: auto; position: relative;">
                <button onclick="closeGroupModal()" style="
                    position: absolute;
                    top: 15px;
                    right: 15px;
                    background: transparent;
                    border: none;
                    font-size: 28px;
                    cursor: pointer;
                    color: #718096;
                    line-height: 1;
                    padding: 0;
                    width: 30px;
                    height: 30px;
                ">&times;</button>
                
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; margin: -30px -30px 20px -30px;">
                    <h2 style="margin: 0 0 10px 0; font-size: 1.8em;">${group.group_name}</h2>
                    <div style="display: flex; gap: 20px; flex-wrap: wrap; opacity: 0.95;">
                        <span>⭐ Compatibility: <strong>${group.compatibility_score.toFixed(3)}</strong></span>
                        <span>📅 Formed: <strong>${formatDate(group.formation_date)}</strong></span>
                        <span style="background: rgba(255,255,255,0.2); padding: 4px 12px; border-radius: 12px;">
                            <strong>${group.status}</strong>
                        </span>
                    </div>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 25px;">
                    <div style="background: #f7fafc; padding: 15px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 2em; color: #667eea; font-weight: bold;">${group.members.length}</div>
                        <div style="color: #718096; font-size: 0.9em;">Team Members</div>
                    </div>
                    <div style="background: #f7fafc; padding: 15px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 2em; color: #667eea; font-weight: bold;">${group.tasks.length}</div>
                        <div style="color: #718096; font-size: 0.9em;">Total Tasks</div>
                    </div>
                </div>
                
                <h3 style="margin: 25px 0 15px 0; color: #2d3748; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px;">
                    👥 Team Members
                </h3>
                <div style="display: grid; gap: 10px; margin-bottom: 25px;">
                    ${group.members.map(member => `
                        <div style="padding: 12px 15px; background: #f7fafc; margin-bottom: 8px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; border-left: 4px solid ${member.role === 'Leader' ? '#f59e0b' : '#667eea'};">
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <span style="font-size: 1.5em;">${member.role === 'Leader' ? '👑' : '👤'}</span>
                                <div>
                                    <div style="font-weight: 600; color: #2d3748;">${member.first_name} ${member.last_name}</div>
                                    <div style="font-size: 0.85em; color: #718096;">${member.email}</div>
                                </div>
                            </div>
                            <div style="text-align: right;">
                                <div style="font-size: 0.75em; text-transform: uppercase; font-weight: 600; color: ${member.role === 'Leader' ? '#f59e0b' : '#667eea'}; margin-bottom: 2px;">
                                    ${member.role}
                                </div>
                                <div style="color: #4a5568; font-weight: 500;">GWA: ${member.gwa}</div>
                            </div>
                        </div>
                    `).join('')}
                </div>
                
                <h3 style="margin: 25px 0 15px 0; color: #2d3748; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px;">
                    📋 Assigned Tasks
                </h3>
                ${group.tasks.length > 0 ? `
                    <div style="display: grid; gap: 12px;">
                        ${group.tasks.map(task => {
                            const statusColors = {
                                'Pending': '#718096',
                                'In Progress': '#ed8936',
                                'Completed': '#48bb78',
                                'Overdue': '#f56565'
                            };
                            const statusColor = statusColors[task.status] || '#718096';
                            
                            return `
                                <div style="padding: 15px; background: #ffffff; border: 1px solid #e2e8f0; border-left: 4px solid ${statusColor}; border-radius: 8px;">
                                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                                        <div style="font-weight: 600; color: #2d3748; font-size: 1.05em; flex: 1;">${task.task_name}</div>
                                        <span style="background: ${statusColor}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.75em; font-weight: 600; white-space: nowrap; margin-left: 10px;">
                                            ${task.status}
                                        </span>
                                    </div>
                                    <p style="font-size: 0.9em; color: #4a5568; margin: 8px 0; line-height: 1.5;">
                                        ${task.description || 'No description provided'}
                                    </p>
                                    <div style="display: flex; gap: 15px; font-size: 0.85em; color: #718096; margin-top: 10px;">
                                        <span>⏱️ ${task.estimated_hours}h</span>
                                        <span>📅 Due: ${formatDate(task.deadline)}</span>
                                        ${task.complexity_level ? `<span>🎯 ${task.complexity_level}</span>` : ''}
                                    </div>
                                </div>
                            `;
                        }).join('')}
                    </div>
                ` : `
                    <div style="text-align: center; padding: 40px; color: #718096; background: #f7fafc; border-radius: 8px;">
                        <div style="font-size: 3em; margin-bottom: 10px;">📝</div>
                        <p style="margin: 0;">No tasks assigned yet</p>
                        <p style="margin: 5px 0 0 0; font-size: 0.9em;">Click "Allocate Tasks" to assign tasks to this group</p>
                    </div>
                `}
                
                <div style="margin-top: 25px; padding-top: 20px; border-top: 1px solid #e2e8f0; display: flex; gap: 10px; justify-content: flex-end;">
                    <button onclick="closeGroupModal()" style="
                        padding: 10px 24px;
                        background: #e2e8f0;
                        color: #2d3748;
                        border: none;
                        border-radius: 6px;
                        cursor: pointer;
                        font-size: 15px;
                        font-weight: 500;
                    ">Close</button>
                    ${group.tasks.length === 0 ? `
                        <button onclick="allocateGroupTasks(${group.id}); closeGroupModal();" style="
                            padding: 10px 24px;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white;
                            border: none;
                            border-radius: 6px;
                            cursor: pointer;
                            font-size: 15px;
                            font-weight: 500;
                        ">Allocate Tasks</button>
                    ` : ''}
                </div>
            </div>
        `;
        
        // Create modal overlay
        const modal = document.getElementById('group-details-modal') || document.createElement('div');
        modal.id = 'group-details-modal';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.75);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10000;
            animation: fadeIn 0.2s ease-out;
        `;
        modal.innerHTML = modalContent;
        
        // Close on background click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeGroupModal();
            }
        });
        
        // Close on Escape key
        const escapeHandler = (e) => {
            if (e.key === 'Escape') {
                closeGroupModal();
                document.removeEventListener('keydown', escapeHandler);
            }
        };
        document.addEventListener('keydown', escapeHandler);
        
        document.body.appendChild(modal);
        
    } catch (error) {
        console.error('Error viewing group details:', error);
        alert('Failed to load group details. Please try again.');
        closeGroupModal();
    }
}

/**
 * Show loading modal
 */
function showLoadingModal() {
    const modal = document.createElement('div');
    modal.id = 'group-details-modal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.75);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 10000;
    `;
    modal.innerHTML = `
        <div style="background: white; padding: 40px; border-radius: 10px; text-align: center;">
            <div style="font-size: 3em; margin-bottom: 15px;">⏳</div>
            <div style="color: #4a5568; font-size: 1.1em;">Loading group details...</div>
        </div>
    `;
    document.body.appendChild(modal);
}

/**
 * Close group details modal
 */
function closeGroupModal() {
    const modal = document.getElementById('group-details-modal');
    if (modal) {
        modal.remove();
    }
}

/**
 * Allocate tasks to a group
 * @param {number} groupId - Group ID
 */
async function allocateGroupTasks(groupId) {
    if (!confirm('Allocate tasks for this group? This will create and assign 6 sample tasks.')) return;
    
    try {
        const response = await apiRequest(`/groups/${groupId}/allocate-tasks`, {
            method: 'POST'
        });
        
        if (response.success) {
            alert(`✓ ${response.message}\n\nTasks allocated: ${response.data.tasks_allocated}`);
            window.location.reload();
        } else {
            throw new Error(response.message);
        }
    } catch (error) {
        console.error('Error allocating tasks:', error);
        alert('Failed to allocate tasks: ' + error.message);
    }
}

/**
 * Update task progress
 * @param {number} taskId - Task ID
 * @param {number} currentProgress - Current completion percentage
 */
async function updateTaskProgress(taskId, currentProgress) {
    const newProgress = prompt(`Enter completion percentage (current: ${currentProgress}%):`, currentProgress);
    
    if (newProgress === null) return;
    
    const percentage = parseInt(newProgress);
    
    if (isNaN(percentage) || percentage < 0 || percentage > 100) {
        alert('Please enter a valid percentage between 0 and 100');
        return;
    }
    
    try {
        const result = await updateTaskStatus(taskId, {
            completion_percentage: percentage,
            status: percentage === 100 ? 'Completed' : 'In Progress'
        });
        
        if (result.success) {
            alert('Progress updated successfully!');
            window.location.reload();
        } else {
            throw new Error(result.message);
        }
    } catch (error) {
        console.error('Error updating task:', error);
        alert('Failed to update task progress');
    }
}

// ============================================================
// INITIALIZATION
// ============================================================

/**
 * Initialize page-specific functionality
 */
document.addEventListener('DOMContentLoaded', () => {
    console.log('✅ MAS System JavaScript initialized');
    
    // Add keyboard navigation support for accessibility
    document.addEventListener('keydown', (e) => {
        // Allow Escape key to close modals or cancel operations
        if (e.key === 'Escape') {
            // Close any open modals or dialogs
            const modals = document.querySelectorAll('.modal.open');
            modals.forEach(modal => modal.classList.remove('open'));
        }
    });
    
    // Add focus visible class for keyboard navigation
    document.addEventListener('mousedown', () => {
        document.body.classList.add('using-mouse');
    });
    
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Tab') {
            document.body.classList.remove('using-mouse');
        }
    });
});

// Make functions globally available
window.apiRequest = apiRequest;
window.updateRangeValue = updateRangeValue;
window.addSkillEntry = addSkillEntry;
window.removeSkillEntry = removeSkillEntry;
window.refreshData = refreshData;
window.viewGroupDetails = viewGroupDetails;
window.closeGroupModal = closeGroupModal;
window.allocateGroupTasks = allocateGroupTasks;
window.updateTaskProgress = updateTaskProgress;
window.getAllStudents = getAllStudents;
window.getAllGroups = getAllGroups;
window.formGroups = formGroups;
window.getFacultyDashboard = getFacultyDashboard;
window.getStudentDashboard = getStudentDashboard;
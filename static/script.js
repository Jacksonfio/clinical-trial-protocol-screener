const API_BASE = window.location.origin;

// State management
let currentTask = null;
let currentObservation = null;
let currentScore = 0.0;
let stepCount = 0;

// UI Elements
const taskList = document.getElementById('task-list');
const patientContent = document.getElementById('patient-content');
const idleScreen = document.getElementById('idle-screen');
const consoleLog = document.getElementById('console-log');
const scoreProgress = document.getElementById('score-progress');
const currentScoreEl = document.getElementById('current-score');
const lastRewardEl = document.getElementById('last-reward');
const clockEl = document.getElementById('hud-clock');

// Initialization
document.addEventListener('DOMContentLoaded', () => {
    fetchTasks();
    updateClock();
    setInterval(updateClock, 1000);
    
    // Bind buttons
    document.getElementById('btn-approve').addEventListener('click', () => handleAction('approve'));
    document.getElementById('btn-reject').addEventListener('click', () => handleAction('reject'));
    document.getElementById('btn-info').addEventListener('click', () => handleAction('request_more_info'));
});

function updateClock() {
    const now = new Date();
    clockEl.textContent = now.toTimeString().split(' ')[0];
}

function log(message, type = 'info') {
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    entry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
    consoleLog.prepend(entry);
}

// Fetch Tasks
async function fetchTasks() {
    try {
        const response = await fetch(`${API_BASE}/tasks`);
        const data = await response.json();
        renderTasks(data);
    } catch (err) {
        log('FAILED TO FETCH PROTOCOLS', 'error');
    }
}

function renderTasks(tasks) {
    taskList.innerHTML = '';
    Object.keys(tasks).forEach(id => {
        const task = tasks[id];
        const card = document.createElement('div');
        card.className = 'task-card';
        card.innerHTML = `
            <div style="font-weight:bold; color:var(--accent-teal)">${id.toUpperCase()}</div>
            <div style="font-size:12px">${task.name}</div>
            <div style="font-size:10px; opacity:0.6">${task.num_patients} PATIENTS</div>
        `;
        card.onclick = () => startTask(id, card);
        taskList.appendChild(card);
    });
}

// Start/Reset Task
async function startTask(taskId, element) {
    document.querySelectorAll('.task-card').forEach(c => c.classList.remove('active'));
    element.classList.add('active');
    
    log(`INITIALIZING PROTOCOL: ${taskId.toUpperCase()}...`);
    currentTask = taskId;
    document.getElementById('current-task-id').textContent = taskId.toUpperCase();
    
    try {
        const response = await fetch(`${API_BASE}/reset?task_id=${taskId}`, { method: 'POST' });
        currentObservation = await response.json();
        updatePatientUI();
        enableButtons(true);
        patientContent.classList.remove('hidden');
        idleScreen.classList.add('hidden');
        currentScore = 0;
        stepCount = 0;
        updateScore(0);
    } catch (err) {
        log('PROTOCOL INITIALIZATION FAILED', 'error');
    }
}

function updatePatientUI() {
    if (!currentObservation) return;
    const p = currentObservation.patient;
    
    document.getElementById('patient-id').textContent = p.id;
    document.getElementById('patient-age').textContent = `${p.age}Y`;
    document.getElementById('patient-sex').textContent = p.sex.toUpperCase();
    document.getElementById('protocol-name').textContent = currentObservation.protocol_name;

    // Conditions
    const condList = document.getElementById('patient-conditions');
    condList.innerHTML = p.conditions.map(c => `<li>${c}</li>`).join('');

    // Meds
    const medList = document.getElementById('patient-medications');
    medList.innerHTML = p.medications.map(m => `<li>${m}</li>`).join('');

    // Labs
    const labGrid = document.getElementById('patient-labs');
    labGrid.innerHTML = Object.keys(p.labs).map(key => `
        <div class="lab-item">
            <span class="name">${key.toUpperCase()}</span>
            <span class="val">${p.labs[key]}</span>
        </div>
    `).join('');

    // Fetch Protocol Info from state or cached
    fetchProtocolInfo();
}

async function fetchProtocolInfo() {
    // We could get this from /state or just trust the obs
    // For simplicity, showing hardcoded or generic placeholders 
    // since the API /tasks returns basic info.
}

// Handle Action
async function handleAction(decision) {
    enableButtons(false);
    log(`RECORDING DECISION: ${decision.toUpperCase()}...`);
    
    try {
        const response = await fetch(`${API_BASE}/step`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ decision, rationale: 'User manual screening' })
        });
        const data = await response.json();
        
        showFeedback(data.reward.value);
        currentObservation = data.observation;
        stepCount++;
        
        // Cumulative score roughly
        currentScore = (currentScore * (stepCount-1) + data.reward.value) / stepCount;
        updateScore(currentScore);
        
        if (data.done) {
            log('ENVIRONMENT DONE. TASK COMPLETE.', 'success');
            finishTask();
        } else {
            updatePatientUI();
            enableButtons(true);
        }
    } catch (err) {
        log('DECISION PROCESSING ERROR', 'error');
        enableButtons(true);
    }
}

function updateScore(score) {
    const val = (score * 100).toFixed(1);
    currentScoreEl.textContent = score.toFixed(2);
    scoreProgress.style.width = `${val}%`;
}

function showFeedback(reward) {
    const overlay = document.getElementById('feedback-overlay');
    const rewardEl = document.getElementById('feedback-reward');
    const resultEl = document.getElementById('feedback-result');
    
    rewardEl.textContent = `+${reward.toFixed(1)}`;
    lastRewardEl.textContent = `+${reward.toFixed(1)}`;
    
    if (reward >= 1.0) {
        resultEl.textContent = "ACCURATE MATCH";
        rewardEl.style.color = "var(--green-success)";
    } else if (reward > 0) {
        resultEl.textContent = "PARTIAL MATCH";
        rewardEl.style.color = "var(--gold)";
    } else {
        resultEl.textContent = "MISMATCH DETECTED";
        rewardEl.style.color = "var(--red-alert)";
    }

    overlay.classList.remove('hidden');
    setTimeout(() => overlay.classList.add('hidden'), 1000);
}

function enableButtons(enabled) {
    document.getElementById('btn-approve').disabled = !enabled;
    document.getElementById('btn-reject').disabled = !enabled;
    document.getElementById('btn-info').disabled = !enabled;
}

async function finishTask() {
    const response = await fetch(`${API_BASE}/grader`);
    const final = await response.json();
    log(`FINAL EVALUATION: ${final.score} ACCURACY`, 'success');
    updateScore(final.score);
}

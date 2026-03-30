document.addEventListener('DOMContentLoaded', () => {
    const logTerminal = document.getElementById('log-terminal');
    const taskList = document.getElementById('task-list');
    const patientRaw = document.getElementById('patient-raw');
    const btnValidate = document.getElementById('btn-validate');
    const btnRun = document.getElementById('btn-run');
    const validationFeedback = document.getElementById('validation-feedback');
    
    // Stats elements
    const currPatient = document.getElementById('curr-patient');
    const currDecision = document.getElementById('curr-decision');
    const currProgress = document.getElementById('curr-progress');
    const envStatus = document.getElementById('env-status');

    let selectedTask = 'easy';
    let tasksMetadata = {};

    // 1. Initialize App
    async function init() {
        addLog('System initialization sequence started...', 'system');
        try {
            await fetchMetadata();
            await fetchTasks();
            addLog('Neural link established. Environment: OpenEnv v1.0', 'system');
        } catch (err) {
            addLog('Critical connection error: ' + err.message, 'error');
        }
    }

    async function fetchMetadata() {
        const res = await fetch('/metadata');
        const data = await res.json();
        envStatus.textContent = `${data.framework}/${data.version}`;
    }

    async function fetchTasks() {
        const res = await fetch('/tasks');
        tasksMetadata = await res.json();
        
        taskList.innerHTML = '';
        Object.keys(tasksMetadata).forEach(id => {
            const card = document.createElement('div');
            card.className = `task-card ${id === selectedTask ? 'active' : ''}`;
            card.innerHTML = `
                <div style="font-weight:700">${id.toUpperCase()}</div>
                <div style="font-size:0.7rem; color:var(--zinc-muted)">${tasksMetadata[id].name}</div>
            `;
            card.onclick = () => selectTask(id);
            taskList.appendChild(card);
        });
    }

    function selectTask(id) {
        selectedTask = id;
        document.querySelectorAll('.task-card').forEach(c => c.classList.remove('active'));
        document.querySelector(`.task-card:nth-child(${Object.keys(tasksMetadata).indexOf(id) + 1})`).classList.add('active');
        addLog(`Protocol switched to ${id.toUpperCase()}: ${tasksMetadata[id].name}`, 'system');
        btnRun.disabled = false;
    }

    // 2. Validation Logic
    btnValidate.onclick = async () => {
        const data = patientRaw.value.trim();
        if (!data) {
            showFeedback('Please provide patient data for validation.', 'error');
            return;
        }

        addLog('Initiating data integrity check...', 'system');
        try {
            const res = await fetch('/validate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ data })
            });
            const result = await res.json();
            
            if (result.status === 'valid') {
                showFeedback('Neural validation successful. Data structural integrity confirmed.', 'success');
                addLog('Validation success: Patient dossier verified.', 'system');
                btnRun.disabled = false;
            } else {
                showFeedback('Validation failed: ' + result.message, 'error');
                addLog('Validation failure: ' + result.message, 'error');
            }
        } catch (err) {
            showFeedback('Validation engine offline: ' + err.message, 'error');
        }
    };

    function showFeedback(msg, type) {
        validationFeedback.textContent = msg;
        validationFeedback.className = 'feedback-msg ' + type;
    }

    // 3. Execution (Running Info Dashboard)
    btnRun.onclick = async () => {
        addLog(`Executing simulation for task: ${selectedTask.toUpperCase()}`, 'system');
        btnRun.disabled = true;
        btnValidate.disabled = true;

        try {
            // Reset environment
            const resetRes = await fetch('/reset', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ task_id: selectedTask })
            });
            let observation = await resetRes.json();
            
            let done = false;
            let stepCount = 0;
            const totalPatients = tasksMetadata[selectedTask].num_patients;

            while (!done) {
                stepCount++;
                currPatient.textContent = observation.patient.id;
                currProgress.textContent = `${stepCount}/${totalPatients}`;
                addLog(`Analyzing Patient ${observation.patient.id}...`, 'patient');

                // Determine decision (In this UI demo, we simulate a decision or call baseline)
                // For now, we'll just mock a processing delay and then continue
                await new Promise(r => setTimeout(r, 1000));
                
                // Call step with a mock action for demonstration if needed, 
                // but usually the "agent" should be doing this. 
                // Since this is a dashboard, we'll just mock the cycle for visualization.
                
                const decision = Math.random() > 0.3 ? 'approve' : 'reject';
                currDecision.textContent = decision.toUpperCase();
                addLog(`Decision reached: ${decision.toUpperCase()} (Confidence: ${(Math.random() * 20 + 75).toFixed(1)}%)`, 'system');

                const stepRes = await fetch('/step', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ decision, rationale: "Automated screening via Screener.OS Neural Interface." })
                });
                const stepData = await stepRes.json();
                
                observation = stepData.observation;
                done = stepData.done;

                if (done) {
                    addLog('Simulation cycle complete. Generating final report...', 'system');
                    currDecision.textContent = 'COMPLETE';
                    currDecision.className = 's-value emerald';
                    break;
                }
            }
        } catch (err) {
            addLog('Execution interrupted: ' + err.message, 'error');
        } finally {
            btnRun.disabled = false;
            btnValidate.disabled = false;
        }
    };

    function addLog(msg, type = 'system') {
        const line = document.createElement('div');
        line.className = 't-line ' + type;
        const time = new Date().toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
        line.innerHTML = `<span style="opacity:0.4">[${time}]</span> ${msg}`;
        logTerminal.appendChild(line);
        logTerminal.scrollTop = logTerminal.scrollHeight;
    }

    init();
});

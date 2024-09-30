gsap.from("header", { opacity: 0, y: -20, duration: 0.6, ease: "power3.out" });
gsap.from("nav", { opacity: 0, y: -10, duration: 0.6, delay: 0.2, ease: "power3.out" });
gsap.from("main", { opacity: 0, y: 20, duration: 0.6, delay: 0.4, ease: "power3.out" });
gsap.from("footer", { opacity: 0, y: 20, duration: 0.6, delay: 0.6, ease: "power3.out" });

const state = {
    currentStep: 0,
    conversation: [],
    maxCompletedStep: 0
};

const elements = {
    userInput: document.getElementById('user-input'),
    sendTextBtn: document.getElementById('sendTextBtn'),
    chatBox: document.getElementById('chat-box'),
    restartBtn: document.getElementById('restartBtn'),
    stageSelect: document.getElementById('stage-select'),
    jumpStageBtn: document.getElementById('jumpStageBtn'),
    nextStageBtn: document.getElementById('nextStageBtn'),
    structureContainer: document.getElementById('dynamic-structure')
};

function disableUserInput() {
    elements.userInput.disabled = true;
    elements.sendTextBtn.disabled = true;
    elements.nextStageBtn.disabled = true;
}

function enableUserInput() {
    elements.userInput.disabled = false;
    elements.sendTextBtn.disabled = false;
    elements.nextStageBtn.disabled = false;
}

function sendMessage(message = '', nextStep = false) {
    if (!message) {
        message = elements.userInput.value;
    }
    if (!message.trim() && state.currentStep !== 0 && !nextStep) return;

    disableUserInput();

    if (message.trim() && !nextStep) {
        elements.chatBox.innerHTML += `<div class="chat-message user-message"><strong>用户:</strong> ${message}</div>`;
    }
    elements.userInput.value = '';

    const bodyData = nextStep ? { state, force_next_step: true } : { message, state };

    fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(bodyData)
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) throw new Error(data.error);
            if (data.response) {
                elements.chatBox.innerHTML += `<div class="chat-message ai-message"><strong>AI:</strong> ${data.response}</div>`;
                elements.chatBox.scrollTop = elements.chatBox.scrollHeight;
            }
            state.currentStep = data.state.current_step;
            updateUI(state.currentStep, data.structure);
            enableUserInput();
        })
        .catch(error => {
            console.error('Error:', error);
            elements.chatBox.innerHTML += `<div class="chat-message ai-message"><strong>错误:</strong> ${error.message || '发生了一个错误，请稍后重试。'}</div>`;
            enableUserInput();
        });
}

function updateUI(step, structure) {
    elements.structureContainer.innerHTML = '';
    structure.forEach((stage, index) => {
        const stepItem = document.createElement('div');
        stepItem.classList.add('structure-item');
        stepItem.textContent = `步骤 ${index + 1}: ${stage.step}`;
        stepItem.style.backgroundColor = index <= step ? '#d1fae5' : 'white';
        elements.structureContainer.appendChild(stepItem);

        if (index < structure.length - 1) {
            const arrow = document.createElement('div');
            arrow.classList.add('structure-arrow');
            elements.structureContainer.appendChild(arrow);
        }

        if (index <= state.maxCompletedStep) updateStageSelect(index, stage.step);
    });

    document.querySelector('h1').textContent = step >= structure.length ? 'AI 作文答疑系统' : 'AI 作文引导系统';
    elements.userInput.placeholder = step >= structure.length ? '在这里输入你的问题...' : '在这里输入你的回答...';
}

function updateStageSelect(completedStep, stepLabel) {
    const options = elements.stageSelect.options;
    if (!Array.from(options).some(option => option.value === String(completedStep))) {
        const option = document.createElement('option');
        option.value = completedStep;
        option.text = `返回 ${stepLabel} 阶段`;
        elements.stageSelect.appendChild(option);
    }
}

window.addEventListener('load', () => sendMessage(''));
elements.sendTextBtn.addEventListener('click', () => sendMessage());
elements.nextStageBtn.addEventListener('click', () => sendMessage("我觉得我的答案已经足够了，我们可以继续下一步吗？", true));
elements.restartBtn.addEventListener('click', () => { location.reload(); });
elements.jumpStageBtn.addEventListener('click', () => {
    const selectedStep = elements.stageSelect.value;
    if (selectedStep !== "") sendMessage('', false);
});

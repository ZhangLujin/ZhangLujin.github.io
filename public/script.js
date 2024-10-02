// 动画效果
gsap.from("header", { opacity: 0, y: -20, duration: 0.6, ease: "power3.out" });
gsap.from("nav", { opacity: 0, y: -10, duration: 0.6, delay: 0.2, ease: "power3.out" });
gsap.from("main", { opacity: 0, y: 20, duration: 0.6, delay: 0.4, ease: "power3.out" });
gsap.from("footer", { opacity: 0, y: 20, duration: 0.6, delay: 0.6, ease: "power3.out" });

// 全局状态
let currentState = { current_step: 0, conversation: [], max_completed_step: 0 };

// 获取元素
const elements = {
    userInput: document.getElementById('user-input'),
    sendTextBtn: document.getElementById('sendTextBtn'),
    chatBox: document.getElementById('chat-box'),
    restartBtn: document.getElementById('restartBtn'),
    stageSelect: document.getElementById('stage-select'),
    jumpStageBtn: document.getElementById('jumpStageBtn'),
    nextStageBtn: document.getElementById('nextStageBtn'),
    structureContainer: document.getElementById('dynamic-structure'),
    chatContainer: document.querySelector('.chat-container')
};

// 禁用用户输入
function disableUserInput() {
    elements.userInput.disabled = true;
    elements.sendTextBtn.disabled = true;
    elements.nextStageBtn.disabled = true;
}

// 启用用户输入
function enableUserInput() {
    elements.userInput.disabled = false;
    elements.sendTextBtn.disabled = false;
    elements.nextStageBtn.disabled = false;
}

// 滚动聊天框到底部
function scrollChatToBottom() {
    requestAnimationFrame(() => {
        elements.chatContainer.scrollTop = elements.chatContainer.scrollHeight;
    });
}

// 发送消息
function sendMessage(message = '', nextStep = false) {
    if (!message) {
        message = elements.userInput.value;
    }
    if (!message.trim() && currentState.current_step !== 0 && !nextStep) return;

    disableUserInput();

    if (message.trim() && !nextStep) {
        elements.chatBox.innerHTML += `<div class="chat-message user-message"><strong>用户:</strong> ${message}</div>`;
        scrollChatToBottom();
    }
    elements.userInput.value = '';

    const bodyData = nextStep
        ? { state: currentState, force_next_step: true }
        : { message: message, state: currentState };

    fetch('/api/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(bodyData)
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) throw new Error(data.error);
            currentState = data.state;
            updateUI(currentState.current_step, data.structure);

            if (data.response) {
                elements.chatBox.innerHTML += `<div class="chat-message ai-message"><strong>AI:</strong> ${data.response}</div>`;
                scrollChatToBottom();
            }

            enableUserInput();
        })
        .catch(error => {
            console.error('Error:', error);
            elements.chatBox.innerHTML += `<div class="chat-message ai-message"><strong>错误:</strong> ${error.message || '发生了一个错误，请稍后重试。'}</div>`;
            scrollChatToBottom();
            enableUserInput();
        });
}

// 更新界面
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

        if (index <= currentState.max_completed_step) {
            updateStageSelect(index, stage.step);
        }
    });

    document.querySelector('h1').textContent = step >= structure.length ? 'AI 作文答疑系统' : 'AI 作文引导系统';
    elements.userInput.placeholder = step >= structure.length ? '在这里输入你的问题...' : '在这里输入你的回答...';
}

// 更新阶段选择下拉框
function updateStageSelect(completedStep, stepLabel) {
    const options = elements.stageSelect.options;
    const existingOptions = Array.from(options).map(option => option.value);

    if (!existingOptions.includes(String(completedStep))) {
        const option = document.createElement('option');
        option.value = completedStep;
        option.text = `返回 ${stepLabel} 阶段`;
        elements.stageSelect.appendChild(option);
    }
}

// 页面加载时发送初始消息
window.addEventListener('load', () => sendMessage(''));

// 按钮事件监听
elements.sendTextBtn.addEventListener('click', () => sendMessage());
elements.nextStageBtn.addEventListener('click', () => {
    const presetUserMessage = "我觉得我的答案已经足够了，我们可以继续下一步吗？";
    elements.chatBox.innerHTML += `<div class="chat-message user-message"><strong>用户:</strong> ${presetUserMessage}</div>`;
    scrollChatToBottom();
    sendMessage(presetUserMessage, true);
});
elements.restartBtn.addEventListener('click', () => {
    currentState = { current_step: 0, conversation: [], max_completed_step: 0 };
    elements.chatBox.innerHTML = '';
    elements.stageSelect.innerHTML = '<option value="">选择你要跳转的阶段</option>';
    sendMessage('');
});
elements.jumpStageBtn.addEventListener('click', () => {
    const selectedStep = elements.stageSelect.value;
    if (selectedStep !== "") {
        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ state: currentState, jump_to_step: parseInt(selectedStep) })
        })
            .then(response => response.json())
            .then(data => {
                currentState = data.state;
                elements.chatBox.innerHTML += `<div class="chat-message ai-message"><strong>AI:</strong> ${data.response}</div>`;
                scrollChatToBottom();
                updateUI(currentState.current_step, data.structure);
            })
            .catch(error => {
                console.error('Error:', error);
                elements.chatBox.innerHTML += `<div class="chat-message ai-message"><strong>错误:</strong> ${error.message || '跳转阶段时发生了一个错误。'}</div>`;
                scrollChatToBottom();
            });
    }
});

// 添加用户输入的键盘事件监听器，处理 Enter 和 Ctrl+Enter
elements.userInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
        if (e.ctrlKey) {
            let start = this.selectionStart;
            let end = this.selectionEnd;
            let value = this.value;
            this.value = value.slice(0, start) + "\n" + value.slice(end);
            this.selectionStart = this.selectionEnd = start + 1;
            e.preventDefault();
        } else {
            e.preventDefault();
            sendMessage();
        }
    }
});

// 侧边栏切换功能
const sidebar = document.querySelector('.sidebar');
const sidebarToggle = document.querySelector('.sidebar-toggle');
sidebarToggle.addEventListener('click', () => {
    sidebar.classList.toggle('open');
});

// 语音输入功能（示例）
document.getElementById('voiceInputBtn').addEventListener('click', function() {
    alert('语音输入功能尚未实现');
});
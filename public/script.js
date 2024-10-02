// 动画效果
gsap.from("header", { opacity: 0, y: -20, duration: 0.6, ease: "power3.out" });
gsap.from("nav", { opacity: 0, y: -10, duration: 0.6, delay: 0.2, ease: "power3.out" });
gsap.from("main", { opacity: 0, y: 20, duration: 0.6, delay: 0.4, ease: "power3.out" });
gsap.from("footer", { opacity: 0, y: 20, duration: 0.6, delay: 0.6, ease: "power3.out" });

// 全局状态
const state = {
    currentStep: 0,
    conversation: [],
    maxCompletedStep: 0
};

// 获取元素
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

// 发送消息
function sendMessage(message = '', nextStep = false) {
    if (!message) {
        message = elements.userInput.value;
    }
    if (!message.trim() && state.currentStep !== 0 && !nextStep) return;

    disableUserInput();

    if (message.trim() && !nextStep) {
        elements.chatBox.innerHTML += `<div class="chat-message user-message"><strong>用户:</strong> ${escapeHTML(message)}</div>`;
    }
    elements.userInput.value = '';
    updateChatScroll();

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
                elements.chatBox.innerHTML += `<div class="chat-message ai-message"><strong>AI:</strong> ${escapeHTML(data.response)}</div>`;
                updateChatScroll();
            }
            state.currentStep = data.state.current_step;
            if (data.state.max_completed_step > state.maxCompletedStep) {
                state.maxCompletedStep = data.state.max_completed_step;
            }
            updateUI(state.currentStep, data.structure);
            enableUserInput();
        })
        .catch(error => {
            console.error('Error:', error);
            elements.chatBox.innerHTML += `<div class="chat-message ai-message"><strong>错误:</strong> ${escapeHTML(error.message) || '发生了一个错误，请稍后重试。'}</div>`;
            updateChatScroll();
            enableUserInput();
        });
}

// 更新聊天区域滚动
function updateChatScroll() {
    elements.chatBox.scrollTop = elements.chatBox.scrollHeight;
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

        if (index <= state.maxCompletedStep) updateStageSelect(index, stage.step);
    });

    document.querySelector('h1').textContent = step >= structure.length ? 'AI 作文答疑系统' : 'AI 作文引导系统';
    elements.userInput.placeholder = step >= structure.length ? '在这里输入你的问题...' : '在这里输入你的回答...';
}

// 更新阶段选择下拉框
function updateStageSelect(completedStep, stepLabel) {
    const options = elements.stageSelect.options;
    if (!Array.from(options).some(option => option.value === String(completedStep))) {
        const option = document.createElement('option');
        option.value = completedStep;
        option.text = `返回 ${stepLabel} 阶段`;
        elements.stageSelect.appendChild(option);
    }
}

// 转义HTML以防止XSS
function escapeHTML(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

// 页面加载时发送初始消息
window.addEventListener('load', () => sendMessage(''));

// 按钮事件监听
elements.sendTextBtn.addEventListener('click', () => sendMessage());
elements.nextStageBtn.addEventListener('click', () => sendMessage("我觉得我的答案已经足够了，我们可以继续下一步吗？", true));
elements.restartBtn.addEventListener('click', () => { location.reload(); });
elements.jumpStageBtn.addEventListener('click', () => {
    const selectedStep = elements.stageSelect.value;
    if (selectedStep !== "") {
        state.currentStep = parseInt(selectedStep);
        sendMessage('', false);
    }
});

// 侧边栏切换功能
const sidebar = document.querySelector('.sidebar');
const sidebarToggle = document.querySelector('.sidebar-toggle');

sidebarToggle.addEventListener('click', () => {
    sidebar.classList.toggle('open');
});

// --------------------- 新增的思维导图功能 ---------------------

// 初始化节点和边
const nodes = new vis.DataSet([
    { id: 1, label: '主题', shape: 'box', font: { multi: true }, fixed: { x: true, y: true } }
]);
const edges = new vis.DataSet([]);

const container = document.getElementById('mindmap');
const data = { nodes, edges };
const options = {
    layout: {
        hierarchical: false
    },
    nodes: {
        shape: 'box',
        widthConstraint: { minimum: 100, maximum: 200 },
        font: { size: 16, multi: true, face: 'Noto Sans SC' },
        borderWidth: 2,
        shadow: true,
        fixed: { x: false, y: false }
    },
    edges: {
        arrows: 'to',
        width: 2,
        smooth: { type: 'cubicBezier', forceDirection: 'vertical', roundness: 0.5 }
    },
    physics: { enabled: false },
    interaction: {
        dragNodes: true,
        dragView: true,
        zoomView: true,
        hover: true,
        selectable: true,
        selectConnectedEdges: false,
        multiselect: false,
        tooltipDelay: 300,
        hideEdgesOnDrag: false,
        hideNodesOnDrag: false
    },
    manipulation: {
        enabled: false // 禁用默认的操作按钮
    }
};

const network = new vis.Network(container, data, options);

let isEditingNode = false;

// 双击节点编辑
network.on('doubleClick', function (params) {
    if (params.nodes.length === 1) {
        const nodeId = params.nodes[0];
        const node = nodes.get(nodeId);
        const pointer = params.pointer.DOM;
        const input = document.createElement('textarea');
        input.value = node.label;
        input.style.position = 'absolute';
        input.style.left = `${pointer.x}px`;
        input.style.top = `${pointer.y}px`;
        input.style.zIndex = 1000;
        input.style.width = '200px';
        input.style.height = '50px';
        input.style.fontSize = '16px';
        input.style.border = '2px solid #ccc';
        input.style.borderRadius = '8px';
        input.style.padding = '10px';
        input.style.boxShadow = '0 4px 10px rgba(0, 0, 0, 0.1)';
        document.body.appendChild(input);
        input.focus();
        input.select();

        // 确认编辑
        const confirmEdit = () => {
            const newLabel = input.value.trim();
            if (newLabel !== '') {
                nodes.update({ id: nodeId, label: newLabel });
                applyCustomLayout();
            }
            if (document.body.contains(input)) {
                document.body.removeChild(input);
            }
            isEditingNode = false;
        };

        input.addEventListener('keydown', (event) => {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                confirmEdit();
            }
        });

        input.addEventListener('blur', () => {
            confirmEdit();
        });
    }
});

// 键盘事件处理
document.addEventListener('keydown', function (event) {
    const selectedNodes = network.getSelectedNodes();
    if (selectedNodes.length === 1) {
        const selectedNode = selectedNodes[0];
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            const newNodeId = getNextNodeId();
            nodes.add({ id: newNodeId, label: `新节点${newNodeId}`, shape: 'box', fixed: { x: false, y: false } });
            edges.add({ from: selectedNode, to: newNodeId });
            applyCustomLayout();
        } else if (event.key === 'Tab') {
            event.preventDefault();
            const newNodeId = getNextNodeId();
            nodes.add({ id: newNodeId, label: `新节点${newNodeId}`, shape: 'box', fixed: { x: false, y: false } });
            edges.add({ from: selectedNode, to: newNodeId });
            applyCustomLayout();
        } else if (event.key === 'Backspace' || event.key === 'Delete') {
            event.preventDefault();
            deleteNodeAndDescendants(selectedNode);
            applyCustomLayout();
        }
    }
});

// 拖动节点时禁用物理引擎
network.on("dragStart", function (params) {
    if (params.nodes.length === 1) {
        network.setOptions({ physics: false });
    }
});

// 拖动结束后应用自定义布局
network.on("dragEnd", function (params) {
    if (params.nodes.length === 1) {
        applyCustomLayout();
    }
});

// 当节点或边数据变化时，重新布局
nodes.on(['add', 'remove', 'update'], function () {
    applyCustomLayout();
});

edges.on(['add', 'remove', 'update'], function () {
    applyCustomLayout();
});

// 获取下一个节点ID
function getNextNodeId() {
    const existingIds = nodes.getIds();
    return Math.max(...existingIds) + 1;
}

// 应用自定义布局
function applyCustomLayout() {
    const tree = buildTree();
    const roots = findRoots(tree);

    const levelSeparation = 150;
    const nodeSpacing = 220;
    const startX = container.clientWidth / 2;
    const startY = 50;

    let currentX = startX;
    roots.forEach(root => {
        currentX = layoutNode(root, 0, currentX, levelSeparation, nodeSpacing);
    });

    nodes.forEach(node => {
        if (tree[node.id]) {
            nodes.update({ id: node.id, x: tree[node.id].x, y: tree[node.id].y });
        }
    });

    network.fit();
}

// 构建树形结构
function buildTree() {
    const tree = {};
    nodes.forEach(node => {
        tree[node.id] = { ...node, children: [] };
    });
    edges.forEach(edge => {
        if (tree[edge.from] && tree[edge.to]) {
            tree[edge.from].children.push(tree[edge.to]);
        }
    });
    return tree;
}

// 查找根节点
function findRoots(tree) {
    return Object.values(tree).filter(node =>
        !edges.get().some(edge => edge.to === node.id)
    );
}

// 布局节点
function layoutNode(node, depth, xOffset, levelSeparation, nodeSpacing) {
    node.y = depth * levelSeparation;
    let numChildren = node.children.length;
    if (numChildren === 0) {
        node.x = xOffset;
        return xOffset + nodeSpacing;
    }
    let currentX = xOffset;
    node.children.forEach(child => {
        currentX = layoutNode(child, depth + 1, currentX, levelSeparation, nodeSpacing);
    });
    const firstChild = node.children[0];
    const lastChild = node.children[node.children.length - 1];
    node.x = (firstChild.x + lastChild.x) / 2;
    return currentX;
}

// 删除节点及其子节点
function deleteNodeAndDescendants(nodeId) {
    const descendants = getDescendants(nodeId);
    nodes.remove([nodeId, ...descendants]);
    edges.remove(edges.get().filter(edge =>
        edge.from === nodeId || edge.to === nodeId || descendants.includes(edge.from) || descendants.includes(edge.to)
    ));
}

// 获取子孙节点
function getDescendants(nodeId) {
    const descendants = [];
    const childEdges = edges.get().filter(edge => edge.from === nodeId);
    childEdges.forEach(edge => {
        descendants.push(edge.to);
        descendants.push(...getDescendants(edge.to));
    });
    return descendants;
}

// 检查是否会形成环路
function willFormCycle(fromId, toId) {
    const visited = new Set();

    function dfs(currentId) {
        if (currentId === fromId) return true;
        if (visited.has(currentId)) return false;

        visited.add(currentId);
        const childEdges = edges.get().filter(edge => edge.from === currentId);
        for (let edge of childEdges) {
            if (dfs(edge.to)) return true;
        }
        return false;
    }

    return dfs(toId);
}

// 初始布局
applyCustomLayout();

// --------------------- 新增的键盘事件监听（处理回车和 Ctrl+回车） ---------------------

// 处理 textarea 的键盘事件
elements.userInput.addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
        if (event.ctrlKey) {
            // 按下 Ctrl + Enter 插入换行
            const { selectionStart, selectionEnd, value } = elements.userInput;
            elements.userInput.value = value.substring(0, selectionStart) + "\n" + value.substring(selectionEnd);
            elements.userInput.selectionStart = elements.userInput.selectionEnd = selectionStart + 1;
            event.preventDefault();
        } else {
            // 按下 Enter 发送消息
            event.preventDefault();
            sendMessage();
        }
    }
});

// 防止表单提交（如果有包裹在表单内）
document.querySelector('form')?.addEventListener('submit', function(event) {
    event.preventDefault();
});
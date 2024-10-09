// undoRedo.js

// 建立 Undo 和 Redo 栈
var undoStack = [];
var redoStack = [];

// 函数：保存初始状态
function saveInitialState() {
    var initialState = {
        nodes: deepCopy(nodes.get()),
        edges: deepCopy(edges.get()),
        lastModifiedNodeId: null
    };
    undoStack.push(initialState);
}

// 在脚本初始化后立即保存初始状态
saveInitialState();

// 函数：记录当前状态到 undoStack
function saveStateToUndo(actionNodeId = null) {
    if (isExecutingUndoRedo) return;
    var currentState = {
        nodes: deepCopy(nodes.get()),
        edges: deepCopy(edges.get()),
        lastModifiedNodeId: actionNodeId
    };
    undoStack.push(currentState);
    // 限制历史记录栈的大小（可选）
    if (undoStack.length > 100) {
        undoStack.shift();
    }
    // 清空 redoStack
    redoStack.length = 0;
}

// 函数：深拷贝对象
function deepCopy(obj) {
    return JSON.parse(JSON.stringify(obj));
}

// 函数：恢复到指定状态
function restoreState(state) {
    isExecutingUndoRedo = true;

    // 清空当前的节点和边
    nodes.clear();
    edges.clear();

    // 恢复节点和边
    nodes.add(state.nodes);
    edges.add(state.edges);

    // 更新最后修改的节点 ID
    lastModifiedNodeId = state.lastModifiedNodeId;

    // 应用自定义布局
    applyCustomLayout();

    isExecutingUndoRedo = false;

    // 选择最后修改的节点
    if (lastModifiedNodeId !== null) {
        network.selectNodes([lastModifiedNodeId]);
    } else {
        network.unselectAll();
    }

    // 显示或隐藏注释面板
    var selectedNodes = network.getSelectedNodes();
    if (selectedNodes.length === 1) {
        var node = nodes.get(selectedNodes[0]);
        if (node && node.annotation) {
            showAnnotationPanel(node);
        } else {
            hideAnnotationPanel();
        }
    } else {
        hideAnnotationPanel();
    }
}

// 撤销按钮点击事件
undoButton.addEventListener('click', function () {
    if (undoStack.length <= 1) return; // 保留初始状态
    var currentState = {
        nodes: deepCopy(nodes.get()),
        edges: deepCopy(edges.get()),
        lastModifiedNodeId: lastModifiedNodeId
    };
    redoStack.push(currentState);
    var previousState = undoStack.pop();
    restoreState(previousState);
});

// 重做按钮点击事件
redoButton.addEventListener('click', function () {
    if (redoStack.length === 0) return;
    var currentState = {
        nodes: deepCopy(nodes.get()),
        edges: deepCopy(edges.get()),
        lastModifiedNodeId: lastModifiedNodeId
    };
    undoStack.push(currentState);
    var nextState = redoStack.pop();
    restoreState(nextState);
});

// 键盘快捷键事件处理
document.addEventListener('keydown', function (event) {
    // Ctrl+Z for Undo
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'z') {
        event.preventDefault();
        undoButton.click();
        return;
    }
    // Ctrl+Y for Redo
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'y') {
        event.preventDefault();
        redoButton.click();
        return;
    }
    // Ctrl+X for Add/Edit Annotation
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'x') {
        event.preventDefault();
        addOrEditAnnotation();
        return;
    }
});
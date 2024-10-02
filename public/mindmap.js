// 初始化节点和边
const nodes = new vis.DataSet([
    { id: 1, label: '主题', shape: 'box', font: { multi: true }, fixed: { x: true, y: true } }
]);
const edges = new vis.DataSet([]);
const container = document.getElementById('mindmap');
const data = { nodes, edges };
const options = {
    layout: { hierarchical: false },
    nodes: {
        shape: 'box',
        widthConstraint: { minimum: 100, maximum: 200 },
        font: { size: 16, multi: true, face: 'Noto Sans SC' },
        borderWidth: 2,
        shadow: true,
        fixed: { x: true, y: true }
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
    manipulation: { enabled: false }
};
const network = new vis.Network(container, data, options);
let isEditingNode = false;

// 双击节点编辑
network.on('doubleClick', function (params) {
    if (params.nodes.length === 1) {
        isEditingNode = true;
        const nodeId = params.nodes[0];
        const node = nodes.get(nodeId);
        const position = network.getPositions([nodeId])[nodeId];
        const domPos = network.canvasToDOM(position);

        const input = document.createElement('textarea');
        input.value = node.label;
        input.style.position = 'absolute';
        input.style.left = `${domPos.x - 100}px`;
        input.style.top = `${domPos.y - 25}px`;
        input.style.zIndex = 1000;
        input.style.width = '200px';
        input.style.height = '50px';
        input.style.fontSize = '16px';
        input.style.border = '2px solid #4299e1';
        input.style.borderRadius = '8px';
        input.style.padding = '10px';
        input.style.boxShadow = '0 4px 10px rgba(0, 0, 0, 0.1)';
        input.style.backgroundColor = 'white';
        document.body.appendChild(input);
        input.focus();
        input.select();

        const handleInputChange = () => {
            const newLabel = input.value.trim();
            if (newLabel !== '') {
                nodes.update({ id: nodeId, label: newLabel });
            }
            if (document.body.contains(input)) {
                document.body.removeChild(input);
            }
            isEditingNode = false;
        };

        input.addEventListener('keydown', (event) => {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                handleInputChange();
            }
        });

        input.addEventListener('blur', handleInputChange);
    }
});

// 键盘事件处理
document.addEventListener('keydown', function (event) {
    if (document.activeElement.tagName === 'INPUT' || document.activeElement.tagName === 'TEXTAREA') {
        return; // 输入框或文本区域聚焦时不处理
    }
    const selectedNodes = network.getSelectedNodes();
    if (selectedNodes.length === 1) {
        const selectedNode = selectedNodes[0];
        if (event.key === 'Enter') {
            event.preventDefault();
            const connectedEdges = network.getConnectedEdges(selectedNode);
            const parentEdge = edges.get(connectedEdges).find(edge => edge.to === selectedNode);
            const newNodeId = getNextNodeId();
            nodes.add({ id: newNodeId, label: `新节点${newNodeId}`, shape: 'box', fixed: { x: false, y: false } });
            if (parentEdge) {
                edges.add({ from: parentEdge.from, to: newNodeId });
            } else {
                edges.add({ from: selectedNode, to: newNodeId });
            }
            setTimeout(applyCustomLayout, 100);
        } else if (event.key === 'Tab') {
            event.preventDefault();
            const newNodeId = getNextNodeId();
            nodes.add({ id: newNodeId, label: `新节点${newNodeId}`, shape: 'box', fixed: { x: false, y: false } });
            edges.add({ from: selectedNode, to: newNodeId });
            setTimeout(applyCustomLayout, 100);
        } else if (event.key === 'Backspace' || event.key === 'Delete') {
            deleteNodeAndDescendants(selectedNode);
            setTimeout(applyCustomLayout, 100);
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
nodes.on(['add', 'remove', 'update'], function (event, properties, senderId) {
    applyCustomLayout();
});

edges.on(['add', 'remove', 'update'], function (event, properties, senderId) {
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
        nodes.update({ id: node.id, x: tree[node.id].x, y: tree[node.id].y });
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
    return Object.values(tree).filter(node => !edges.get().some(edge => edge.to === node.id));
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
    edges.remove(edges.get().filter(edge => edge.from === nodeId || edge.to === nodeId || descendants.includes(edge.from) || descendants.includes(edge.to)));
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

// 初始布局
applyCustomLayout();

// 窗口大小改变时重新布局
window.addEventListener('resize', applyCustomLayout);
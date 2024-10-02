// 初始化节点和边
const nodes = new vis.DataSet([
    { id: 1, label: '主题', shape: 'box', font: { multi: true }, fixed: { x: true, y: true } }
]);
const edges = new vis.DataSet([]);
const container = document.getElementById('mindmap');
const data = { nodes, edges };
let isEditingNode = false; // 编辑状态标志

const options = {
    layout: {
        hierarchical: {
            enabled: true,
            direction: 'LR', // 从左到右
            sortMethod: 'directed',
            nodeSpacing: 150,    // 节点之间的水平间距
            levelSeparation: 100 // 层级之间的垂直间距
        }
    },
    nodes: {
        shape: 'box',
        widthConstraint: { minimum: 100, maximum: 200 },
        font: { size: 16, multi: true, face: 'Noto Sans SC' },
        borderWidth: 2,
        shadow: true
    },
    edges: {
        arrows: 'to',
        width: 2,
        smooth: { type: 'cubicBezier', forceDirection: 'horizontal', roundness: 0.5 }
    },
    physics: {
        hierarchicalRepulsion: {
            nodeDistance: 150
        },
        enabled: false
    },
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

// 双击节点编辑
network.on('doubleClick', function (params) {
    if (params.nodes.length === 1) {
        isEditingNode = true;
        const nodeId = params.nodes[0];
        const node = nodes.get(nodeId);
        const position = network.getPositions([nodeId])[nodeId];
        const canvasPosition = {
            x: (position.x - network.getScale() * network.canvas.frame.canvas.width / 2) + network.canvas.frame.view.x,
            y: (position.y - network.getScale() * network.canvas.frame.canvas.height / 2) + network.canvas.frame.view.y
        };
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
                // 不再需要 event.stopPropagation()
            }
        });

        input.addEventListener('blur', handleInputChange);
    }
});

// 键盘事件处理
document.addEventListener('keydown', function (event) {
    if (isEditingNode) {
        return; // 正在编辑节点时不处理其他键盘事件
    }
    const selectedNodes = network.getSelectedNodes();
    if (selectedNodes.length === 1) {
        const selectedNode = selectedNodes[0];
        if (event.key === 'Enter') {
            event.preventDefault();
            const connectedEdges = network.getConnectedEdges(selectedNode);
            const parentEdge = edges.get(connectedEdges).find(edge => edge.to === selectedNode);
            const newNodeId = getNextNodeId();
            nodes.add({ id: newNodeId, label: `新节点${newNodeId}`, shape: 'box' });
            if (parentEdge) {
                edges.add({ from: parentEdge.from, to: newNodeId });
            } else {
                edges.add({ from: selectedNode, to: newNodeId });
            }
        } else if (event.key === 'Tab') {
            event.preventDefault();
            const newNodeId = getNextNodeId();
            nodes.add({ id: newNodeId, label: `新节点${newNodeId}`, shape: 'box' });
            edges.add({ from: selectedNode, to: newNodeId });
        } else if (event.key === 'Backspace' || event.key === 'Delete') {
            deleteNodeAndDescendants(selectedNode);
        }
    }
});

// 拖动节点时禁用物理引擎
network.on("dragStart", function (params) {
    if (params.nodes.length === 1) {
        network.setOptions({ physics: false });
    }
});

// 拖动结束后重新启用物理引擎并应用布局
network.on("dragEnd", function (params) {
    if (params.nodes.length === 1) {
        network.setOptions({ physics: false }); // 保持物理引擎禁用
        network.fit();
    }
});

// 当节点或边数据变化时，重新布局
nodes.on(['add', 'remove', 'update'], function (event, properties, senderId) {
    network.setOptions(options); // 重新应用布局选项
});

edges.on(['add', 'remove', 'update'], function (event, properties, senderId) {
    network.setOptions(options); // 重新应用布局选项
});

// 获取下一个节点ID
function getNextNodeId() {
    const existingIds = nodes.getIds();
    return Math.max(...existingIds) + 1;
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
network.setOptions(options);

// 窗口大小改变时重新布局
window.addEventListener('resize', () => {
    network.fit();
});

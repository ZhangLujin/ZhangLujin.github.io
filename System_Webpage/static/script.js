document.getElementById('send-btn').addEventListener('click', sendMessage);

function sendMessage() {
    const userInput = document.getElementById('user-input').value;

    // 清空输入框
    document.getElementById('user-input').value = '';

    // 发送请求到后端
    fetch('/api/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: userInput })
    })
        .then(response => response.json())
        .then(data => {
            // 显示AI的回复
            const responseBox = document.getElementById('response-box');
            responseBox.innerHTML = `<p>${data.response}</p>`;
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

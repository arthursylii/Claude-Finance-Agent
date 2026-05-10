<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Claude Finance Advisor</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-950 text-white">
  <div class="max-w-3xl mx-auto p-6">
    <h1 class="text-5xl font-bold text-center mb-2">💰 Claude Finance</h1>
    <p class="text-center text-gray-400 mb-8">AI Investment Advisor</p>
    
    <div id="chat" class="bg-gray-900 rounded-3xl p-6 h-[70vh] overflow-y-auto mb-6"></div>
    
    <div class="flex gap-3">
      <input id="input" type="text" class="flex-1 bg-gray-800 border border-gray-700 rounded-2xl px-6 py-5" 
             placeholder="Ask about stocks, portfolio, retirement...">
      <button onclick="sendMessage()" class="bg-blue-600 hover:bg-blue-700 px-10 rounded-2xl">Send</button>
    </div>
  </div>

  <script>
    async function sendMessage() {
      const input = document.getElementById('input');
      const msg = input.value.trim();
      if (!msg) return;

      addMessage('user', msg);
      input.value = '';

      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message: msg})
      });
      const data = await res.json();
      addMessage('assistant', data.reply || data.error);
    }

    function addMessage(role, text) {
      const chat = document.getElementById('chat');
      const div = document.createElement('div');
      div.className = role === 'user' ? 'text-right' : 'text-left';
      div.innerHTML = `<div class="inline-block max-w-[80%] ${role==='user'?'bg-blue-600':'bg-gray-800'} rounded-3xl px-5 py-3">${text}</div>`;
      chat.appendChild(div);
      chat.scrollTop = chat.scrollHeight;
    }

    document.getElementById('input').addEventListener('keypress', e => {
      if (e.key === 'Enter') sendMessage();
    });
  </script>
</body>
</html>
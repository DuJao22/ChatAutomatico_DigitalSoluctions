let currentStep = 'name';

const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');

function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addMessage(text, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = isUser ? 'message-user flex' : 'message-bot flex';
    
    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = 'max-w-[80%] px-5 py-3';
    
    const textP = document.createElement('p');
    textP.className = 'text-sm leading-relaxed';
    
    // Converte URLs em links clicáveis
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    const formattedText = text.replace(urlRegex, (url) => {
        return `<a href="${url}" target="_blank" class="text-blue-400 underline hover:text-blue-300 font-medium">🔗 Clique aqui para ver</a>`;
    });
    
    // Preserva quebras de linha
    textP.innerHTML = formattedText.replace(/\n/g, '<br>');
    
    bubbleDiv.appendChild(textP);
    messageDiv.appendChild(bubbleDiv);
    chatMessages.appendChild(messageDiv);
    
    scrollToBottom();
}

function showTypingIndicator() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message-bot flex';
    messageDiv.id = 'typing-indicator';
    
    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = 'max-w-[80%] px-5 py-3';
    
    const typingDiv = document.createElement('div');
    typingDiv.className = 'typing-indicator';
    typingDiv.innerHTML = '<span></span><span></span><span></span>';
    
    bubbleDiv.appendChild(typingDiv);
    messageDiv.appendChild(bubbleDiv);
    chatMessages.appendChild(messageDiv);
    
    scrollToBottom();
}

function hideTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.remove();
    }
}

async function sendMessage() {
    const message = userInput.value.trim();
    
    if (!message) return;
    
    addMessage(message, true);
    userInput.value = '';
    
    showTypingIndicator();
    
    try {
        let endpoint = '/start';
        
        if (currentStep === 'chat') {
            endpoint = '/chat_ai';
        }
        
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });
        
        const data = await response.json();
        
        hideTypingIndicator();
        
        if (data.success) {
            addMessage(data.response, false);
            
            if (data.step) {
                currentStep = data.step;
            }
            
            if (currentStep === 'chat' && data.response.includes('registrados')) {
                setTimeout(() => {
                    addMessage('Quando terminarmos, você pode conhecer mais sobre nossas soluções. Digite "finalizar" quando quiser encerrar.', false);
                }, 1000);
            }
        } else {
            addMessage(data.response || 'Erro ao processar mensagem.', false);
        }
        
    } catch (error) {
        hideTypingIndicator();
        addMessage('Desculpe, ocorreu um erro. Tente novamente.', false);
        console.error('Erro:', error);
    }
    
    if (message.toLowerCase() === 'finalizar' && currentStep === 'chat') {
        setTimeout(() => {
            window.location.href = '/redirect';
        }, 1000);
    }
}

sendBtn.addEventListener('click', sendMessage);

userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

userInput.focus();

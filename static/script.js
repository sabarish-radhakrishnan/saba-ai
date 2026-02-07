const chatBox = document.getElementById('chatBox');
const chatForm = document.getElementById('chatForm');
const userInput = document.getElementById('userInput');
const analyticsBtn = document.getElementById('analyticsBtn');
const resetBtn = document.getElementById('resetBtn');
const analyticsModal = document.getElementById('analyticsModal');
const closeBtn = document.querySelector('.close');

// Load history on page load
document.addEventListener('DOMContentLoaded', loadHistory);

// Handle form submission
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const message = userInput.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addMessage(message, 'user');
    userInput.value = '';
    
    // Show loading indicator
    const loadingId = showLoading();
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });
        
        const data = await response.json();
        
        // Remove loading indicator
        removeLoading(loadingId);
        
        if (data.success) {
            addMessage(data.response, 'ai');
        } else {
            addMessage('Error: ' + data.error, 'ai');
        }
    } catch (error) {
        removeLoading(loadingId);
        addMessage('Connection error. Please try again.', 'ai');
        console.error('Error:', error);
    }
    
    // Focus back on input
    userInput.focus();
});

// Analytics button
analyticsBtn.addEventListener('click', showAnalytics);

// Reset button
resetBtn.addEventListener('click', async () => {
    if (confirm('Are you sure you want to clear the conversation context?')) {
        try {
            const response = await fetch('/api/reset', {
                method: 'POST'
            });
            
            if (response.ok) {
                chatBox.innerHTML = '';
                addMessage('Context has been cleared. Starting fresh!', 'ai');
            }
        } catch (error) {
            console.error('Error:', error);
        }
    }
});

// Modal close
closeBtn.addEventListener('click', () => {
    analyticsModal.style.display = 'none';
});

window.addEventListener('click', (e) => {
    if (e.target === analyticsModal) {
        analyticsModal.style.display = 'none';
    }
});

// Functions
function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = text;
    
    messageDiv.appendChild(contentDiv);
    
    const timeDiv = document.createElement('div');
    timeDiv.className = 'message-time';
    const now = new Date();
    timeDiv.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    messageDiv.appendChild(timeDiv);
    
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function showLoading() {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message ai';
    loadingDiv.id = 'loading-' + Date.now();
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'loading';
    contentDiv.innerHTML = '<span></span><span></span><span></span>';
    
    loadingDiv.appendChild(contentDiv);
    chatBox.appendChild(loadingDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
    
    return loadingDiv.id;
}

function removeLoading(loadingId) {
    const loadingDiv = document.getElementById(loadingId);
    if (loadingDiv) {
        loadingDiv.remove();
    }
}

async function showAnalytics() {
    try {
        const response = await fetch('/api/analytics');
        const data = await response.json();
        
        let analyticsHTML = '<div>';
        analyticsHTML += `<div>💬 Total Exchanges: <strong>${data.total_exchanges}</strong></div>`;
        analyticsHTML += `<div>🧠 Memories Learned: <strong>${data.memories_learned}</strong></div>`;
        
        if (data.sentiment !== undefined) {
            const sentimentText = data.sentiment > 0.3 ? '😊 Positive' : 
                                  data.sentiment < -0.3 ? '😞 Negative' : '😐 Neutral';
            analyticsHTML += `<div>😔 Sentiment: <strong>${sentimentText}</strong> (${data.sentiment.toFixed(2)})</div>`;
        }
        
        if (data.top_topics && data.top_topics.length > 0) {
            analyticsHTML += '<div>🏷️ Top Topics:<ul>';
            data.top_topics.forEach(topic => {
                analyticsHTML += `<li><strong>${topic.topic}</strong>: ${topic.count} mentions</li>`;
            });
            analyticsHTML += '</ul></div>';
        }
        
        analyticsHTML += '</div>';
        document.getElementById('analyticsContent').innerHTML = analyticsHTML;
        analyticsModal.style.display = 'block';
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('analyticsContent').innerHTML = '<div>Error loading analytics</div>';
        analyticsModal.style.display = 'block';
    }
}

async function loadHistory() {
    try {
        const response = await fetch('/api/history');
        const data = await response.json();
        
        if (data.history && data.history.length > 0) {
            data.history.forEach(exchange => {
                addMessage(exchange.user, 'user');
                addMessage(exchange.ai, 'ai');
            });
        }
    } catch (error) {
        console.error('Error loading history:', error);
    }
    
    userInput.focus();
}

// Style for analytics content
const style = document.createElement('style');
style.textContent = `
    #analyticsContent ul {
        margin: 10px 0 10px 20px;
        list-style-type: none;
    }
    #analyticsContent li {
        padding: 5px 0;
        border-bottom: 1px dotted #ddd;
    }
`;
document.head.appendChild(style);

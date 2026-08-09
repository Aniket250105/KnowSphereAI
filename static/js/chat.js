document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chatMessages');
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');
    let sessionId = crypto.randomUUID();

    const newChatBtn = document.getElementById('newChatBtn');
    if (newChatBtn) {
        newChatBtn.addEventListener('click', () => {
            sessionId = crypto.randomUUID();
            chatMessages.innerHTML = `
                <div class="message bot">
                    <div class="bubble">
                        Started a new conversation. What's on your mind?
                    </div>
                </div>
            `;
        });
    }

    // Use marked options for better rendering
    if (typeof marked !== 'undefined') {
        marked.setOptions({
            breaks: true,
            gfm: true
        });
    }

    function addMessage(id, isUser = false) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${isUser ? 'user' : 'bot'}`;
        msgDiv.id = `msg-${id}`;
        
        let bubbleHtml = `
            <div class="bubble">
                <div class="content" id="content-${id}"></div>
                ${!isUser ? `<div class="sources" id="sources-${id}" style="display:none; font-size:0.8rem; margin-top:0.5rem; color:var(--text-muted);"></div>` : ''}
                ${!isUser ? `
                    <div class="actions" style="display:none; gap:0.5rem; margin-top:0.5rem; align-items:center;" id="actions-${id}">
                        <button class="btn btn-outline" style="padding: 0.25rem; font-size:0.75rem;" onclick="copyMsg('${id}')" title="Copy"><i data-feather="copy" style="width:14px;height:14px;"></i></button>
                        <button class="btn btn-outline" style="padding: 0.25rem; font-size:0.75rem;" onclick="regenerateMsg()" title="Regenerate"><i data-feather="refresh-cw" style="width:14px;height:14px;"></i></button>
                        <button class="btn btn-outline" style="padding: 0.25rem; font-size:0.75rem;" onclick="submitFeedback('${id}', 1)" title="Helpful"><i data-feather="thumbs-up" style="width:14px;height:14px;"></i></button>
                        <button class="btn btn-outline" style="padding: 0.25rem; font-size:0.75rem;" onclick="submitFeedback('${id}', -1)" title="Not Helpful"><i data-feather="thumbs-down" style="width:14px;height:14px;"></i></button>
                    </div>
                ` : ''}
            </div>
        `;
        
        msgDiv.innerHTML = bubbleHtml;
        chatMessages.appendChild(msgDiv);
        if (typeof feather !== 'undefined') feather.replace();
        scrollToBottom();
        
        return id;
    }
    
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Document Upload Logic for Chat
    const chatUploadBtn = document.getElementById('chatUploadBtn');
    const chatFileInput = document.getElementById('chatFileInput');

    if (chatUploadBtn && chatFileInput) {
        chatUploadBtn.addEventListener('click', () => {
            chatFileInput.click();
        });

        chatFileInput.addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (!file) return;

            const validExtensions = ['pdf', 'txt', 'docx'];
            const ext = file.name.split('.').pop().toLowerCase();
            if (!validExtensions.includes(ext)) {
                window.Toast?.error('Invalid file type. Supports PDF, DOCX, TXT only.');
                chatFileInput.value = '';
                return;
            }

            const botMsgId = addMessage(crypto.randomUUID());
            const contentEl = document.getElementById(`content-${botMsgId}`);
            contentEl.innerHTML = `<i data-feather="loader" class="spin" style="width: 14px; height: 14px;"></i> Uploading and indexing ${file.name}...`;
            if (typeof feather !== 'undefined') feather.replace();

            try {
                const formData = new FormData();
                formData.append('file', file);
                
                const response = await fetch('/api/v1/upload', {
                    method: 'POST',
                    body: formData,
                    // api.js handles auth, but here we do a direct fetch for formData. We need credentials if using cookies.
                    credentials: 'same-origin'
                });

                if (!response.ok) throw new Error('Upload failed');
                const result = await response.json();
                
                contentEl.innerHTML = `✅ Successfully uploaded and indexed: **${result.filename}**. You can now ask questions about it!`;
                if (typeof marked !== 'undefined') {
                    contentEl.innerHTML = marked.parse(contentEl.innerHTML);
                }
                window.Toast?.success('Document uploaded and indexed successfully!');
            } catch (error) {
                console.error('Chat upload error:', error);
                contentEl.innerHTML = `❌ Failed to upload ${file.name}.`;
                window.Toast?.error('Upload failed.');
            } finally {
                chatFileInput.value = '';
            }
        });
    }

    window.submitFeedback = async function(messageId, rating) {
        try {
            await ApiClient.submitFeedback(messageId, rating);
            const actionsDiv = document.getElementById(`actions-${messageId}`);
            if (actionsDiv) {
                actionsDiv.innerHTML = `<span style="font-size:0.8rem; color:var(--primary);"><i data-feather="check" style="width:14px;height:14px; vertical-align:middle;"></i> Feedback submitted</span>`;
                if (typeof feather !== 'undefined') feather.replace();
            }
            window.Toast?.success("Thank you for your feedback!");
        } catch (e) {
            console.error("Feedback failed", e);
            window.Toast?.error("Failed to submit feedback");
        }
    }

    window.copyMsg = function(id) {
        const el = document.getElementById(`content-${id}`);
        if (el) {
            navigator.clipboard.writeText(el.innerText);
            window.Toast?.success("Copied to clipboard");
        }
    }

    window.regenerateMsg = function() {
        alert("Regenerate not fully implemented on frontend, please re-type your query!");
    }

    async function sendMessage() {
        const text = chatInput.value.trim();
        if (!text) return;
        
        chatInput.value = '';
        const userMsgId = crypto.randomUUID();
        addMessage(userMsgId, true);
        document.getElementById(`content-${userMsgId}`).textContent = text;
        
        const botMsgId = crypto.randomUUID();
        addMessage(botMsgId, false);
        const contentDiv = document.getElementById(`content-${botMsgId}`);
        
        // Show loading
        contentDiv.innerHTML = 'Thinking... <i data-feather="loader" class="spin" style="width: 16px; height: 16px;"></i>';
        if (typeof feather !== 'undefined') feather.replace();
        
        try {
            // Need to get access token from cookies if required, but browser fetch will send it automatically 
            // if we use ApiClient or fetch with credentials. Using fetch here for streaming.
            const response = await fetch('/api/v1/chat/stream', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text, session_id: sessionId })
            });
            
            if (response.status === 401) {
                window.location.href = '/login';
                return;
            }
            if (!response.ok) {
                throw new Error(`HTTP Error ${response.status}`);
            }
            
            const reader = response.body.getReader();
            const decoder = new TextDecoder("utf-8");
            let fullText = "";
            let isFirstToken = true;
            
            while (true) {
                const { value, done } = await reader.read();
                if (done) break;
                
                const chunk = decoder.decode(value, { stream: true });
                const lines = chunk.split('\n');
                for (let line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.substring(6));
                            if (data.type === 'token') {
                                if (isFirstToken) {
                                    contentDiv.innerHTML = '';
                                    isFirstToken = false;
                                }
                                fullText += data.content;
                                contentDiv.innerHTML = marked.parse(fullText);
                                scrollToBottom();
                            } else if (data.type === 'metadata') {
                                if (data.metadata && data.metadata.sources && data.metadata.sources.length > 0) {
                                    const sourcesDiv = document.getElementById(`sources-${botMsgId}`);
                                    const uniqueSources = [...new Set(data.metadata.sources.map(s => `${s.document} (pg ${s.page})`))];
                                    sourcesDiv.innerHTML = `<strong>Sources:</strong> ${uniqueSources.join(', ')}`;
                                    sourcesDiv.style.display = 'block';
                                }
                            } else if (data.type === 'error') {
                                fullText += `\n**Error:** ${data.content}`;
                                contentDiv.innerHTML = marked.parse(fullText);
                            }
                        } catch (e) {
                            // ignore incomplete chunks if any
                        }
                    }
                }
            }
            
            document.getElementById(`actions-${botMsgId}`).style.display = 'flex';
            
        } catch (error) {
            contentDiv.innerHTML = 'Network error occurred.';
            document.getElementById(`actions-${botMsgId}`).style.display = 'flex';
        }
    }

    if (sendBtn) sendBtn.addEventListener('click', sendMessage);
    if (chatInput) {
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
    }
});

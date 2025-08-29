// VoxAura - ChatGPT Style Interface
class VoxAuraApp {
    constructor() {
        this.socket = null;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;
        this.sessionId = null;
        this.messageCount = 0;
        this.currentStreamingMessage = null;

        this.initializeApp();
        this.initializeWebSocket();
        this.initializeNeuralNetwork();
    }

    initializeApp() {
        this.sessionId = this.generateSessionId();
        this.currentPersona = 'default';

        // Event listeners
        document.getElementById('voiceBtn').addEventListener('click', () => this.toggleRecording());
        document.getElementById('sendBtn').addEventListener('click', () => this.sendMessage());
        document.getElementById('chatInput').addEventListener('keydown', (e) => this.handleKeyDown(e));
        document.getElementById('chatInput').addEventListener('input', () => this.autoResizeTextarea());
        document.getElementById('personaSelect').addEventListener('change', (e) => this.changePersona(e.target.value));

        // Sidebar event listeners
        document.getElementById('sidebarToggle').addEventListener('click', toggleSidebar);
        document.getElementById('newChatBtn').addEventListener('click', startNewChat);
        document.getElementById('chatSearch').addEventListener('input', searchChats);
    }

    initializeWebSocket() {
        this.socket = io();

        this.socket.on('connect', () => {
            console.log('✅ Connected to VoxAura');
            this.updateConnectionStatus(true);
            this.socket.emit('register_session', { session_id: this.sessionId });
        });

        this.socket.on('disconnect', () => {
            console.log('❌ Disconnected from VoxAura');
            this.updateConnectionStatus(false);
        });

        this.socket.on('llm_streaming_chunk', (data) => {
            this.updateStreamingMessage(data.chunk);
        });

        this.socket.on('llm_streaming_complete', (data) => {
            this.finalizeStreamingMessage(data.final_response);
            this.generateTTSForLastMessage();
        });

        this.socket.on('llm_error', (data) => {
            console.error('LLM error:', data.error);
            if (data.fallback_response) {
                this.addMessage('assistant', data.fallback_response, true);
            }
        });
    }

    initializeNeuralNetwork() {
        // Neural network canvas is not needed for this interface
        console.log('Neural network background handled by CSS animations');
    }

    generateSessionId() {
        return 'voxaura_' + Date.now() + '_' + Math.random().toString(36).substring(2, 15);
    }

    changePersona(persona) {
        const previousPersona = this.currentPersona;
        this.currentPersona = persona;

        // Update status text
        const statusText = document.querySelector('.status-text');
        const personaNames = {
            'default': 'VoxAura - Premium Voice Assistant',
            'pirate': 'Captain VoxBeard - Ahoy there, matey!'
        };

        statusText.textContent = personaNames[persona] || 'Premium Voice Assistant - Ready';

        // Add voice change announcement if persona actually changed
        if (previousPersona !== persona) {
            this.announceVoiceChange(persona);

            // Add persona change message
            this.addPersonaChangeMessage(persona);
        }

        console.log('🎭 Persona changed to:', persona);
        console.log('🎵 Voice characteristics updated for persona:', persona);
    }

    announceVoiceChange(persona) {
        const announcements = {
            'pirate': 'Arrr! Switching to me pirate voice now, matey!',
            'default': 'Switching back to my default voice.'
        };

        const announcement = announcements[persona];
        if (announcement) {
            console.log('🎭 VOICE CHANGE ANNOUNCEMENT:', announcement);

            // Create TTS for voice change announcement
            this.generateTTSAnnouncement(announcement, persona);

            // Show visual feedback
            this.showVoiceChangeNotification(announcement);
        }
    }

    async generateTTSAnnouncement(text, persona) {
        try {
            console.log('🔊 Generating voice change announcement TTS...');

            const response = await fetch('/generate-tts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    text: text,
                    persona: persona 
                })
            });

            const data = await response.json();

            if (data.success && data.audio_url) {
                console.log('✅ Voice change announcement TTS generated');

                // Play the announcement
                const audio = new Audio(data.audio_url);
                audio.play().then(() => {
                    console.log('🎵 Voice change announcement played');
                }).catch(error => {
                    console.error('❌ Failed to play voice change announcement:', error);
                });
            }
        } catch (error) {
            console.error('❌ Voice change announcement TTS error:', error);
        }
    }

    showVoiceChangeNotification(message) {
        // Create temporary notification
        const notification = document.createElement('div');
        notification.className = 'voice-change-notification';
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-volume-up"></i>
                <span>${message}</span>
            </div>
        `;

        // Add to page
        document.body.appendChild(notification);

        // Remove after 3 seconds
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    addPersonaChangeMessage(persona) {
        const personaIntros = {
            'default': 'Hello! I\'m VoxAura, your helpful AI assistant. How can I help you today?',
            'pirate': 'Arrr! Ahoy there, me trusted crew member! Captain VoxBeard at yer service, ready to sail these digital seas together! The old ship creaks with excitement... What treasure of knowledge can this old sea dog help ye find today? Say "Test pirate voice" if ye want to hear me full pirate speech, matey!'
        };

        const message = personaIntros[persona];
        this.addMessage('assistant', message, true);

        // Add special debug info for pirate voice
        if (persona === 'pirate') {
            console.log('🏴‍☠️ PIRATE VOICE FEATURES ACTIVATED:');
            console.log('   • Lower pitch voice (-15%)');
            console.log('   • Slower speech (10% reduction)');
            console.log('   • Gruff/authoritative style');
            console.log('   • Dramatic pauses and emphasis');
            console.log('   • Pirate vocabulary and expressions');
            console.log('   • Interactive crew member relationship');
            console.log('🎯 Say "Test pirate voice" to verify voice changes!');
        }
    }

    updateConnectionStatus(connected) {
        const status = document.getElementById('connectionStatus');
        if (connected) {
            status.classList.add('active');
            status.style.background = '#00ff88';
        } else {
            status.classList.remove('active');
            status.style.background = '#ff4444';
        }
    }

    autoResizeTextarea() {
        const textarea = document.getElementById('chatInput');
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }

    handleKeyDown(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            this.sendMessage();
        }
    }

    toggleRecording() {
        if (this.isRecording) {
            this.stopRecording();
        } else {
            this.startRecording();
        }
    }

    async startRecording() {
        try {
            console.log('🎤 User started recording...');

            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.mediaRecorder = new MediaRecorder(stream);
            this.audioChunks = [];

            // Add console logs for debugging
            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                    console.log('📦 Audio chunk captured:', event.data.size, 'bytes');
                }
            };

            this.mediaRecorder.onstop = () => {
                const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
                console.log('🛑 Recording stopped');
                console.log(`📦 Audio blob created (${audioBlob.size} bytes)`);
                this.sendAudioMessage(audioBlob);
            };

            this.mediaRecorder.start();
            this.isRecording = true;
            this.updateRecordingUI(true);

            console.log('✅ Recording started successfully');

        } catch (error) {
            console.error('❌ Microphone error:', error);
            alert('Please allow microphone access to use voice features.');
        }
    }

    stopRecording() {
        if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
            this.mediaRecorder.stop();
            console.log('🛑 User stopped recording...');
            console.log('🔄 Turn detection: User stopped speaking');
            this.isRecording = false;
            this.updateRecordingUI(false);

            console.log('✅ Turn detection completed');
        }
    }

    updateRecordingUI(isRecording) {
        const recordButton = document.getElementById('voiceBtn');
        const recordIcon = document.getElementById('voiceIcon');

        if (recordButton) {
            // Add voice-btn class for enhanced styling
            recordButton.classList.add('voice-btn');

            if (isRecording) {
                recordButton.classList.add('recording');
                if (recordIcon) {
                    // Handle both regular elements and SVG elements
                    if (recordIcon.className && typeof recordIcon.className === 'string') {
                        recordIcon.className = 'fas fa-stop';
                    } else if (recordIcon.setAttribute) {
                        recordIcon.setAttribute('class', 'fas fa-stop');
                    }
                }
            } else {
                recordButton.classList.remove('recording');
                if (recordIcon) {
                    // Handle both regular elements and SVG elements
                    if (recordIcon.className && typeof recordIcon.className === 'string') {
                        recordIcon.className = 'fas fa-microphone';
                    } else if (recordIcon.setAttribute) {
                        recordIcon.setAttribute('class', 'fas fa-microphone');
                    }
                }
            }
        }
    }

    async sendMessage() {
        const input = document.getElementById('chatInput');
        const message = input.value.trim();

        if (!message) return;

        console.log('💬 TEXT PIPELINE INITIATED');
        console.log('📝 User typed message:', message);
        console.log('📏 Message length:', message.length, 'characters');

        input.value = '';
        input.style.height = 'auto';

        this.addMessage('user', message);
        this.showProcessingIndicator();

        try {
            console.log('📤 Sending text message to LLM service...');
            const response = await fetch('/llm/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    message: message,
                    persona: this.currentPersona 
                })
            });

            console.log('📥 LLM service response status:', response.status);

            const data = await response.json();
            console.log('📊 LLM service response data:', data);

            this.hideProcessingIndicator();

            if (data.response) {
                console.log('🤖 LLM Response:', data.response);
                console.log('📏 Response length:', data.response.length, 'characters');
                this.addMessage('assistant', data.response, true);
                console.log('✅ TEXT PIPELINE SUCCESS');
            } else {
                console.error('❌ No response from LLM service');
                this.addMessage('assistant', 'Sorry, I encountered an error processing your message.');
            }
        } catch (error) {
            console.error('❌ TEXT PIPELINE ERROR:', error);
            this.hideProcessingIndicator();
            this.addMessage('assistant', 'Network error. Please try again.');
        }
    }

    async sendAudioMessage(audioBlob) {
        console.log('🎯 Voice pipeline initiated');
        console.log('📁 Audio file size:', audioBlob.size, 'bytes');

        this.showProcessingIndicator();

        const formData = new FormData();
        formData.append('audio', audioBlob, 'voice_message.webm');

        try {
            console.log('📤 Sending audio message to server...');
            const response = await fetch(`/agent/chat/${this.sessionId}`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            console.log('📥 Server response received:', result);

            if (result.success) {
                const userMessage = result.transcription;
                const botResponse = result.llm_response;

                console.log('👤 User input:', userMessage);
                console.log('🤖 LLM response:', botResponse);

                this.addMessage('user', userMessage);
                this.addMessage('assistant', botResponse, true);

                // Play audio response if available
                if (result.audio_url) {
                    console.log('🔊 Playing audio response:', result.audio_url);
                    await this.playAudioResponse(result.audio_url);
                }
            } else {
                console.error('❌ Pipeline failed:', result.error);
                this.addMessage('assistant', 'Sorry, I encountered an error processing your message.');
            }
        } catch (error) {
            console.error('❌ Audio processing error:', error);
            this.hideProcessingIndicator();
            this.addMessage('assistant', 'Network error. Please try again.');
        }
    }

    addMessage(role, content, enableAudio = false) {
        const chatMessages = document.getElementById('chatMessages');

        // Remove welcome screen if it exists
        const welcomeScreen = chatMessages.querySelector('.welcome-screen');
        if (welcomeScreen) {
            welcomeScreen.remove();
        }

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;

        const messageId = 'msg_' + Date.now() + '_' + Math.random().toString(36).substring(2);
        const avatarIcon = role === 'user' ? 'fas fa-user' : 'fas fa-robot';

        let audioControls = '';
        if (role === 'assistant' && enableAudio) {
            audioControls = `
                <div class="audio-controls">
                    <button class="audio-btn" onclick="app.playAudio('${messageId}', this)">
                        <i class="fas fa-play"></i> Play
                    </button>
                    <button class="audio-btn" onclick="app.stopAudio('${messageId}')">
                        <i class="fas fa-stop"></i> Stop
                    </button>
                </div>
                <audio id="audio_${messageId}" style="display: none;"></audio>
            `;
        }

        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="${avatarIcon}"></i>
            </div>
            <div class="message-content" id="${messageId}">
                ${content}
                ${audioControls}
            </div>
        `;

        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        if (role === 'assistant' && enableAudio) {
            this.generateTTS(messageId, content);
        }
    }

    updateStreamingMessage(chunk) {
        if (!this.currentStreamingMessage) {
            this.addMessage('assistant', '', false);
            const messages = document.querySelectorAll('.message.assistant');
            this.currentStreamingMessage = messages[messages.length - 1].querySelector('.message-content');
            this.currentStreamingMessage.classList.add('streaming-text');
        }

        this.currentStreamingMessage.textContent += chunk;
        document.getElementById('chatMessages').scrollTop = document.getElementById('chatMessages').scrollHeight;
    }

    finalizeStreamingMessage(finalResponse) {
        if (this.currentStreamingMessage) {
            this.currentStreamingMessage.textContent = finalResponse;
            this.currentStreamingMessage.classList.remove('streaming-text');

            const messageId = 'msg_' + Date.now() + '_' + Math.random().toString(36).substring(2);
            this.currentStreamingMessage.id = messageId;

            const audioControls = `
                <div class="audio-controls">
                    <button class="audio-btn" onclick="app.playAudio('${messageId}', this)">
                        <i class="fas fa-play"></i> Play
                    </button>
                    <button class="audio-btn" onclick="app.stopAudio('${messageId}')">
                        <i class="fas fa-stop"></i> Stop
                    </button>
                </div>
                <audio id="audio_${messageId}" style="display: none;"></audio>
            `;

            this.currentStreamingMessage.innerHTML = finalResponse + audioControls;
            this.currentStreamingMessage = null;

            this.generateTTS(messageId, finalResponse);
        }
    }

    showProcessingIndicator() {
        const chatMessages = document.getElementById('chatMessages');
        const indicator = document.createElement('div');
        indicator.className = 'processing-indicator';
        indicator.id = 'processingIndicator';
        indicator.innerHTML = `
            <i class="fas fa-spinner fa-spin"></i>
            <span>Processing...</span>
        `;
        chatMessages.appendChild(indicator);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    hideProcessingIndicator() {
        const indicator = document.getElementById('processingIndicator');
        if (indicator) {
            indicator.remove();
        }
    }

    async generateTTS(messageId, text) {
        try {
            console.log('🔊 TTS Generation started for message:', messageId);
            console.log('📝 TTS Text:', text);

            const response = await fetch('/generate-tts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    text: text,
                    persona: this.currentPersona 
                })
            });

            console.log('📥 TTS Response status:', response.status);

            const data = await response.json();
            console.log('📊 TTS Response data:', data);

            if (data.success && data.audio_url) {
                console.log('✅ TTS SUCCESS - Audio URL:', data.audio_url);
                const audioElement = document.getElementById(`audio_${messageId}`);
                if (audioElement) {
                    audioElement.src = data.audio_url;
                    audioElement.preload = 'metadata';
                    console.log('🎵 Audio element updated for message:', messageId);
                }
            } else {
                console.warn('⚠️ TTS did not return audio URL');
            }
        } catch (error) {
            console.error('❌ TTS Generation error:', error);
        }
    }

    generateTTSForLastMessage() {
        const assistantMessages = document.querySelectorAll('.message.assistant .message-content');
        if (assistantMessages.length > 0) {
            const lastMessage = assistantMessages[assistantMessages.length - 1];
            if (lastMessage.id && !document.getElementById(`audio_${lastMessage.id}`)) {
                this.generateTTS(lastMessage.id, lastMessage.textContent);
            }
        }
    }

    playAudio(messageId, button) {
        const audioElement = document.getElementById(`audio_${messageId}`);

        if (!audioElement || !audioElement.src) {
            console.warn('No audio available');
            return;
        }

        if (audioElement.paused) {
            audioElement.play().then(() => {
                button.innerHTML = '<i class="fas fa-pause"></i> Pause';
                audioElement.onended = () => {
                    button.innerHTML = '<i class="fas fa-play"></i> Play';
                };
            }).catch(error => {
                console.error('Audio playback failed:', error);
            });
        } else {
            audioElement.pause();
            button.innerHTML = '<i class="fas fa-play"></i> Play';
        }
    }

    stopAudio(messageId) {
        const audioElement = document.getElementById(`audio_${messageId}`);
        const playButton = document.querySelector(`button[onclick="app.playAudio('${messageId}', this)"]`);

        if (audioElement) {
            audioElement.pause();
            audioElement.currentTime = 0;

            if (playButton) {
                playButton.innerHTML = '<i class="fas fa-play"></i> Play';
            }
        }
    }



    playAudioResponse(audioUrl) {
        return new Promise((resolve, reject) => {
            const audio = new Audio(audioUrl);
            audio.play().then(() => {
                audio.onended = () => {
                    resolve();
                };
            }).catch(error => {
                console.error('Error playing audio response:', error);
                reject(error);
            });
        });
    }

    // Demo weather skill
    demoWeatherSkill() {
        console.log('🌤️ DAY 25: DEMONSTRATING WEATHER SKILL');

        // Demo messages for weather skill
        const weatherDemos = [
            "What's the weather like in New York?",
            "Tell me the temperature in London",
            "How's the weather in Tokyo?",
            "What's the forecast for Paris?"
        ];

        const randomDemo = weatherDemos[Math.floor(Math.random() * weatherDemos.length)];

        // Set the input and send
        const input = document.getElementById('chatInput');
        input.value = randomDemo;
        this.sendMessage();

        console.log('🌤️ Weather skill demo triggered:', randomDemo);
    }
}

// Global variables
let currentSessionId = generateSessionId();
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;
let isPlaying = false;
let currentAudio = null;
let socket = null;
let chatHistory = JSON.parse(localStorage.getItem('voxaura_chat_history') || '[]');
let currentChatMessages = [];


// Sidebar functionality
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('open');
}

function startNewChat() {
    currentSessionId = generateSessionId();
    currentChatMessages = [];

    // Clear chat area
    const chatHistoryElement = document.getElementById('chatHistory');
    chatHistoryElement.innerHTML = '';

    // Update UI
    updateChatTitle('New Chat');
    toggleSidebar();

    // Focus on text input
    document.getElementById('chatInput').focus();
}

function saveChatToHistory() {
    if (currentChatMessages.length === 0) return;

    const firstMessage = currentChatMessages[0];
    const title = firstMessage.text ? 
        firstMessage.text.substring(0, 30) + (firstMessage.text.length > 30 ? '...' : '') :
        'Voice Chat';

    const chatData = {
        id: currentSessionId,
        title: title,
        messages: [...currentChatMessages],
        timestamp: new Date().toISOString(),
        preview: firstMessage.text || 'Voice conversation'
    };

    // Remove existing chat with same ID
    chatHistory = chatHistory.filter(chat => chat.id !== currentSessionId);

    // Add to beginning of array
    chatHistory.unshift(chatData);

    // Keep only last 50 chats
    if (chatHistory.length > 50) {
        chatHistory = chatHistory.slice(0, 50);
    }

    // Save to localStorage
    localStorage.setItem('voxaura_chat_history', JSON.stringify(chatHistory));

    // Update sidebar
    updateChatHistoryList();
}

function loadChatFromHistory(chatId) {
    const chat = chatHistory.find(c => c.id === chatId);
    if (!chat) return;

    currentSessionId = chatId;
    currentChatMessages = [...chat.messages];

    // Clear and reload chat area
    const chatHistoryElement = document.getElementById('chatHistory');
    chatHistoryElement.innerHTML = '';

    // Restore messages
    chat.messages.forEach(message => {
        if (message.type === 'user') {
            addUserMessage(message.text, message.isVoice);
        } else if (message.type === 'ai') {
            addAIMessage(message.text, message.audioUrl);
        }
    });

    // Update UI
    updateChatTitle(chat.title);
    updateChatHistoryList();
    toggleSidebar();
}

function updateChatHistoryList() {
    const listElement = document.getElementById('chatHistoryList');
    if (!listElement) return;

    listElement.innerHTML = '';

    chatHistory.forEach(chat => {
        const item = document.createElement('div');
        item.className = 'chat-history-item';
        if (chat.id === currentSessionId) {
            item.classList.add('active');
        }

        const timeStr = new Date(chat.timestamp).toLocaleDateString();

        item.innerHTML = `
            <div class="chat-title">${chat.title}</div>
            <div class="chat-preview">${chat.preview}</div>
            <div class="chat-time">${timeStr}</div>
        `;

        item.onclick = () => loadChatFromHistory(chat.id);
        listElement.appendChild(item);
    });
}

function searchChats() {
    const searchTerm = document.getElementById('chatSearch').value.toLowerCase();
    const items = document.querySelectorAll('.chat-history-item');

    items.forEach(item => {
        const title = item.querySelector('.chat-title').textContent.toLowerCase();
        const preview = item.querySelector('.chat-preview').textContent.toLowerCase();

        if (title.includes(searchTerm) || preview.includes(searchTerm)) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}

function updateChatTitle(title) {
    document.title = `VoxAura AI - ${title}`;
}

// Auto-record after AI responses
function enableAutoRecord() {
}

function addUserMessage(message, isVoice = false) {
    const chatHistory = document.getElementById('chatHistory');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user-message';

    const icon = isVoice ? 'fa-microphone' : 'fa-keyboard';

    messageDiv.innerHTML = `
        <div class="message-content">
            <div class="message-header">
                <i class="fas ${icon}"></i>
                <span>You</span>
                <small>${new Date().toLocaleTimeString()}</small>
            </div>
            <div class="message-text">${message}</div>
        </div>
    `;

    chatHistory.appendChild(messageDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;

    // Save to current chat messages
    currentChatMessages.push({
        type: 'user',
        text: message,
        isVoice: isVoice,
        timestamp: new Date().toISOString()
    });
}

function addAIMessage(message, audioUrl = null) {
    const chatHistory = document.getElementById('chatHistory');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message ai-message';

    messageDiv.innerHTML = `
        <div class="message-content">
            <div class="message-header">
                <i class="fas fa-robot"></i>
                <span>VoxAura AI</span>
                <small>${new Date().toLocaleTimeString()}</small>
            </div>
            <div class="message-text">${message}</div>
            ${audioUrl ? `
                <div class="audio-controls">
                    <button class="btn btn-sm btn-outline-primary me-2" onclick="playAudio('${audioUrl}')">
                        <i class="fas fa-play"></i> Play
                    </button>
                    <button class="btn btn-sm btn-outline-secondary" onclick="generateSummary('${message.replace(/'/g, "\\'")}')">
                        <i class="fas fa-compress-alt"></i> Summary
                    </button>
                </div>
            ` : ''}
        </div>
    `;

    chatHistory.appendChild(messageDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;

    // Save to current chat messages
    currentChatMessages.push({
        type: 'ai',
        text: message,
        audioUrl: audioUrl,
        timestamp: new Date().toISOString()
    });

    // Save chat to history
    saveChatToHistory();
}

// Initialize app when page loads
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();

    // Initialize chat history
    updateChatHistoryList();

    // Initialize text input
    const textInput = document.getElementById('chatInput');
    if (textInput) {
        textInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendTextMessage();
            }
        });
    }

    // Close sidebar when clicking outside
    document.addEventListener('click', function(e) {
        const sidebar = document.getElementById('sidebar');
        const sidebarToggle = document.querySelector('.sidebar-toggle');

        if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
            sidebar.classList.remove('open');
        }
    });
});

// Initialize voice controls
function initializeVoiceControls() {
    console.log('✅ Voice controls initialized');
    // Voice controls are handled within VoxAuraApp class
}

// PDF upload initialization function  
function initializePdfUpload() {
    console.log('✅ PDF upload initialized');

    const fileInput = document.getElementById('pdfFileInput');
    const uploadBtn = document.getElementById('uploadPdfBtn');

    if (fileInput && uploadBtn) {
        uploadBtn.addEventListener('click', async () => {
            const file = fileInput.files[0];
            if (!file) {
                alert('Please select a PDF file first');
                return;
            }

            const formData = new FormData();
            formData.append('file', file);

            try {
                uploadBtn.disabled = true;
                uploadBtn.textContent = 'Uploading...';

                const response = await fetch('/upload-pdf', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (result.success) {
                    // Add the summary to chat
                    if (window.app) {
                        window.app.addMessage('assistant', result.summary, true);
                    }
                } else {
                    alert('Upload failed: ' + result.error);
                }
            } catch (error) {
                console.error('Upload error:', error);
                alert('Upload failed');
            } finally {
                uploadBtn.disabled = false;
                uploadBtn.textContent = 'Upload PDF';
                fileInput.value = '';
            }
        });
    }
}

// Initialize voice controls
initializeVoiceControls();

// Initialize PDF upload
initializePdfUpload();

// Utility functions to be used in HTML onclick attributes
function sendTextMessage() {
    if (window.app) {
        window.app.sendMessage();
    }
}

function playAudio(audioUrl) {
    if (window.app) {
        // Find the message ID associated with this audio URL
        // This is a bit of a hack, assumes the button's parent has an audio tag
        const button = event.target.closest('.audio-controls').querySelector('button');
        const messageId = button.getAttribute('onclick').match(/app\.playAudio\('([^']+)', this\)/)[1];
        window.app.playAudio(messageId, button);
    }
}

function generateSummary(message) {
    if (window.app) {
        // This function is a placeholder for generating summaries
        console.log("Generating summary for:", message);
        window.app.addMessage('assistant', `Summary for "${message}" would be generated here.`);
    }
}


// Initialize app
let app;
document.addEventListener('DOMContentLoaded', function() {
    app = new VoxAuraApp();
});
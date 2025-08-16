
/**
 * WebSocket Client for VoxAura
 * Handles real-time communication with the server
 */

class WebSocketClient {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectInterval = 3000;
        
        this.initializeElements();
        this.connect();
    }

    initializeElements() {
        this.wsIndicator = document.getElementById('wsIndicator');
        this.wsStatusText = document.getElementById('wsStatusText');
        this.chatMessages = document.getElementById('chatMessages');
    }

    connect() {
        try {
            console.log('Connecting to WebSocket server...');
            this.updateStatus('connecting', 'Connecting to WebSocket...');
            
            // Initialize Socket.IO connection
            this.socket = io({
                transports: ['websocket', 'polling'],
                timeout: 10000,
                forceNew: true
            });

            this.setupEventHandlers();
            
        } catch (error) {
            console.error('WebSocket connection error:', error);
            this.handleConnectionError();
        }
    }

    setupEventHandlers() {
        this.socket.on('connect', () => {
            console.log('Connected to WebSocket server');
            this.isConnected = true;
            this.reconnectAttempts = 0;
            this.updateStatus('connected', 'WebSocket Connected');
            
            // Register session
            this.socket.emit('register_session', {
                session_id: window.sessionId || 'default'
            });
        });

        this.socket.on('disconnect', () => {
            console.log('Disconnected from WebSocket server');
            this.isConnected = false;
            this.updateStatus('disconnected', 'WebSocket Disconnected');
            this.attemptReconnect();
        });

        this.socket.on('status', (data) => {
            console.log('Server status:', data);
            if (data.connected) {
                this.updateStatus('connected', `Connected (${data.active_sessions} sessions)`);
            }
        });

        this.socket.on('echo_response', (data) => {
            console.log('Echo response:', data);
            this.displayMessage(data.echo_response, 'system');
        });

        this.socket.on('chat_response', (data) => {
            console.log('Chat response:', data);
            this.displayMessage(data.ai_response, 'assistant');
        });

        this.socket.on('connect_error', (error) => {
            console.error('WebSocket connection error:', error);
            this.handleConnectionError();
        });

        this.socket.on('error', (error) => {
            console.error('WebSocket error:', error);
        });
    }

    updateStatus(status, text) {
        if (this.wsIndicator && this.wsStatusText) {
            this.wsIndicator.className = `connection-indicator ${status}`;
            this.wsStatusText.textContent = text;
        }
    }

    displayMessage(message, type = 'system') {
        if (this.chatMessages) {
            const messageElement = document.createElement('div');
            messageElement.className = `message ${type}`;
            messageElement.innerHTML = `
                <div class="message-content">
                    <span class="message-text">${message}</span>
                    <span class="message-time">${new Date().toLocaleTimeString()}</span>
                </div>
            `;
            this.chatMessages.appendChild(messageElement);
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }
    }

    sendMessage(message) {
        if (this.isConnected && this.socket) {
            this.socket.emit('message', message);
            this.displayMessage(message, 'user');
        } else {
            console.warn('Cannot send message: WebSocket not connected');
            this.displayMessage('Cannot send message: Not connected', 'error');
        }
    }

    sendChatMessage(message, sessionId = null) {
        if (this.isConnected && this.socket) {
            this.socket.emit('chat_message', {
                message: message,
                session_id: sessionId || window.sessionId || 'default'
            });
            this.displayMessage(message, 'user');
        } else {
            console.warn('Cannot send chat message: WebSocket not connected');
            this.displayMessage('Cannot send message: Not connected', 'error');
        }
    }

    handleConnectionError() {
        this.isConnected = false;
        this.updateStatus('disconnected', 'Connection Failed');
        this.attemptReconnect();
    }

    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            this.updateStatus('connecting', `Reconnecting... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
            
            setTimeout(() => {
                this.connect();
            }, this.reconnectInterval);
        } else {
            this.updateStatus('disconnected', 'Connection failed - Refresh to retry');
        }
    }

    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
        }
    }
}

// Initialize WebSocket client when DOM loads
document.addEventListener('DOMContentLoaded', () => {
    window.wsClient = new WebSocketClient();
});

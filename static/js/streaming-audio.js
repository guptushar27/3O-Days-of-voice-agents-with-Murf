
/**
 * Streaming Audio Client for VoxAura
 * Handles Day 16: Audio Streaming and Day 17: Real-time Transcription
 */

class StreamingAudioClient {
    constructor() {
        this.socket = null;
        this.mediaRecorder = null;
        this.audioStream = null;
        this.isStreaming = false;
        this.isTranscribing = false;
        this.sessionId = 'streaming_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        
        this.initializeElements();
        this.connectWebSocket();
        
        console.log('🎤 Streaming Audio Client initialized');
        console.log('📋 Session ID:', this.sessionId);
    }

    initializeElements() {
        // Day 16 controls
        this.startStreamBtn = document.getElementById('startStream');
        this.stopStreamBtn = document.getElementById('stopStream');
        
        // Day 17 controls
        this.startTranscriptionBtn = document.getElementById('startTranscription');
        this.stopTranscriptionBtn = document.getElementById('stopTranscription');
        
        // Display elements
        this.statusDisplay = document.getElementById('streamingStatus');
        this.transcriptionDisplay = document.getElementById('transcriptionOutput');
        
        // Bind event listeners
        if (this.startStreamBtn) {
            this.startStreamBtn.addEventListener('click', () => this.startAudioStreaming());
        }
        if (this.stopStreamBtn) {
            this.stopStreamBtn.addEventListener('click', () => this.stopAudioStreaming());
        }
        if (this.startTranscriptionBtn) {
            this.startTranscriptionBtn.addEventListener('click', () => this.startTranscription());
        }
        if (this.stopTranscriptionBtn) {
            this.stopTranscriptionBtn.addEventListener('click', () => this.stopTranscription());
        }
    }

    connectWebSocket() {
        this.updateStatus('Connecting to WebSocket server...', 'connecting');
        
        this.socket = io({
            transports: ['websocket', 'polling'],
            timeout: 10000,
            forceNew: true
        });

        this.setupSocketHandlers();
    }

    setupSocketHandlers() {
        this.socket.on('connect', () => {
            console.log('✅ Connected to WebSocket server');
            this.updateStatus('Connected to VoxAura WebSocket server', 'connected');
            
            // Register session
            this.socket.emit('register_session', {
                session_id: this.sessionId
            });
        });

        this.socket.on('disconnect', () => {
            console.log('❌ Disconnected from WebSocket server');
            this.updateStatus('Disconnected from WebSocket server', 'error');
        });

        this.socket.on('status', (data) => {
            console.log('Server status:', data);
            this.updateStatus(`Connected (${data.active_sessions} active sessions)`, 'connected');
        });

        this.socket.on('audio_processed', (data) => {
            console.log('Audio processed:', data);
            if (data.status === 'saved') {
                this.updateStatus(`Audio chunk ${data.chunk_count} saved successfully`, 'streaming');
            }
        });

        this.socket.on('transcription_status', (data) => {
            console.log('Transcription status:', data);
            if (data.status === 'started') {
                this.updateStatus('Real-time transcription active - Speak now!', 'transcribing');
            } else if (data.status === 'error') {
                this.updateStatus(data.message, 'error');
                this.updateTranscriptionUI(false);
                this.isTranscribing = false;
            } else if (data.status === 'stopped') {
                this.updateStatus('Real-time transcription stopped', 'info');
                this.updateTranscriptionUI(false);
                this.isTranscribing = false;
            }
        });

        this.socket.on('transcription', (data) => {
            console.log('📝 DAY 17 TRANSCRIPTION RECEIVED:', data.text);
            this.displayTranscription(data.text);
        });

        this.socket.on('streaming_transcription_response', (data) => {
            console.log('Streaming transcription response:', data);
        });

        // Day 18: Turn detection handler
        this.socket.on('turn_detected', (data) => {
            console.log('🎯 DAY 18 TURN DETECTION: User stopped talking');
            console.log('Turn detected:', data);
            this.displayTurnDetection(data);
        });

        this.socket.on('error', (error) => {
            console.error('Socket error:', error);
            this.updateStatus('WebSocket error: ' + error, 'error');
        });
    }

    async startAudioStreaming() {
        try {
            console.log('🎤 Starting Day 16 audio streaming...');
            this.updateStatus('Requesting microphone access...', 'starting');

            // Get user media
            this.audioStream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    sampleRate: 16000,
                    channelCount: 1,
                    echoCancellation: true,
                    noiseSuppression: true
                }
            });

            // Create MediaRecorder
            this.mediaRecorder = new MediaRecorder(this.audioStream, {
                mimeType: 'audio/webm;codecs=opus'
            });

            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0 && this.socket && this.socket.connected) {
                    // Convert blob to base64 and send
                    const reader = new FileReader();
                    reader.onload = () => {
                        const base64Data = reader.result.split(',')[1];
                        this.socket.emit('audio_stream', {
                            audio_chunk: base64Data,
                            session_id: this.sessionId,
                            timestamp: Date.now()
                        });
                    };
                    reader.readAsDataURL(event.data);
                }
            };

            this.mediaRecorder.onerror = (event) => {
                console.error('MediaRecorder error:', event.error);
                this.updateStatus('Recording error: ' + event.error, 'error');
            };

            // Start recording with 250ms chunks
            this.mediaRecorder.start(250);
            this.isStreaming = true;
            this.updateUI(true, this.isTranscribing);
            this.updateStatus('🎤 Audio streaming active - Speaking into microphone...', 'streaming');

            console.log('✅ Day 16 audio streaming started successfully');

        } catch (error) {
            console.error('Failed to start audio streaming:', error);
            this.updateStatus('Failed to access microphone: ' + error.message, 'error');
        }
    }

    stopAudioStreaming() {
        console.log('🔴 Stopping Day 16 audio streaming...');

        if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
            this.mediaRecorder.stop();
        }

        if (this.audioStream) {
            this.audioStream.getTracks().forEach(track => track.stop());
            this.audioStream = null;
        }

        this.isStreaming = false;
        this.updateUI(false, this.isTranscribing);
        this.updateStatus('Audio streaming stopped', 'stopped');

        console.log('✅ Day 16 audio streaming stopped');
    }

    startTranscription() {
        if (!this.socket || !this.socket.connected) {
            this.updateStatus('WebSocket not connected', 'error');
            return;
        }

        console.log('📝 Starting Day 17 real-time transcription...');
        
        this.socket.emit('start_streaming_transcription', {
            session_id: this.sessionId
        });
        
        this.isTranscribing = true;
        this.updateTranscriptionUI(true);
        this.updateStatus('Starting real-time transcription with AssemblyAI...', 'starting');

        // Also start audio streaming for transcription
        if (!this.isStreaming) {
            this.startAudioStreamingForTranscription();
        }
    }

    async startAudioStreamingForTranscription() {
        try {
            console.log('🎤 Starting audio streaming for transcription...');

            this.audioStream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    sampleRate: 16000,
                    channelCount: 1,
                    echoCancellation: true,
                    noiseSuppression: true
                }
            });

            this.mediaRecorder = new MediaRecorder(this.audioStream, {
                mimeType: 'audio/webm;codecs=opus'
            });

            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0 && this.socket && this.socket.connected && this.isTranscribing) {
                    const reader = new FileReader();
                    reader.onload = () => {
                        const base64Data = reader.result.split(',')[1];
                        this.socket.emit('streaming_audio_transcription', {
                            audio_chunk: base64Data,
                            session_id: this.sessionId,
                            timestamp: Date.now()
                        });
                    };
                    reader.readAsDataURL(event.data);
                }
            };

            this.mediaRecorder.start(250);
            console.log('✅ Audio streaming for transcription started');

        } catch (error) {
            console.error('Failed to start audio for transcription:', error);
            this.updateStatus('Failed to access microphone for transcription: ' + error.message, 'error');
        }
    }

    stopTranscription() {
        console.log('🔴 Stopping Day 17 real-time transcription...');
        
        if (this.socket && this.socket.connected) {
            this.socket.emit('stop_streaming_transcription', {
                session_id: this.sessionId
            });
        }
        
        this.isTranscribing = false;
        this.updateTranscriptionUI(false);
        this.updateStatus('Real-time transcription stopped', 'stopped');

        // Stop audio streaming if it was started for transcription
        if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
            this.mediaRecorder.stop();
        }
        if (this.audioStream) {
            this.audioStream.getTracks().forEach(track => track.stop());
            this.audioStream = null;
        }

        console.log('✅ Day 17 transcription stopped');
    }

    displayTranscription(text) {
        console.log('📝 DAY 17 TRANSCRIPTION OUTPUT:', text);
        
        if (!this.transcriptionDisplay) return;

        const transcriptionElement = document.createElement('div');
        const isPartial = text.includes('PARTIAL:');
        const isFinal = text.includes('FINAL:');
        
        transcriptionElement.className = `transcription-item mb-3 p-3 border rounded ${isPartial ? 'border-warning bg-warning bg-opacity-10' : 'border-success bg-success bg-opacity-10'}`;
        transcriptionElement.innerHTML = `
            <div class="d-flex align-items-start">
                <i class="fas fa-${isPartial ? 'circle-notch fa-spin text-warning' : 'check-circle text-success'} me-3 mt-1"></i>
                <div class="flex-grow-1">
                    <strong class="${isPartial ? 'text-warning' : 'text-success'}">${isPartial ? 'Partial' : 'Final'} Transcription:</strong>
                    <div class="mt-1">${text.replace(/^(PARTIAL:|FINAL:)\s*/, '')}</div>
                    <small class="text-muted">${new Date().toLocaleTimeString()}</small>
                </div>
            </div>
        `;
        
        this.transcriptionDisplay.appendChild(transcriptionElement);
        this.transcriptionDisplay.scrollTop = this.transcriptionDisplay.scrollHeight;

        // Animation
        transcriptionElement.style.opacity = '0';
        transcriptionElement.style.transform = 'translateY(-10px)';
        setTimeout(() => {
            transcriptionElement.style.transition = 'all 0.3s ease';
            transcriptionElement.style.opacity = '1';
            transcriptionElement.style.transform = 'translateY(0)';
        }, 100);
    }

    displayTurnDetection(data) {
        console.log('🎯 DAY 18 TURN DETECTION: Displaying in UI');
        
        if (!this.transcriptionDisplay) return;

        const turnElement = document.createElement('div');
        turnElement.className = 'turn-detection mb-3 p-3 border border-primary bg-primary bg-opacity-10 rounded';
        turnElement.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas fa-hand-paper text-primary me-3 fa-lg"></i>
                <div class="flex-grow-1">
                    <strong class="text-primary">🎯 Turn Detected (Day 18):</strong> ${data.message || 'User stopped talking'}
                    <div class="mt-1 text-muted small">
                        ${data.transcript ? `Transcript: "${data.transcript}"` : ''}
                    </div>
                    <small class="text-muted">${new Date().toLocaleTimeString()}</small>
                </div>
            </div>
        `;
        
        this.transcriptionDisplay.appendChild(turnElement);
        this.transcriptionDisplay.scrollTop = this.transcriptionDisplay.scrollHeight;
        
        // Animation
        turnElement.style.opacity = '0';
        turnElement.style.transform = 'translateY(-10px)';
        setTimeout(() => {
            turnElement.style.transition = 'all 0.3s ease';
            turnElement.style.opacity = '1';
            turnElement.style.transform = 'translateY(0)';
        }, 100);
    }

    updateStatus(message, type) {
        if (!this.statusDisplay) return;

        const iconMap = {
            'connecting': 'circle-notch fa-spin text-primary',
            'connected': 'check-circle text-success',
            'streaming': 'microphone text-danger',
            'transcribing': 'closed-captioning text-info',
            'starting': 'play text-primary',
            'stopped': 'stop text-secondary',
            'error': 'exclamation-triangle text-danger'
        };

        const icon = iconMap[type] || 'info-circle text-info';
        
        this.statusDisplay.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas fa-${icon} fa-2x me-3"></i>
                <div>
                    <div class="fw-bold">${message}</div>
                    <small class="text-muted">${new Date().toLocaleTimeString()}</small>
                    ${type === 'streaming' || type === 'transcribing' ? '<div class="recording-indicator"></div>' : ''}
                </div>
            </div>
        `;
    }

    updateUI(streaming, transcribing) {
        if (this.startStreamBtn) this.startStreamBtn.disabled = streaming;
        if (this.stopStreamBtn) this.stopStreamBtn.disabled = !streaming;
        this.updateTranscriptionUI(transcribing);
    }

    updateTranscriptionUI(transcribing) {
        if (this.startTranscriptionBtn) this.startTranscriptionBtn.disabled = transcribing;
        if (this.stopTranscriptionBtn) this.stopTranscriptionBtn.disabled = !transcribing;
    }
}

// Clear transcriptions function
function clearTranscriptions() {
    const output = document.getElementById('transcriptionOutput');
    if (output) {
        output.innerHTML = `
            <div class="text-center text-muted p-4">
                <i class="fas fa-comment-dots fa-3x mb-3 opacity-50"></i>
                <p>Start transcription to see real-time results...</p>
                <small>Partial and final transcriptions will appear here</small>
            </div>
        `;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.streamingAudioClient = new StreamingAudioClient();
    window.clearTranscriptions = clearTranscriptions;
    
    console.log('🎤 Streaming Audio Client initialized');
    console.log('📋 Available functions: clearTranscriptions()');
});

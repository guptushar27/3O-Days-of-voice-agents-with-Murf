/**
 * Echo Bot JavaScript
 * Handles voice recording and playback using MediaRecorder API
 */

class EchoBot {
    constructor() {
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.stream = null;
        this.recordedAudioBlob = null;

        this.initializeElements();
        this.bindEvents();
        this.checkMicrophoneSupport();
    }

    initializeElements() {
        // Recording controls
        this.startRecordingBtn = document.getElementById('startRecordingBtn');
        this.stopRecordingBtn = document.getElementById('stopRecordingBtn');
        this.recordingStatus = document.getElementById('recordingStatus');
        this.recordingIndicator = document.getElementById('recordingIndicator');

        // Playback elements
        this.playbackSection = document.getElementById('playbackSection');
        this.playbackAudio = document.getElementById('playbackAudio');
        this.playAgainBtn = document.getElementById('playAgainBtn');
        this.downloadRecordingBtn = document.getElementById('downloadRecordingBtn');

        // Transcription elements
        this.transcribeBtn = document.getElementById('transcribeBtn');
        this.transcriptionLoading = document.getElementById('transcriptionLoading');
        this.transcriptionResult = document.getElementById('transcriptionResult');
        this.transcriptionText = document.getElementById('transcriptionText');
        this.transcriptionMeta = document.getElementById('transcriptionMeta');
        this.copyTranscriptionBtn = document.getElementById('copyTranscriptionBtn');
        this.transcriptionError = document.getElementById('transcriptionError');
        this.transcriptionErrorText = document.getElementById('transcriptionErrorText');

        // Error handling
        this.echoErrorMessage = document.getElementById('echoErrorMessage');
    }

    bindEvents() {
        // Recording controls
        this.startRecordingBtn.addEventListener('click', () => {
            this.startRecording();
        });

        this.stopRecordingBtn.addEventListener('click', () => {
            this.stopRecording();
        });

        // Playback controls
        this.playAgainBtn.addEventListener('click', () => {
            this.playRecording();
        });

        this.downloadRecordingBtn.addEventListener('click', () => {
            this.downloadRecording();
        });

        // Transcription controls
        this.transcribeBtn.addEventListener('click', () => {
            this.transcribeAudio();
        });

        this.copyTranscriptionBtn.addEventListener('click', () => {
            this.copyTranscription();
        });
    }

    checkMicrophoneSupport() {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            this.showError('Your browser does not support microphone recording.');
            this.startRecordingBtn.disabled = true;
            return false;
        }

        if (!window.MediaRecorder) {
            this.showError('Your browser does not support audio recording.');
            this.startRecordingBtn.disabled = true;
            return false;
        }

        this.recordingStatus.textContent = 'Ready to record';
        this.recordingStatus.className = 'badge bg-secondary fs-6';
        return true;
    }

    async startRecording() {
        try {
            this.hideError();
            this.hidePlayback();

            // Request microphone access
            this.stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    sampleRate: 44100
                } 
            });

            // Initialize MediaRecorder
            this.mediaRecorder = new MediaRecorder(this.stream, {
                mimeType: this.getSupportedMimeType()
            });

            this.audioChunks = [];

            // Set up event handlers
            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };

            this.mediaRecorder.onstop = () => {
                this.handleRecordingComplete();
            };

            this.mediaRecorder.onerror = (event) => {
                this.showError('Recording error: ' + event.error);
                this.resetRecordingState();
            };

            // Start recording
            this.mediaRecorder.start();

            // Update UI
            this.updateRecordingUI(true);
            this.recordingStatus.textContent = 'Recording...';

            console.log('Recording started');

        } catch (error) {
            console.error('Error starting recording:', error);
            this.showError('Could not access microphone. Please ensure you have granted permission.');
            this.resetRecordingState();
        }
    }

    stopRecording() {
        if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
            this.mediaRecorder.stop();

            // Stop all tracks to release microphone
            if (this.stream) {
                this.stream.getTracks().forEach(track => track.stop());
            }

            this.updateRecordingUI(false);
            this.recordingStatus.textContent = 'Processing recording...';

            console.log('Recording stopped');
        }
    }

    handleRecordingComplete() {
        // Create blob from recorded chunks
        this.recordedAudioBlob = new Blob(this.audioChunks, { 
            type: this.getSupportedMimeType() 
        });

        // Update status for Echo Bot v2 processing
        this.recordingStatus.textContent = 'Processing with Echo Bot v2...';
        this.recordingStatus.className = 'badge bg-primary fs-6';

        console.log('Recording processed successfully - starting Echo Bot v2');

        // Process with Echo Bot v2 (transcribe + Murf TTS)
        this.processEchoBotV2();

        // Show transcription section
        this.showTranscriptionSection();

        // Clean up
        this.resetRecordingState();
    }

    playRecording() {
        if (this.playbackAudio.src) {
            this.playbackAudio.currentTime = 0;
            this.playbackAudio.play().catch(error => {
                console.error('Playback error:', error);
                this.showError('Failed to play recording.');
            });
        }
    }

    downloadRecording() {
        if (this.recordedAudioBlob) {
            const url = URL.createObjectURL(this.recordedAudioBlob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `echo-recording-${Date.now()}.webm`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
    }

    async processEchoBotV2() {
        if (!this.recordedAudioBlob) {
            this.showError('No recording available to process');
            return;
        }

        try {
            // Update status to show Echo Bot v2 processing
            this.recordingStatus.textContent = 'Transcribing and generating Murf voice...';
            this.recordingStatus.className = 'badge bg-primary fs-6';

            // Create FormData for file upload
            const formData = new FormData();
            const filename = `echo-v2-recording-${Date.now()}.webm`;
            formData.append('audio', this.recordedAudioBlob, filename);

            // Make Echo Bot v2 request with timeout
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout

            try {
                const response = await fetch('/tts/echo', {
                    method: 'POST',
                    body: formData,
                    signal: controller.signal
                });

                clearTimeout(timeoutId);
                const result = await response.json();

                if (response.ok && result.success) {
                    // Echo Bot v2 successful
                    this.recordingStatus.textContent = '✓ Murf voice generated successfully!';
                    this.recordingStatus.className = 'badge bg-success fs-6';

                    console.log('Echo Bot v2 successful:', result);

                    // Set up playback with Murf-generated audio
                    this.playbackAudio.src = result.audio_url;
                    this.playbackAudio.load();
                    this.playbackSection.classList.remove('d-none');

                    // Set up audio playback
                    this.playbackAudio.addEventListener('canplaythrough', () => {
                        console.log('Audio can play through');
                    });

                    this.playbackAudio.addEventListener('error', (e) => {
                        console.error('Audio error:', e);
                        this.showError('Failed to load audio file. Please try again.');
                    });

                    // Show manual play button instead of autoplay
                    const playButton = document.getElementById('playResponseBtn');
                    if (playButton) {
                        playButton.style.display = 'inline-block';
                        playButton.onclick = () => {
                            this.playAudioResponse();
                        };
                    }

                    this.showMessage('🎉 VoxAura response ready! Click the play button to listen.', 'success');


                    // Show transcription if available
                    if (result.transcription) {
                        this.displayTranscription(result.transcription, {
                            voice_used: result.voice_used,
                            word_count: result.transcription.split(' ').length
                        });
                    }

                    // Show success details briefly
                    setTimeout(() => {
                        this.recordingStatus.textContent = `Echo Bot v2: Ready to play (${result.voice_used})`;
                        this.recordingStatus.className = 'badge bg-secondary fs-6';
                    }, 3000);

                } else {
                    // Echo Bot v2 failed - handle gracefully
                    this.handleEchoBotError(result, response.status);
                }

            } catch (fetchError) {
                clearTimeout(timeoutId);

                if (fetchError.name === 'AbortError') {
                    throw new Error('Request timed out - the service is taking too long to respond');
                } else {
                    throw fetchError;
                }
            }

        } catch (error) {
            console.error('Echo Bot v2 error:', error);

            this.recordingStatus.textContent = '✗ Echo Bot v2 error';
            this.recordingStatus.className = 'badge bg-danger fs-6';

            // Show specific error messages
            let errorMessage = 'Network error during Echo Bot v2 processing';
            if (error.message.includes('timeout')) {
                errorMessage = 'Request timed out - the service is taking too long to respond';
            } else if (error.message.includes('network') || error.name === 'TypeError') {
                errorMessage = 'Network connection error - please check your internet connection';
            }

            this.showError(errorMessage);

            // Reset status after error
            setTimeout(() => {
                this.recordingStatus.textContent = 'Echo Bot v2 - try again';
                this.recordingStatus.className = 'badge bg-warning fs-6';
            }, 3000);
        }
    }

    handleEchoBotError(result, statusCode) {
        console.error('Echo Bot v2 failed:', result);

        // Check if we have a fallback audio URL
        if (result.fallback_audio_url) {
            this.recordingStatus.textContent = '⚠ Using fallback response';
            this.recordingStatus.className = 'badge bg-warning fs-6';

            // Play fallback audio
            this.playbackAudio.src = result.fallback_audio_url;
            this.playbackAudio.load();
            this.showPlayback();

            // Show fallback message
            this.showError(`Service partially unavailable: ${result.error || 'Unknown error'}. Playing fallback response.`, 'warning');

            // Show transcription if available
            if (result.transcription || result.transcription_fallback) {
                this.displayTranscription(result.transcription || result.transcription_fallback, {
                    note: 'Using fallback due to service issues',
                    fallback: true
                });
            }

        } else {
            // No fallback available
            this.recordingStatus.textContent = '✗ Echo Bot v2 failed';
            this.recordingStatus.className = 'badge bg-danger fs-6';

            // Determine error type and show appropriate message
            let errorMessage = result.error || 'Echo Bot v2 processing failed';

            if (statusCode === 503 || errorMessage.includes('not configured')) {
                errorMessage = 'Voice services are temporarily unavailable. Please try again later.';
            } else if (statusCode === 500 && errorMessage.includes('API')) {
                errorMessage = 'AI services are experiencing issues. Please try again in a moment.';
            }

            this.showError(errorMessage);

            // Show transcription if available even on failure
            if (result.transcription) {
                this.displayTranscription(result.transcription, {
                    note: 'Transcription successful, but voice generation failed'
                });
            }
        }

        // Reset status after showing error
        setTimeout(() => {
            this.recordingStatus.textContent = 'Echo Bot v2 - try again';
            this.recordingStatus.className = 'badge bg-warning fs-6';
        }, 5000);
    }

    async uploadAudioToServer() {
        // This method is kept for backwards compatibility but not used in Echo Bot v2
        // Echo Bot v2 uses processEchoBotV2() instead
        console.log('Note: uploadAudioToServer is deprecated in Echo Bot v2');
    }

    getSupportedMimeType() {
        // Try different MIME types in order of preference
        const mimeTypes = [
            'audio/webm;codecs=opus',
            'audio/webm',
            'audio/mp4',
            'audio/wav'
        ];

        for (const mimeType of mimeTypes) {
            if (MediaRecorder.isTypeSupported(mimeType)) {
                return mimeType;
            }
        }

        return 'audio/webm'; // Fallback
    }

    updateRecordingUI(isRecording) {
        if (isRecording) {
            this.startRecordingBtn.disabled = true;
            this.stopRecordingBtn.disabled = false;
            this.recordingIndicator.classList.remove('d-none');
        } else {
            this.startRecordingBtn.disabled = false;
            this.stopRecordingBtn.disabled = true;
            this.recordingIndicator.classList.add('d-none');
        }
    }

    showPlayback() {
        this.playbackSection.classList.remove('d-none');
    }

    hidePlayback() {
        this.playbackSection.classList.add('d-none');
    }

    showError(message, severity = 'danger') {
        const errorSpan = this.echoErrorMessage.querySelector('span');
        if (errorSpan) {
            errorSpan.textContent = message;
        } else {
            this.echoErrorMessage.textContent = message;
        }

        // Update error styling based on severity
        this.echoErrorMessage.className = `alert alert-${severity} mb-3`;
        this.echoErrorMessage.classList.remove('d-none');

        // Auto-hide error after time based on severity
        const hideDelay = severity === 'warning' ? 6000 : 8000;
        setTimeout(() => {
            this.hideError();
        }, hideDelay);
    }

    hideError() {
        this.echoErrorMessage.classList.add('d-none');
    }

    resetRecordingState() {
        this.updateRecordingUI(false);

        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }

        this.mediaRecorder = null;
    }

    async transcribeAudio() {
        if (!this.recordedAudioBlob) {
            this.showTranscriptionError('No recording available to transcribe');
            return;
        }

        try {
            // Update UI to show loading
            this.hideTranscriptionError();
            this.hideTranscriptionResult();
            this.showTranscriptionLoading();
            this.transcribeBtn.disabled = true;
            this.transcribeBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Transcribing...';

            // Create FormData for file upload
            const formData = new FormData();
            const filename = `transcribe-${Date.now()}.webm`;
            formData.append('audio', this.recordedAudioBlob, filename);

            // Make transcription request with timeout
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 45000); // 45 second timeout

            try {
                const response = await fetch('/transcribe/file', {
                    method: 'POST',
                    body: formData,
                    signal: controller.signal
                });

                clearTimeout(timeoutId);
                const result = await response.json();

                if (response.ok && result.success) {
                    // Transcription successful
                    this.displayTranscription(result);
                    console.log('Transcription successful:', result);

                } else {
                    // Transcription failed - handle gracefully
                    this.handleTranscriptionError(result, response.status);
                }

            } catch (fetchError) {

    playAudioResponse() {
        if (!this.playbackAudio.src) {
            this.showError('No audio to play');
            return;
        }

        // Reset audio to beginning
        this.playbackAudio.currentTime = 0;
        
        // Attempt to play with proper error handling
        const playPromise = this.playbackAudio.play();
        
        if (playPromise !== undefined) {
            playPromise
                .then(() => {
                    console.log('Audio playback started successfully');
                })
                .catch(error => {
                    console.error('Audio playback failed:', error);
                    
                    // Show specific error messages
                    if (error.name === 'NotAllowedError') {
                        this.showError('Audio playback blocked. Please interact with the page first.');
                    } else if (error.name === 'NotSupportedError') {
                        this.showError('Audio format not supported by your browser.');
                    } else if (error.name === 'AbortError') {
                        this.showError('Audio playback was interrupted.');
                    } else {
                        this.showError('Failed to play audio. Please try again.');
                    }
                });
        }
    }

                clearTimeout(timeoutId);

                if (fetchError.name === 'AbortError') {
                    throw new Error('Transcription timed out - the service is taking too long to respond');
                } else {
                    throw fetchError;
                }
            }

        } catch (error) {
            console.error('Transcription error:', error);

            // Show specific error messages
            let errorMessage = 'Network error during transcription';
            if (error.message.includes('timeout')) {
                errorMessage = 'Transcription timed out - please try again with a shorter audio clip';
            } else if (error.message.includes('network') || error.name === 'TypeError') {
                errorMessage = 'Network connection error - please check your internet connection and try again';
            }

            this.showTranscriptionError(errorMessage);
        } finally {
            // Reset button state
            this.hideTranscriptionLoading();
            this.transcribeBtn.disabled = false;
            this.transcribeBtn.innerHTML = '<i class="fas fa-language me-1"></i>Transcribe';
        }
    }

    handleTranscriptionError(result, statusCode) {
        console.error('Transcription failed:', result);

        let errorMessage = result.error || 'Transcription failed';
        let fallbackMessage = result.fallback_message || '';

        // Show user-friendly error messages based on status codes
        if (statusCode === 503 || result.service_error) {
            if (fallbackMessage) {
                errorMessage = fallbackMessage;
            } else {
                errorMessage = 'Speech recognition service is temporarily unavailable. Please try again later.';
            }
        } else if (statusCode === 400 && result.error && result.error.includes('No speech detected')) {
            errorMessage = fallbackMessage || 'No speech detected in your audio. Please try speaking more clearly.';
        } else if (errorMessage.includes('API key') || errorMessage.includes('authentication')) {
            errorMessage = 'Speech recognition service is not available right now. Please try again later.';
        } else if (errorMessage.includes('network') || errorMessage.includes('connection')) {
            errorMessage = 'Network issue detected. Please check your connection and try again.';
        } else if (fallbackMessage) {
            errorMessage = fallbackMessage;
        }

        this.showTranscriptionError(errorMessage);

        // If we have a partial transcription result, show it
        if (result.transcription && result.transcription !== "No speech detected in audio") {
            this.displayTranscription({
                transcription: result.transcription,
                confidence: result.confidence,
                message: 'Partial transcription result',
                word_count: result.transcription.split(' ').length,
                note: 'This transcription may be incomplete due to service issues'
            });
        }
    }

    displayTranscription(result) {
        // Display the transcription text
        this.transcriptionText.textContent = result.transcription;

        // Display metadata
        const wordCount = result.word_count || 0;
        const confidence = result.confidence ? `${Math.round(result.confidence * 100)}%` : 'N/A';
        const duration = result.audio_duration ? `${result.audio_duration.toFixed(1)}s` : 'N/A';

        this.transcriptionMeta.innerHTML = `
            <span><i class="fas fa-clock me-1"></i>${duration}</span>
            <span class="mx-2">•</span>
            <span><i class="fas fa-list-ol me-1"></i>${wordCount} words</span>
            <span class="mx-2">•</span>
            <span><i class="fas fa-chart-line me-1"></i>Confidence: ${confidence}</span>
        `;

        // Show the result
        this.showTranscriptionResult();
    }

    async copyTranscription() {
        if (!this.transcriptionText.textContent) {
            return;
        }

        try {
            await navigator.clipboard.writeText(this.transcriptionText.textContent);

            // Show copied feedback
            const originalBtn = this.copyTranscriptionBtn.innerHTML;
            this.copyTranscriptionBtn.innerHTML = '<i class="fas fa-check me-1"></i>Copied!';
            this.copyTranscriptionBtn.classList.add('copied');

            // Reset after 2 seconds
            setTimeout(() => {
                this.copyTranscriptionBtn.innerHTML = originalBtn;
                this.copyTranscriptionBtn.classList.remove('copied');
            }, 2000);

        } catch (error) {
            console.error('Copy failed:', error);
            this.showTranscriptionError('Failed to copy transcription');
        }
    }

    showTranscriptionSection() {
        // Enable transcribe button once recording is complete
        this.transcribeBtn.disabled = false;
    }

    showTranscriptionLoading() {
        this.transcriptionLoading.classList.remove('d-none');
    }

    hideTranscriptionLoading() {
        this.transcriptionLoading.classList.add('d-none');
    }

    showTranscriptionResult() {
        this.transcriptionResult.classList.remove('d-none');
    }

    hideTranscriptionResult() {
        this.transcriptionResult.classList.add('d-none');
    }

    showTranscriptionError(message) {
        this.transcriptionErrorText.textContent = message;
        this.transcriptionError.classList.remove('d-none');

        // Auto-hide error after 8 seconds
        setTimeout(() => {
            this.hideTranscriptionError();
        }, 8000);
    }

    hideTranscriptionError() {
        this.transcriptionError.classList.add('d-none');
    }

    // Helper to display user messages in the chat interface
    showMessage(message, type = 'info') {
        const chatMessages = document.getElementById('chatMessages');
        const messageElement = document.createElement('div');
        messageElement.className = `message ${type}`; // e.g., message info, message success, message error
        messageElement.textContent = message;
        chatMessages.appendChild(messageElement);

        // Scroll to the bottom to show the latest message
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

// Initialize the Echo Bot when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const echoBot = new EchoBot();

    console.log('Echo Bot initialized');
    console.log('Ready to record and playback audio');
});

// Add global error handling for unhandled promise rejections
window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection in Echo Bot:', event.reason);
});
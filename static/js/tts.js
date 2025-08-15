/**
 * TTS Client JavaScript
 * Handles text-to-speech generation and audio playback
 */

class TTSClient {
    constructor() {
        this.initializeElements();
        this.bindEvents();
        this.currentAudioUrl = null;
    }

    initializeElements() {
        // Form elements
        this.form = document.getElementById('ttsForm');
        this.textInput = document.getElementById('textInput');
        this.generateBtn = document.getElementById('generateBtn');

        // UI elements
        this.loading = document.getElementById('loading');
        this.audioSection = document.getElementById('audioSection');
        this.errorMessage = document.getElementById('errorMessage');

        // Audio elements
        this.audioPlayer = document.getElementById('audioPlayer');
        this.replayBtn = document.getElementById('replayBtn');
    }

    bindEvents() {
        // Form submission
        this.form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.generateTTS();
        });

        // Audio controls
        this.replayBtn.addEventListener('click', () => {
            this.replayAudio();
        });

        // Audio player events
        this.audioPlayer.addEventListener('error', (e) => {
            console.error('Audio error:', e);
            this.showError('Failed to load audio. Please try again.');
        });
    }



    async generateTTS() {
        const text = this.textInput.value.trim();
        
        if (!text) {
            this.showError('Please enter some text to convert.');
            return;
        }



        try {
            this.showLoading(true);
            this.hideError();
            this.hideAudioPlayer();

            const response = await fetch('/generate-tts', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: text })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || `Server error: ${response.status}`);
            }

            if (data.audio_url || data.url) {
                // Handle different response formats
                const audioUrl = data.audio_url || data.url;
                await this.loadAudio(audioUrl, text);
            } else {
                throw new Error('No audio URL received from server');
            }

        } catch (error) {
            console.error('TTS Generation Error:', error);
            this.showError(error.message);
        } finally {
            this.showLoading(false);
        }
    }

    async loadAudio(audioUrl, text) {
        try {
            // Store current audio URL
            this.currentAudioUrl = audioUrl;
            
            // Check if this is a demo audio endpoint that returns JSON
            if (audioUrl.includes('/audio-demo/')) {
                // Fetch the demo audio data from the endpoint
                const audioResponse = await fetch(audioUrl);
                const audioData = await audioResponse.json();
                
                if (audioData.audio_data) {
                    // Use the audio data URL
                    this.audioPlayer.src = audioData.audio_data;
                } else {
                    throw new Error('No audio data received');
                }
            } else {
                // Direct audio URL (real TTS file)
                this.audioPlayer.src = audioUrl;
            }
            
            // Show audio player
            this.showAudioPlayer();
            
            // Preload the audio
            this.audioPlayer.load();
            
            console.log('Audio loaded successfully:', audioUrl);
            
        } catch (error) {
            console.error('Audio loading error:', error);
            this.showError('Failed to load audio. Please try again.');
        }
    }

    replayAudio() {
        if (this.audioPlayer.src) {
            this.audioPlayer.currentTime = 0;
            this.audioPlayer.play().catch(error => {
                console.error('Replay error:', error);
                this.showError('Failed to replay audio.');
            });
        }
    }

    showLoading(show) {
        if (show) {
            this.loading.classList.remove('d-none');
            this.generateBtn.disabled = true;
            this.generateBtn.textContent = 'Generating...';
        } else {
            this.loading.classList.add('d-none');
            this.generateBtn.disabled = false;
            this.generateBtn.textContent = 'Generate Audio';
        }
    }

    showAudioPlayer() {
        this.audioSection.classList.remove('d-none');
    }

    hideAudioPlayer() {
        this.audioSection.classList.add('d-none');
    }

    showError(message) {
        const errorSpan = this.errorMessage.querySelector('span');
        if (errorSpan) {
            errorSpan.textContent = message;
        } else {
            this.errorMessage.textContent = message;
        }
        this.errorMessage.classList.remove('d-none');
        
        // Auto-hide error after 5 seconds
        setTimeout(() => {
            this.hideError();
        }, 5000);
    }

    hideError() {
        this.errorMessage.classList.add('d-none');
    }
}

// Initialize the TTS client when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const ttsClient = new TTSClient();
    
    // Add some helpful console logs for debugging
    console.log('TTS Client initialized');
    console.log('Ready to generate speech from text');
});

// Add global error handling for unhandled promise rejections
window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
});

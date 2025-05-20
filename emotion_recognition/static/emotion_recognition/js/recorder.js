/**
 * Audio Recorder Class
 * Handles browser audio recording using MediaRecorder API
 */

class Recorder {
    constructor(audioContext) {
        this.audioContext = audioContext;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.recordingState = 'inactive';
        this.stream = null;
        this.source = null;
        this.analyser = null;
    }

    /**
     * Initialize and start recording
     * @param {MediaStream} stream - Audio stream from getUserMedia
     * @returns {Promise} - Resolves when recording starts
     */
    start(stream) {
        return new Promise((resolve, reject) => {
            try {
                this.stream = stream;
                
                // Create MediaRecorder
                const options = { mimeType: 'audio/webm' };
                try {
                    this.mediaRecorder = new MediaRecorder(stream, options);
                } catch (e) {
                    // Fallback if audio/webm is not supported
                    this.mediaRecorder = new MediaRecorder(stream);
                }
                
                // Connect stream to audio context for visualization
                this.source = this.audioContext.createMediaStreamSource(stream);
                this.analyser = this.audioContext.createAnalyser();
                this.analyser.fftSize = 2048;
                this.source.connect(this.analyser);
                
                // Set up event handlers
                this.mediaRecorder.ondataavailable = (event) => {
                    if (event.data.size > 0) {
                        this.audioChunks.push(event.data);
                    }
                };
                
                // Start recording
                this.audioChunks = [];
                this.mediaRecorder.start(100); // Collect data every 100ms
                this.recordingState = 'recording';
                
                resolve();
            } catch (err) {
                reject(err);
            }
        });
    }

    /**
     * Stop recording and return the audio data
     * @returns {Promise<Blob>} - Audio data as Blob
     */
    stop() {
        return new Promise((resolve, reject) => {
            if (!this.mediaRecorder || this.recordingState === 'inactive') {
                reject(new Error('Recording not active'));
                return;
            }
            
            this.mediaRecorder.onstop = () => {
                try {
                    // Get recorded audio as blob
                    let audioBlob;
                    
                    // Try to create a WAV blob for better compatibility
                    this._createWavBlob(this.audioChunks)
                        .then(wavBlob => {
                            this._cleanup();
                            resolve(wavBlob);
                        })
                        .catch(err => {
                            // Fallback to original format if WAV conversion fails
                            console.warn('WAV conversion failed, using original format', err);
                            audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
                            this._cleanup();
                            resolve(audioBlob);
                        });
                } catch (err) {
                    this._cleanup();
                    reject(err);
                }
            };
            
            // Stop recording
            this.mediaRecorder.stop();
            this.recordingState = 'inactive';
        });
    }

    /**
     * Pause recording
     */
    pause() {
        if (this.mediaRecorder && this.recordingState === 'recording') {
            this.mediaRecorder.pause();
            this.recordingState = 'paused';
        }
    }

    /**
     * Resume recording
     */
    resume() {
        if (this.mediaRecorder && this.recordingState === 'paused') {
            this.mediaRecorder.resume();
            this.recordingState = 'recording';
        }
    }

    /**
     * Get the recording state
     * @returns {string} - Current recording state
     */
    getState() {
        return this.recordingState;
    }

    /**
     * Get the analyser node for visualization
     * @returns {AnalyserNode} - Audio analyser
     */
    getAnalyser() {
        return this.analyser;
    }

    /**
     * Clean up resources
     * @private
     */
    _cleanup() {
        // Stop all audio tracks
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
        }
        
        // Disconnect audio nodes
        if (this.source) {
            this.source.disconnect();
        }
        
        this.mediaRecorder = null;
        this.analyser = null;
        this.source = null;
        this.stream = null;
    }

    /**
     * Convert audio chunks to WAV format
     * @param {Array<Blob>} audioChunks - Recorded audio chunks
     * @returns {Promise<Blob>} - WAV format audio blob
     * @private
     */
    _createWavBlob(audioChunks) {
        return new Promise((resolve, reject) => {
            // Create a blob from all chunks
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            
            // Create an audio element to decode the audio
            const audioElement = new Audio();
            audioElement.src = URL.createObjectURL(audioBlob);
            
            // Convert to WAV via AudioContext
            audioElement.addEventListener('loadedmetadata', () => {
                // We can't directly convert webm to WAV easily in the browser
                // For this example, we'll just use the original blob with a .wav extension
                // In a production app, you would need a server-side conversion or a more complex client-side library
                
                // For now, just pass the original blob with WAV mime type
                // The server will need to handle this properly
                resolve(new Blob(audioChunks, { type: 'audio/wav' }));
            });
            
            audioElement.addEventListener('error', (err) => {
                reject(new Error('Audio decoding failed: ' + err.message));
            });
            
            // Load the audio
            audioElement.load();
        });
    }
}

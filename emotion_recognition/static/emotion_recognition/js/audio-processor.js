/**
 * Audio Processor Class
 * Handles audio visualization and processing
 */

class AudioProcessor {
    constructor(audioContext, stream) {
        this.audioContext = audioContext;
        this.stream = stream;
        this.source = null;
        this.analyser = null;
        this.dataArray = null;
        this.canvas = null;
        this.canvasCtx = null;
        this.animationFrame = null;
        this.initialized = false;
        this.running = false;
    }

    /**
     * Connect the audio source to an analyser for visualization
     * @param {HTMLCanvasElement} canvas - Canvas element for visualization
     */
    connectVisualizer(canvas) {
        if (!this.audioContext || !this.stream) {
            console.error('AudioProcessor not properly initialized');
            return;
        }
        
        // Create audio source from stream
        this.source = this.audioContext.createMediaStreamSource(this.stream);
        
        // Create analyser
        this.analyser = this.audioContext.createAnalyser();
        this.analyser.fftSize = 2048;
        const bufferLength = this.analyser.frequencyBinCount;
        this.dataArray = new Uint8Array(bufferLength);
        
        // Connect source to analyser
        this.source.connect(this.analyser);
        
        // Set up canvas
        this.canvas = canvas;
        this.canvasCtx = canvas.getContext('2d');
        
        this.initialized = true;
    }

    /**
     * Start visualizing audio
     */
    start() {
        if (!this.initialized) {
            console.error('Visualizer not initialized. Call connectVisualizer first.');
            return;
        }
        
        this.running = true;
        this._visualize();
    }

    /**
     * Stop visualizing audio
     */
    stop() {
        this.running = false;
        if (this.animationFrame) {
            cancelAnimationFrame(this.animationFrame);
            this.animationFrame = null;
        }
        
        // Clean up
        this._clearCanvas();
        
        if (this.source) {
            this.source.disconnect();
            this.source = null;
        }
    }

    /**
     * Clear the canvas
     * @private
     */
    _clearCanvas() {
        if (this.canvas && this.canvasCtx) {
            const width = this.canvas.width;
            const height = this.canvas.height;
            this.canvasCtx.clearRect(0, 0, width, height);
            
            // Draw background
            this.canvasCtx.fillStyle = getComputedStyle(this.canvas).backgroundColor || 'rgba(0, 0, 0, 0)';
            this.canvasCtx.fillRect(0, 0, width, height);
            
            // Draw center line
            this.canvasCtx.strokeStyle = '#0ea5e9';
            this.canvasCtx.lineWidth = 2;
            this.canvasCtx.beginPath();
            this.canvasCtx.moveTo(0, height / 2);
            this.canvasCtx.lineTo(width, height / 2);
            this.canvasCtx.stroke();
        }
    }

    /**
     * Draw waveform visualization
     * @private
     */
    _visualize() {
        if (!this.running) return;
        
        const width = this.canvas.width = this.canvas.offsetWidth;
        const height = this.canvas.height = this.canvas.offsetHeight;
        
        // Get time domain data
        this.analyser.getByteTimeDomainData(this.dataArray);
        
        // Clear canvas
        this._clearCanvas();
        
        // Draw waveform
        this.canvasCtx.lineWidth = 2;
        this.canvasCtx.strokeStyle = '#0ea5e9';
        this.canvasCtx.beginPath();
        
        const sliceWidth = width / this.dataArray.length;
        let x = 0;
        
        for (let i = 0; i < this.dataArray.length; i++) {
            const v = this.dataArray[i] / 128.0;
            const y = v * height / 2;
            
            if (i === 0) {
                this.canvasCtx.moveTo(x, y);
            } else {
                this.canvasCtx.lineTo(x, y);
            }
            
            x += sliceWidth;
        }
        
        this.canvasCtx.lineTo(width, height / 2);
        this.canvasCtx.stroke();
        
        // Continue animation
        this.animationFrame = requestAnimationFrame(() => this._visualize());
    }

    /**
     * Get audio features for analysis (not implemented in this example)
     * @returns {Object} - Audio features
     */
    getFeatures() {
        // In a real implementation, this would extract MFCC and other features
        // This is just a placeholder
        return {};
    }
}

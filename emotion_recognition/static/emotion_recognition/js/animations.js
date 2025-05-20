/**
 * Emotion-based animations
 * Provides animations for different emotional states
 */

/**
 * Initialize animations based on detected emotion
 * @param {string} emotion - The detected emotion
 */
function initEmotionAnimations(emotion) {
    // Set animation properties based on emotion
    const animationProps = getEmotionAnimationProps(emotion);
    
    // Apply animations to appropriate elements
    applyEmotionBackgroundEffect(animationProps);
    createEmotionParticles(animationProps);
    
    // Add emotion-specific text animation
    animateEmotionTexts(emotion);
}

/**
 * Get animation properties for a specific emotion
 * @param {string} emotion - The emotion name
 * @returns {Object} - Animation properties
 */
function getEmotionAnimationProps(emotion) {
    const props = {
        particleCount: 0,
        colors: [],
        speed: 1,
        size: 5,
        duration: 2000,
        background: null
    };
    
    switch (emotion) {
        case 'happy':
            props.particleCount = 30;
            props.colors = ['#FDE68A', '#FBBF24', '#F59E0B'];
            props.speed = 1.5;
            props.size = 8;
            props.background = 'radial-gradient(circle, rgba(253,224,71,0.1) 0%, rgba(253,224,71,0) 70%)';
            break;
            
        case 'sad':
            props.particleCount = 15;
            props.colors = ['#93C5FD', '#3B82F6', '#2563EB'];
            props.speed = 0.7;
            props.size = 6;
            props.background = 'radial-gradient(circle, rgba(96,165,250,0.1) 0%, rgba(96,165,250,0) 70%)';
            break;
            
        case 'angry':
            props.particleCount = 25;
            props.colors = ['#FCA5A5', '#EF4444', '#B91C1C'];
            props.speed = 2;
            props.size = 7;
            props.background = 'radial-gradient(circle, rgba(239,68,68,0.1) 0%, rgba(239,68,68,0) 60%)';
            break;
            
        case 'neutral':
            props.particleCount = 10;
            props.colors = ['#D1D5DB', '#9CA3AF', '#6B7280'];
            props.speed = 1;
            props.size = 5;
            props.background = 'radial-gradient(circle, rgba(156,163,175,0.1) 0%, rgba(156,163,175,0) 70%)';
            break;
            
        case 'fear':
            props.particleCount = 20;
            props.colors = ['#DDD6FE', '#A78BFA', '#7C3AED'];
            props.speed = 1.8;
            props.size = 6;
            props.background = 'radial-gradient(circle, rgba(167,139,250,0.1) 0%, rgba(167,139,250,0) 70%)';
            break;
            
        case 'disgust':
            props.particleCount = 15;
            props.colors = ['#A7F3D0', '#34D399', '#059669'];
            props.speed = 1.2;
            props.size = 6;
            props.background = 'radial-gradient(circle, rgba(52,211,153,0.1) 0%, rgba(52,211,153,0) 70%)';
            break;
            
        case 'surprised':
            props.particleCount = 40;
            props.colors = ['#FBCFE8', '#EC4899', '#DB2777'];
            props.speed = 2.2;
            props.size = 7;
            props.background = 'radial-gradient(circle, rgba(236,72,153,0.1) 0%, rgba(236,72,153,0) 70%)';
            break;
    }
    
    return props;
}

/**
 * Apply subtle background effect based on emotion
 * @param {Object} props - Animation properties
 */
function applyEmotionBackgroundEffect(props) {
    if (!props.background) return;
    
    // Find the emotion card element
    const emotionCard = document.querySelector('.emotion-card');
    if (emotionCard) {
        emotionCard.style.position = 'relative';
        emotionCard.style.overflow = 'hidden';
        
        // Create a background effect element
        const bgEffect = document.createElement('div');
        bgEffect.classList.add('emotion-bg-effect');
        bgEffect.style.position = 'absolute';
        bgEffect.style.top = '0';
        bgEffect.style.left = '0';
        bgEffect.style.right = '0';
        bgEffect.style.bottom = '0';
        bgEffect.style.zIndex = '-1';
        bgEffect.style.background = props.background;
        bgEffect.style.opacity = '0';
        bgEffect.style.transform = 'scale(0.8)';
        bgEffect.style.transition = 'opacity 1.5s ease-in-out, transform 1.5s ease-in-out';
        
        // Add to card
        emotionCard.prepend(bgEffect);
        
        // Trigger animation
        setTimeout(() => {
            bgEffect.style.opacity = '1';
            bgEffect.style.transform = 'scale(1)';
        }, 100);
    }
}

/**
 * Create particle animation effects
 * @param {Object} props - Animation properties
 */
function createEmotionParticles(props) {
    if (props.particleCount <= 0) return;
    
    // Find the emotion card element
    const emotionCard = document.querySelector('.emotion-card');
    if (emotionCard) {
        // Create a container for particles
        const container = document.createElement('div');
        container.classList.add('particles-container');
        container.style.position = 'absolute';
        container.style.top = '0';
        container.style.left = '0';
        container.style.right = '0';
        container.style.bottom = '0';
        container.style.overflow = 'hidden';
        container.style.zIndex = '-1';
        container.style.pointerEvents = 'none';
        
        emotionCard.prepend(container);
        
        // Create particles
        for (let i = 0; i < props.particleCount; i++) {
            createParticle(container, props);
        }
    }
}

/**
 * Create a single particle element
 * @param {HTMLElement} container - Container element
 * @param {Object} props - Animation properties
 */
function createParticle(container, props) {
    // Create particle element
    const particle = document.createElement('div');
    particle.classList.add('emotion-particle');
    
    // Get random properties
    const size = Math.random() * props.size + 2;
    const colorIdx = Math.floor(Math.random() * props.colors.length);
    const color = props.colors[colorIdx];
    
    // Calculate random position
    const containerRect = container.getBoundingClientRect();
    const left = Math.random() * containerRect.width;
    const top = Math.random() * containerRect.height;
    
    // Set particle styles
    particle.style.position = 'absolute';
    particle.style.width = `${size}px`;
    particle.style.height = `${size}px`;
    particle.style.backgroundColor = color;
    particle.style.borderRadius = '50%';
    particle.style.left = `${left}px`;
    particle.style.top = `${top}px`;
    particle.style.opacity = '0';
    particle.style.transform = 'scale(0)';
    
    // Add to container
    container.appendChild(particle);
    
    // Animate the particle
    setTimeout(() => {
        const duration = Math.random() * props.duration + 1000;
        particle.style.transition = `opacity ${duration/2}ms ease-in-out, transform ${duration}ms ease-in-out`;
        particle.style.opacity = Math.random() * 0.7 + 0.3;
        particle.style.transform = 'scale(1)';
        
        // Move the particle
        const moveAnimation = () => {
            const newLeft = Math.random() * containerRect.width;
            const newTop = Math.random() * containerRect.height;
            const moveDuration = Math.random() * 3000 + 2000;
            
            particle.style.transition = `left ${moveDuration}ms ease-in-out, top ${moveDuration}ms ease-in-out`;
            particle.style.left = `${newLeft}px`;
            particle.style.top = `${newTop}px`;
            
            // Continue moving
            setTimeout(moveAnimation, moveDuration);
        };
        
        moveAnimation();
    }, Math.random() * 1000);
}

/**
 * Animate emotion-related text elements
 * @param {string} emotion - The detected emotion
 */
function animateEmotionTexts(emotion) {
    // Define text animation based on emotion
    let textAnimation = '';
    
    switch (emotion) {
        case 'happy':
            textAnimation = 'animate-bounce';
            break;
        case 'sad':
            textAnimation = 'animate-pulse-slow';
            break;
        case 'angry':
            textAnimation = 'animate-pulse';
            break;
        case 'surprised':
            textAnimation = 'animate-bounce';
            break;
        default:
            textAnimation = 'animate-pulse-slow';
    }
    
    // Find and animate the emotion label
    const emotionSpan = document.querySelector('.emotion-card h3 span');
    if (emotionSpan) {
        emotionSpan.classList.add(textAnimation);
    }
}

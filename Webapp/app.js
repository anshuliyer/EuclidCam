document.addEventListener('DOMContentLoaded', () => {
  const bootScreen = document.getElementById('boot-screen');
  const conceptScreen = document.getElementById('concept-screen');
  const mainGrid = document.getElementById('main-grid');

  console.log('--- EuclidCam Sequence Initiated ---');

  // The initial sequence locks scrolling until the animation finishes.
  console.log('--- EuclidCam Hero Loading... ---');
  
  // Fade in the EuclidCam text with a smooth entrance
  setTimeout(() => {
    const heroText = document.getElementById('hero-brand-text');
    if (heroText) heroText.classList.add('visible');
  }, 800);

  setTimeout(() => {
    document.body.classList.remove('scroll-lock');
    console.log('--- Boot Complete. Scroll Unlocked. ---');
  }, 1800);

  // Scroll Animation for Hero Brand Text
  const heroText = document.getElementById('hero-brand-text');
  if (heroText) {
    window.addEventListener('scroll', () => {
      // Toggle sticky class when scrolled past a certain threshold (e.g. 50px)
      if (window.scrollY > 50) {
        heroText.classList.add('sticky');
      } else {
        heroText.classList.remove('sticky');
      }
    });
  }

  // Theme Toggle Logic
  const themeToggle = document.getElementById('theme-toggle');
  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const isDark = document.body.classList.toggle('dark-mode');
      const themeLabel = document.getElementById('theme-label');
      if (themeLabel) {
        themeLabel.textContent = isDark ? 'DARK' : 'LIGHT';
      }
      
      const bootGifImg = document.getElementById('boot-gif-img');
      if (bootGifImg) {
        bootGifImg.src = isDark ? 'assets/transparent_logo_dark.png' : 'assets/transparent_logo_light.png';
      }
    });
  }

  // Interactive handling for grid items
  const gridItems = document.querySelectorAll('.grid-item');
  gridItems.forEach(item => {
    item.addEventListener('click', () => {
      const label = item.querySelector('h2').innerText;
      console.log(`Navigation triggered: /${label.toLowerCase()}`);

      // Add a "flash" effect like before
      item.style.backgroundColor = 'rgba(191, 164, 138, 0.15)';
      setTimeout(() => {
        item.style.backgroundColor = '';
        
        // Handle Gallery Navigation
        if (label.toLowerCase() === 'gallery') {
          const galleryScreen = document.getElementById('gallery-screen');
          mainGrid.classList.add('hidden');
          setTimeout(() => {
            mainGrid.style.display = 'none';
            galleryScreen.classList.remove('hidden');
          }, 1000);
        } else if (label.toLowerCase() === 'design') {
          window.location.href = 'viewer.html';
        } else if (label.toLowerCase() === 'sdk') {
          window.open('https://github.com/anshuliyer/EuclidCamSDK', '_blank');
        } else if (label.toLowerCase() === 'source code') {
          window.open('https://github.com/anshuliyer/EuclidCam', '_blank');
        }
      }, 200);
    });
  });

  // Gallery Back Button Logic
  const galleryBack = document.getElementById('gallery-back');
  const galleryScreen = document.getElementById('gallery-screen');
  if (galleryBack) {
    galleryBack.addEventListener('click', () => {
      galleryScreen.classList.add('hidden');
      setTimeout(() => {
        mainGrid.style.display = 'grid';
        mainGrid.classList.remove('hidden');
      }, 500);
    });
  }

  // Gallery Modal Logic
  const imageModal = document.getElementById('image-modal');
  const modalImage = document.getElementById('modal-image');
  const modalClose = document.getElementById('modal-close');
  const galleryImages = document.querySelectorAll('.gallery-img-container img');

  galleryImages.forEach(img => {
    img.parentElement.addEventListener('click', () => {
      modalImage.src = img.src;
      imageModal.classList.remove('hidden');
    });
  });

  if (imageModal) {
    imageModal.addEventListener('click', (e) => {
      if (e.target !== modalImage) {
        imageModal.classList.add('hidden');
        setTimeout(() => {
          modalImage.src = '';
        }, 300);
      }
    });
  }

  // Interactive Golden Ratio (Phyllotaxis) Canvas Background
  const canvas = document.createElement('canvas');
  canvas.id = 'bg-canvas';
  document.body.prepend(canvas);
  const ctx = canvas.getContext('2d');
  
  let width, height;
  let particles = [];
  let mouse = { x: null, y: null };
  
  // Mathematical constants for Golden Spiral / Phyllotaxis
  const goldenAngle = Math.PI * (3 - Math.sqrt(5)); // Approx 137.5 degrees
  let rotationOffset = 0;
  
  function resize() {
    width = window.innerWidth;
    height = window.innerHeight;
    canvas.width = width;
    canvas.height = height;
    init(); // Re-initialize spiral to center on resize
  }
  
  window.addEventListener('resize', resize);

  window.addEventListener('mousemove', (e) => {
    mouse.x = e.clientX;
    mouse.y = e.clientY;
  });

  window.addEventListener('mouseout', () => {
    mouse.x = null;
    mouse.y = null;
  });

  window.addEventListener('touchmove', (e) => {
    if (e.touches.length > 0) {
      mouse.x = e.touches[0].clientX;
      mouse.y = e.touches[0].clientY;
    }
  });

  window.addEventListener('touchstart', (e) => {
    if (e.touches.length > 0) {
      mouse.x = e.touches[0].clientX;
      mouse.y = e.touches[0].clientY;
    }
  });

  window.addEventListener('touchend', () => {
    mouse.x = null;
    mouse.y = null;
  });

  class GoldenParticle {
    constructor(index) {
      this.index = index;
      this.c = 28; // Spacing factor
      
      // Calculate polar coordinates using Golden Angle
      this.r = this.c * Math.sqrt(this.index);
      this.theta = this.index * goldenAngle;
      
      this.x = width / 2 + this.r * Math.cos(this.theta);
      this.y = height / 2 + this.r * Math.sin(this.theta);
      
      this.baseX = this.x;
      this.baseY = this.y;
      
      // Points closer to center are slightly larger
      this.size = Math.max(0.4, 2.5 - (this.r / 800));
      this.density = (Math.random() * 20) + 1;
    }
    
    update() {
      // The entire spiral slowly rotates mathematically
      let currentTheta = this.theta + rotationOffset;
      this.baseX = width / 2 + this.r * Math.cos(currentTheta);
      this.baseY = height / 2 + this.r * Math.sin(currentTheta);
      
      let dx = mouse.x - this.x;
      let dy = mouse.y - this.y;
      let distance = Math.sqrt(dx * dx + dy * dy);
      let maxDist = 200;
      
      if (mouse.x != null && distance < maxDist) {
        let forceDirectionX = dx / distance;
        let forceDirectionY = dy / distance;
        let force = (maxDist - distance) / maxDist;
        let directionX = forceDirectionX * force * this.density * 0.8;
        let directionY = forceDirectionY * force * this.density * 0.8;
        
        // Organically repel from cursor
        this.x -= directionX;
        this.y -= directionY;
      } else {
        // Snap back into mathematical perfection
        if (this.x !== this.baseX) {
          this.x -= (this.x - this.baseX) / 15;
        }
        if (this.y !== this.baseY) {
          this.y -= (this.y - this.baseY) / 15;
        }
      }
    }
    
    draw() {
      ctx.fillStyle = document.body.classList.contains('dark-mode') ? 'rgba(242, 186, 154, 0.4)' : 'rgba(228, 174, 134, 0.6)';
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
      ctx.closePath();
      ctx.fill();
    }
  }

  function init() {
    particles = [];
    // Calculate enough particles to cover the screen diagonally
    let diagonal = Math.sqrt(width * width + height * height);
    let numParticles = Math.pow(diagonal / 2 / 28, 2); 
    
    // Cap it to prevent performance issues
    numParticles = Math.min(numParticles, 1200);
    
    for (let i = 1; i <= numParticles; i++) {
      particles.push(new GoldenParticle(i));
    }
  }
  
  function animate() {
    ctx.clearRect(0, 0, width, height);
    
    // Increment global rotation for the entire galaxy of dots
    rotationOffset += 0.0006;
    
    for (let i = 0; i < particles.length; i++) {
      particles[i].update();
      particles[i].draw();
    }
    requestAnimationFrame(animate);
  }
  
  resize(); // triggers init
  animate();
});

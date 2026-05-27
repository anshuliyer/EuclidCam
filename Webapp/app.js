document.addEventListener('DOMContentLoaded', () => {
  const bootScreen = document.getElementById('boot-screen');
  const conceptScreen = document.getElementById('concept-screen');
  const mainGrid = document.getElementById('main-grid');

  console.log('--- EuclidCam Sequence Initiated ---');

  // The initial sequence locks scrolling until the animation finishes.
  console.log('--- EuclidCam Hero Loading... ---');
  setTimeout(() => {
    document.body.classList.remove('scroll-lock');
    console.log('--- Boot Complete. Scroll Unlocked. ---');
  }, 4800);

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
        bootGifImg.src = isDark ? 'assets/euclid_construction_dark.gif' : 'assets/euclid_construction_light.gif';
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
});

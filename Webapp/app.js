document.addEventListener('DOMContentLoaded', () => {
  const bootScreen = document.getElementById('boot-screen');
  const conceptScreen = document.getElementById('concept-screen');
  const mainGrid = document.getElementById('main-grid');

  console.log('--- EuclidCam Sequence Initiated ---');

  // Sequence 1: Boot Screen (Splash)
  setTimeout(() => {
    console.log('--- Boot Complete. Transitioning to Concept. ---');
    bootScreen.style.opacity = '0';



    setTimeout(() => {
      bootScreen.style.display = 'none';
      conceptScreen.classList.remove('hidden');
      conceptScreen.style.display = 'grid';
      conceptScreen.style.opacity = '1';

      // Sequence 2: Concept Screen (Camera Outline Show)
      setTimeout(() => {
        console.log('--- Concept Explained. Loading Dashboard. ---');
        setTimeout(() => {
          conceptScreen.style.opacity = '0';
          setTimeout(() => {
            conceptScreen.style.display = 'none';
            mainGrid.classList.remove('hidden');
          }, 1000);
        }, 4500); // Comfortable reading time for the concept overview
      }, 800);
    }, 800);
  }, 4800); // Wait for the super fast GIF construction + 3s hold for EC text

  // Theme Toggle Logic
  const themeToggle = document.getElementById('theme-toggle');
  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const isDark = document.body.classList.toggle('dark-mode');
      const toggleText = themeToggle.querySelector('.toggle-text');
      if (toggleText) {
        toggleText.textContent = isDark ? 'MODE: DARK' : 'MODE: LIGHT';
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

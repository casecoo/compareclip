document.addEventListener('DOMContentLoaded', () => {
  // Default tags list is empty as requested by the user
  let tags = [];
  let currentLang = 'tr'; // Default language is TR

  const translations = {
    tr: {
      subtitle: "İki dikey video yükleyin, karakter isimlerini ve kategorileri özelleştirin, ritim senkronlu VS videosu oluşturun.",
      player1Badge: "1. OYUNCU (UST)",
      player2Badge: "2. OYUNCU (ALT)",
      characterTitleLabel: "KARAKTER / BASLIK",
      videoClipLabel: "VIDEO KLIP (MIN 6SN, MAX 20SN)",
      chooseVideo1: "1. Videoyu Seçin veya Sürükleyin",
      chooseVideo2: "2. Videoyu Seçin veya Sürükleyin",
      videoFileInfo: "Dikey MP4/MOV tavsiye edilir",
      categoriesTitle: "KARSILASTIRMA KATEGORILERI",
      categoriesHint: "Ritim uyumu için 9 tag gereklidir (6sn intro + 9 round)",
      addTagPlaceholder: "Özel tag ekle (örn. GÜÇ)",
      addTagBtn: "+ Tag Ekle",
      generateBtn: "🎬 VS VIDEO OLUSTUR",
      renderingTitle: "VIDEONUZ HAZIRLANIYOR...",
      elapsedTime: "Geçen süre:",
      coldStartNotice: "<strong>Render.com Soğuk Başlangıç:</strong> Sunucu son zamanlarda kullanılmadıysa, ilk istek 30–60 saniye sürebilir. Lütfen bekleyin!",
      videoReadyTitle: "VIDEO HAZIR!",
      downloadBtn: "💾 MP4 VIDEOYU INDIR",
      createAnotherBtn: "🔄 BASKA OLUSTUR",
      need9Tags: "LÜTFEN RİTİM UYUMU İÇİN TAM 9 KATEGORİ TAG'İ EKLEYİN.",
      max9Tags: "MAKSİMUM 9 KATEGORİ TAG'İ EKLENEBİLİR!",
      needBothVideos: "LÜTFEN HEM 1. HEM DE 2. VİDEO KLİPLERİNİ YÜKLEYİN.",
      vid1Min6s: "1. VİDEO EN AZ 6 SANİYE OLMALIDIR (MEVCUT: ",
      vid2Min6s: "2. VİDEO EN AZ 6 SANİYE OLMALIDIR (MEVCUT: ",
      player1Default: "1. OYUNCU",
      player2Default: "2. OYUNCU",
      failedGen: "VİDEO OLUŞTURMA BAŞARISIZ OLDU: "
    },
    en: {
      subtitle: "Upload two vertical clips, customize character names & categories, and generate a beat-synced VS video.",
      player1Badge: "PLAYER 1 (TOP)",
      player2Badge: "PLAYER 2 (BOTTOM)",
      characterTitleLabel: "Character / Title",
      videoClipLabel: "Video Clip (Min 6s, Max 20s)",
      chooseVideo1: "Choose or drop Video 1",
      chooseVideo2: "Choose or drop Video 2",
      videoFileInfo: "Vertical MP4/MOV recommended",
      categoriesTitle: "Comparison Categories",
      categoriesHint: "9 tags required for beat-sync (6s intro + 9 rounds)",
      addTagPlaceholder: "Add custom tag (e.g. STRENGTH)",
      addTagBtn: "+ Add Tag",
      generateBtn: "🎬 GENERATE VS VIDEO",
      renderingTitle: "RENDERING YOUR VIDEO...",
      elapsedTime: "Elapsed time:",
      coldStartNotice: "<strong>Render.com Cold Start:</strong> If the server hasn't been used recently, the initial request can take 30–60 seconds to spin up. Please hang tight!",
      videoReadyTitle: "VIDEO READY!",
      downloadBtn: "💾 DOWNLOAD MP4 VIDEO",
      createAnotherBtn: "🔄 CREATE ANOTHER",
      need9Tags: "PLEASE PROVIDE EXACTLY 9 CATEGORY TAGS FOR BEAT SYNC.",
      max9Tags: "MAXIMUM 9 CATEGORY TAGS ALLOWED!",
      needBothVideos: "PLEASE UPLOAD BOTH VIDEO 1 AND VIDEO 2 CLIPS.",
      vid1Min6s: "VIDEO 1 MUST BE AT LEAST 6 SECONDS LONG (CURRENT: ",
      vid2Min6s: "VIDEO 2 MUST BE AT LEAST 6 SECONDS LONG (CURRENT: ",
      player1Default: "PLAYER 1",
      player2Default: "PLAYER 2",
      failedGen: "FAILED TO GENERATE VIDEO: "
    }
  };

  // DOM Elements
  const generatorForm = document.getElementById('generatorForm');
  const tagsContainer = document.getElementById('tagsContainer');
  const tagCountText = document.getElementById('tagCountText');
  const newTagInput = document.getElementById('newTagInput');
  const addTagBtn = document.getElementById('addTagBtn');

  const video1Input = document.getElementById('video1');
  const video2Input = document.getElementById('video2');
  const label1 = document.getElementById('label1');
  const label2 = document.getElementById('label2');
  const dropzone1 = document.getElementById('dropzone1');
  const dropzone2 = document.getElementById('dropzone2');

  const processingCard = document.getElementById('processingCard');
  const resultCard = document.getElementById('resultCard');
  const timerText = document.getElementById('timerText');
  const outputVideoPlayer = document.getElementById('outputVideoPlayer');
  const downloadBtn = document.getElementById('downloadBtn');
  const resetBtn = document.getElementById('resetBtn');
  const submitBtn = document.getElementById('submitBtn');
  const langBtns = document.querySelectorAll('.lang-btn');

  const retroToast = document.getElementById('retroToast');
  const toastMessage = document.getElementById('toastMessage');
  const toastCloseBtn = document.getElementById('toastCloseBtn');
  let toastTimeout = null;

  function showToast(msg, isError = false) {
    if (!retroToast || !toastMessage) {
      alert(msg);
      return;
    }
    toastMessage.textContent = msg;
    if (isError) {
      retroToast.classList.add('toast-error');
    } else {
      retroToast.classList.remove('toast-error');
    }
    retroToast.classList.remove('hidden');

    if (toastTimeout) clearTimeout(toastTimeout);
    toastTimeout = setTimeout(() => {
      retroToast.classList.add('hidden');
    }, 3500);
  }

  if (toastCloseBtn) {
    toastCloseBtn.addEventListener('click', () => {
      retroToast.classList.add('hidden');
    });
  }

  let timerInterval = null;
  let currentObjectUrl = null;

  // Language Switcher Logic
  function setLanguage(lang) {
    if (!translations[lang]) return;
    currentLang = lang;

    // Update active button state
    langBtns.forEach(btn => {
      if (btn.getAttribute('data-lang') === lang) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });

    const t = translations[lang];

    // Update text content for elements with data-i18n attribute
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      if (t[key]) {
        el.textContent = t[key];
      }
    });

    // Update innerHTML for elements with data-i18n-html attribute
    document.querySelectorAll('[data-i18n-html]').forEach(el => {
      const key = el.getAttribute('data-i18n-html');
      if (t[key]) {
        el.innerHTML = t[key];
      }
    });

    // Update placeholders
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
      const key = el.getAttribute('data-i18n-placeholder');
      if (t[key]) {
        el.placeholder = t[key];
      }
    });

    // Update file dropzone default labels if no file selected
    if (!video1Input.files || !video1Input.files[0]) {
      label1.textContent = t.chooseVideo1;
    }
    if (!video2Input.files || !video2Input.files[0]) {
      label2.textContent = t.chooseVideo2;
    }

    document.documentElement.lang = lang;
  }

  // Register Language Switcher Click Handlers
  langBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const selectedLang = btn.getAttribute('data-lang');
      setLanguage(selectedLang);
    });
  });

  // Render Category Tags
  function renderTags() {
    tagsContainer.innerHTML = '';
    if (tagCountText) {
      tagCountText.textContent = tags.length;
    }
    tags.forEach((tag, idx) => {
      const pill = document.createElement('span');
      pill.className = 'tag-pill';
      pill.innerHTML = `
        ${escapeHtml(tag)}
        <button type="button" class="tag-remove-btn" data-index="${idx}">&times;</button>
      `;
      tagsContainer.appendChild(pill);
    });
  }

  function escapeHtml(text) {
    return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  // Add custom tag (Maximum 9 tags to match song timing)
  function addTag() {
    const t = translations[currentLang];
    if (tags.length >= 9) {
      showToast(t.max9Tags);
      return;
    }
    const val = newTagInput.value.trim().toUpperCase();
    if (val && !tags.includes(val)) {
      tags.push(val);
      newTagInput.value = '';
      renderTags();
    }
  }

  addTagBtn.addEventListener('click', addTag);
  newTagInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addTag();
    }
  });

  // Remove tag
  tagsContainer.addEventListener('click', (e) => {
    if (e.target.classList.contains('tag-remove-btn')) {
      const idx = parseInt(e.target.getAttribute('data-index'), 10);
      tags.splice(idx, 1);
      renderTags();
    }
  });

  // File Input Visual Handlers
  function handleFileInputChange(input, labelElement, defaultKey) {
    input.addEventListener('change', () => {
      if (input.files && input.files[0]) {
        labelElement.textContent = `📁 ${input.files[0].name}`;
      } else {
        labelElement.textContent = translations[currentLang][defaultKey];
      }
    });
  }

  handleFileInputChange(video1Input, label1, 'chooseVideo1');
  handleFileInputChange(video2Input, label2, 'chooseVideo2');

  // Drag and drop support
  [dropzone1, dropzone2].forEach((dropzone) => {
    dropzone.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropzone.classList.add('dragover');
    });

    dropzone.addEventListener('dragleave', () => {
      dropzone.classList.remove('dragover');
    });

    dropzone.addEventListener('drop', () => {
      dropzone.classList.remove('dragover');
    });
  });

  // Start Elapsed Timer
  function startTimer() {
    let seconds = 0;
    timerText.textContent = '00:00';
    clearInterval(timerInterval);
    timerInterval = setInterval(() => {
      seconds++;
      const mins = String(Math.floor(seconds / 60)).padStart(2, '0');
      const secs = String(seconds % 60).padStart(2, '0');
      timerText.textContent = `${mins}:${secs}`;
    }, 1000);
  }

  function stopTimer() {
    clearInterval(timerInterval);
  }

  // Helper to read video file duration in browser
  function getVideoDuration(file) {
    return new Promise((resolve) => {
      const video = document.createElement('video');
      video.preload = 'metadata';
      video.onloadedmetadata = () => {
        URL.revokeObjectURL(video.src);
        resolve(video.duration);
      };
      video.onerror = () => resolve(0);
      video.src = URL.createObjectURL(file);
    });
  }

  // Form Submit Handler
  generatorForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const t = translations[currentLang];

    if (tags.length !== 9) {
      showToast(t.need9Tags);
      return;
    }

    if (!video1Input.files[0] || !video2Input.files[0]) {
      showToast(t.needBothVideos);
      return;
    }

    // Validate minimum 6-second video duration
    const dur1 = await getVideoDuration(video1Input.files[0]);
    const dur2 = await getVideoDuration(video2Input.files[0]);

    if (dur1 > 0 && dur1 < 6.0) {
      showToast(`${t.vid1Min6s}${dur1.toFixed(1)}s).`);
      return;
    }

    if (dur2 > 0 && dur2 < 6.0) {
      showToast(`${t.vid2Min6s}${dur2.toFixed(1)}s).`);
      return;
    }

    const player1Name = document.getElementById('player1Name').value.trim() || t.player1Default;
    const player2Name = document.getElementById('player2Name').value.trim() || t.player2Default;

    // Automatic backend resolution: localhost/file protocol for local dev, Render.com for production
    const isLocalHost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' || window.location.protocol === 'file:' || window.location.hostname === '';
    const defaultRenderUrl = 'https://compareclip-backend.onrender.com';
    const apiUrlInput = document.getElementById('apiUrl');
    const baseUrl = apiUrlInput && apiUrlInput.value.trim()
      ? apiUrlInput.value.trim().replace(/\/$/, '')
      : (isLocalHost ? 'http://localhost:8000' : defaultRenderUrl);

    const formData = new FormData();
    formData.append('video1', video1Input.files[0]);
    formData.append('video2', video2Input.files[0]);
    formData.append('player1_name', player1Name);
    formData.append('player2_name', player2Name);
    formData.append('categories', JSON.stringify(tags));

    // Show processing card
    generatorForm.classList.add('hidden');
    resultCard.classList.add('hidden');
    processingCard.classList.remove('hidden');
    startTimer();

    try {
      const response = await fetch(`${baseUrl}/api/v1/compare`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        let errMessage = `Server error ${response.status}`;
        try {
          const errorJson = await response.json();
          if (errorJson.detail) errMessage = errorJson.detail;
        } catch (_) { }
        throw new Error(errMessage);
      }

      // Read video blob
      const videoBlob = await response.blob();

      if (currentObjectUrl) {
        URL.revokeObjectURL(currentObjectUrl);
      }
      currentObjectUrl = URL.createObjectURL(videoBlob);

      outputVideoPlayer.src = currentObjectUrl;
      downloadBtn.href = currentObjectUrl;
      downloadBtn.download = `${player1Name}_vs_${player2Name}.mp4`;

      // Show result card
      stopTimer();
      processingCard.classList.add('hidden');
      resultCard.classList.remove('hidden');

    } catch (err) {
      stopTimer();
      processingCard.classList.add('hidden');
      generatorForm.classList.remove('hidden');
      showToast(`${t.failedGen}${err.message}`, true);
    }
  });

  // Reset Button
  resetBtn.addEventListener('click', () => {
    resultCard.classList.add('hidden');
    generatorForm.classList.remove('hidden');
    if (currentObjectUrl) {
      URL.revokeObjectURL(currentObjectUrl);
      currentObjectUrl = null;
    }
  });

  // Floating Pixel Space Canvas Particle System (Matching Reference Image 1)
  function initPixelSpaceCanvas() {
    const canvas = document.getElementById('pixelSpaceCanvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    window.addEventListener('resize', () => {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    });

    const particles = [];
    const particleCount = Math.min(140, Math.floor((width * height) / 9000));

    const colors = [
      'rgba(255, 255, 255, ',
      'rgba(167, 139, 250, ',
      'rgba(56, 189, 248, ',
      'rgba(244, 114, 182, ',
      'rgba(251, 191, 36, '
    ];

    for (let i = 0; i < particleCount; i++) {
      particles.push({
        x: Math.random() * width,
        y: Math.random() * height,
        size: Math.floor(Math.random() * 3 + 1) * 2, // 2px, 4px, 6px pixel squares
        speedY: (Math.random() - 0.5) * 0.45,
        speedX: (Math.random() - 0.5) * 0.35,
        alpha: Math.random() * 0.6 + 0.15,
        colorPrefix: colors[Math.floor(Math.random() * colors.length)],
        pulseSpeed: Math.random() * 0.015 + 0.005
      });
    }

    function animate() {
      ctx.clearRect(0, 0, width, height);

      particles.forEach((p) => {
        p.y += p.speedY;
        p.x += p.speedX;
        p.alpha += p.pulseSpeed;

        if (p.alpha > 0.8 || p.alpha < 0.1) {
          p.pulseSpeed = -p.pulseSpeed;
        }

        if (p.x < 0) p.x = width;
        if (p.x > width) p.x = 0;
        if (p.y < 0) p.y = height;
        if (p.y > height) p.y = 0;

        ctx.fillStyle = `${p.colorPrefix}${p.alpha.toFixed(2)})`;
        ctx.fillRect(Math.floor(p.x), Math.floor(p.y), p.size, p.size);
      });

      requestAnimationFrame(animate);
    }

    animate();
  }

  // Initialize Canvas Background
  initPixelSpaceCanvas();

  // Initialize TR language by default
  setLanguage('tr');

  // Initial tag render (empty by default)
  renderTags();
});

document.addEventListener('DOMContentLoaded', () => {
  // Default tags list
  let tags = ['IQ', 'SPEED', 'BATTLE IQ', 'DURABILITY'];

  // DOM Elements
  const generatorForm = document.getElementById('generatorForm');
  const tagsContainer = document.getElementById('tagsContainer');
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

  let timerInterval = null;
  let currentObjectUrl = null;

  // Render Category Tags
  function renderTags() {
    tagsContainer.innerHTML = '';
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

  // Add custom tag
  function addTag() {
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
  function handleFileInputChange(input, labelElement, defaultText) {
    input.addEventListener('change', () => {
      if (input.files && input.files[0]) {
        labelElement.textContent = `📁 ${input.files[0].name}`;
      } else {
        labelElement.textContent = defaultText;
      }
    });
  }

  handleFileInputChange(video1Input, label1, 'Choose or drop Video 1');
  handleFileInputChange(video2Input, label2, 'Choose or drop Video 2');

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

  // Form Submit Handler
  generatorForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    if (tags.length === 0) {
      alert('Please add at least one comparison category tag.');
      return;
    }

    if (!video1Input.files[0] || !video2Input.files[0]) {
      alert('Please upload both Video 1 and Video 2 clips.');
      return;
    }

    const player1Name = document.getElementById('player1Name').value.trim() || 'BATMAN';
    const player2Name = document.getElementById('player2Name').value.trim() || 'X-MEN';
    const baseUrl = document.getElementById('apiUrl').value.trim().replace(/\/$/, '');

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
        } catch (_) {}
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
      alert(`Failed to generate video: ${err.message}`);
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

  // Initial tag render
  renderTags();
});

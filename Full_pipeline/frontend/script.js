// Enhanced PTD Generator with backend integration

const API_BASE = window.API_BASE || 'http://localhost:5000';

class PTDGenerator {
  constructor() {
    this.protocolFile = null;
    this.crfFile = null;
    this.isProcessing = false;
    this.init();
  }

  init() {
    this.setupEventListeners();
    this.setupDragAndDrop();
    this.updateGenerateButton();
    this.pingStatus();
  }

  setupEventListeners() {
    const protocolInput = document.getElementById('protocolFile');
    const crfInput = document.getElementById('crfFile');
    const generateBtn = document.getElementById('generateBtn');

    if (protocolInput) {
      protocolInput.addEventListener('change', (e) => this.handleFileSelect(e, 'protocol'));
    }
    if (crfInput) {
      crfInput.addEventListener('change', (e) => this.handleFileSelect(e, 'crf'));
    }
    if (generateBtn) {
      generateBtn.addEventListener('click', () => this.generatePTD());
    }
  }

  setupDragAndDrop() {
    const dropZone = document.getElementById('dropZone');
    if (!dropZone) return;

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
      dropZone.addEventListener(eventName, this.preventDefaults, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
      dropZone.addEventListener(eventName, () => {
        dropZone.classList.add('dragover');
      }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
      dropZone.addEventListener(eventName, () => {
        dropZone.classList.remove('dragover');
      }, false);
    });

    dropZone.addEventListener('drop', (e) => this.handleDrop(e), false);
  }

  preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;

    if (files.length >= 2) {
      this.protocolFile = files[0];
      this.crfFile = files[1];
      this.updateFilePreviews();
      this.updateGenerateButton();
      this.showToast('Files uploaded successfully!', 'success');
    } else if (files.length === 1) {
      this.showFileTypeModal(files[0]);
    }
  }

  showFileTypeModal(file) {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
      <div class="modal-content">
        <h3>Select File Type</h3>
        <p>Which type of document is "${file.name}"?</p>
        <div class="modal-buttons">
          <button data-type="protocol" class="modal-btn">
            <i class="fas fa-file-alt"></i> Protocol Document
          </button>
          <button data-type="crf" class="modal-btn">
            <i class="fas fa-file-medical"></i> CRF Document
          </button>
        </div>
        <button class="modal-close">
          <i class="fas fa-times"></i>
        </button>
      </div>
    `;

    modal.querySelector('.modal-close').addEventListener('click', () => modal.remove());
    modal.querySelectorAll('.modal-btn').forEach(btn => {
      btn.addEventListener('click', (ev) => {
        const type = ev.currentTarget.getAttribute('data-type');
        this.assignFileType(type, file);
        modal.remove();
      });
    });

    document.body.appendChild(modal);
  }

  assignFileType(type, file) {
    if (type === 'protocol') {
      this.protocolFile = file;
    } else {
      this.crfFile = file;
    }
    this.updateFilePreviews();
    this.updateGenerateButton();
    this.showToast(`${type.toUpperCase()} file assigned successfully!`, 'success');
  }

  handleFileSelect(e, type) {
    const file = e.target.files[0];
    if (file) {
      if (type === 'protocol') {
        this.protocolFile = file;
      } else {
        this.crfFile = file;
      }
      this.updateFilePreviews();
      this.updateGenerateButton();
      this.showToast(`${type.toUpperCase()} file selected successfully!`, 'success');
    }
  }

  updateFilePreviews() {
    this.updateFilePreview('protocol', this.protocolFile);
    this.updateFilePreview('crf', this.crfFile);
  }

  updateFilePreview(type, file) {
    const preview = document.getElementById(`${type}Preview`);
    if (!preview) return;

    if (file) {
      preview.innerHTML = `
        <div class="file-preview-item">
          <div class="file-preview-icon">
            <i class="fas fa-file-${type === 'protocol' ? 'alt' : 'medical'}"></i>
          </div>
          <div class="file-preview-info">
            <div class="file-preview-name">${file.name}</div>
            <div class="file-preview-size">${this.formatFileSize(file.size)}</div>
          </div>
          <button class="file-preview-remove">
            <i class="fas fa-times"></i>
          </button>
        </div>
      `;
      const removeBtn = preview.querySelector('.file-preview-remove');
      removeBtn.addEventListener('click', () => this.removeFile(type));
      preview.classList.add('show');
    } else {
      preview.classList.remove('show');
      preview.innerHTML = '';
    }
  }

  removeFile(type) {
    if (type === 'protocol') {
      this.protocolFile = null;
      const input = document.getElementById('protocolFile');
      if (input) input.value = '';
    } else {
      this.crfFile = null;
      const input = document.getElementById('crfFile');
      if (input) input.value = '';
    }
    this.updateFilePreviews();
    this.updateGenerateButton();
    this.showToast(`${type.toUpperCase()} file removed`, 'warning');
  }

  updateGenerateButton() {
    const btn = document.getElementById('generateBtn');
    if (!btn) return;

    const canGenerate = this.protocolFile && this.crfFile && !this.isProcessing;
    btn.disabled = !canGenerate;

    if (this.isProcessing) {
      btn.innerHTML = `
        <span class="btn-text">Processing...</span>
        <span class="btn-icon"><i class="fas fa-spinner fa-spin"></i></span>
      `;
    } else {
      btn.innerHTML = `
        <span class="btn-text">Generate PTD</span>
        <span class="btn-icon"><i class="fas fa-magic"></i></span>
      `;
    }
  }

  async generatePTD() {
    if (!this.protocolFile || !this.crfFile) {
      this.showToast('Please upload both Protocol and CRF documents.', 'error');
      return;
    }
    if (this.isProcessing) return;

    this.isProcessing = true;
    this.updateGenerateButton();
    this.showProgressSection();
    this.startProgressAnimation();

    try {
      const responseJson = await this.postRunPipelineWithFiles();

      if (responseJson.success) {
        this.showToast(responseJson.message || 'Processed successfully!', 'success');
        this.showOutputSection();

        if (responseJson.results) {
          this.displayResults(responseJson.results);
        }

        if (responseJson.download_url) {
          const downloadLink = document.getElementById('downloadLink');
          if (downloadLink) {
            downloadLink.href = `${API_BASE}${responseJson.download_url}`;
          }
        }
      } else {
        const err = responseJson.error || 'Processing failed.';
        this.showToast(err, 'error');
        console.error('API error:', responseJson);
      }
    } catch (error) {
      this.showToast('Error communicating with backend. See console for details.', 'error');
      console.error('Network/API error:', error);
    } finally {
      this.isProcessing = false;
      this.updateGenerateButton();
    }
  }

  showProgressSection() {
    const el = document.getElementById('progressSection');
    if (!el) return;
    el.classList.remove('hidden');
    el.classList.add('fade-in');
  }

  startProgressAnimation() {
    const steps = ['step1', 'step2', 'step3', 'step4'];
    const progressFill = document.getElementById('progressFill');
    if (!progressFill) return;

    steps.forEach((stepId, index) => {
      setTimeout(() => {
        progressFill.style.width = `${(index + 1) * 25}%`;
        const step = document.getElementById(stepId);
        if (step) step.classList.add('active');

        if (index > 0) {
          const prev = document.getElementById(steps[index - 1]);
          if (prev) {
            prev.classList.remove('active');
            prev.classList.add('completed');
          }
        }

        if (index === steps.length - 1) {
          setTimeout(() => {
            const sec = document.getElementById('progressSection');
            if (sec) sec.classList.add('hidden');
          }, 1000);
        }
      }, index * 1200);
    });
  }

  showOutputSection() {
    const outputSection = document.getElementById('outputSection');
    if (!outputSection) return;
    outputSection.classList.remove('hidden');
    outputSection.classList.add('fade-in');

    const date = new Date();
    const dateEl = document.getElementById('generationDate');
    if (dateEl) dateEl.textContent = date.toLocaleDateString();
  }

  displayResults(results) {
    try {
      const outputSection = document.getElementById('outputSection');
      if (!outputSection) return;

      let resultsContainer = document.getElementById('resultsContainer');
      if (!resultsContainer) {
        resultsContainer = document.createElement('div');
        resultsContainer.id = 'resultsContainer';
        resultsContainer.style.marginTop = '16px';
        resultsContainer.style.padding = '12px';
        resultsContainer.style.background = '#0b1324';
        resultsContainer.style.border = '1px solid #243b55';
        resultsContainer.style.borderRadius = '8px';
        const heading = document.createElement('h5');
        heading.textContent = 'Structured Results';
        heading.style.margin = '0 0 8px 0';
        heading.style.fontWeight = '600';
        const pre = document.createElement('pre');
        pre.id = 'resultsPre';
        pre.style.whiteSpace = 'pre-wrap';
        pre.style.wordBreak = 'break-word';
        pre.style.margin = '0';
        pre.style.fontSize = '12px';
        pre.style.lineHeight = '1.4';
        resultsContainer.appendChild(heading);
        resultsContainer.appendChild(pre);
        outputSection.appendChild(resultsContainer);
      }
      const pre = document.getElementById('resultsPre');
      if (pre) pre.textContent = JSON.stringify(results, null, 2);
    } catch (_) {
      // best-effort display
    }
  }

  formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  showToast(message, type = 'success') {
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    const icons = {
      success: 'fas fa-check-circle',
      error: 'fas fa-exclamation-circle',
      warning: 'fas fa-exclamation-triangle'
    };

    toast.innerHTML = `
      <div class="toast-icon">
        <i class="${icons[type]}"></i>
      </div>
      <div class="toast-content">
        <div class="toast-message">${message}</div>
      </div>
      <button class="toast-close">
        <i class="fas fa-times"></i>
      </button>
    `;

    toast.querySelector('.toast-close').addEventListener('click', () => toast.remove());
    toastContainer.appendChild(toast);

    setTimeout(() => {
      if (toast.parentElement) toast.remove();
    }, 5000);
  }

  async postRunPipelineWithFiles() {
    const formData = new FormData();
    formData.append('protocol_file', this.protocolFile);
    formData.append('crf_file', this.crfFile);

    const resp = await fetch(`${API_BASE}/run_pipeline`, {
      method: 'POST',
      body: formData
    });

    const data = await resp.json().catch(() => ({ success: false, error: 'Invalid JSON response' }));
    if (!resp.ok) {
      throw new Error(data.error || `HTTP ${resp.status}`);
    }
    return data;
  }

  async pingStatus() {
    try {
      const resp = await fetch(`${API_BASE}/status`);
      const data = await resp.json();
      console.log('Backend status:', data);
    } catch (e) {
      console.warn('Unable to reach backend status at', API_BASE);
    }
  }
}

// Global helpers for HTML onclick handlers
let ptdGenerator;
document.addEventListener('DOMContentLoaded', () => {
  ptdGenerator = new PTDGenerator();
});

function generatePTD() {
  if (ptdGenerator) ptdGenerator.generatePTD();
}

function resetForm() {
  if (!ptdGenerator) return;
  ptdGenerator.protocolFile = null;
  ptdGenerator.crfFile = null;
  ptdGenerator.isProcessing = false;

  const protocolInput = document.getElementById('protocolFile');
  const crfInput = document.getElementById('crfFile');
  if (protocolInput) protocolInput.value = '';
  if (crfInput) crfInput.value = '';

  const outputSection = document.getElementById('outputSection');
  const progressSection = document.getElementById('progressSection');
  if (outputSection) outputSection.classList.add('hidden');
  if (progressSection) progressSection.classList.add('hidden');

  const resultsContainer = document.getElementById('resultsContainer');
  if (resultsContainer && resultsContainer.parentElement) {
    resultsContainer.parentElement.removeChild(resultsContainer);
  }

  ptdGenerator.updateFilePreviews();
  ptdGenerator.updateGenerateButton();
  ptdGenerator.showToast('Form reset successfully!', 'success');
}

function shareResults() {
  if (navigator.share) {
    navigator.share({
      title: 'PTD Generated',
      text: 'Check out my generated PTD file!',
      url: window.location.href
    }).catch(() => {});
  } else {
    const url = window.location.href;
    navigator.clipboard.writeText(url).then(() => {
      if (ptdGenerator) ptdGenerator.showToast('Link copied to clipboard!', 'success');
    });
  }
}

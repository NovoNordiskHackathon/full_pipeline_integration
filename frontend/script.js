// Enhanced PTD Generator with modern interactions

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
  }

  setupEventListeners() {
    // File input listeners
    document.getElementById('protocolFile').addEventListener('change', (e) => {
      this.handleFileSelect(e, 'protocol');
    });

    document.getElementById('crfFile').addEventListener('change', (e) => {
      this.handleFileSelect(e, 'crf');
    });

    // Generate button
    document.getElementById('generateBtn').addEventListener('click', () => {
      this.generatePTD();
    });
  }

  setupDragAndDrop() {
    const dropZone = document.getElementById('dropZone');
   
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

    dropZone.addEventListener('drop', (e) => {
      this.handleDrop(e);
    }, false);
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
      // If only one file, ask user to specify which type
      this.showFileTypeModal(files[0]);
    }
  }

  showFileTypeModal(file) {
    // Create a simple modal to ask which type of file this is
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
      <div class="modal-content">
        <h3>Select File Type</h3>
        <p>Which type of document is "${file.name}"?</p>
        <div class="modal-buttons">
          <button onclick="ptdGenerator.assignFileType('protocol', '${file.name}')" class="modal-btn">
            <i class="fas fa-file-alt"></i> Protocol Document
          </button>
          <button onclick="ptdGenerator.assignFileType('crf', '${file.name}')" class="modal-btn">
            <i class="fas fa-file-medical"></i> CRF Document
          </button>
        </div>
        <button onclick="this.closest('.modal-overlay').remove()" class="modal-close">
          <i class="fas fa-times"></i>
        </button>
      </div>
    `;
    document.body.appendChild(modal);
  }

  assignFileType(type, fileName) {
    const file = this.protocolFile || this.crfFile;
    if (type === 'protocol') {
      this.protocolFile = file;
    } else {
      this.crfFile = file;
    }
    this.updateFilePreviews();
    this.updateGenerateButton();
    document.querySelector('.modal-overlay').remove();
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
          <button class="file-preview-remove" onclick="ptdGenerator.removeFile('${type}')">
            <i class="fas fa-times"></i>
          </button>
        </div>
      `;
      preview.classList.add('show');
    } else {
      preview.classList.remove('show');
      preview.innerHTML = '';
    }
  }

  removeFile(type) {
    if (type === 'protocol') {
      this.protocolFile = null;
      document.getElementById('protocolFile').value = '';
    } else {
      this.crfFile = null;
      document.getElementById('crfFile').value = '';
    }
    this.updateFilePreviews();
    this.updateGenerateButton();
    this.showToast(`${type.toUpperCase()} file removed`, 'warning');
  }

  updateGenerateButton() {
    const btn = document.getElementById('generateBtn');
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
      this.showToast('Please upload both Protocol and CRF JSON files.', 'error');
      return;
    }

    if (this.isProcessing) return;

    this.isProcessing = true;
    this.updateGenerateButton();
    this.showProgressSection();
    this.startProgressAnimation();

    try {
      const formData = new FormData();
      formData.append('protocol_json', this.protocolFile);
      formData.append('ecrf_json', this.crfFile);
      // Optional: template upload field can be added to UI and appended here
      // formData.append('template_xlsx', templateFile);
      formData.append('mode', 'default');
      formData.append('fast', 'true');

      const res = await fetch('http://localhost:5000/run_pipeline', {
        method: 'POST',
        body: formData
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ error: 'Request failed' }));
        throw new Error(err.error || 'Backend error');
      }

      const data = await res.json();
      if (data.download_url) {
        this.showOutputSection();
        const downloadLink = document.getElementById('downloadLink');
        // Use absolute URL to backend
        const url = new URL(data.download_url, 'http://localhost:5000');
        downloadLink.href = url.toString();
        // Update file name if present
        const fileName = (data.output || '').split('/').pop() || 'PTD_Template.xlsx';
        downloadLink.setAttribute('download', fileName);
        this.showToast('PTD generated successfully!', 'success');
      } else if (data.note) {
        // If only schedule grid is returned
        this.showOutputSection();
        const downloadLink = document.getElementById('downloadLink');
        const url = new URL(data.download_url, 'http://localhost:5000');
        downloadLink.href = url.toString();
        const fileName = (data.output || '').split('/').pop() || 'schedule_grid.xlsx';
        downloadLink.setAttribute('download', fileName);
        this.showToast(data.note, 'success');
      } else {
        throw new Error('Unexpected response from backend');
      }
    } catch (error) {
      this.showToast('Error generating PTD. Please try again.', 'error');
      console.error('Error:', error);
    } finally {
      this.isProcessing = false;
      this.updateGenerateButton();
    }
  }

  showProgressSection() {
    document.getElementById('progressSection').classList.remove('hidden');
    document.getElementById('progressSection').classList.add('fade-in');
  }

  startProgressAnimation() {
    const steps = ['step1', 'step2', 'step3', 'step4'];
    const progressFill = document.getElementById('progressFill');
   
    steps.forEach((stepId, index) => {
      setTimeout(() => {
        // Update progress bar
        progressFill.style.width = `${(index + 1) * 25}%`;
       
        // Update step status
        const step = document.getElementById(stepId);
        step.classList.add('active');
       
        if (index > 0) {
          document.getElementById(steps[index - 1]).classList.remove('active');
          document.getElementById(steps[index - 1]).classList.add('completed');
        }
       
        if (index === steps.length - 1) {
          setTimeout(() => {
            document.getElementById('progressSection').classList.add('hidden');
          }, 1000);
        }
      }, index * 2000);
    });
  }

  async simulateProcessing() {
    // Simulate realistic processing time
    const steps = [
      { name: 'Uploading files...', duration: 2000 },
      { name: 'Analyzing document structure...', duration: 3000 },
      { name: 'Extracting data...', duration: 2500 },
      { name: 'Generating PTD...', duration: 2000 },
      { name: 'Finalizing output...', duration: 1500 }
    ];

    for (const step of steps) {
      await new Promise(resolve => setTimeout(resolve, step.duration));
    }
  }

  showOutputSection() {
    const outputSection = document.getElementById('outputSection');
    outputSection.classList.remove('hidden');
    outputSection.classList.add('fade-in');
   
    // Set generation date
    const date = new Date();
    document.getElementById('generationDate').textContent = date.toLocaleDateString();
   
    // Create a sample download link (in real implementation, this would be the actual file)
    const downloadLink = document.getElementById('downloadLink');
    downloadLink.href = 'data:text/plain;charset=utf-8,This is a sample PTD file content';
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
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
   
    const icons = {
      success: 'fas fa-check-circle',
      error: 'fas fa-exclamation-circle',
      warning: 'fas fa-exclamation-triangle'
    };
   // Enhanced PTD Generator with modern interactions

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
  }

  setupEventListeners() {
    // File input listeners
    document.getElementById('protocolFile').addEventListener('change', (e) => {
      this.handleFileSelect(e, 'protocol');
    });

    document.getElementById('crfFile').addEventListener('change', (e) => {
      this.handleFileSelect(e, 'crf');
    });

    // Generate button
    document.getElementById('generateBtn').addEventListener('click', () => {
      this.generatePTD();
    });
  }

  setupDragAndDrop() {
    const dropZone = document.getElementById('dropZone');
   
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

    dropZone.addEventListener('drop', (e) => {
      this.handleDrop(e);
    }, false);
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
      // If only one file, ask user to specify which type
      this.showFileTypeModal(files[0]);
    }
  }

  showFileTypeModal(file) {
    // Create a simple modal to ask which type of file this is
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
      <div class="modal-content">
        <h3>Select File Type</h3>
        <p>Which type of document is "${file.name}"?</p>
        <div class="modal-buttons">
          <button onclick="ptdGenerator.assignFileType('protocol', '${file.name}')" class="modal-btn">
            <i class="fas fa-file-alt"></i> Protocol Document
          </button>
          <button onclick="ptdGenerator.assignFileType('crf', '${file.name}')" class="modal-btn">
            <i class="fas fa-file-medical"></i> CRF Document
          </button>
        </div>
        <button onclick="this.closest('.modal-overlay').remove()" class="modal-close">
          <i class="fas fa-times"></i>
        </button>
      </div>
    `;
    document.body.appendChild(modal);
  }

  assignFileType(type, fileName) {
    const file = this.protocolFile || this.crfFile;
    if (type === 'protocol') {
      this.protocolFile = file;
    } else {
      this.crfFile = file;
    }
    this.updateFilePreviews();
    this.updateGenerateButton();
    document.querySelector('.modal-overlay').remove();
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
          <button class="file-preview-remove" onclick="ptdGenerator.removeFile('${type}')">
            <i class="fas fa-times"></i>
          </button>
        </div>
      `;
      preview.classList.add('show');
    } else {
      preview.classList.remove('show');
      preview.innerHTML = '';
    }
  }

  removeFile(type) {
    if (type === 'protocol') {
      this.protocolFile = null;
      document.getElementById('protocolFile').value = '';
    } else {
      this.crfFile = null;
      document.getElementById('crfFile').value = '';
    }
    this.updateFilePreviews();
    this.updateGenerateButton();
    this.showToast(`${type.toUpperCase()} file removed`, 'warning');
  }

  updateGenerateButton() {
    const btn = document.getElementById('generateBtn');
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
      // Simulate processing with realistic steps
      await this.simulateProcessing();
     
      // Show success
      this.showOutputSection();
      this.showToast('PTD generated successfully!', 'success');
     
    } catch (error) {
      this.showToast('Error generating PTD. Please try again.', 'error');
      console.error('Error:', error);
    } finally {
      this.isProcessing = false;
      this.updateGenerateButton();
    }
  }

  showProgressSection() {
    document.getElementById('progressSection').classList.remove('hidden');
    document.getElementById('progressSection').classList.add('fade-in');
  }

  startProgressAnimation() {
    const steps = ['step1', 'step2', 'step3', 'step4'];
    const progressFill = document.getElementById('progressFill');
   
    steps.forEach((stepId, index) => {
      setTimeout(() => {
        // Update progress bar
        progressFill.style.width = `${(index + 1) * 25}%`;
       
        // Update step status
        const step = document.getElementById(stepId);
        step.classList.add('active');
       
        if (index > 0) {
          document.getElementById(steps[index - 1]).classList.remove('active');
          document.getElementById(steps[index - 1]).classList.add('completed');
        }
       
        if (index === steps.length - 1) {
          setTimeout(() => {
            document.getElementById('progressSection').classList.add('hidden');
          }, 1000);
        }
      }, index * 2000);
    });
  }

  async simulateProcessing() {
    // Simulate realistic processing time
    const steps = [
      { name: 'Uploading files...', duration: 2000 },
      { name: 'Analyzing document structure...', duration: 3000 },
      { name: 'Extracting data...', duration: 2500 },
      { name: 'Generating PTD...', duration: 2000 },
      { name: 'Finalizing output...', duration: 1500 }
    ];

    for (const step of steps) {
      await new Promise(resolve => setTimeout(resolve, step.duration));
    }
  }

  showOutputSection() {
    const outputSection = document.getElementById('outputSection');
    outputSection.classList.remove('hidden');
    outputSection.classList.add('fade-in');
   
    // Set generation date
    const date = new Date();
    document.getElementById('generationDate').textContent = date.toLocaleDateString();
   
    // Create a sample download link (in real implementation, this would be the actual file)
    const downloadLink = document.getElementById('downloadLink');
    downloadLink.href = 'data:text/plain;charset=utf-8,This is a sample PTD file content';
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
      <button class="toast-close" onclick="this.parentElement.remove()">
        <i class="fas fa-times"></i>
      </button>
    `;
   
    toastContainer.appendChild(toast);
   
    // Auto remove after 5 seconds
    setTimeout(() => {
      if (toast.parentElement) {
        toast.remove();
      }
    }, 5000);
  }
}

// Global functions for HTML onclick handlers
function generatePTD() {
  ptdGenerator.generatePTD();
}

function resetForm() {
  ptdGenerator.protocolFile = null;
  ptdGenerator.crfFile = null;
  ptdGenerator.isProcessing = false;
 
  document.getElementById('protocolFile').value = '';
  document.getElementById('crfFile').value = '';
  document.getElementById('outputSection').classList.add('hidden');
  document.getElementById('progressSection').classList.add('hidden');
 
  ptdGenerator.updateFilePreviews();
  ptdGenerator.updateGenerateButton();
 
  ptdGenerator.showToast('Form reset successfully!', 'success');
}

function shareResults() {
  if (navigator.share) {
    navigator.share({
      title: 'PTD Generated Successfully',
      text: 'Check out my generated PTD file!',
      url: window.location.href
    });
  } else {
    // Fallback for browsers that don't support Web Share API
    const url = window.location.href;
    navigator.clipboard.writeText(url).then(() => {
      ptdGenerator.showToast('Link copied to clipboard!', 'success');
    });
  }
}

// Initialize the PTD Generator when the page loads
let ptdGenerator;
document.addEventListener('DOMContentLoaded', () => {
  ptdGenerator = new PTDGenerator();
});
    toast.innerHTML = `
      <div class="toast-icon">
        <i class="${icons[type]}"></i>
      </div>
      <div class="toast-content">
        <div class="toast-message">${message}</div>
      </div>
      <button class="toast-close" onclick="this.parentElement.remove()">
        <i class="fas fa-times"></i>
      </button>
    `;
   
    toastContainer.appendChild(toast);
   
    // Auto remove after 5 seconds
    setTimeout(() => {
      if (toast.parentElement) {
        toast.remove();
      }
    }, 5000);
  }
}

// Global functions for HTML onclick handlers
function generatePTD() {
  ptdGenerator.generatePTD();
}

function resetForm() {
  ptdGenerator.protocolFile = null;
  ptdGenerator.crfFile = null;
  ptdGenerator.isProcessing = false;
 
  document.getElementById('protocolFile').value = '';
  document.getElementById('crfFile').value = '';
  document.getElementById('outputSection').classList.add('hidden');
  document.getElementById('progressSection').classList.add('hidden');
 
  ptdGenerator.updateFilePreviews();
  ptdGenerator.updateGenerateButton();
 
  ptdGenerator.showToast('Form reset successfully!', 'success');
}

function shareResults() {
  if (navigator.share) {
    navigator.share({
      title: 'PTD Generated Successfully',
      text: 'Check out my generated PTD file!',
      url: window.location.href
    });
  } else {
    // Fallback for browsers that don't support Web Share API
    const url = window.location.href;
    navigator.clipboard.writeText(url).then(() => {
      ptdGenerator.showToast('Link copied to clipboard!', 'success');
    });
  }
}

// Initialize the PTD Generator when the page loads
let ptdGenerator;
document.addEventListener('DOMContentLoaded', () => {
  ptdGenerator = new PTDGenerator();
});

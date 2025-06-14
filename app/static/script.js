// JavaScript for the LLM Function Calling app

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('processForm');
    const fileInput = document.getElementById('files');
    const fileList = document.getElementById('fileList');
    const submitBtn = document.getElementById('submitBtn');
    const submitText = document.getElementById('submitText');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const results = document.getElementById('results');
    const resultContent = document.getElementById('resultContent');
    const dropZone = fileInput.parentElement;

    let selectedFiles = [];

    // Handle file selection
    fileInput.addEventListener('change', function(e) {
        handleFiles(e.target.files);
    });

    // Handle drag and drop
    dropZone.addEventListener('dragover', function(e) {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });

    dropZone.addEventListener('dragleave', function(e) {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
    });

    dropZone.addEventListener('drop', function(e) {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        handleFiles(e.dataTransfer.files);
    });

    function handleFiles(files) {
        // Add new files to selectedFiles array
        for (let file of files) {
            // Check if file is already selected
            if (!selectedFiles.find(f => f.name === file.name && f.size === file.size)) {
                selectedFiles.push(file);
            }
        }
        updateFileList();
    }

    function updateFileList() {
        fileList.innerHTML = '';
        
        selectedFiles.forEach((file, index) => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            
            fileItem.innerHTML = `
                <span class="file-name">${file.name} (${formatFileSize(file.size)})</span>
                <button type="button" class="remove-file" onclick="removeFile(${index})">Remove</button>
            `;
            
            fileList.appendChild(fileItem);
        });
    }

    // Make removeFile globally accessible
    window.removeFile = function(index) {
        selectedFiles.splice(index, 1);
        updateFileList();
    };

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Handle form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const prompt = document.getElementById('prompt').value.trim();
        
        if (!prompt) {
            showError('Please enter a prompt describing what you want to do.');
            return;
        }

        if (selectedFiles.length === 0) {
            showError('Please upload at least one file.');
            return;
        }

        // Show loading state
        setLoadingState(true);
        hideResults();

        try {
            // Create FormData
            const formData = new FormData();
            formData.append('prompt', prompt);
            
            selectedFiles.forEach(file => {
                formData.append('files', file);
            });

            // Send request
            const response = await fetch('/process', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok && data.success) {
                showSuccess(data);
            } else {
                showError(data.detail || 'An error occurred during processing.');
            }

        } catch (error) {
            console.error('Error:', error);
            showError('Network error. Please check your connection and try again.');
        } finally {
            setLoadingState(false);
        }
    });

    function setLoadingState(loading) {
        if (loading) {
            submitBtn.disabled = true;
            submitText.classList.add('hidden');
            loadingSpinner.classList.remove('hidden');
        } else {
            submitBtn.disabled = false;
            submitText.classList.remove('hidden');
            loadingSpinner.classList.add('hidden');
        }
    }

    function showSuccess(data) {
        const successHtml = `
            <div class="success-message">
                ✅ ${data.message}
            </div>
            
            <div class="processing-info">
                <h4>Processing Details</h4>
                <p><strong>Function Used:</strong> ${data.function_used}</p>
                <p><strong>Files Processed:</strong> ${selectedFiles.length}</p>
            </div>
            
            ${data.result_file_path ? `
                <div class="text-center">
                    <a href="/download/${data.result_file_path}" class="download-btn" download>
                        📥 Download Result
                    </a>
                </div>
            ` : ''}
        `;
        
        resultContent.innerHTML = successHtml;
        results.classList.remove('hidden');
        
        // Scroll to results
        results.scrollIntoView({ behavior: 'smooth' });
    }

    function showError(message) {
        const errorHtml = `
            <div class="error-message">
                ❌ Error: ${message}
            </div>
        `;
        
        resultContent.innerHTML = errorHtml;
        results.classList.remove('hidden');
        
        // Scroll to results
        results.scrollIntoView({ behavior: 'smooth' });
    }

    function hideResults() {
        results.classList.add('hidden');
    }

    // Add some example prompts on click
    const promptExamples = [
        "Compress these images to 70% quality for web use",
        "Convert this Word document to PDF format",
        "Create a PDF from these photos with A4 pages",
        "Extract all files from this zip archive",
        "Analyze the contents of this archive",
        "Replace 'IITM' with 'IIT Madras' in all files",
        "Find and replace 'old_text' with 'new_text' in the archive",
        "Reduce the file size of these images by half",
        "Make a professional PDF from this document"
    ];

    // Add click handler for prompt placeholder
    const promptTextarea = document.getElementById('prompt');
    let exampleIndex = 0;
    
    promptTextarea.addEventListener('focus', function() {
        if (!this.value) {
            this.placeholder = promptExamples[exampleIndex % promptExamples.length];
            exampleIndex++;
        }
    });
});

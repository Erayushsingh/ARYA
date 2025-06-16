// JavaScript for the LLM Function Calling app

// App initialization and error handling
let appInitialized = false;

async function initializeApp() {
    // Initialize app with retry mechanism for cold starts
    if (appInitialized) return;
    
    try {
        console.log('🚀 Initializing ARYA app...');
        
        // Try to ping the server to wake it up if it's sleeping
        const startTime = Date.now();
        showLoadingMessage('Waking up server... This may take a moment on first visit.');
        
        // Attempt to warm up the server
        const warmupResponse = await fetch('/warmup', {
            method: 'GET',
            signal: AbortSignal.timeout(30000) // 30 second timeout
        });
        
        if (warmupResponse.ok) {
            const warmupData = await warmupResponse.json();
            console.log('✅ Server warmup complete:', warmupData);
            hideLoadingMessage();
        } else {
            console.warn('⚠️ Warmup request failed, continuing anyway...');
        }
        
        const initTime = Date.now() - startTime;
        console.log(`✅ App initialized in ${initTime}ms`);
        appInitialized = true;
        
    } catch (error) {
        console.error('❌ App initialization failed:', error);
        hideLoadingMessage();
        showErrorMessage('Server is starting up. Please wait a moment and refresh the page.');
    }
}

function showLoadingMessage(message) {
    const loadingDiv = document.createElement('div');
    loadingDiv.id = 'appLoadingMessage';
    loadingDiv.innerHTML = `
        <div style="
            position: fixed; 
            top: 0; 
            left: 0; 
            width: 100%; 
            height: 100%; 
            background: rgba(255,255,255,0.9); 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            z-index: 10000;
            backdrop-filter: blur(5px);
        ">            <div style="text-align: center; padding: 2rem; background: white; border-radius: 1rem; box-shadow: 0 10px 25px rgba(0,0,0,0.1);">
                <div style="font-size: 2rem; margin-bottom: 1rem;">🚀</div>
                <h3 style="margin: 0 0 1rem 0; color: #333;">ARYA</h3>
                <p style="margin: 0; color: #666;">${message}</p>
                <div style="margin-top: 1rem;">
                    <div class="loading-spinner" style="
                        border: 3px solid #f3f3f3;
                        border-top: 3px solid #4285f4;
                        border-radius: 50%;
                        width: 30px;
                        height: 30px;
                        animation: spin 1s linear infinite;
                        margin: 0 auto;
                    "></div>
                </div>
            </div>
        </div>
        <style>
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    `;
    document.body.appendChild(loadingDiv);
}

function hideLoadingMessage() {
    const loadingDiv = document.getElementById('appLoadingMessage');
    if (loadingDiv) {
        loadingDiv.remove();
    }
}

function showErrorMessage(message) {
    const errorDiv = document.createElement('div');
    errorDiv.innerHTML = `
        <div style="
            position: fixed; 
            top: 20px; 
            right: 20px; 
            background: #ff4444; 
            color: white; 
            padding: 1rem; 
            border-radius: 0.5rem; 
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 10001;
            max-width: 300px;
        ">
            <strong>⚠️ Notice:</strong><br>
            ${message}
            <button onclick="this.parentElement.remove()" style="
                background: none; 
                border: none; 
                color: white; 
                float: right; 
                cursor: pointer; 
                font-size: 1.2rem;
                margin-left: 10px;
            ">×</button>
        </div>
    `;
    document.body.appendChild(errorDiv);
    
    // Auto-remove after 10 seconds
    setTimeout(() => {
        if (errorDiv.parentElement) {
            errorDiv.remove();
        }
    }, 10000);
}

// Initialize app when page loads
document.addEventListener('DOMContentLoaded', async function () {
    // Initialize the app first
    await initializeApp();
    
    const form = document.getElementById('processForm');
    const fileInput = document.getElementById('files');
    const fileList = document.getElementById('fileList');
    const submitBtn = document.getElementById('submitBtn');
    const submitText = document.getElementById('submitText');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const results = document.getElementById('results');
    const resultContent = document.getElementById('resultContent');
    const dropZone = document.getElementById('dropZone');

    let selectedFiles = [];

    // Debug: Check if elements exist
    console.log('Elements found:');
    console.log('form:', form);
    console.log('fileInput:', fileInput);
    console.log('fileList:', fileList);
    console.log('dropZone:', dropZone);

    if (!fileInput || !fileList || !dropZone) {
        console.error('Required elements not found!');
        return;
    }

    // Handle file selection
    fileInput.addEventListener('change', function (e) {
        handleFiles(e.target.files);
    });

    // Handle drag and drop
    dropZone.addEventListener('dragover', function (e) {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });

    dropZone.addEventListener('dragleave', function (e) {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
    });

    dropZone.addEventListener('drop', function (e) {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        handleFiles(e.dataTransfer.files);
    }); function handleFiles(files) {
        console.log('Files selected:', files.length);
        // Add new files to selectedFiles array
        for (let file of files) {
            console.log('Processing file:', file.name, file.size, file.type);
            // Check if file is already selected
            if (!selectedFiles.find(f => f.name === file.name && f.size === file.size)) {
                selectedFiles.push(file);
                console.log('File added to selection:', file.name);
            } else {
                console.log('File already selected:', file.name);
            }
        }
        console.log('Total selected files:', selectedFiles.length);
        updateFileList();
    } function updateFileList() {
        console.log('Updating file list, selected files:', selectedFiles.length);
        // Force clear and reset the fileList container
        if (fileList) {
            fileList.innerHTML = '';
            fileList.style.display = 'block';
            fileList.style.visibility = 'visible';
            fileList.style.opacity = '1';
            fileList.style.height = 'auto';
            fileList.style.zIndex = '99999';
            fileList.style.position = 'relative';
            console.log('FileList container reset with z-index 99999');
        } else {
            console.error('FileList element not found!');
            return;
        }

        if (selectedFiles.length === 0) {
            console.log('No files selected, hiding file list');
            fileList.style.display = 'none';
            return;
        }

        // Add a header for the file list
        const header = document.createElement('div');
        header.className = 'file-list-header'; header.style.cssText = `
            margin-bottom: 1rem !important;
            display: flex !important;
            align-items: center !important;
            gap: 0.5rem !important;
            font-size: 1.125rem !important;
            font-weight: 600 !important;
            color: #1f2937 !important;
            padding: 0.5rem 0 !important;
            border-bottom: 1px solid #e5e7eb !important;
            z-index: 99996 !important;
            position: relative !important;
        `;
        header.innerHTML = `
            <i class="fas fa-paperclip" style="color: #3b82f6 !important; font-size: 1rem !important;"></i>
            <span>Selected Files (${selectedFiles.length})</span>
        `;
        fileList.appendChild(header);
        console.log('Header added to file list');

        selectedFiles.forEach((file, index) => {
            console.log('Creating file item for:', file.name);
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            // Force visibility with inline styles
            fileItem.style.cssText = `
                background: rgba(255, 255, 255, 0.95) !important;
                border: 2px solid #e5e7eb !important;
                border-radius: 1rem !important;
                padding: 1rem !important;
                margin: 0.75rem 0 !important;
                display: flex !important;
                justify-content: space-between !important;
                align-items: center !important;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
                transition: all 0.3s ease !important;
                opacity: 1 !important;
                visibility: visible !important;
                min-height: 60px !important;
                z-index: 99997 !important;
                position: relative !important;
            `;

            // Get file type icon
            const fileIcon = getFileIcon(file.name);

            fileItem.innerHTML = `
                <div style="display: flex !important; align-items: center !important; gap: 0.75rem !important; flex-grow: 1 !important;">
                    <div style="font-size: 1.5rem !important; min-width: 2rem !important;">${fileIcon}</div>
                    <div style="flex-grow: 1 !important; min-width: 0 !important;">
                        <div style="font-size: 0.875rem !important; color: #1f2937 !important; font-weight: 500 !important; word-break: break-all !important;">${file.name}</div>
                        <div style="font-size: 0.75rem !important; color: #6b7280 !important; margin-top: 0.25rem !important;">${formatFileSize(file.size)} • ${file.type || 'Unknown type'}</div>
                    </div>
                </div>
                <button type="button" style="
                    background: linear-gradient(135deg, #ef4444, #dc2626) !important;
                    color: white !important;
                    border: none !important;
                    border-radius: 0.5rem !important;
                    padding: 0.5rem 0.75rem !important;
                    font-size: 0.75rem !important;
                    font-weight: 500 !important;
                    cursor: pointer !important;
                    display: flex !important;
                    align-items: center !important;
                    gap: 0.25rem !important;
                    transition: all 0.2s ease !important;
                " onclick="removeFile(${index})" onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                    <i class="fas fa-times"></i>
                    <span>Remove</span>
                </button>
            `;

            fileList.appendChild(fileItem);
            console.log('File item added for:', file.name);
        });

        // Force a reflow to ensure rendering
        fileList.offsetHeight;
        console.log('File list updated, DOM elements created:', fileList.children.length);
        console.log('FileList final styles:', window.getComputedStyle(fileList).display, window.getComputedStyle(fileList).visibility);
    }// Make removeFile globally accessible
    window.removeFile = function (index) {
        console.log('Removing file at index:', index);
        selectedFiles.splice(index, 1);
        console.log('Files remaining:', selectedFiles.length);
        updateFileList();
    }; function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    function getFileIcon(filename) {
        const extension = filename.split('.').pop().toLowerCase();
        const iconMap = {
            // Images
            'jpg': '🖼️', 'jpeg': '🖼️', 'png': '🖼️', 'gif': '🖼️', 'bmp': '🖼️', 'tiff': '🖼️', 'webp': '🖼️',
            // Documents
            'pdf': '📄', 'doc': '📝', 'docx': '📝', 'txt': '📄', 'rtf': '📄',
            // Archives
            'zip': '📦', 'rar': '📦', '7z': '📦', 'tar': '📦', 'gz': '📦',
            // Audio
            'mp3': '🎵', 'wav': '🎵', 'flac': '🎵', 'aac': '🎵', 'm4a': '🎵', 'ogg': '🎵',
            // Video
            'mp4': '🎬', 'avi': '🎬', 'mov': '🎬', 'wmv': '🎬', 'mkv': '🎬',
            // Spreadsheets
            'xls': '📊', 'xlsx': '📊', 'csv': '📊',
            // Presentations
            'ppt': '📊', 'pptx': '📊'
        };
        return iconMap[extension] || '📄';
    }

    // Handle form submission
    form.addEventListener('submit', async function (e) {
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
    ];    // Add click handler for prompt placeholder
    const promptTextarea = document.getElementById('prompt');
    let exampleIndex = 0;

    promptTextarea.addEventListener('focus', function () {
        if (!this.value) {
            this.placeholder = promptExamples[exampleIndex % promptExamples.length];
            exampleIndex++;
        }
    });    // Speech Recognition functionality using Sarvam AI
    const microphoneBtn = document.getElementById('microphoneBtn');
    const micIcon = document.getElementById('micIcon');
    const micActiveIcon = document.getElementById('micActiveIcon');
    const speechStatus = document.getElementById('speechStatus');

    let mediaRecorder = null;
    let audioChunks = [];
    let isListening = false;
    let recordingStream = null;

    // Check if MediaRecorder is supported
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia && window.MediaRecorder) {

        // Add click handler for microphone button
        microphoneBtn.addEventListener('click', function () {
            if (isListening) {
                stopRecording();
            } else {
                startRecording();
            }
        }); async function startRecording() {
            try {
                // Request microphone access
                recordingStream = await navigator.mediaDevices.getUserMedia({
                    audio: {
                        sampleRate: 44100,
                        channelCount: 1,
                        volume: 1.0
                    }
                });                // Check for supported MIME types in order of preference for Sarvam AI
                const supportedTypes = [
                    'audio/wav',           // Best compatibility with Sarvam AI
                    'audio/wave',          // Alternative WAV format
                    'audio/mpeg',          // MP3 format
                    'audio/mp3',           // Another MP3 variant
                    'audio/webm;codecs=pcm', // WebM PCM (will be converted to WAV)
                    'audio/webm;codecs=opus', // WebM Opus (will be converted to WAV)
                    'audio/webm',          // Basic WebM (will be converted to WAV)
                    'audio/mp4',           // MP4/M4A as last resort
                ];

                let selectedMimeType = null;
                for (const type of supportedTypes) {
                    if (MediaRecorder.isTypeSupported(type)) {
                        selectedMimeType = type;
                        console.log('Selected audio format:', type);
                        break;
                    }
                }

                if (!selectedMimeType) {
                    throw new Error('No supported audio format found');
                }
                // Create MediaRecorder with supported format
                mediaRecorder = new MediaRecorder(recordingStream, {
                    mimeType: selectedMimeType
                });

                audioChunks = [];

                // Store the selected MIME type for later reference
                mediaRecorder.recordedMimeType = selectedMimeType;

                // Handle data available
                mediaRecorder.ondataavailable = function (event) {
                    if (event.data.size > 0) {
                        audioChunks.push(event.data);
                    }
                };

                // Handle recording stop
                mediaRecorder.onstop = function () {
                    processAudioWithSarvam();
                };

                // Start recording
                mediaRecorder.start();
                isListening = true;
                // Update UI for recording state
                micIcon.classList.add('hidden');
                micActiveIcon.classList.remove('hidden');
                speechStatus.classList.remove('hidden');
                speechStatus.textContent = 'Listening... (Sarvam AI)';
                microphoneBtn.classList.add('recording');
                microphoneBtn.title = 'Recording... Click to stop';

                console.log('Started recording with format:', selectedMimeType);

            } catch (error) {
                console.error('Failed to start recording:', error);
                let errorMessage = 'Microphone access denied. Please enable microphone permissions.';
                if (error.name === 'NotAllowedError') {
                    errorMessage = 'Microphone access denied. Please enable microphone permissions and reload the page.';
                } else if (error.name === 'NotFoundError') {
                    errorMessage = 'No microphone found. Please connect a microphone.';
                }
                alert(errorMessage);
                resetMicrophoneUI();
            }
        }

        function stopRecording() {
            if (mediaRecorder && mediaRecorder.state !== 'inactive') {
                mediaRecorder.stop();

                // Stop all tracks
                if (recordingStream) {
                    recordingStream.getTracks().forEach(track => track.stop());
                }

                // Update UI to show processing
                speechStatus.textContent = 'Processing audio...';
                microphoneBtn.title = 'Processing...';
            }
        } async function processAudioWithSarvam() {
            try {
                // Create audio blob with the recorded MIME type
                let audioBlob = new Blob(audioChunks, { type: mediaRecorder.recordedMimeType || mediaRecorder.mimeType });
                let fileExtension = '.wav'; // Default
                const mimeType = mediaRecorder.recordedMimeType || mediaRecorder.mimeType;

                console.log('Processing audio with MIME type:', mimeType);

                // Handle format conversion if needed
                if (mimeType.includes('wav')) {
                    fileExtension = '.wav';
                } else if (mimeType.includes('mp4') || mimeType.includes('m4a')) {
                    fileExtension = '.m4a';
                } else if (mimeType.includes('mpeg') || mimeType.includes('mp3')) {
                    fileExtension = '.mp3';
                } else if (mimeType.includes('webm')) {
                    // Try to convert WebM to WAV for better compatibility
                    speechStatus.textContent = 'Converting audio format...';
                    try {
                        audioBlob = await convertWebMToWAV(audioBlob);
                        fileExtension = '.wav';
                        console.log('Successfully converted WebM to WAV');
                    } catch (conversionError) {
                        console.log('Conversion failed, using WebM:', conversionError);
                        fileExtension = '.webm';
                    }
                }

                // Create FormData for upload
                const formData = new FormData();
                formData.append('audio', audioBlob, `recording${fileExtension}`);
                formData.append('language', 'auto'); // Auto-detect language
                formData.append('model', 'saarika:v2');

                // Update status
                speechStatus.textContent = 'Transcribing with Sarvam AI...';

                console.log('Sending audio with format:', fileExtension, 'Size:', audioBlob.size, 'bytes');

                // Send to Sarvam AI endpoint
                const response = await fetch('/api/sarvam-speech-to-text', {
                    method: 'POST',
                    body: formData
                });
                const result = await response.json();

                // Debug: Log the actual response
                console.log('Raw Sarvam AI response:', result);
                if (result.success) {
                    // Handle different possible response formats
                    const transcript = result.transcribed_text || result.transcript || result.text || result.transcription || '';
                    const detectedLanguage = result.language || result.detected_language || result.detected_lang || 'Unknown';
                    const detectedScript = result.detected_script || 'Unknown';
                    const confidence = result.confidence || 0;

                    if (!transcript) {
                        console.error('No transcript found in response:', result);
                        throw new Error('No transcript in response');
                    }

                    // Add the transcript to the textarea
                    if (promptTextarea.value.trim()) {
                        promptTextarea.value += ' ' + transcript;
                    } else {
                        promptTextarea.value = transcript;
                    }

                    // Trigger input event
                    promptTextarea.dispatchEvent(new Event('input', { bubbles: true }));

                    // Show success message with detected language and script
                    const statusMessage = `✓ ${detectedLanguage} (${detectedScript}) - ${(confidence * 100).toFixed(0)}% confidence`;
                    speechStatus.textContent = statusMessage;
                    speechStatus.classList.add('text-green-500');

                    console.log('🎉 Sarvam AI transcription successful!');
                    console.log('📝 Native script transcript:', transcript);
                    console.log('🌐 Detected language:', detectedLanguage);
                    console.log('📜 Detected script:', detectedScript);
                    console.log('🎯 Confidence:', confidence);

                    setTimeout(() => {
                        resetMicrophoneUI();
                    }, 4000); // Show success message longer

                } else {
                    console.error('Sarvam AI response error:', result);
                    throw new Error(result.error || result.message || 'Transcription failed');
                }

            } catch (error) {
                console.error('Sarvam AI transcription error:', error);

                // Show error message
                speechStatus.textContent = 'Transcription failed. Please try again.';
                speechStatus.classList.add('text-red-500');

                setTimeout(() => {
                    resetMicrophoneUI();
                }, 3000);
            }
        }
        function resetMicrophoneUI() {
            isListening = false;
            micIcon.classList.remove('hidden');
            micActiveIcon.classList.add('hidden');
            speechStatus.classList.add('hidden');
            speechStatus.classList.remove('text-red-500', 'text-green-500');
            speechStatus.textContent = 'Listening...';
            microphoneBtn.classList.remove('recording');
            microphoneBtn.title = 'Click to speak your request (Sarvam AI)';
        }

        // Add keyboard shortcut (Ctrl/Cmd + M) for microphone
        document.addEventListener('keydown', function (e) {
            if ((e.ctrlKey || e.metaKey) && e.key === 'm') {
                e.preventDefault();
                microphoneBtn.click();
            }
        });

    } else {
        // MediaRecorder not supported
        microphoneBtn.addEventListener('click', function () {
            alert('Audio recording is not supported in this browser. Please use Chrome, Firefox, or Safari for voice input.');
        });
        microphoneBtn.classList.add('opacity-50', 'cursor-not-allowed');
        microphoneBtn.title = 'Voice input not supported in this browser';
    }// Google Translate Enhancement Functions
    initializeGoogleTranslate();
    initializeLanguageDropdown();
});

// Language Dropdown Initialization
function initializeLanguageDropdown() {
    const languageDropdown = document.getElementById('languageDropdown');

    if (languageDropdown) {
        // Load saved language preference
        const savedLanguage = localStorage.getItem('selectedLanguage') || 'en';
        languageDropdown.value = savedLanguage;

        // Handle language change
        languageDropdown.addEventListener('change', function (e) {
            const selectedLang = e.target.value;
            changeLanguage(selectedLang);

            // Save language preference
            localStorage.setItem('selectedLanguage', selectedLang);

            // Add visual feedback
            showLanguageChangeStatus(selectedLang);
        });

        // Set initial language if not English
        if (savedLanguage !== 'en') {
            setTimeout(() => changeLanguage(savedLanguage), 1000);
        }
    }
}

function showLanguageChangeStatus(langCode) {
    // Get language name from dropdown
    const dropdown = document.getElementById('languageDropdown');
    const selectedOption = dropdown.querySelector(`option[value="${langCode}"]`);
    const languageName = selectedOption ? selectedOption.textContent : langCode.toUpperCase();

    // Show indicator
    showLanguageIndicator();

    // Show status message
    showTranslationStatus(`Changing to ${languageName}...`, 'info');

    // Hide status after translation completes
    setTimeout(() => {
        hideLanguageIndicator();
        showTranslationStatus(`Language changed to ${languageName}`, 'success');
        setTimeout(() => hideTranslationStatus(), 2000);
    }, 1500);
}

// Google Translate Enhancement Functions
function initializeGoogleTranslate() {
    // Wait for Google Translate to load
    const checkTranslateLoaded = setInterval(() => {
        if (window.google && window.google.translate) {
            clearInterval(checkTranslateLoaded);
            enhanceGoogleTranslate();
        }
    }, 100);
}

function enhanceGoogleTranslate() {
    // Hide the Google Translate banner that appears at the top
    const style = document.createElement('style');
    style.textContent = `
        .goog-te-banner-frame { display: none !important; }
        body { top: 0 !important; }
        .skiptranslate { display: none !important; }
    `;
    document.head.appendChild(style);

    // Add translation status indicator
    monitorTranslationState();

    // Add custom language shortcuts
    addLanguageShortcuts();

    // Monitor language changes for UI translation
    monitorLanguageChanges();
}

function monitorLanguageChanges() {
    // Watch for changes in the Google Translate dropdown
    const checkForSelect = setInterval(() => {
        const selectElement = document.querySelector('.goog-te-combo');
        if (selectElement) {
            clearInterval(checkForSelect);

            selectElement.addEventListener('change', function (e) {
                const selectedLanguage = e.target.value;
                currentLanguage = selectedLanguage;

                // Trigger Sarvam AI translation for UI elements
                if (selectedLanguage && selectedLanguage !== 'en') {
                    setTimeout(() => {
                        translateUIElements(selectedLanguage);
                    }, 1000); // Wait for Google Translate to finish
                }
            });
        }
    }, 100);
}

function monitorTranslationState() {
    // Monitor when translation starts/ends
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                const body = document.body;
                if (body.classList.contains('translated-rtl') || body.classList.contains('translated-ltr')) {
                    onTranslationStart();
                } else {
                    onTranslationEnd();
                }
            }
        });
    });

    observer.observe(document.body, {
        attributes: true,
        attributeFilter: ['class']
    });
}

function onTranslationStart() {
    console.log('Translation started');
    document.body.classList.add('translating');

    // Show a subtle loading indicator
    showTranslationStatus('Translating page...', 'info');
}

function onTranslationEnd() {
    console.log('Translation completed');
    document.body.classList.remove('translating');

    // Show completion message briefly
    showTranslationStatus('Translation complete!', 'success');
    setTimeout(() => hideTranslationStatus(), 2000);
}

function showTranslationStatus(message, type = 'info') {
    // Remove existing status
    const existing = document.getElementById('translation-status');
    if (existing) existing.remove();

    // Create status element
    const status = document.createElement('div');
    status.id = 'translation-status';
    status.className = `fixed top-4 right-4 px-4 py-2 rounded-md shadow-lg z-50 text-sm font-medium transition-all duration-300 ${type === 'success' ? 'bg-green-500 text-white' :
        type === 'error' ? 'bg-red-500 text-white' :
            'bg-blue-500 text-white'
        }`;
    status.textContent = message;

    document.body.appendChild(status);
}

function hideTranslationStatus() {
    const status = document.getElementById('translation-status');
    if (status) {
        status.style.opacity = '0';
        setTimeout(() => status.remove(), 300);
    }
}

function addLanguageShortcuts() {
    // Common language shortcuts for Indian users
    const languageShortcuts = [
        { code: 'hi', name: 'हिंदी (Hindi)', flag: '🇮🇳' },
        { code: 'gu', name: 'ગુજરાતી (Gujarati)', flag: '🇮🇳' },
        { code: 'ta', name: 'தமிழ் (Tamil)', flag: '🇮🇳' },
        { code: 'te', name: 'తెలుగు (Telugu)', flag: '🇮🇳' },
        { code: 'bn', name: 'বাংলা (Bengali)', flag: '🇮🇳' },
        { code: 'mr', name: 'मराठी (Marathi)', flag: '🇮🇳' },
        { code: 'pa', name: 'ਪੰਜਾਬੀ (Punjabi)', flag: '🇮🇳' },
        { code: 'kn', name: 'ಕನ್ನಡ (Kannada)', flag: '🇮🇳' },
        { code: 'ml', name: 'മലയാളം (Malayalam)', flag: '🇮🇳' },
        { code: 'or', name: 'ଓଡ଼ିଆ (Odia)', flag: '🇮🇳' },
        { code: 'as', name: 'অসমীয়া (Assamese)', flag: '🇮🇳' },
        { code: 'en', name: 'English', flag: '🇺🇸' }
    ];    // Add keyboard shortcuts for quick language switching
    document.addEventListener('keydown', (e) => {
        // Alt + L for language dropdown
        if (e.altKey && e.key === 'l') {
            e.preventDefault();
            const languageDropdown = document.getElementById('languageDropdown');
            if (languageDropdown) {
                languageDropdown.focus();
                languageDropdown.click();
            }
        }

        // Alt + Number keys for quick language selection
        if (e.altKey && e.key >= '1' && e.key <= '9') {
            e.preventDefault();
            const quickLanguages = ['en', 'hi', 'gu', 'ta', 'te', 'bn', 'mr', 'pa', 'kn'];
            const langIndex = parseInt(e.key) - 1;
            if (langIndex < quickLanguages.length) {
                const langCode = quickLanguages[langIndex];
                changeLanguage(langCode);

                // Update dropdown
                const dropdown = document.getElementById('languageDropdown');
                if (dropdown) {
                    dropdown.value = langCode;
                }
            }
        }
    });
}

// Function to programmatically change language
function changeLanguage(langCode) {
    // First try to change via Google Translate element
    const selectElement = document.querySelector('.goog-te-combo');
    if (selectElement) {
        selectElement.value = langCode;
        selectElement.dispatchEvent(new Event('change'));

        // Update current language and trigger Sarvam AI translation
        currentLanguage = langCode;
        if (langCode && langCode !== 'en') {
            setTimeout(() => {
                translateUIElements(langCode);
            }, 1500); // Wait for Google Translate to finish
        }
    } else {
        // If Google Translate isn't ready, wait and try again
        setTimeout(() => {
            const retrySelectElement = document.querySelector('.goog-te-combo');
            if (retrySelectElement) {
                retrySelectElement.value = langCode;
                retrySelectElement.dispatchEvent(new Event('change'));

                // Update current language and trigger Sarvam AI translation
                currentLanguage = langCode;
                if (langCode && langCode !== 'en') {
                    setTimeout(() => {
                        translateUIElements(langCode);
                    }, 1500);
                }
            }
        }, 500);
    }

    // Update our custom dropdown to match
    const customDropdown = document.getElementById('languageDropdown');
    if (customDropdown && customDropdown.value !== langCode) {
        customDropdown.value = langCode;
    }
}

// Add helpful tooltip for users
function addTranslationTooltip() {
    const translateElement = document.getElementById('google_translate_element');
    if (translateElement) {
        translateElement.title = 'Select your language / अपनी भाषा चुनें / તમારી ભાષા પસંદ કરો';
    }

    // Add tooltip to custom dropdown
    const languageDropdown = document.getElementById('languageDropdown');
    if (languageDropdown) {
        languageDropdown.title = 'Select your preferred language - Alt+L to open | Alt+1-9 for quick selection';
    }
}

// Add language change indicator
function addLanguageIndicator() {
    const header = document.querySelector('.flex.justify-between.items-center.mb-4');
    if (header) {
        const indicator = document.createElement('div');
        indicator.id = 'language-indicator';
        indicator.className = 'language-indicator hidden';
        indicator.title = 'Language is being changed';

        const languageSection = header.querySelector('.flex.items-center.space-x-2');
        if (languageSection) {
            languageSection.appendChild(indicator);
        }
    }
}

// Show/hide language indicator
function showLanguageIndicator() {
    const indicator = document.getElementById('language-indicator');
    if (indicator) {
        indicator.classList.remove('hidden');
    }
}

function hideLanguageIndicator() {
    const indicator = document.getElementById('language-indicator');
    if (indicator) {
        indicator.classList.add('hidden');
    }
}

// Initialize tooltip when page loads
setTimeout(() => {
    addTranslationTooltip();
    addLanguageIndicator();
}, 1000);    // UI Text Translation with Sarvam AI
const uiTexts = {
    'prompt_placeholder': 'What would you like to do? Try: "Convert this image to PDF", "Compress these images", "Extract text from this image", "Convert Word to PDF", "Speak this text in Hindi", or "Transcribe this audio"',
    'upload_title': 'Upload Files',
    'upload_description': 'Click to upload files',
    'upload_subtitle': 'or drag and drop',
    'upload_formats': 'Supports: Images (JPG, PNG, etc.), Word documents (.docx), Audio files (WAV, MP3, M4A, FLAC, AAC), and ZIP files',
    'submit_button': 'Process Files',
    'processing_text': 'Processing...',
    'speech_status': 'Listening...',
    'feature_stt_title': '🎤 Speech to Text',
    'feature_stt_desc': 'Convert audio to text in 12+ Indian languages',
    'feature_tts_title': '🔊 Text to Speech',
    'feature_tts_desc': 'Convert text to natural-sounding speech',
    'feature_image_title': '🖼️ Image Processing',
    'feature_image_desc': 'Compress, convert, and manipulate images',
    'feature_doc_title': '📄 Document Processing',
    'feature_doc_desc': 'Convert Word to PDF and extract text'
};

let currentLanguage = 'en';
let translationCache = {};

async function translateUIElements(targetLanguage) {
    if (targetLanguage === 'en' || targetLanguage === currentLanguage) {
        return; // No translation needed for English or same language
    }

    // Check cache first
    const cacheKey = targetLanguage;
    if (translationCache[cacheKey]) {
        applyTranslations(translationCache[cacheKey]);
        return;
    }

    try {
        showTranslationStatus('Translating interface...', 'info');

        // Get Sarvam AI language code
        const sarvamLanguageCode = getSarvamLanguageCode(targetLanguage);

        // Call our translation API
        const response = await fetch('/api/translate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                texts: uiTexts,
                source_language: 'en-IN',
                target_language: sarvamLanguageCode
            })
        });

        const result = await response.json();

        if (result.success) {
            // Cache the translations
            translationCache[cacheKey] = result.translations;

            // Apply translations to UI
            applyTranslations(result.translations);

            showTranslationStatus('Interface translated!', 'success');
            setTimeout(() => hideTranslationStatus(), 2000);
        } else {
            console.log('Translation failed:', result.error);
            showTranslationStatus('Translation unavailable', 'error');
            setTimeout(() => hideTranslationStatus(), 3000);
        }

    } catch (error) {
        console.error('Translation error:', error);
        showTranslationStatus('Translation error', 'error');
        setTimeout(() => hideTranslationStatus(), 3000);
    }
}

function getSarvamLanguageCode(googleTranslateCode) {
    const mapping = {
        'hi': 'hi-IN',
        'gu': 'gu-IN',
        'pa': 'pa-IN',
        'mr': 'mr-IN',
        'bn': 'bn-IN',
        'ta': 'ta-IN',
        'te': 'te-IN',
        'kn': 'kn-IN',
        'ml': 'ml-IN',
        'or': 'or-IN',
        'as': 'as-IN',
        'en': 'en-IN'
    };
    return mapping[googleTranslateCode] || 'hi-IN';
}

function applyTranslations(translations) {
    // Update placeholder text
    const promptInput = document.getElementById('prompt');
    if (promptInput && translations['prompt_placeholder']) {
        promptInput.placeholder = translations['prompt_placeholder'];
    }

    // Update upload section
    const uploadTitle = document.querySelector('label[for="files"]');
    if (uploadTitle && translations['upload_title']) {
        uploadTitle.textContent = translations['upload_title'];
    }

    // Update upload description
    const uploadDesc = document.querySelector('.text-lg.font-medium');
    if (uploadDesc && translations['upload_description']) {
        uploadDesc.textContent = translations['upload_description'];
    }

    // Update upload subtitle
    const uploadSubtitle = document.querySelector('.text-sm');
    if (uploadSubtitle && translations['upload_subtitle']) {
        uploadSubtitle.textContent = translations['upload_subtitle'];
    }

    // Update submit button
    const submitText = document.getElementById('submitText');
    if (submitText && translations['submit_button']) {
        submitText.textContent = translations['submit_button'];
    }

    // Update feature cards
    updateFeatureCards(translations);
}

function updateFeatureCards(translations) {
    const featureCards = document.querySelectorAll('.feature-card');

    featureCards.forEach((card, index) => {
        const title = card.querySelector('h3');
        const desc = card.querySelector('p');

        if (index === 0 && translations['feature_stt_title']) {
            if (title) title.textContent = translations['feature_stt_title'];
            if (desc) desc.textContent = translations['feature_stt_desc'];
        } else if (index === 1 && translations['feature_tts_title']) {
            if (title) title.textContent = translations['feature_tts_title'];
            if (desc) desc.textContent = translations['feature_tts_desc'];
        } else if (index === 2 && translations['feature_image_title']) {
            if (title) title.textContent = translations['feature_image_title'];
            if (desc) desc.textContent = translations['feature_image_desc'];
        } else if (index === 3 && translations['feature_doc_title']) {
            if (title) title.textContent = translations['feature_doc_title'];
            if (desc) desc.textContent = translations['feature_doc_desc'];
        }
    });
}

// Convert WebM audio to WAV format using Web Audio API
async function convertWebMToWAV(webmBlob) {
    try {
        console.log('Converting WebM to WAV...');

        // Create audio context
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();

        // Convert blob to array buffer
        const arrayBuffer = await webmBlob.arrayBuffer();

        // Decode audio data
        const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

        console.log('Audio decoded:', {
            channels: audioBuffer.numberOfChannels,
            sampleRate: audioBuffer.sampleRate,
            duration: audioBuffer.duration
        });

        // Convert to WAV
        const wavArrayBuffer = audioBufferToWav(audioBuffer);

        // Create WAV blob
        const wavBlob = new Blob([wavArrayBuffer], { type: 'audio/wav' });

        console.log('Conversion successful. WAV size:', wavBlob.size, 'bytes');
        return wavBlob;

    } catch (error) {
        console.error('WebM to WAV conversion failed:', error);
        throw error;
    }
}

// Convert AudioBuffer to WAV format
function audioBufferToWav(buffer) {
    const numberOfChannels = Math.min(buffer.numberOfChannels, 2); // Limit to stereo
    const sampleRate = buffer.sampleRate;
    const format = 1; // PCM
    const bitDepth = 16;

    const bytesPerSample = bitDepth / 8;
    const blockAlign = numberOfChannels * bytesPerSample;
    const byteRate = sampleRate * blockAlign;
    const dataSize = buffer.length * blockAlign;
    const bufferLength = 44 + dataSize;

    const arrayBuffer = new ArrayBuffer(bufferLength);
    const view = new DataView(arrayBuffer);

    // WAV header
    const writeString = (offset, string) => {
        for (let i = 0; i < string.length; i++) {
            view.setUint8(offset + i, string.charCodeAt(i));
        }
    };

    // RIFF chunk descriptor
    writeString(0, 'RIFF');
    view.setUint32(4, bufferLength - 8, true);
    writeString(8, 'WAVE');

    // FMT sub-chunk
    writeString(12, 'fmt ');
    view.setUint32(16, 16, true); // Subchunk1Size
    view.setUint16(20, format, true); // AudioFormat (PCM)
    view.setUint16(22, numberOfChannels, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, byteRate, true);
    view.setUint16(32, blockAlign, true);
    view.setUint16(34, bitDepth, true);

    // Data sub-chunk
    writeString(36, 'data');
    view.setUint32(40, dataSize, true);

    // Convert float samples to 16-bit PCM
    let offset = 44;
    for (let i = 0; i < buffer.length; i++) {
        for (let channel = 0; channel < numberOfChannels; channel++) {
            const channelData = buffer.getChannelData(channel);
            let sample = Math.max(-1, Math.min(1, channelData[i])); // Clamp to [-1, 1]

            // Convert to 16-bit PCM
            const intSample = sample < 0 ? sample * 32768 : sample * 32767;
            view.setInt16(offset, intSample, true);
            offset += 2;
        }
    }

    return arrayBuffer;
}

// Test function to debug file list rendering
window.testFileList = function () {
    console.log('Testing file list rendering...');
    const testFile = new File(['test'], 'test.txt', { type: 'text/plain' });
    selectedFiles = [testFile];
    updateFileList();
};

// Also add this to global scope for debugging
window.debugFileList = function () {
    console.log('FileList element:', fileList);
    console.log('FileList display:', fileList ? window.getComputedStyle(fileList).display : 'Element not found');
    console.log('FileList visibility:', fileList ? window.getComputedStyle(fileList).visibility : 'Element not found');
    console.log('FileList children:', fileList ? fileList.children.length : 'Element not found');
    console.log('Selected files:', selectedFiles.length);
};

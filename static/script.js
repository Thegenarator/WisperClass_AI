// Global variables
let currentVideoId = null;
let currentQuiz = null;
let currentFlashcards = null;
let currentFlashcardIndex = 0;
let quizResults = [];
let authToken = localStorage.getItem('authToken');
let currentUser = JSON.parse(localStorage.getItem('currentUser'));

// DOM elements
const tabBtns = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');
const fileUploadArea = document.getElementById('fileUploadArea');
const videoFileInput = document.getElementById('videoFile');
const videoUrlInput = document.getElementById('videoUrl');
const processUrlBtn = document.getElementById('processUrl');
const uploadProgress = document.getElementById('uploadProgress');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const uploadResult = document.getElementById('uploadResult');
const resultMessage = document.getElementById('resultMessage');
const viewStudyMaterialsBtn = document.getElementById('viewStudyMaterials');
const videoLibrary = document.getElementById('videoLibrary');
const studyContent = document.getElementById('studyContent');
const noVideoSelected = document.getElementById('noVideoSelected');
const studyVideoTitle = document.getElementById('studyVideoTitle');
const studyModeBtns = document.querySelectorAll('.study-mode-btn');
const studyModeContents = document.querySelectorAll('.study-mode-content');
const summaryContent = document.getElementById('summaryContent');
const quizContent = document.getElementById('quizContent');
const flashcardsContent = document.getElementById('flashcardsContent');
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const sendMessageBtn = document.getElementById('sendMessage');
const loadingOverlay = document.getElementById('loadingOverlay');

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    initializeAuth();
    initializeTabs();
    initializeFileUpload();
    initializeUrlProcessing();
    initializeStudyModes();
    initializeChat();
    
    if (authToken) {
        loadVideoLibrary();
        updateAuthUI();
    } else {
        showAuthOverlay();
    }
});

// Authentication functionality
function initializeAuth() {
    const loginBtn = document.getElementById('loginBtn');
    const signupBtn = document.getElementById('signupBtn');
    const logoutBtn = document.getElementById('logoutBtn');
    const authModal = document.getElementById('authModal');
    const authOverlay = document.getElementById('authOverlay');
    const authForm = document.getElementById('authFormElement');
    const authTitle = document.getElementById('authTitle');
    const authSubmitBtn = document.getElementById('authSubmitBtn');
    const authSwitchText = document.getElementById('authSwitchText');
    const authSwitchLink = document.getElementById('authSwitchLink');
    const closeModal = document.querySelector('.close');
    const promptLoginBtn = document.getElementById('promptLoginBtn');
    
    let isLoginMode = true;
    
    // Event listeners
    loginBtn?.addEventListener('click', () => showAuthModal(true));
    signupBtn?.addEventListener('click', () => showAuthModal(false));
    promptLoginBtn?.addEventListener('click', () => showAuthModal(true));
    logoutBtn?.addEventListener('click', handleLogout);
    closeModal?.addEventListener('click', hideAuthModal);
    authSwitchLink?.addEventListener('click', (e) => {
        e.preventDefault();
        toggleAuthMode();
    });
    
    authForm?.addEventListener('submit', handleAuthSubmit);
    
    // Modal click outside to close
    authModal?.addEventListener('click', (e) => {
        if (e.target === authModal) {
            hideAuthModal();
        }
    });
    
    function showAuthModal(loginMode = true) {
        isLoginMode = loginMode;
        updateAuthModal();
        authModal.style.display = 'flex';
        authOverlay.style.display = 'none';
    }
    
    function hideAuthModal() {
        authModal.style.display = 'none';
    }
    
    function toggleAuthMode() {
        isLoginMode = !isLoginMode;
        updateAuthModal();
    }
    
    function updateAuthModal() {
        if (isLoginMode) {
            authTitle.textContent = 'Login';
            authSubmitBtn.textContent = 'Login';
            authSwitchText.textContent = "Don't have an account?";
            authSwitchLink.textContent = 'Sign up';
        } else {
            authTitle.textContent = 'Sign Up';
            authSubmitBtn.textContent = 'Sign Up';
            authSwitchText.textContent = 'Already have an account?';
            authSwitchLink.textContent = 'Login';
        }
    }
    
    async function handleAuthSubmit(e) {
        e.preventDefault();
        
        const email = document.getElementById('authEmail').value;
        const password = document.getElementById('authPassword').value;
        
        if (!email || !password) {
            showNotification('Please fill in all fields', 'error');
            return;
        }
        
        const endpoint = isLoginMode ? '/api/auth/login' : '/api/auth/signup';
        
        try {
            authSubmitBtn.disabled = true;
            authSubmitBtn.textContent = 'Processing...';
            
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password }),
            });
            
            const data = await response.json();
            
            if (data.success) {
                authToken = data.token;
                currentUser = data.user;
                
                localStorage.setItem('authToken', authToken);
                localStorage.setItem('currentUser', JSON.stringify(currentUser));
                
                hideAuthModal();
                updateAuthUI();
                loadVideoLibrary();
                showNotification(data.message, 'success');
            } else {
                showNotification(data.error || 'Authentication failed', 'error');
            }
        } catch (error) {
            console.error('Auth error:', error);
            showNotification('Network error. Please try again.', 'error');
        } finally {
            authSubmitBtn.disabled = false;
            authSubmitBtn.textContent = isLoginMode ? 'Login' : 'Sign Up';
        }
    }
    
    function handleLogout() {
        authToken = null;
        currentUser = null;
        localStorage.removeItem('authToken');
        localStorage.removeItem('currentUser');
        
        updateAuthUI();
        showAuthOverlay();
        showNotification('Logged out successfully', 'success');
    }
}

function updateAuthUI() {
    const authButtons = document.getElementById('authButtons');
    const userInfo = document.getElementById('userInfo');
    const userEmail = document.getElementById('userEmail');
    
    if (authToken && currentUser) {
        authButtons.style.display = 'none';
        userInfo.style.display = 'flex';
        userEmail.textContent = currentUser.email;
    } else {
        authButtons.style.display = 'flex';
        userInfo.style.display = 'none';
    }
}

function showAuthOverlay() {
    const authOverlay = document.getElementById('authOverlay');
    authOverlay.style.display = 'flex';
}

function hideAuthOverlay() {
    const authOverlay = document.getElementById('authOverlay');
    authOverlay.style.display = 'none';
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Add to document
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Helper function to make authenticated API calls
async function makeAuthenticatedRequest(url, options = {}) {
    if (!authToken) {
        showAuthOverlay();
        throw new Error('Authentication required');
    }
    
    const headers = {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    const response = await fetch(url, {
        ...options,
        headers
    });
    
    if (response.status === 401) {
        // Token expired or invalid
        authToken = null;
        currentUser = null;
        localStorage.removeItem('authToken');
        localStorage.removeItem('currentUser');
        updateAuthUI();
        showAuthOverlay();
        throw new Error('Authentication expired');
    }
    
    return response;
}

// Tab functionality
function initializeTabs() {
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.dataset.tab;
            
            // Update tab buttons
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Update tab content
            tabContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === tabId) {
                    content.classList.add('active');
                }
            });
            
            // Load library when switching to library tab
            if (tabId === 'library') {
                loadVideoLibrary();
            }
        });
    });
}

// File upload functionality
function initializeFileUpload() {
    fileUploadArea.addEventListener('click', () => {
        videoFileInput.click();
    });
    
    fileUploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        fileUploadArea.style.borderColor = '#764ba2';
    });
    
    fileUploadArea.addEventListener('dragleave', () => {
        fileUploadArea.style.borderColor = '#667eea';
    });
    
    fileUploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        fileUploadArea.style.borderColor = '#667eea';
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            videoFileInput.files = files;
            handleFileUpload(files[0]);
        }
    });
    
    videoFileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });
    
    viewStudyMaterialsBtn.addEventListener('click', () => {
        if (currentVideoId) {
            loadStudyMaterials(currentVideoId);
            switchToStudyTab();
        }
    });
}

// URL processing functionality
function initializeUrlProcessing() {
    processUrlBtn.addEventListener('click', handleUrlProcessing);
    
    videoUrlInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleUrlProcessing();
        }
    });
}

// Study modes functionality
function initializeStudyModes() {
    studyModeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const mode = btn.dataset.mode;
            
            // Update study mode buttons
            studyModeBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Update study mode content
            studyModeContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === mode + 'Mode') {
                    content.classList.add('active');
                }
            });
            
            // Load mode-specific content
            if (currentVideoId) {
                switch(mode) {
                    case 'quiz':
                        loadQuiz();
                        break;
                    case 'flashcards':
                        loadFlashcards();
                        break;
                }
            }
        });
    });
}

// Chat functionality
function initializeChat() {
    sendMessageBtn.addEventListener('click', sendChatMessage);
    
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendChatMessage();
        }
    });
}

// File upload handler
async function handleFileUpload(file) {
    if (!file.type.startsWith('video/')) {
        showNotification('Please select a valid video file.', 'error');
        return;
    }
    
    if (!authToken) {
        showAuthOverlay();
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    showProgress('Uploading video...');
    
    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
            },
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            currentVideoId = result.video_id;
            updateProgress(50, 'Processing video...');
            
            // Process the uploaded video
            await processVideo(currentVideoId);
        } else {
            throw new Error(result.error || 'Upload failed');
        }
    } catch (error) {
        hideProgress();
        alert('Error uploading video: ' + error.message);
    }
}

// URL processing handler
async function handleUrlProcessing() {
    const url = videoUrlInput.value.trim();
    
    if (!url) {
        alert('Please enter a video URL.');
        return;
    }
    
    if (!url.includes('youtube.com') && !url.includes('youtu.be')) {
        alert('Currently only YouTube URLs are supported.');
        return;
    }
    
    showProgress('Downloading video from URL...');
    
    try {
        const response = await fetch('/api/process-url', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url })
        });
        
        const result = await response.json();
        
        if (result.success) {
            currentVideoId = result.video_id;
            updateProgress(50, 'Processing video...');
            
            // Process the video
            await processVideo(currentVideoId);
        } else {
            throw new Error(result.error || 'URL processing failed');
        }
    } catch (error) {
        hideProgress();
        alert('Error processing URL: ' + error.message);
    }
}

// Process video (transcription, summary, etc.)
async function processVideo(videoId) {
    try {
        showLoadingOverlay();
        
        const response = await fetch(`/api/process/${videoId}`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            updateProgress(100, 'Complete!');
            
            setTimeout(() => {
                hideProgress();
                hideLoadingOverlay();
                showUploadResult('Video processed successfully! Your AI tutor is ready.');
                loadVideoLibrary(); // Refresh library
            }, 1000);
        } else {
            throw new Error(result.error || 'Processing failed');
        }
    } catch (error) {
        hideProgress();
        hideLoadingOverlay();
        alert('Error processing video: ' + error.message);
    }
}

// Load video library
async function loadVideoLibrary() {
    try {
        const response = await fetch('/api/videos');
        const videos = await response.json();
        
        if (Array.isArray(videos)) {
            displayVideoLibrary(videos);
        } else {
            throw new Error('Failed to load videos');
        }
    } catch (error) {
        console.error('Error loading video library:', error);
        videoLibrary.innerHTML = '<div class="loading"><p>Error loading videos</p></div>';
    }
}

// Display video library
function displayVideoLibrary(videos) {
    if (videos.length === 0) {
        videoLibrary.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-video"></i>
                <h3>No videos yet</h3>
                <p>Upload your first video to get started!</p>
            </div>
        `;
        return;
    }
    
    videoLibrary.innerHTML = videos.map(video => `
        <div class="video-card" onclick="selectVideo(${video.id})">
            <h3>${video.title}</h3>
            <p>${video.summary || 'Processing...'}</p>
            <div class="video-date">${new Date(video.created_at).toLocaleDateString()}</div>
        </div>
    `).join('');
}

// Select video from library
async function selectVideo(videoId) {
    currentVideoId = videoId;
    await loadStudyMaterials(videoId);
    switchToStudyTab();
}

// Load study materials for a video
async function loadStudyMaterials(videoId) {
    try {
        const response = await fetch(`/api/video/${videoId}`);
        const video = await response.json();
        
        if (video.id) {
            studyVideoTitle.textContent = video.title;
            
            // Load summary
            summaryContent.innerHTML = `
                <div class="content-box">
                    <h3><i class="fas fa-file-alt"></i> Video Summary</h3>
                    <p>${video.summary || 'Summary not available'}</p>
                </div>
            `;
            
            // Store quiz and flashcards data
            currentQuiz = video.quiz;
            currentFlashcards = video.flashcards;
            
            // Show study content
            noVideoSelected.style.display = 'none';
            studyContent.style.display = 'block';
        } else {
            throw new Error('Video not found');
        }
    } catch (error) {
        console.error('Error loading study materials:', error);
        alert('Error loading study materials: ' + error.message);
    }
}

// Load quiz
function loadQuiz() {
    if (!currentQuiz || !currentQuiz.questions) {
        quizContent.innerHTML = '<div class="loading"><p>Quiz not available</p></div>';
        return;
    }
    
    quizResults = new Array(currentQuiz.questions.length).fill(null);
    
    const questionsHtml = currentQuiz.questions.map((q, index) => `
        <div class="quiz-question" id="question-${index}">
            <div class="question-text">${index + 1}. ${q.question}</div>
            <div class="quiz-options">
                ${q.options.map((option, optIndex) => `
                    <div class="quiz-option" onclick="selectQuizOption(${index}, ${optIndex})">
                        ${String.fromCharCode(65 + optIndex)}. ${option}
                    </div>
                `).join('')}
            </div>
            <div class="quiz-explanation" id="explanation-${index}" style="display: none;">
                <strong>Explanation:</strong> ${q.explanation}
            </div>
        </div>
    `).join('');
    
    quizContent.innerHTML = `
        <div class="content-box">
            <h3><i class="fas fa-question-circle"></i> Interactive Quiz</h3>
            ${questionsHtml}
            <div class="quiz-controls">
                <button class="btn btn-primary" onclick="submitQuiz()">
                    <i class="fas fa-check"></i> Submit Quiz
                </button>
            </div>
        </div>
    `;
}

// Select quiz option
function selectQuizOption(questionIndex, optionIndex) {
    const questionElement = document.getElementById(`question-${questionIndex}`);
    const options = questionElement.querySelectorAll('.quiz-option');
    
    // Clear previous selections
    options.forEach(opt => opt.classList.remove('selected'));
    
    // Select current option
    options[optionIndex].classList.add('selected');
    
    // Store result
    quizResults[questionIndex] = optionIndex;
}

// Submit quiz
function submitQuiz() {
    if (quizResults.includes(null)) {
        alert('Please answer all questions before submitting.');
        return;
    }
    
    let correctCount = 0;
    
    currentQuiz.questions.forEach((question, index) => {
        const questionElement = document.getElementById(`question-${index}`);
        const options = questionElement.querySelectorAll('.quiz-option');
        const explanationElement = document.getElementById(`explanation-${index}`);
        
        const userAnswer = quizResults[index];
        const correctAnswer = question.correct;
        
        options.forEach((option, optIndex) => {
            if (optIndex === correctAnswer) {
                option.classList.add('correct');
            } else if (optIndex === userAnswer && optIndex !== correctAnswer) {
                option.classList.add('incorrect');
            }
        });
        
        if (userAnswer === correctAnswer) {
            correctCount++;
        }
        
        explanationElement.style.display = 'block';
    });
    
    const score = Math.round((correctCount / currentQuiz.questions.length) * 100);
    
    // Show results
    const resultsHtml = `
        <div class="quiz-score">
            <h3>Quiz Complete!</h3>
            <p>Your Score: ${score}%</p>
            <p>You got ${correctCount} out of ${currentQuiz.questions.length} questions correct.</p>
            <button class="btn btn-primary" onclick="loadQuiz()">
                <i class="fas fa-redo"></i> Retake Quiz
            </button>
        </div>
    `;
    
    quizContent.innerHTML += resultsHtml;
}

// Load flashcards
function loadFlashcards() {
    if (!currentFlashcards || !currentFlashcards.cards) {
        flashcardsContent.innerHTML = '<div class="loading"><p>Flashcards not available</p></div>';
        return;
    }
    
    currentFlashcardIndex = 0;
    displayFlashcard();
}

// Display current flashcard
function displayFlashcard() {
    const cards = currentFlashcards.cards;
    const currentCard = cards[currentFlashcardIndex];
    
    flashcardsContent.innerHTML = `
        <div class="content-box">
            <h3><i class="fas fa-clone"></i> Flashcards</h3>
            <div class="flashcard" onclick="flipCard()">
                <div class="flashcard-indicator">${currentFlashcardIndex + 1} / ${cards.length}</div>
                <div class="flashcard-content">
                    <div class="flashcard-front">${currentCard.front}</div>
                    <div class="flashcard-back">${currentCard.back}</div>
                </div>
            </div>
            <div class="flashcard-controls">
                <button class="btn btn-primary" onclick="previousCard()" ${currentFlashcardIndex === 0 ? 'disabled' : ''}>
                    <i class="fas fa-chevron-left"></i> Previous
                </button>
                <button class="btn btn-primary" onclick="flipCard()">
                    <i class="fas fa-sync-alt"></i> Flip
                </button>
                <button class="btn btn-primary" onclick="nextCard()" ${currentFlashcardIndex === cards.length - 1 ? 'disabled' : ''}>
                    <i class="fas fa-chevron-right"></i> Next
                </button>
            </div>
        </div>
    `;
}

// Flip flashcard
function flipCard() {
    const flashcard = document.querySelector('.flashcard');
    flashcard.classList.toggle('flipped');
}

// Navigate flashcards
function previousCard() {
    if (currentFlashcardIndex > 0) {
        currentFlashcardIndex--;
        displayFlashcard();
    }
}

function nextCard() {
    if (currentFlashcardIndex < currentFlashcards.cards.length - 1) {
        currentFlashcardIndex++;
        displayFlashcard();
    }
}

// Send chat message
async function sendChatMessage() {
    const message = chatInput.value.trim();
    
    if (!message || !currentVideoId) {
        return;
    }
    
    // Add user message to chat
    addChatMessage(message, 'user');
    chatInput.value = '';
    
    // Show typing indicator
    const typingElement = addChatMessage('AI is thinking...', 'bot', true);
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                video_id: currentVideoId,
                message: message
            })
        });
        
        const result = await response.json();
        
        // Remove typing indicator
        typingElement.remove();
        
        if (result.response) {
            addChatMessage(result.response, 'bot');
        } else {
            throw new Error('No response received');
        }
    } catch (error) {
        typingElement.remove();
        addChatMessage('Sorry, I encountered an error. Please try again.', 'bot');
        console.error('Chat error:', error);
    }
}

// Add message to chat
function addChatMessage(message, type, isTemporary = false) {
    const messageElement = document.createElement('div');
    messageElement.className = `chat-message ${type}-message`;
    
    const avatar = type === 'bot' ? '<i class="fas fa-robot"></i>' : '<i class="fas fa-user"></i>';
    
    messageElement.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">
            <p>${message}</p>
        </div>
    `;
    
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    return messageElement;
}

// Switch to study tab
function switchToStudyTab() {
    // Update tab buttons
    tabBtns.forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.tab === 'study') {
            btn.classList.add('active');
        }
    });
    
    // Update tab content
    tabContents.forEach(content => {
        content.classList.remove('active');
        if (content.id === 'study') {
            content.classList.add('active');
        }
    });
}

// Progress and loading functions
function showProgress(text) {
    uploadProgress.style.display = 'block';
    uploadResult.style.display = 'none';
    progressFill.style.width = '0%';
    progressText.textContent = text;
}

function updateProgress(percent, text) {
    progressFill.style.width = percent + '%';
    progressText.textContent = text;
}

function hideProgress() {
    uploadProgress.style.display = 'none';
}

function showUploadResult(message) {
    uploadResult.style.display = 'block';
    resultMessage.textContent = message;
}

function showLoadingOverlay() {
    loadingOverlay.style.display = 'flex';
}

function hideLoadingOverlay() {
    loadingOverlay.style.display = 'none';
}
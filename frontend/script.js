// script.js - Complete ClearMind with AI reply space + DEBUG + Auto-resize + AUTH

document.addEventListener('DOMContentLoaded', function() {
    
    // ===== AUTH STATE MANAGEMENT (NEW) =====
    function updateAuthUI() {
        const token = localStorage.getItem('token');
        const user = JSON.parse(localStorage.getItem('user') || 'null');
        
        const loginLink = document.getElementById('loginLink');
        const registerLink = document.getElementById('registerLink');
        const userGreeting = document.getElementById('userGreeting');
        const logoutBtn = document.getElementById('logoutBtn');
        
        if (token && user) {
            // User is logged in
            if (loginLink) loginLink.style.display = 'none';
            if (registerLink) registerLink.style.display = 'none';
            if (userGreeting) {
                userGreeting.style.display = 'inline';
                userGreeting.textContent = `Hi, ${user.username}`;
            }
            if (logoutBtn) logoutBtn.style.display = 'inline-block';
        } else {
            // User is logged out
            if (loginLink) loginLink.style.display = 'inline-block';
            if (registerLink) registerLink.style.display = 'inline-block';
            if (userGreeting) userGreeting.style.display = 'none';
            if (logoutBtn) logoutBtn.style.display = 'none';
        }
    }
    
    // Handle logout (NEW)
    document.addEventListener('click', async (e) => {
        if (e.target.id === 'logoutBtn') {
            const token = localStorage.getItem('token');
            
            try {
                await fetch('/api/logout', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
            } catch (error) {
                console.error('Logout error:', error);
            }
            
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            updateAuthUI();
            window.location.href = 'index.html';
        }
    });
    
    // Call this when page loads
    updateAuthUI();
    
    // ===== INDEX PAGE FUNCTIONALITY =====
    
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ 
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Button hover effects
    const buttons = document.querySelectorAll('.action-button');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', () => {
            button.style.transition = 'all 0.3s cubic-bezier(0.2, 0, 0, 1)';
        });
        
        button.addEventListener('mouseleave', () => {
            button.style.transform = 'translateY(0)';
        });
        
        button.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                window.location.href = button.getAttribute('href');
            }
        });
    });
    
    // Professional console greeting
    console.log('%c🔷 ClearMind • Professional Student Tool', 'color: #1e3a5f; font-size: 14px; font-weight: 600;');
    console.log('%cBuild version: 1.0.0 | Designed for clarity', 'color: #547089; font-size: 12px;');
    
    // Intersection Observer for process steps
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, { 
        threshold: 0.2,
        rootMargin: '20px'
    });
    
    document.querySelectorAll('.process-step').forEach((step, index) => {
        step.style.opacity = '0';
        step.style.transform = 'translateY(15px)';
        step.style.transition = `all 0.5s ease ${index * 0.1}s`;
        observer.observe(step);
    });
    
    // ===== LOG MISTAKE PAGE FUNCTIONALITY =====
    const submitButton = document.getElementById('submitMistake');
    const textarea = document.getElementById('mistakeInput');
    const conversationArea = document.getElementById('conversationArea');
    const welcomeMessage = document.getElementById('welcomeMessage');
    
    if (submitButton && textarea && conversationArea) {
        
        // 🔥 NEW: Auto-resize textarea function
        function autoResizeTextarea() {
            textarea.style.height = 'auto';
            textarea.style.height = (textarea.scrollHeight) + 'px';
        }
        
        // 🔥 NEW: Reset textarea height
        function resetTextareaHeight() {
            textarea.style.height = 'auto';
            textarea.style.height = '24px'; // Minimum height
        }
        
        // Function to add a message to the conversation - UPDATED for new structure
        function addMessage(text, isUser = false) {
            console.log('📝 addMessage called with:', text.substring(0, 30) + '...', 'isUser:', isUser);
            
            const messageDiv = document.createElement('div');
            messageDiv.className = `message-row ${isUser ? 'user-message' : 'ai-message'}`;
            
            if (!isUser) {
                // AI message has avatar
                const avatar = document.createElement('div');
                avatar.className = 'message-avatar';
                avatar.textContent = 'CM';
                messageDiv.appendChild(avatar);
            }
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            
            const bubble = document.createElement('div');
            bubble.className = 'message-bubble';
            
            const paragraph = document.createElement('p');
            paragraph.textContent = text;
            bubble.appendChild(paragraph);
            
            const time = document.createElement('span');
            time.className = 'message-time';
            time.textContent = 'just now';
            
            contentDiv.appendChild(bubble);
            contentDiv.appendChild(time);
            messageDiv.appendChild(contentDiv);
            
            conversationArea.appendChild(messageDiv);
            
            // Scroll to bottom smoothly
            messageDiv.scrollIntoView({ behavior: 'smooth', block: 'end' });
            
            console.log('✅ Message added to DOM. Total messages:', document.querySelectorAll('.message-row').length);
        }
        
        // Function to show thinking indicator
        function showThinking() {
            console.log('⏳ Showing thinking indicator');
            const thinkingDiv = document.createElement('div');
            thinkingDiv.className = 'message-row ai-message thinking';
            thinkingDiv.id = 'thinkingIndicator';
            
            const avatar = document.createElement('div');
            avatar.className = 'message-avatar';
            avatar.textContent = 'CM';
            
            const bubble = document.createElement('div');
            bubble.className = 'message-bubble thinking-indicator';
            
            const dotsDiv = document.createElement('div');
            dotsDiv.className = 'thinking-dots';
            dotsDiv.innerHTML = '<span></span><span></span><span></span>';
            
            bubble.appendChild(dotsDiv);
            thinkingDiv.appendChild(avatar);
            thinkingDiv.appendChild(bubble);
            
            conversationArea.appendChild(thinkingDiv);
            conversationArea.scrollTop = conversationArea.scrollHeight;
        }
        
        // Function to remove thinking indicator
        function removeThinking() {
            const indicator = document.getElementById('thinkingIndicator');
            if (indicator) {
                indicator.remove();
                console.log('✅ Thinking indicator removed');
            }
        }
        
        // Function to format AI response
        function displayAIAnalysis(analysis) {
            console.log('🔥 DEBUG - analysis received:', analysis);
            console.log('🔥 DEBUG - analysis.response:', analysis ? analysis.response : 'undefined');
            
            if (analysis && analysis.response) {
                console.log('✅ Calling addMessage with response');
                addMessage(analysis.response);
                
                // Double-check that message was added
                setTimeout(() => {
                    const messages = document.querySelectorAll('.message-row');
                    console.log('📊 Final message count:', messages.length);
                    console.log('📊 Conversation area HTML:', conversationArea.innerHTML.substring(0, 200) + '...');
                }, 100);
                
            } else {
                console.error('❌ Bad analysis format:', analysis);
                addMessage('Thanks for sharing. Let me think about that...');
            }
        }
        
        // 🔥 NEW: Add input event for auto-resize
        textarea.addEventListener('input', function() {
            autoResizeTextarea();
            // Keep your existing border color reset
            textarea.style.borderColor = '#e2e8f0';
            textarea.style.backgroundColor = '#ffffff';
        });
        
        // Handle submit button click
        submitButton.addEventListener('click', async function() {
            const userInput = textarea.value.trim();
            console.log('🚀 Submit clicked. Input:', userInput);
            
            if (userInput === '') {
                textarea.style.borderColor = '#c53030';
                textarea.style.backgroundColor = '#fff5f5';
                
                setTimeout(() => {
                    textarea.style.borderColor = '#e2e8f0';
                    textarea.style.backgroundColor = '#ffffff';
                }, 2000);
                
                return;
            }
            
            // Add user message to conversation
            addMessage(userInput, true);
            
            // Disable button and show thinking
            submitButton.disabled = true;
            submitButton.style.opacity = '0.6';
            submitButton.style.cursor = 'not-allowed';
            
            textarea.disabled = true;
            textarea.placeholder = 'AI is analyzing...';
            
            // Show thinking indicator
            showThinking();
            
            try {
                // Call backend with token (UPDATED)
                console.log('📡 Sending request to backend...');
                const token = localStorage.getItem('token'); // NEW: Get token
                
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': token ? `Bearer ${token}` : '' // NEW: Add token header
                    },
                    body: JSON.stringify({
                        text: userInput
                        // Removed user_id - backend gets it from token
                    })
                });
                
                const data = await response.json();
                console.log('📡 Response received:', data);
                
                // Remove thinking indicator
                removeThinking();
                
                if (data.success) {
                    console.log('✅ Success, calling displayAIAnalysis');
                    displayAIAnalysis(data.analysis);
                    
                    // Clear textarea and reset height
                    textarea.value = '';
                    resetTextareaHeight();
                    
                    // Store for dashboard later
                    sessionStorage.setItem('lastAnalysis', JSON.stringify(data.analysis));
                    
                } else {
                    console.error('❌ Server returned error:', data.error);
                    addMessage(`I encountered an error: ${data.error}. Please try again.`);
                }
                
            } catch (error) {
                console.error('❌ Error:', error);
                removeThinking();
                addMessage('Connection error. Please make sure the server is running.');
                
            } finally {
                // Re-enable everything
                submitButton.disabled = false;
                submitButton.style.opacity = '1';
                submitButton.style.cursor = 'pointer';
                textarea.disabled = false;
                textarea.placeholder = 'Describe the question, what answer you thought and explain your thinking. Write naturally - no format needed. Honesty improves accuracy.';
                textarea.focus();
            }
        });
        
        // Handle Enter key
        textarea.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                submitButton.click();
            }
        });
        
        // Focus textarea
        textarea.focus();
        
        // 🔥 NEW: Initial height set
        resetTextareaHeight();
    }
});
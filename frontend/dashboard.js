// frontend/dashboard.js
document.addEventListener('DOMContentLoaded', async function() {
    const token = localStorage.getItem('token');
    const user = JSON.parse(localStorage.getItem('user') || 'null');
    
    if (!token || !user) {
        window.location.href = 'login.html';
        return;
    }
    
    document.getElementById('userGreeting').textContent = `Hi, ${user.username}`;
    
    // Load dashboard data
    try {
        // Get patterns
        const patternsRes = await fetch('/api/patterns', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const patternsData = await patternsRes.json();
        
        // Get history
        const historyRes = await fetch('/api/history', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const historyData = await historyRes.json();
        
        if (patternsData.success) {
            updatePatterns(patternsData);
        }
        
        if (historyData.success) {
            updateHistory(historyData.history);
        }
        
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
    
    // Logout handler
    document.getElementById('logoutBtn').addEventListener('click', async () => {
        await fetch('/api/logout', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = 'index.html';
    });
});

function updatePatterns(data) {
    document.getElementById('totalCount').textContent = data.total_mistakes || 0;
    document.getElementById('weeklyCount').textContent = data.recent_count || 0;
    
    const patterns = data.patterns || [];
    if (patterns.length > 0) {
        document.getElementById('topPattern').textContent = patterns[0].category;
    }
    
    const patternsList = document.getElementById('patternsList');
    patternsList.innerHTML = patterns.map(p => `
        <div class="pattern-item">
            <span class="pattern-name">${p.category}</span>
            <span class="pattern-count">${p.count} times</span>
        </div>
    `).join('');
}

function updateHistory(history) {
    const historyList = document.getElementById('historyList');
    if (history.length === 0) {
        historyList.innerHTML = '<p>No mistakes logged yet.</p>';
        return;
    }
    
    historyList.innerHTML = history.map(item => `
        <div class="history-item">
            <p class="history-input">"${item.input.substring(0, 100)}${item.input.length > 100 ? '...' : ''}"</p>
            <p class="history-date">${new Date(item.date).toLocaleDateString()}</p>
        </div>
    `).join('');
}
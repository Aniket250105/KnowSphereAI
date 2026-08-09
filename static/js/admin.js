function renderStatus(elementId, statusValue) {
    const el = document.getElementById(elementId);
    if (!el) return;
    
    const isOk = (statusValue || '').toLowerCase() === 'ok';
    
    el.textContent = isOk ? 'Operational' : 'Failing';
    el.style.backgroundColor = isOk ? '#dcfce7' : '#fee2e2';
    el.style.color = isOk ? '#166534' : '#991b1b';
}

async function loadHealth() {
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) refreshBtn.classList.add('spin');
    
    try {
        const data = await ApiClient.getHealth();
        
        renderStatus('status-api', data.api_status);
        renderStatus('status-vector', data.vector_db_status);
        renderStatus('status-llm', data.llm_status);
        renderStatus('status-embedding', data.embedding_model_status);
        
        const timeEl = document.getElementById('lastUpdated');
        if (timeEl) timeEl.textContent = new Date().toLocaleTimeString();
    } catch (e) {
        console.error('Failed to load health', e);
        ['status-api', 'status-vector', 'status-llm', 'status-embedding'].forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.textContent = 'Error';
                el.style.backgroundColor = '#fee2e2';
                el.style.color = '#991b1b';
            }
        });
        const timeEl = document.getElementById('lastUpdated');
        if (timeEl) timeEl.textContent = new Date().toLocaleTimeString() + ' (Failed)';
    } finally {
        if (refreshBtn) refreshBtn.classList.remove('spin');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadHealth();
    
    // Auto refresh every 30 seconds
    setInterval(loadHealth, 30000);
    
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', loadHealth);
    }
});

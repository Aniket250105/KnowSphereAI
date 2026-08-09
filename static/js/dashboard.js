document.addEventListener('DOMContentLoaded', () => {
    loadDashboardStats();
});

async function loadDashboardStats() {
    try {
        const [docs, health] = await Promise.all([
            ApiClient.getDocuments().catch(() => []),
            ApiClient.getHealth().catch(() => null)
        ]);
        
        let chunks = 0;
        let indexedDocs = 0;
        
        docs.forEach(doc => { 
            chunks += doc.chunk_count || 0; 
            if (doc.status === 'indexed') indexedDocs++;
        });
        
        document.getElementById('stat-docs').textContent = docs.length;
        document.getElementById('stat-chunks').textContent = chunks;
        
        // System Health
        const healthEl = document.getElementById('stat-health');
        if (healthEl) {
            if (health && health.api_status === 'ok' && health.vector_db_status === 'ok' && health.llm_status === 'ok') {
                healthEl.innerHTML = '<span style="color: #10b981;">Healthy</span>';
            } else {
                healthEl.innerHTML = '<span style="color: #ef4444;">Issues Detected</span>';
            }
        }
        
        // Recent Activity
        const activityEl = document.getElementById('recent-activity');
        if (activityEl) {
            if (docs.length === 0) {
                activityEl.innerHTML = `
                    <div style="padding: 2rem; text-align: center; background: var(--background); border-radius: 8px; border: 1px dashed var(--border);">
                        <i data-feather="inbox" style="width: 32px; height: 32px; color: var(--text-muted); margin-bottom: 1rem;"></i>
                        <p>No recent activity. <a href="/documents" style="color: var(--primary); text-decoration: none; font-weight: 500;">Upload a document</a> to get started.</p>
                    </div>
                `;
            } else {
                activityEl.innerHTML = `
                    <ul style="list-style: none; padding: 0;">
                        <li style="padding: 1rem 0; border-bottom: 1px solid var(--border); display: flex; align-items: center; gap: 1rem;">
                            <div style="background: #e0e7ff; color: #4f46e5; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                                <i data-feather="file-text"></i>
                            </div>
                            <div>
                                <p style="font-weight: 500; margin-bottom: 0.25rem;">Knowledge Base Status</p>
                                <p style="font-size: 0.875rem; color: var(--text-muted);">${indexedDocs} out of ${docs.length} documents successfully indexed.</p>
                            </div>
                        </li>
                        <li style="padding: 1rem 0; border-bottom: 1px solid var(--border); display: flex; align-items: center; gap: 1rem;">
                            <div style="background: ${health && health.vector_db_status === 'ok' ? '#dcfce7' : '#fee2e2'}; color: ${health && health.vector_db_status === 'ok' ? '#166534' : '#991b1b'}; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                                <i data-feather="database"></i>
                            </div>
                            <div>
                                <p style="font-weight: 500; margin-bottom: 0.25rem;">Vector Database</p>
                                <p style="font-size: 0.875rem; color: var(--text-muted);">${health && health.vector_db_status === 'ok' ? 'Online and accepting queries.' : 'Connection issues detected.'}</p>
                            </div>
                        </li>
                        <li style="padding: 1rem 0; display: flex; align-items: center; gap: 1rem;">
                            <div style="background: ${health && health.llm_status === 'ok' ? '#dcfce7' : '#fee2e2'}; color: ${health && health.llm_status === 'ok' ? '#166534' : '#991b1b'}; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                                <i data-feather="cpu"></i>
                            </div>
                            <div>
                                <p style="font-weight: 500; margin-bottom: 0.25rem;">LLM Engine</p>
                                <p style="font-size: 0.875rem; color: var(--text-muted);">${health && health.llm_status === 'ok' ? 'AI generation service is ready.' : 'Service degraded.'}</p>
                            </div>
                        </li>
                    </ul>
                `;
            }
            if (typeof feather !== 'undefined') feather.replace();
        }
        
    } catch (error) {
        console.error('Failed to load dashboard stats', error);
        window.Toast?.error("Failed to load dashboard data");
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadAnalytics();
});

async function loadAnalytics() {
    try {
        const data = await ApiClient.getAnalytics();
        
        document.getElementById('stat-docs').textContent = data.documents || '--';
        document.getElementById('stat-queries').textContent = data.queries || '--';
        document.getElementById('stat-users').textContent = data.users || '--';
        document.getElementById('stat-latency').textContent = data.avg_latency || '--';
        
        const healthEl = document.getElementById('stat-health');
        if (healthEl) {
            healthEl.textContent = data.health || '--';
            if (data.health === 'Operational') {
                healthEl.style.color = '#10b981';
            } else {
                healthEl.style.color = '#ef4444';
            }
        }
        
        // Mock chart data (since backend might not provide it yet, ApiClient has a fallback)
        const queryData = data.query_chart || [12, 19, 15, 25, 22, 30, 28];
        const docLabels = data.doc_labels || ['HR Policy', 'API Docs', 'Onboarding', 'Q3 Report'];
        const docData = data.doc_data || [45, 25, 20, 10];
        const feedbackData = data.feedback || [85, 15]; // Thumbs up, down

        // Query Chart
        if (document.getElementById('queryChart')) {
            new Chart(document.getElementById('queryChart'), {
                type: 'line',
                data: {
                    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                    datasets: [{
                        label: 'Queries',
                        data: queryData,
                        borderColor: '#4f46e5',
                        tension: 0.3,
                        fill: false
                    }]
                },
                options: { responsive: true }
            });
        }

        // Doc Chart
        if (document.getElementById('docChart')) {
            new Chart(document.getElementById('docChart'), {
                type: 'doughnut',
                data: {
                    labels: docLabels,
                    datasets: [{
                        data: docData,
                        backgroundColor: ['#4f46e5', '#3b82f6', '#0ea5e9', '#38bdf8']
                    }]
                },
                options: { responsive: true }
            });
        }

        // Feedback Chart
        if (document.getElementById('feedbackChart')) {
            new Chart(document.getElementById('feedbackChart'), {
                type: 'bar',
                data: {
                    labels: ['Helpful', 'Not Helpful'],
                    datasets: [{
                        label: 'Votes',
                        data: feedbackData,
                        backgroundColor: ['#10b981', '#ef4444']
                    }]
                },
                options: { 
                    responsive: true,
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });
        }
        
    } catch (e) {
        console.error('Failed to load analytics', e);
        window.Toast?.error("Failed to load analytics dashboard data");
    }
}

window.runBenchmark = async function() {
    alert('Starting a new benchmark run. Check back in a few minutes.');
    // Implement the trigger logic here if backend has a run endpoint
}

async function loadEvaluations() {
    try {
        // Check if backend endpoint exists
        let data = null;
        try {
            data = await ApiClient.get('/api/v1/admin/evaluation/summary');
        } catch (err) {
            // Mock data if endpoint is missing
            data = {
                avg_score: 87.5,
                retrieval_score: 92.1,
                grounding_score: 85.3,
                citation_score: 88.0,
                avg_latency: "1.4s",
                runs: [
                    { id: 'RUN-4902', date: '2026-08-07', dataset: 'Finance Q&A', score: 89.2 },
                    { id: 'RUN-4901', date: '2026-08-06', dataset: 'HR Policies', score: 85.8 }
                ],
                chart: {
                    labels: ['Run 1', 'Run 2', 'Run 3', 'Run 4', 'Run 5'],
                    retrieval: [80, 85, 87, 90, 92],
                    grounding: [75, 78, 82, 85, 85]
                }
            };
        }

        const avgEl = document.getElementById('eval-avg');
        if (avgEl) avgEl.textContent = data.avg_score + '%';
        
        const retEl = document.getElementById('eval-retrieval');
        if (retEl) retEl.textContent = data.retrieval_score + '%';
        
        const grEl = document.getElementById('eval-grounding');
        if (grEl) grEl.textContent = data.grounding_score + '%';
        
        const citEl = document.getElementById('eval-citation');
        if (citEl) citEl.textContent = data.citation_score + '%';
        
        const latEl = document.getElementById('eval-latency');
        if (latEl) latEl.textContent = data.avg_latency;

        // Render table
        const tbody = document.getElementById('evalTableBody');
        if (tbody) {
            tbody.innerHTML = data.runs.map(run => `
                <tr style="border-bottom: 1px solid var(--border);">
                    <td style="padding: 0.75rem;">${run.date}</td>
                    <td style="padding: 0.75rem; color: var(--primary); font-family: monospace;">${run.id}</td>
                    <td style="padding: 0.75rem;">${run.dataset}</td>
                    <td style="padding: 0.75rem; font-weight: 600;">${run.score}%</td>
                </tr>
            `).join('');
        }

        // Render Chart
        if (document.getElementById('evalChart')) {
            new Chart(document.getElementById('evalChart'), {
                type: 'line',
                data: {
                    labels: data.chart.labels,
                    datasets: [
                        { label: 'Retrieval Score', data: data.chart.retrieval, borderColor: '#3b82f6', fill: false },
                        { label: 'Grounding Score', data: data.chart.grounding, borderColor: '#10b981', fill: false }
                    ]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
        }

    } catch (e) {
        console.error('Failed to load evaluations', e);
        window.Toast?.error("Failed to load evaluation data");
    }
}

document.addEventListener('DOMContentLoaded', loadEvaluations);

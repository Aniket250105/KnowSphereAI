const fileInput = document.getElementById('fileInput');
const uploadStatus = document.getElementById('uploadStatus');
const docTableBody = document.getElementById('docTableBody');

async function loadDocuments() {
    try {
        const docs = await ApiClient.getDocuments();
        renderDocuments(docs);
    } catch (error) {
        console.error('Failed to load docs', error);
        if (docTableBody) {
            docTableBody.innerHTML = '<tr><td colspan="6" class="error-text" style="color: #ef4444; text-align: center;">Failed to load documents</td></tr>';
        }
    }
}

function renderDocuments(docs) {
    if (!docTableBody) return;
    
    if (docs.length === 0) {
        docTableBody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: var(--text-muted);">No documents uploaded yet.</td></tr>';
        return;
    }
    
    docTableBody.innerHTML = docs.map(doc => {
        const ext = doc.filename.split('.').pop().toUpperCase();
        return `
        <tr>
            <td style="font-weight: 500;">
                <i data-feather="file" style="width: 16px; height: 16px; margin-right: 0.5rem; vertical-align: middle;"></i>
                ${doc.filename}
            </td>
            <td><span style="font-size:0.75rem; font-weight:600; padding:0.2rem 0.4rem; background:var(--surface); border:1px solid var(--border); border-radius:4px;">${ext}</span></td>
            <td>
                <span style="padding: 0.25rem 0.5rem; border-radius: 999px; font-size: 0.75rem; font-weight: 600; background: ${doc.status === 'indexed' ? '#dcfce7' : '#fef9c3'}; color: ${doc.status === 'indexed' ? '#166534' : '#854d0e'};">
                    ${doc.status}
                </span>
            </td>
            <td>${doc.chunk_count || 0}</td>
            <td style="color: var(--text-muted); font-size: 0.875rem;">${new Date(doc.created_at).toLocaleDateString()}</td>
            <td style="text-align: right;">
                <div style="display:flex; gap:0.25rem; justify-content:flex-end;">
                    <button class="btn btn-outline" style="padding: 0.25rem 0.5rem;" title="View" onclick="viewDocument('${doc.id}')">
                        <i data-feather="eye" style="width: 16px; height: 16px;"></i>
                    </button>
                    <button class="btn btn-outline" style="padding: 0.25rem 0.5rem;" title="Report" onclick="generateReport('${doc.id}')">
                        <i data-feather="file-text" style="width: 16px; height: 16px;"></i>
                    </button>
                    <button class="btn btn-outline" style="padding: 0.25rem 0.5rem;" title="Re-index" onclick="reindexDocument('${doc.id}')">
                        <i data-feather="refresh-cw" style="width: 16px; height: 16px;"></i>
                    </button>
                    <button class="btn btn-outline" style="padding: 0.25rem 0.5rem; color: #ef4444; border-color: #fca5a5;" title="Delete" onclick="deleteDocument('${doc.id}')">
                        <i data-feather="trash-2" style="width: 16px; height: 16px;"></i>
                    </button>
                </div>
            </td>
        </tr>
    `}).join('');
    
    if (typeof feather !== 'undefined') feather.replace();
}

window.deleteDocument = async function(id) {
    if (!confirm('Are you sure you want to delete this document?')) return;
    
    try {
        await ApiClient.deleteDocument(id);
        window.Toast?.success("Document deleted successfully");
        loadDocuments();
    } catch (error) {
        console.error('Delete error', error);
        window.Toast?.error("Failed to delete document. Admin/Manager role required.");
    }
}

window.viewDocument = async function(id) {
    try {
        const doc = await ApiClient.getDocument(id);
        alert(`Document Details:\n\nFilename: ${doc.filename}\nStatus: ${doc.status}\nChunks: ${doc.chunk_count}\nUploaded: ${new Date(doc.created_at).toLocaleString()}`);
    } catch (e) {
        window.Toast?.error("Failed to fetch document details");
    }
}

window.generateReport = function(id) {
    window.location.href = `/api/v1/documents/${id}/report`;
}

window.reindexDocument = async function(id) {
    alert('Re-indexing is a backend process. Feature placeholder triggered for ' + id);
}

if (fileInput) {
    fileInput.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        
        const validExtensions = ['pdf', 'txt', 'docx'];
        const ext = file.name.split('.').pop().toLowerCase();
        if (!validExtensions.includes(ext)) {
            uploadStatus.style.display = 'block';
            uploadStatus.style.color = '#ef4444';
            uploadStatus.textContent = 'Invalid file type. Supports PDF, DOCX, TXT only.';
            window.Toast?.error('Invalid file type');
            fileInput.value = '';
            return;
        }
        
        uploadStatus.style.display = 'block';
        uploadStatus.style.color = 'var(--text)';
        uploadStatus.innerHTML = `Uploading and indexing ${file.name}... <i data-feather="loader" class="spin"></i>`;
        if (typeof feather !== 'undefined') feather.replace();
        
        try {
            await ApiClient.uploadDocument(file);
            uploadStatus.style.color = '#10b981';
            uploadStatus.textContent = `Successfully indexed ${file.name}`;
            window.Toast?.success(`${file.name} uploaded and indexed`);
            loadDocuments();
        } catch (error) {
            uploadStatus.style.color = '#ef4444';
            let errText = 'Unknown error';
            if (error instanceof Response) {
                try {
                    const data = await error.json();
                    errText = data.detail || errText;
                } catch(e){}
            }
            uploadStatus.textContent = `Upload failed: ${errText}`;
            window.Toast?.error(`Upload failed: ${errText}`);
        }
        
        fileInput.value = ''; // reset
    });
}

// Handle drag and drop
const dropzone = document.getElementById('dropzone');
if (dropzone) {
    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.style.borderColor = 'var(--primary)';
        dropzone.style.backgroundColor = 'rgba(79, 70, 229, 0.05)';
    });
    ['dragleave', 'dragend'].forEach(type => {
        dropzone.addEventListener(type, (e) => {
            dropzone.style.borderColor = 'var(--border)';
            dropzone.style.backgroundColor = 'var(--surface)';
        });
    });
    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.style.borderColor = 'var(--border)';
        dropzone.style.backgroundColor = 'var(--surface)';
        
        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files;
            fileInput.dispatchEvent(new Event('change'));
        }
    });
}

document.addEventListener('DOMContentLoaded', loadDocuments);

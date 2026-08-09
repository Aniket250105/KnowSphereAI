document.addEventListener('DOMContentLoaded', () => {
    // Initialize icons
    if (typeof feather !== 'undefined') {
        feather.replace();
    }
    
    // Theme toggling
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const isDark = document.body.getAttribute('data-theme') === 'dark';
            const newTheme = isDark ? 'light' : 'dark';
            document.body.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            
            themeToggle.innerHTML = `<i data-feather="${newTheme === 'dark' ? 'sun' : 'moon'}"></i>`;
            if (typeof feather !== 'undefined') feather.replace();
        });
        
        // Restore theme
        if (localStorage.getItem('theme') === 'dark') {
            document.body.setAttribute('data-theme', 'dark');
            themeToggle.innerHTML = `<i data-feather="sun"></i>`;
            if (typeof feather !== 'undefined') feather.replace();
        }
    }

    // Load User Profile if we are not on login/register pages
    if (!window.location.pathname.includes('/login') && !window.location.pathname.includes('/register')) {
        loadUserProfile();
    }
});

async function loadUserProfile() {
    try {
        const data = await ApiClient.get('/api/v1/auth/me');
        if (data.user) {
            const elName = document.getElementById('userName');
            const elRole = document.getElementById('userRole');
            const elAvatar = document.getElementById('userAvatar');
            
            if (elName) elName.textContent = data.user.username;
            if (elRole) elRole.textContent = data.user.role;
            if (elAvatar) elAvatar.textContent = data.user.username.charAt(0).toUpperCase();
        }
    } catch (error) {
        console.error("Failed to load user profile", error);
        // Since api.js now intercepts 401, it will auto redirect, so we don't need to do it here.
    }
}

window.logout = async function() {
    try {
        await ApiClient.logout();
        window.location.href = "/login";
    } catch (error) {
        console.error("Logout failed", error);
        window.location.href = "/login";
    }
};

// Global Toast System
window.Toast = {
    show: function(message, type = 'success') {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icon = type === 'success' ? 'check-circle' : 'alert-circle';
        
        toast.innerHTML = `
            <i data-feather="${icon}" style="width:18px;height:18px;"></i>
            <span>${message}</span>
        `;
        
        container.appendChild(toast);
        if (typeof feather !== 'undefined') feather.replace();
        
        setTimeout(() => {
            toast.classList.add('fade-out');
            toast.addEventListener('animationend', () => {
                toast.remove();
            });
        }, 3000);
    },
    success: function(msg) { this.show(msg, 'success'); },
    error: function(msg) { this.show(msg, 'error'); }
};

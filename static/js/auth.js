document.addEventListener('DOMContentLoaded', () => {
    // Login Form Logic
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const errorDiv = document.getElementById('loginError');
            const submitBtn = document.getElementById('submitBtn');
            const btnText = document.getElementById('btnText');
            const btnLoader = document.getElementById('btnLoader');
            
            // Reset state
            errorDiv.style.display = 'none';
            submitBtn.disabled = true;
            btnText.style.display = 'none';
            btnLoader.style.display = 'inline-block';
            
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            try {
                const response = await ApiClient.login(email, password);
                
                // Set cookie (since backend returns it in body for frontend to use, or sets it via set-cookie)
                if (response.access_token) {
                    document.cookie = `access_token=${response.access_token}; path=/; max-age=86400; samesite=strict`;
                }
                
                window.location.href = "/dashboard";
                
            } catch (error) {
                let errText = "Invalid email or password";
                if (error instanceof Response) {
                    try {
                        const data = await error.json();
                        if (typeof data.detail === 'string') {
                            errText = data.detail;
                        } else if (Array.isArray(data.detail)) {
                            errText = data.detail.map(d => d.msg).join(', ');
                        } else if (typeof data.detail === 'object') {
                            errText = JSON.stringify(data.detail);
                        }
                    } catch(e) {}
                }
                
                errorDiv.textContent = errText;
                errorDiv.style.display = 'block';
                submitBtn.disabled = false;
                btnText.style.display = 'inline';
                btnLoader.style.display = 'none';
            }
        });
    }

    // Register Form Logic
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const errorDiv = document.getElementById('registerError');
            const submitBtn = document.getElementById('submitBtn');
            const btnText = document.getElementById('btnText');
            const btnLoader = document.getElementById('btnLoader');
            
            // Reset state
            errorDiv.style.display = 'none';
            submitBtn.disabled = true;
            btnText.style.display = 'none';
            btnLoader.style.display = 'inline-block';
            
            const fullname = document.getElementById('fullname').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirmPassword').value;
            
            // Client side validation
            if (password !== confirmPassword) {
                errorDiv.textContent = "Passwords do not match";
                errorDiv.style.display = 'block';
                submitBtn.disabled = false;
                btnText.style.display = 'inline';
                btnLoader.style.display = 'none';
                return;
            }
            
            try {
                await ApiClient.register(fullname, email, password);
                // Immediately login after registration
                const loginResponse = await ApiClient.login(email, password);
                if (loginResponse.access_token) {
                    document.cookie = `access_token=${loginResponse.access_token}; path=/; max-age=86400; samesite=strict`;
                }
                window.location.href = "/dashboard";
            } catch (error) {
                let errText = "Registration failed";
                if (error instanceof Response) {
                    try {
                        const data = await error.json();
                        if (typeof data.detail === 'string') {
                            errText = data.detail;
                        } else if (Array.isArray(data.detail)) {
                            errText = data.detail.map(d => d.msg).join(', ');
                        }
                    } catch(e) {}
                }
                
                errorDiv.textContent = errText;
                errorDiv.style.display = 'block';
                submitBtn.disabled = false;
                btnText.style.display = 'inline';
                btnLoader.style.display = 'none';
            }
        });
    }
});

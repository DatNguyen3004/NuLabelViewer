document.addEventListener('DOMContentLoaded', function() {
    const togglePassword = document.querySelector('#toggle-password');
    const passwordInput = document.querySelector('#password-input');
    const eyeIcon = document.querySelector('#eye-icon');

    if (togglePassword) {
        togglePassword.addEventListener('click', function() {
            // Chuyển đổi type
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            
            // Đổi icon mắt (fa-eye <-> fa-eye-slash)
            this.querySelector('i').classList.toggle('fa-eye');
            this.querySelector('i').classList.toggle('fa-eye-slash');
        });
    }
});
document.getElementById('toggleButton').addEventListener('click', function() {
    const content1 = document.querySelector('.Login');
    const content2 = document.querySelector('.Main');
    const button = document.getElementById('toggleButton');
    const passwordInput = document.getElementById('passwordInput');
    const errorMessage = document.getElementById('errorMessage');
    
    if (content2.style.display === 'none') {
        // Trying to log in
        if (passwordInput.value === '123') {
            content2.style.display = 'block';
            content1.style.display = 'none';
            button.textContent = 'Logout';
            errorMessage.style.display = 'none';
            passwordInput.value = ''; // Clear the password field
        } else {
            errorMessage.style.display = 'block';
        }
    } else {
        // Logging out
        content2.style.display = 'none';
        content1.style.display = 'block';
        button.textContent = 'Login';
        errorMessage.style.display = 'none';
    }
});
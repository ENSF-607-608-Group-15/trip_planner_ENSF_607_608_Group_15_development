function submitVacationPlan(event) {
    event.preventDefault();
    const formData = new FormData(document.getElementById('vacationForm'));
    
    document.getElementById('loadingSpinner').style.display = 'block';
    document.getElementById('vacationResult').innerHTML = '';
    
    fetch('/plan', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('loadingSpinner').style.display = 'none';
        document.getElementById('vacationResult').innerHTML = data.vacation_plan.replace(/\n/g, '<br>');
    })
    .catch(error => {
        document.getElementById('loadingSpinner').style.display = 'none';
        document.getElementById('vacationResult').innerHTML = 'Error: Failed to get vacation plan';
        console.error('Error:', error);
    });
}

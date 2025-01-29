// Function to handle form submission
async function handleFormSubmit(url, formData) {
    try {
        let response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        let result = await response.json();
        if (response.ok) {
            alert('Success: ' + result.message);
        } else {
            alert('Error: ' + result.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    }
}

// Event listener for Donor form submission
document.querySelector('#donorForm').addEventListener('submit', function(event) {
    event.preventDefault();
    let donorData = {
        name: document.querySelector('#donorName').value,
        email: document.querySelector('#donorEmail').value,
        foodDetails: document.querySelector('#foodDetails').value
    };
    handleFormSubmit('/api/donors', donorData);
});

// Event listener for Receiver form submission
document.querySelector('#receiverForm').addEventListener('submit', function(event) {
    event.preventDefault();
    let receiverData = {
        name: document.querySelector('#receiverName').value,
        email: document.querySelector('#receiverEmail').value
    };
    handleFormSubmit('/api/receivers', receiverData);
});

// Event listener for Volunteer form submission
document.querySelector('#volunteerForm').addEventListener('submit', function(event) {
    event.preventDefault();
    let volunteerData = {
        name: document.querySelector('#volunteerName').value,
        email: document.querySelector('#volunteerEmail').value,
        availability: document.querySelector('#availability').value
    };
    handleFormSubmit('/api/volunteers', volunteerData);
});

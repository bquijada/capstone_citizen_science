let observationMethodCount = 0;
let observations = [];

// Adds observation method to a global list of observation methods
function addObservationMethod(index, methodName) {
    const promptInput = document.getElementById(`prompt${index}`);
    const optionsInput = document.getElementById(`options${index}`);

    const observationMethod = {
        methodName: methodName,
        prompt: promptInput.value,
        options: methodName === 'Dropdown' || methodName === 'Checkbox' ? optionsInput.value.split(',').map(option => option.trim()) : null
    };

    observations.push(observationMethod);

    observationMethodCount++;

}

// Event listener for selecting an observation method value from dropdown menu
function onDropdownChange() {
    const methodNameDropdown = document.getElementById('methodName');
    const selectedMethodName = methodNameDropdown.value;

    const observationMethodDiv = document.createElement('div');
    observationMethodDiv.innerHTML = `
        <label for="prompt${observationMethodCount}">${selectedMethodName} Prompt:</label>
        <input type="text" id="prompt${observationMethodCount}" required>

        <label for="options${observationMethodCount}">${selectedMethodName} Options (must be comma-separated):</label>
        <input type="text" id="options${observationMethodCount}" ${selectedMethodName !== 'Dropdown' &&
        selectedMethodName !== 'Checkbox' ? 'disabled' : ''}>
        <button type="button" onclick="addObservationMethod(${observationMethodCount}, '${selectedMethodName}'); this.disabled = true;">Add Observation Method</button>
        <hr>
    `;
    // update the dom with new div
    const observationMethodsContainer = document.getElementById('observationMethods');
    observationMethodsContainer.appendChild(observationMethodDiv);
}

// Finalizes project by sending title, description, and list of observations to datastore
function createProject() {
    const projectTitle = document.getElementById('projectTitle').value;
    const projectDescription = document.getElementById('projectDescription').value;

    const payload = {
        title: projectTitle,
        description: projectDescription,
        observations,
    };

    sendToDatabase('/projects', 'POST', payload)
        .then(response => {
            console.log('Project created successfully:', response);
        })
        .catch(error => {
            console.error('Error creating project:', error);
        });
}

// POST to datastore
function sendToDatabase(url, method, payload) {
    return new Promise((resolve, reject) => {
        fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error. Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            resolve(data);
        })
        .catch(error => {
            reject(error);
        });
    });
}

document.getElementById('methodName').addEventListener('change', onDropdownChange);


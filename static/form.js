class InputItem {
  constructor(observation_type, prompt, options = null) {
    this.prompt = prompt
    this.observation_type = observation_type; // 'Text', 'Dropdown', 'Checkbox', 'Numerical'
    this.options = options; // Used for 'dropdown' and 'checkbox' types
  }
}


class Project {
  constructor(title, description, parameters) {
    this.title = title
    this.description = description;
    this.parameters = parameters; // list of InputItem objects
  }
}

let observationMethodCount = 0;
let observation_methods = []

// Adds observation method to a global list of observation methods
function addObservationMethod(index, observation_type) {
    const promptInput = document.getElementById(`prompt${index}`);
    const optionsInput = document.getElementById(`options${index}`);
    let options = observation_type === 'Dropdown' || observation_type === 'Checkbox' ? optionsInput.value.split(',').map(option => option.trim()) : null

    let methodItem = new InputItem(observation_type, promptInput.value, options);
    observation_methods.push(methodItem)

    observationMethodCount++;

    // Clear input fields
    promptInput.value = '';
    optionsInput.value = '';

}

// Event listener for selecting an observation method value from dropdown menu
function onDropdownChange() {
    const observationTypeDropdown = document.getElementById('observationType');
    const selectedObservationType = observationTypeDropdown.value;

    const observationMethodDiv = document.createElement('div');
    observationMethodDiv.innerHTML = `
        <label for="prompt${observationMethodCount}">${selectedObservationType} Prompt:</label>
        <input type="text" id="prompt${observationMethodCount}" required>

        <label for="options${observationMethodCount}">${selectedObservationType} Options (must be comma-separated):</label>
        <input type="text" id="options${observationMethodCount}" ${selectedObservationType !== 'Dropdown' &&
        selectedObservationType !== 'Checkbox' ? 'disabled' : ''}>
        <button type="button" onclick="addObservationMethod(${observationMethodCount}, '${selectedObservationType}'); this.disabled = true;">Add Observation Method</button>
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


    let newProject = new Project(projectTitle, projectDescription, observation_methods);

    sendToDatabase('/projects', 'POST', newProject)
        .then(response => {
            code = response.code
            title = response.title
            description = response.description
            return window.location.href = '/view_created_project' + '?' + 'code=' + code +'&' + 'title=' + title +'&' + 'description=' + description
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

document.getElementById('observationType').addEventListener('change', onDropdownChange);


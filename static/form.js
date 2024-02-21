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


const addBtn = document.querySelector(".add");
const input = document.querySelector(".inp-group");

function removeInput(){
    this.parentElement.remove();
}

// Adds an observation method input form
function addInput(){
    const observationMethodTypeSelect = document.getElementById("observationMethodType");
    const observationMethodType = observationMethodTypeSelect.value;

    if (observationMethodType === "") {
        alert("Please select a method type to add!");
        return;
    }

    const prompt = document.createElement("input");
    prompt.type = "text";
    prompt.placeholder = `Enter ${observationMethodType} Prompt`;

    const options = document.createElement("input");
    options.type = "text";
    options.placeholder= "Enter Options (comma separated)";

    if (observationMethodType === "Numerical") {
        options.disabled = true;
        options.placeholder= "No options for numerical entry";
    }


    const btn = document.createElement("a");
    btn.className = "delete";
    btn.innerHTML = "&times";

    btn.addEventListener("click", removeInput);

    const flex = document.createElement("div");
    flex.className = "flex";
    flex.dataset.observationType = observationMethodType;

    input.appendChild(flex);
    flex.appendChild(prompt);
    flex.appendChild(options);
    flex.appendChild(btn);

}

addBtn.addEventListener("click", addInput);

// Creates new project and sets it to the database
function createProject(){
    // Gather observation methods
    const flexDivs = document.querySelectorAll(".flex");
    const numberOfFlexDivs = flexDivs.length;
    if (numberOfFlexDivs === 0) {
        alert("Please add at least one observation method!");
        return;
    }
    if (numberOfFlexDivs > 5) {
        alert("Observation method limit is 5. Please remove surplus methods to proceed.");
        return;
    }
    const inputItems = [];
    flexDivs.forEach((flexDiv, index) => {
        const promptInput = flexDiv.querySelector("input[type='text']:first-child");
        const optionsInput = flexDiv.querySelector("input[type='text']:nth-child(2)");

        const observationType = flexDiv.dataset.observationType;
        const prompt = promptInput.value;
        const options = optionsInput ? optionsInput.value.split(',').map(option => option.trim()) : [];

        const inputItem = new InputItem(observationType, prompt, options);
        if (observationType == "Numerical"){
            inputItem.options = []
        }

        inputItems.push(inputItem);
    });
    // Create new project
    const projectTitle = document.getElementById("projectName").value;
    const projectDescription = document.getElementById("projectDescription").value;
    let newProject = new Project(projectTitle, projectDescription, inputItems);

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
document.getElementById('download-csv').addEventListener('click', function() {

    var csvContent = "Prompt,Value,Student ID,Time & Date\n";
    for (var i = 0; i < projectData[0].parameters.length; i++) {
        for (var j = 0; j < projectData[0].observations_list.length; j++) {
            for (var k = 0; k < projectData[0].observations_list[j].observation_parameters.length; k++) {
                if (projectData[0].observations_list[j].observation_parameters[k].prompt == projectData[0].parameters[i].prompt) {
                    csvContent += projectData[0].parameters[i].prompt + "," +
                                  projectData[0].observations_list[j].observation_parameters[k].value + "," +
                                  projectData[0].observations_list[j].student_id + "," +
                                  projectData[0].observations_list[j].time_date + "\n";
                }
            }
        }
    }

    var blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });

    var link = document.createElement("a");
    if (link.download !== undefined) { 
        var url = URL.createObjectURL(blob);
        link.setAttribute("href", url);
        link.setAttribute("download", projectData[0].code + ".csv");


        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    } else {
        alert("Your browser doesn't support downloading files. Please try again with a different browser.");
    }
});


document.addEventListener("DOMContentLoaded", function() {
    var downloadCSVButton = document.getElementById("downloadCSV");

    if (downloadCSVButton) {
        downloadCSVButton.addEventListener("click", function() {
            var currentDate = new Date();
            var dateString = currentDate.toISOString().slice(0, 19).replace(/:/g, "-"); // Format: YYYY-MM-DDTHH-mm-ss
            var filename = project_code + "_" + dateString + ".csv";

            var csvContent = "data:text/csv;charset=utf-8,";
            csvContent += "Prompt,Value,Student ID,Time and Date,Comment\n";

            for (var prompt in observations_grouped) {
                if (observations_grouped.hasOwnProperty(prompt)) {
                    var observations = observations_grouped[prompt];
                    for (var i = 0; i < observations.length; i++) {
                        var observation = observations[i];
                        csvContent += prompt + "," + observation.value + "," + observation.student_id + "," + observation.time_date + "," + observation.comment + "\n";
                    }
                }
            }

            var encodedUri = encodeURI(csvContent);
            var link = document.createElement("a");
            link.setAttribute("href", encodedUri);
            link.setAttribute("download", filename);
            
            document.body.appendChild(link);
            link.click();
        });
    }
});


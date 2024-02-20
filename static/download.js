
document.addEventListener('DOMContentLoaded', function() {
    var downloadLinks = document.querySelectorAll('.download-csv');

    downloadLinks.forEach(function(link) {
        link.addEventListener('click', function(event) {
            event.preventDefault();
            var project = JSON.parse(this.getAttribute('data-project'));
            var csvContent = "data:text/csv;charset=utf-8,";

            csvContent += "Code,Title,Student ID,Time & Date,Prompt,Value,Comment\n";

            project.observation.forEach(function(obs) {
                var row = `${project.code},${project.title},${project.student_id},${project.time_date},${obs.prompt},${obs.value},${obs.comment}\n`;
                csvContent += row;
            });

            var encodedUri = encodeURI(csvContent);
            var link = document.createElement("a");
            link.setAttribute("href", encodedUri);
            link.setAttribute("download", project.code + ".csv");
            document.body.appendChild(link);

            link.click();
        });
    });
});

function generateGraph(index, observations_grouped) {
    var graphType = document.getElementById('graph-type-' + index).value;
    var data = {};
    
    // Count the frequency of each unique student response
    for (const observation of observations_grouped.values()) {
        for (const item of observation) {
            var response = item.value;
            if (data[response] === undefined) {
                data[response] = 1;
            } else {
                data[response]++;
            }
        }
    }

    var labels = Object.keys(data);
    var counts = Object.values(data);

    var canvas = document.createElement('canvas');
    canvas.id = 'graphCanvas' + index;
    document.getElementById('graph-container-' + index).innerHTML = '';
    document.getElementById('graph-container-' + index).appendChild(canvas);

    var ctx = document.getElementById('graphCanvas' + index).getContext('2d');
    var chart = new Chart(ctx, {
        type: graphType,
        data: {
            labels: labels,
            datasets: [{
                label: 'Frequency',
                data: counts,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Frequency'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Unique Student Responses'
                    }
                }
            }
        }
    });
}

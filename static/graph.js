$(document).ready(function() {
    $('.graph-btn').click(function() {
        const prompt = $(this).data('prompt');
        const obsType = $(this).data('type');

        const relevantData = extractData(projectData, prompt);

        if (obsType === 'Numerical') {
            generateScatterPlot(prompt, relevantData);
        } else if (obsType === 'Dropdown') {
            generateBarChart(prompt, relevantData);
        }
    });

    function extractData(projectData, prompt) {
        const relevantData = [];

        for (const observationSet of projectData[0].observations_list) {
            for (const obsParam of observationSet.observation_parameters) {
                if (obsParam.prompt === prompt) {
                    const time_str = observationSet.time_date;
                    const [date, time] = time_str.split(" ");
                    new_time = convertTimeToDecimal(time)

                    relevantData.push({
                        value: obsParam.value,
                        student_id: observationSet.student_id,
                        date: date,
                        time: new_time 
                    });
                }
            }
        }
        return relevantData;
    }

    function generateScatterPlot(prompt, data) { 
        if (window.myChart && typeof window.myChart.destroy === 'function') {
            window.myChart.destroy();
        }

        var ctx = document.getElementById('myChart').getContext('2d');

        const xValues = data.map(item => item.value);
        const yValues = data.map(item => item.time);

        window.myChart = new Chart(ctx, {
            type: 'scatter',
            data: { 
                labels: xValues,
                datasets: [{
                    label: prompt,
                    data: yValues
                    // Add more styling options here
                }]
            },
            options: {
                scales: {
                    x: {  // Options for the x-axis
                        title: {
                            display: true,
                            text: 'Value' 
                        }
                    },
                    y: {  // Options for the y-axis
                        title: {
                            display: true,
                            text: 'Tine' 
                        }
                    }
                }
            }
            // Add more Chart.js options here for customization
        }); 
    }

    function generateBarChart(prompt, data) {
        if (window.myChart && typeof window.myChart.destroy === 'function') {
            window.myChart.destroy();
        }

        var ctx = document.getElementById('myChart').getContext('2d');

        // Calculate frequencies
        const valueCounts = {};
        data.forEach(item => {
            valueCounts[item.value] = (valueCounts[item.value] || 0) + 1;
        });

        const labels = Object.keys(valueCounts);
        const frequencies = Object.values(valueCounts);
        window.myChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: prompt, 
                    data: frequencies,
                    // Add more styling options here
                }]
            },
            options: {
                scales: {
                    x: {  // Options for the x-axis
                        title: {
                            display: true,
                            text: 'Value' 
                        }
                    },
                    y: {  // Options for the y-axis
                        title: {
                            display: true,
                            text: 'Frequency' 
                        }
                    }
                }
            }
            // Add more Chart.js options here for customization
        });
    }

    function convertTimeToDecimal(time) {
        const [hoursStr, minutesStr, secondsStr] = time.split(":");
        const hours = parseInt(hoursStr, 10);
        const minutes = parseInt(minutesStr, 10) / 60; 
        const seconds = parseInt(secondsStr, 10) / 3600; 
    
        return hours + minutes + seconds;
    }
});

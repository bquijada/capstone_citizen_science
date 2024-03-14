$(document).ready(function() {
    $('.graph-btn').click(function() {
        const prompt = $(this).data('prompt');
        const obsType = $(this).data('type');

        const relevantData = extractData(projectData, prompt);

        if (obsType === 'Numerical') {
            generateScatterPlot(prompt, relevantData);
        } 
        else if (obsType === 'Dropdown') {
            generateBarChart(prompt, relevantData);
        }

        else if (obsType === 'Text'){
            generateWordCloud(relevantData);
        }

        else if (obsType === 'Checkbox'){
            data = checkboxToBarChartData(relevantData);
            generateBarChartFromCheckbox(prompt, data);
        }

        else if (obsType === 'Checklist'){
            data = checkboxToBarChartData(relevantData);
            generateBarChartFromCheckbox(prompt, data);
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
                        time: new_time,
                        datetime: date + "T" + time 
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
        removeWordCloudImage();
        var ctx = document.getElementById('myChart').getContext('2d');
        const yValues = data.map(item => item.value);
        const xValues = data.map(item => item.datetime);
        
        //Handle mins of graph
        var newDate =  new Date(xValues[0])
        var startDate = new Date()
        startDate.setDate(newDate.getDate())
        var endDate = new Date()
        endDate.setDate(newDate.getDate() +1)
        var min = startDate.toISOString().split('T')[0]
        var max = endDate.toISOString().split('T')[0]
        xValues.unshift(min)
        yValues.unshift(null)
        xValues.push(max)
        yValues.push(null)

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
                    x: {
                        type: 'time',
                        time: {
                            unit: 'day',
                            displayFormats: {
                                day: 'yyyy-MM-dd'
                            }
                            
                        },
                        title: {
                            display: true,
                            text: 'Date' 

                        },
                        ticks:{
                            autoSkip: false,
                            maxTicksLimit: 10,
                            stepSize:1,
                            minRotation: 45,
                        }
                    },
                    y: {  // Options for the y-axis
                        title: {
                            display: true,
                            text: 'Value' 
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
        removeWordCloudImage();
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


    function generateWordCloud(relevantData){

       if (window.myChart && typeof window.myChart.destroy === 'function') {
            window.myChart.destroy();
        }
       const valuesArray = relevantData.map(item => item.value);
       const concatenatedString = valuesArray.join(' ');

       if (!concatenatedString || concatenatedString.length === 0) {
        // Send an alert to the user if data is missing
        alert("Cannot generate word cloud without student responses.");
        return;
    }
        fetch('https://capstone-citizen-science.wl.r.appspot.com/wordcloud', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            text: concatenatedString,
        }),
      })
        .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        // Server returns the base64-encoded png image
        return response.text();
    })
        .then(data => {
            console.log(data);
            renderCloud(data);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }

    function renderCloud(imageUrl) {
        const canvasContainer = document.getElementById('myChartContainer');

        // Create img element
        const img = new Image();
        img.id = 'wordCloudImage';
        img.src = `data:image/svg+xml;base64,${imageUrl}`;
        img.alt = 'Word Cloud';

        // Append the img element
        canvasContainer.innerHTML = '';
        canvasContainer.appendChild(img);
}


    function removeWordCloudImage() {
        const wordCloudImage = document.getElementById('wordCloudImage');
        if (wordCloudImage) {
            wordCloudImage.remove();
        }
    }


    function checkboxToBarChartData(relevantData){
        const valuesArray = relevantData.flatMap(item => {
    if (Array.isArray(item.value)) {
        // If item.value is an array, split it into individual items
        return item.value;
    } else {
        // If item.value is not an array, create a new array with the single item
        return [item.value];
    }
    });
    return valuesArray;
    }


    function generateBarChartFromCheckbox(prompt, data) {
        if (window.myChart && typeof window.myChart.destroy === 'function') {
            window.myChart.destroy();
        }
        removeWordCloudImage();
        var ctx = document.getElementById('myChart').getContext('2d');

        // Calculate frequencies
        const valueCounts = {};
        data.forEach(item => {
            valueCounts[item] = (valueCounts[item] || 0) + 1;
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
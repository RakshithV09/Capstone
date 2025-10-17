document.addEventListener('DOMContentLoaded', () => {
    // Single Review Form elements
    const form = document.getElementById('review-form');
    const reviewText = document.getElementById('review-text');
    const resultDiv = document.getElementById('result');

    // CSV Batch Upload elements
    const csvForm = document.getElementById('csv-form');
    const csvFileInput = document.getElementById('csvFile');
    const csvResultDiv = document.getElementById('csv-result');
    const progressBar = document.getElementById('uploadProgress');
    const csvErrorDiv = document.getElementById('csv-error');

    // Chart elements
    const chartContainer = document.getElementById('chart-container');
    let aspectChart = null;

    // Single review submit handler
    form.addEventListener('submit', async e => {
        e.preventDefault();

        const review = reviewText.value.trim();
        if (!review) {
            resultDiv.textContent = 'Please enter a review.';
            chartContainer.style.display = 'none';
            return;
        }

        resultDiv.textContent = 'Analyzing...';
        chartContainer.style.display = 'none';

        try {
            const response = await fetch('/api/predict/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken(),
                },
                body: JSON.stringify({ review }),
            });

            if (!response.ok) {
                throw new Error('Server error: ' + response.statusText);
            }

            const data = await response.json();

            // Robotic styled output block
            let html = `<span style="color:#80ffd0;font-weight:bold;">Overall Sentiment:</span> <span style="color:#fffb8e;">${data.sentiment}</span><br>`;
            if (data.aspects && Object.keys(data.aspects).length > 0) {
                html += `<span style="color:#56ecf1;font-weight:bold;">Aspect Analysis:</span><ul style="margin-top:0.2em;">`;
                const labels = [];
                const values = [];
                for (const [aspect, sentiment] of Object.entries(data.aspects)) {
                    html += `<li><b style="color:#00ffe7">${aspect}</b>: <span style="color:#f788e9;">${sentiment}</span></li>`;
                    labels.push(aspect);
                    let numeric = sentiment.toLowerCase().includes('positive') ? 1 :
                        (sentiment.toLowerCase().includes('negative') ? -1 : 0);
                    values.push(numeric);
                }
                html += `</ul>`;
                drawAspectChart(labels, values);
            } else {
                chartContainer.style.display = 'none';
            }
            if (data.original_language) {
                html += `<br><span style="color:#a7cbf7;font-weight:bold;">Language:</span> <span style="color:#fff;">${data.original_language}</span>`;
            }
            if (data.original_text) {
                html += `<br><span style="color:#a7cbf7;font-weight:bold;">Original Text:</span> <span style="color:#f4f9fb">${data.original_text}</span>`;
            }
            if (data.translated_text && data.translated_text !== data.original_text) {
                html += `<br><span style="color:#a7cbf7;font-weight:bold;">Translated Text:</span> <span style="color:#fde0a1">${data.translated_text}</span>`;
            }

            resultDiv.innerHTML = html;
            resultDiv.style.display = "block";
        } catch (error) {
            resultDiv.textContent = 'Error: ' + error.message;
            chartContainer.style.display = 'none';
        }
    });

    // CSV upload handler with progress and error display
    csvForm.addEventListener('submit', e => {
        e.preventDefault();

        const file = csvFileInput.files[0];
        if (!file) {
            csvResultDiv.textContent = 'Please select a CSV file.';
            return;
        }

        csvResultDiv.textContent = '';
        csvErrorDiv.textContent = '';
        progressBar.style.display = 'block';
        progressBar.value = 0;

        const formData = new FormData();
        formData.append('file', file);

        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/api/upload_csv/', true);
        xhr.setRequestHeader('X-CSRFToken', getCSRFToken());

        xhr.upload.onprogress = function(event) {
            if (event.lengthComputable) {
                progressBar.value = (event.loaded / event.total) * 100;
            }
        };

        xhr.onload = function() {
            progressBar.style.display = 'none';
            if (xhr.status >= 200 && xhr.status < 300) {
                const data = JSON.parse(xhr.responseText);
                csvResultDiv.textContent = `Processed ${data.total_reviews} reviews. Positive: ${data.positive}, Neutral: ${data.neutral}, Negative: ${data.negative}`;
                if (data.download_url) {
                    csvResultDiv.innerHTML += `<br><a href="${data.download_url}" target="_blank" download>Download Results CSV</a>`;
                }
            } else {
                let errMsg = 'Upload failed.';
                try {
                    const errorData = JSON.parse(xhr.responseText);
                    if (errorData.error) errMsg = errorData.error;
                } catch {}
                csvErrorDiv.textContent = errMsg;
            }
        };

        xhr.onerror = function() {
            progressBar.style.display = 'none';
            csvErrorDiv.textContent = 'An error occurred during the upload. Please try again.';
        };

        xhr.send(formData);
    });

    // Function to draw aspect sentiment chart
    function drawAspectChart(labels, values) {
        const ctx = document.getElementById('aspectChart').getContext('2d');
        chartContainer.style.display = 'block';
        if (aspectChart) aspectChart.destroy();
        aspectChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Aspect Sentiment',
                    data: values,
                    backgroundColor: values.map(v => v > 0 ? '#27ae60' : (v < 0 ? '#e74c3c' : '#bdc3c7'))
                }]
            },
            options: {
                scales: {
                    y: {
                        min: -1,
                        max: 1,
                        ticks: {
                            callback: function(value) {
                                return value === 1 ? 'Positive' : (value === 0 ? 'Neutral' : 'Negative');
                            }
                        }
                    }
                }
            }
        });
    }

    // CSRF token helper
    function getCSRFToken() {
        let cookieValue = null;
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith('csrftoken=')) {
                cookieValue = cookie.substring('csrftoken='.length);
                break;
            }
        }
        return cookieValue;
    }
});

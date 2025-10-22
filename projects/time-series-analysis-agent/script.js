// File upload handling
const fileUpload = document.getElementById('fileUpload');
const csvFile = document.getElementById('csvFile');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const removeFile = document.getElementById('removeFile');

csvFile.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        fileName.textContent = file.name;
        fileUpload.style.display = 'none';
        fileInfo.style.display = 'flex';
    }
});

removeFile.addEventListener('click', () => {
    csvFile.value = '';
    fileUpload.style.display = 'block';
    fileInfo.style.display = 'none';
});

// Drag and drop
fileUpload.addEventListener('dragover', (e) => {
    e.preventDefault();
    fileUpload.style.borderColor = '#764ba2';
    fileUpload.style.background = '#f0f2ff';
});

fileUpload.addEventListener('dragleave', () => {
    fileUpload.style.borderColor = '#667eea';
    fileUpload.style.background = '#f8f9ff';
});

fileUpload.addEventListener('drop', (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file && file.name.endsWith('.csv')) {
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        csvFile.files = dataTransfer.files;

        fileName.textContent = file.name;
        fileUpload.style.display = 'none';
        fileInfo.style.display = 'flex';
    } else {
        alert('Please upload a CSV file');
    }
    fileUpload.style.borderColor = '#667eea';
    fileUpload.style.background = '#f8f9ff';
});

// Sample questions
const sampleButtons = document.querySelectorAll('.sample-btn');
const userQuestion = document.getElementById('userQuestion');

sampleButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        const question = btn.getAttribute('data-question');
        userQuestion.value = question;
        userQuestion.focus();
    });
});

// Temperature slider
const temperature = document.getElementById('temperature');
const tempValue = document.getElementById('tempValue');

temperature.addEventListener('input', (e) => {
    tempValue.textContent = e.target.value;
});

// Form submission
const analysisForm = document.getElementById('analysisForm');
const submitBtn = document.getElementById('submitBtn');
const loadingSpinner = document.getElementById('loadingSpinner');
const resultsSection = document.getElementById('resultsSection');

analysisForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Get form data
    const formData = new FormData(analysisForm);
    const file = csvFile.files[0];
    const question = userQuestion.value;
    const model = document.getElementById('modelName').value;
    const temp = parseFloat(temperature.value);
    const showCode = document.getElementById('showCode').checked;
    const showLogs = document.getElementById('showLogs').checked;

    // Validate
    if (!file) {
        alert('Please upload a CSV file');
        return;
    }

    if (!question.trim()) {
        alert('Please enter a question');
        return;
    }

    // Show loading
    loadingSpinner.style.display = 'block';
    resultsSection.style.display = 'none';
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';

    try {
        // Read CSV file
        const csvText = await file.text();

        // Prepare request
        const requestData = {
            csv_data: csvText,
            question: question,
            model_name: model,
            temperature: temp,
            show_code: showCode,
            show_logs: showLogs
        };

        // Make API call (replace with your backend endpoint)
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();

        // Display results
        displayResults(result);

    } catch (error) {
        console.error('Error:', error);
        displayError(error.message);
    } finally {
        loadingSpinner.style.display = 'none';
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-play"></i> Analyze Data';
    }
});

function displayResults(result) {
    resultsSection.style.display = 'block';

    // Status message
    const statusMessage = document.getElementById('statusMessage');
    const status = result.execution?.status || 'unknown';
    const statusEmoji = {
        'success': '✅',
        'no_data': '⚠️',
        'invalid_date': '⚠️',
        'invalid_filter': '⚠️',
        'ambiguous_request': '❓',
        'error': '❌'
    }[status] || 'ℹ️';

    statusMessage.textContent = `${statusEmoji} Status: ${status.toUpperCase()}`;
    statusMessage.className = 'status-message ' + (status === 'success' ? 'success' : status === 'error' ? 'error' : 'warning');

    // Generated code
    const codeSection = document.getElementById('codeSection');
    const generatedCode = document.getElementById('generatedCode');
    if (result.execution?.code && document.getElementById('showCode').checked) {
        generatedCode.textContent = result.execution.code;
        codeSection.style.display = 'block';
    } else {
        codeSection.style.display = 'none';
    }

    // Execution logs
    const logsSection = document.getElementById('logsSection');
    const executionLogs = document.getElementById('executionLogs');
    if (result.execution?.stdout && document.getElementById('showLogs').checked) {
        executionLogs.textContent = result.execution.stdout;
        logsSection.style.display = 'block';
    } else {
        logsSection.style.display = 'none';
    }

    // Answer text
    const answerSection = document.getElementById('answerSection');
    const answerText = document.getElementById('answerText');
    if (result.execution?.answer_text) {
        answerText.innerHTML = formatAnswerText(result.execution.answer_text);
        answerSection.style.display = 'block';
    } else {
        answerSection.style.display = 'none';
    }

    // Visualization (if available)
    const visualSection = document.getElementById('visualSection');
    const visualImage = document.getElementById('visualImage');
    if (result.visualization) {
        visualImage.src = result.visualization;
        visualSection.style.display = 'block';
    } else {
        visualSection.style.display = 'none';
    }

    // Data table
    const tableSection = document.getElementById('tableSection');
    const dataTable = document.getElementById('dataTable');
    if (result.execution?.answer_df) {
        dataTable.innerHTML = formatDataFrame(result.execution.answer_df);
        tableSection.style.display = 'block';
    } else if (result.execution?.answer_json) {
        dataTable.innerHTML = `<pre>${JSON.stringify(result.execution.answer_json, null, 2)}</pre>`;
        tableSection.style.display = 'block';
    } else {
        tableSection.style.display = 'none';
    }

    // Error
    const errorSection = document.getElementById('errorSection');
    const errorMessage = document.getElementById('errorMessage');
    if (result.execution?.error) {
        errorMessage.textContent = result.execution.error;
        errorSection.style.display = 'block';
    } else {
        errorSection.style.display = 'none';
    }

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function displayError(message) {
    resultsSection.style.display = 'block';

    const statusMessage = document.getElementById('statusMessage');
    statusMessage.textContent = '❌ Error occurred';
    statusMessage.className = 'status-message error';

    const errorSection = document.getElementById('errorSection');
    const errorMessage = document.getElementById('errorMessage');
    errorMessage.textContent = message;
    errorSection.style.display = 'block';

    // Hide other sections
    document.getElementById('codeSection').style.display = 'none';
    document.getElementById('logsSection').style.display = 'none';
    document.getElementById('answerSection').style.display = 'none';
    document.getElementById('visualSection').style.display = 'none';
    document.getElementById('tableSection').style.display = 'none';

    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function formatAnswerText(text) {
    // Convert newlines to <br> and preserve formatting
    return text
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>');
}

function formatDataFrame(df) {
    // Simple DataFrame to HTML table conversion
    if (typeof df === 'string') {
        return `<pre>${df}</pre>`;
    }

    // If it's an object, convert to table
    let html = '<table style="width:100%; border-collapse: collapse;">';
    html += '<thead><tr style="background: #667eea; color: white;">';

    const columns = Object.keys(df[0] || {});
    columns.forEach(col => {
        html += `<th style="padding: 12px; text-align: left; border: 1px solid #ddd;">${col}</th>`;
    });
    html += '</tr></thead><tbody>';

    df.forEach((row, idx) => {
        const bgColor = idx % 2 === 0 ? '#f8f9fa' : 'white';
        html += `<tr style="background: ${bgColor};">`;
        columns.forEach(col => {
            html += `<td style="padding: 10px; border: 1px solid #ddd;">${row[col]}</td>`;
        });
        html += '</tr>';
    });

    html += '</tbody></table>';
    return html;
}

// Note: This is a frontend-only implementation
// For production, you'll need a backend API endpoint that:
// 1. Receives CSV data and question
// 2. Processes with Gemini AI
// 3. Executes generated Python code
// 4. Returns results with visualizations

// Demo mode (for testing without backend)
if (window.location.search.includes('demo=true')) {
    console.log('Demo mode enabled');
    analysisForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        loadingSpinner.style.display = 'block';
        resultsSection.style.display = 'none';

        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 2000));

        loadingSpinner.style.display = 'none';

        // Mock response
        const mockResult = {
            execution: {
                status: 'success',
                code: 'monthly = df.set_index("Order_Date").resample("ME")["Revenue"].sum()\nplt.plot(monthly)\nplt.show()',
                stdout: 'LOG: Filtered 10000 rows\nLOG: Generated monthly aggregation',
                answer_text: 'In 2024, Electronics generated $2.3M in revenue across 1,245 orders, showing 15% growth vs 2023. Top product was MacBook Air ($450K).',
                answer_json: null,
                answer_df: null,
                error: null
            }
        };

        displayResults(mockResult);
    });
}

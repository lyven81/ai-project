// Global variables
let salesData = null;
let db = null;
let ordersTable = null;

// Initialize event listeners
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('fileInput');
    const uploadArea = document.getElementById('uploadArea');

    // File input change event
    fileInput.addEventListener('change', handleFileSelect);

    // Drag and drop events
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);

    // Query input enter key
    document.getElementById('queryInput').addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 'Enter') {
            submitQuery();
        }
    });
});

// File handling functions
function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.style.background = 'var(--primary-light)';
}

function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.style.background = 'var(--background-alt)';
}

function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.style.background = 'var(--background-alt)';

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        document.getElementById('fileInput').files = files;
        handleFileSelect({ target: { files: files } });
    }
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.name.endsWith('.csv')) {
        alert('Please upload a CSV file');
        return;
    }

    const reader = new FileReader();
    reader.onload = function(event) {
        try {
            const csvData = event.target.result;
            processCSVData(csvData, file.name);
        } catch (error) {
            alert('Error reading file: ' + error.message);
        }
    };
    reader.readAsText(file);
}

function processCSVData(csvData, fileName) {
    // Parse CSV data
    const lines = csvData.split('\n');
    const headers = lines[0].split(',').map(h => h.trim());

    const data = [];
    for (let i = 1; i < lines.length; i++) {
        if (lines[i].trim()) {
            const values = parseCSVLine(lines[i]);
            const row = {};
            headers.forEach((header, index) => {
                row[header] = values[index] ? values[index].trim() : '';
            });
            data.push(row);
        }
    }

    salesData = data;

    // Calculate statistics
    const stats = calculateStats(data);

    // Display file info
    document.getElementById('fileName').textContent = fileName;
    document.getElementById('recordCount').textContent = data.length.toLocaleString();
    document.getElementById('dateRange').textContent = stats.dateRange;
    document.getElementById('totalRevenue').textContent = stats.totalRevenue;
    document.getElementById('fileInfo').style.display = 'block';

    console.log('Data loaded:', data.length, 'records');
}

function parseCSVLine(line) {
    const result = [];
    let current = '';
    let inQuotes = false;

    for (let i = 0; i < line.length; i++) {
        const char = line[i];

        if (char === '"') {
            inQuotes = !inQuotes;
        } else if (char === ',' && !inQuotes) {
            result.push(current);
            current = '';
        } else {
            current += char;
        }
    }
    result.push(current);

    return result;
}

function calculateStats(data) {
    // Calculate date range
    const dates = data
        .map(row => row.Order_Date)
        .filter(date => date)
        .sort();
    const dateRange = dates.length > 0
        ? `${dates[0]} to ${dates[dates.length - 1]}`
        : 'N/A';

    // Calculate total revenue
    const totalRevenue = data.reduce((sum, row) => {
        const revenue = parseFloat(row.Revenue);
        return sum + (isNaN(revenue) ? 0 : revenue);
    }, 0);

    return {
        dateRange,
        totalRevenue: `$${totalRevenue.toLocaleString(undefined, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        })}`
    };
}

// Query functions
function fillQuery(queryText) {
    document.getElementById('queryInput').value = queryText;
    document.getElementById('queryInput').focus();
}

function submitQuery() {
    const queryInput = document.getElementById('queryInput');
    const query = queryInput.value.trim();

    if (!query) {
        alert('Please enter a question');
        return;
    }

    if (!salesData) {
        alert('Please upload a CSV file first');
        return;
    }

    // Show loading state
    const submitBtn = document.getElementById('submitQuery');
    submitBtn.querySelector('.btn-text').style.display = 'none';
    submitBtn.querySelector('.btn-loader').style.display = 'inline';
    submitBtn.disabled = true;

    // Simulate query processing (in real implementation, this would call the Python backend)
    setTimeout(() => {
        processQuery(query);

        // Reset button
        submitBtn.querySelector('.btn-text').style.display = 'inline';
        submitBtn.querySelector('.btn-loader').style.display = 'none';
        submitBtn.disabled = false;
    }, 2000);
}

function processQuery(query) {
    // This is a mock implementation
    // In a real application, this would send the query to a Python backend

    const result = generateMockResult(query);
    displayResults(result);
}

function generateMockResult(query) {
    // Generate a mock result based on the query
    const queryLower = query.toLowerCase();

    let answer = '';
    let code = '';
    let debugLog = '';
    let error = null;

    if (queryLower.includes('total sales') || queryLower.includes('revenue')) {
        const totalRevenue = salesData.reduce((sum, row) => {
            return sum + (parseFloat(row.Revenue) || 0);
        }, 0);

        answer = `Total sales revenue is $${totalRevenue.toLocaleString(undefined, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        })} across ${salesData.length} orders.`;

        code = `# Calculate total revenue
orders = orders_tbl.all()
total_revenue = sum(o['Revenue'] for o in orders)
answer_text = f"Total sales revenue is $${total_revenue:,.2f} across {len(orders)} orders."`;

        debugLog = `Processing ${salesData.length} records\nCalculating total revenue`;
    } else if (queryLower.includes('region')) {
        const regions = {};
        salesData.forEach(row => {
            const region = row.Region || 'Unknown';
            regions[region] = (regions[region] || 0) + (parseFloat(row.Revenue) || 0);
        });

        const topRegion = Object.entries(regions).sort((a, b) => b[1] - a[1])[0];

        answer = `${topRegion[0]} region generated the highest revenue with $${topRegion[1].toLocaleString(undefined, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        })}.`;

        code = `# Calculate revenue by region
from collections import defaultdict
region_revenue = defaultdict(float)
for order in orders_tbl.all():
    region_revenue[order['Region']] += order['Revenue']
top_region = max(region_revenue.items(), key=lambda x: x[1])
answer_text = f"{top_region[0]} region generated the highest revenue with $${top_region[1]:,.2f}."`;

        debugLog = `Analyzing ${Object.keys(regions).length} regions\nFound top region: ${topRegion[0]}`;
    } else if (queryLower.includes('product')) {
        const products = {};
        salesData.forEach(row => {
            const product = row.Product_Name || 'Unknown';
            products[product] = (products[product] || 0) + (parseFloat(row.Revenue) || 0);
        });

        const topProducts = Object.entries(products)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 5);

        answer = `Top 5 products by revenue: ${topProducts.map((p, i) =>
            `${i + 1}. ${p[0]} ($${p[1].toLocaleString()})`
        ).join(', ')}.`;

        code = `# Calculate top products by revenue
from collections import defaultdict
product_revenue = defaultdict(float)
for order in orders_tbl.all():
    product_revenue[order['Product_Name']] += order['Revenue']
top_5 = sorted(product_revenue.items(), key=lambda x: x[1], reverse=True)[:5]
answer_text = "Top 5 products: " + ", ".join([f"{p[0]} ($${p[1]:,.2f})" for p in top_5])`;

        debugLog = `Analyzing ${Object.keys(products).length} unique products\nIdentified top 5 by revenue`;
    } else {
        answer = `Analysis complete for: "${query}". This is a demo response. In a production environment, the AI would generate specific Python code to analyze your data and provide detailed insights.`;

        code = `# Custom query analysis
# The AI would generate specific code based on your question
answer_text = "Analysis results would appear here"`;

        debugLog = 'Query processed\nDemo mode active';
    }

    return {
        answer,
        code,
        debugLog,
        error
    };
}

function displayResults(result) {
    // Show results section
    const resultsSection = document.getElementById('resultsSection');
    resultsSection.style.display = 'block';

    // Populate answer
    document.getElementById('answerText').textContent = result.answer;

    // Populate code
    document.getElementById('generatedCode').textContent = result.code;

    // Show/hide debug logs
    if (result.debugLog) {
        document.getElementById('debugLogs').textContent = result.debugLog;
        document.getElementById('debugBox').style.display = 'block';
    } else {
        document.getElementById('debugBox').style.display = 'none';
    }

    // Show/hide error
    if (result.error) {
        document.getElementById('errorText').textContent = result.error;
        document.getElementById('errorBox').style.display = 'block';
    } else {
        document.getElementById('errorBox').style.display = 'none';
    }

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Helper function to format currency
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(value);
}

// Console info
console.log('%c Sales Dashboard Agent ', 'background: #10b981; color: white; font-size: 16px; padding: 5px;');
console.log('Web interface loaded. Upload a CSV file to begin analysis.');

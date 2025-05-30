// JavaScript for the Admission Probability Calculator

document.addEventListener('DOMContentLoaded', function() {
    const calculatorForm = document.getElementById('calculatorForm');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const resultsContainer = document.getElementById('resultsContainer');
    const errorContainer = document.getElementById('errorContainer');
    const errorMessage = document.getElementById('errorMessage');
    const noResultsContainer = document.getElementById('noResultsContainer');
    const resultsTableBody = document.getElementById('resultsTableBody');
    const resultsSummary = document.getElementById('resultsSummary');
    
    calculatorForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Get form values
        const score = parseFloat(document.getElementById('score').value);
        const group = document.getElementById('group').value;
        const sector = document.getElementById('sector').value;
        const topN = parseInt(document.getElementById('topN').value);
        
        // Validate inputs
        if (isNaN(score) || score < 0 || score > 700) {
            showError('Please enter a valid score between 0 and 700.');
            return;
        }
        
        if (!group) {
            showError('Please select a group.');
            return;
        }
        
        // Show loading indicator
        hideAllContainers();
        loadingIndicator.classList.remove('d-none');
        
        // Prepare request data
        const requestData = {
            score: score,
            group: group,
            sector: sector,
            topN: topN
        };
        
        // Send API request
        fetch('/api/calculate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'An error occurred during calculation.');
                });
            }
            return response.json();
        })
        .then(data => {
            hideAllContainers();
            
            if (data.results && data.results.length > 0) {
                displayResults(data);
            } else {
                noResultsContainer.classList.remove('d-none');
            }
        })
        .catch(error => {
            hideAllContainers();
            errorMessage.textContent = error.message;
            errorContainer.classList.remove('d-none');
        });
    });
    
    function hideAllContainers() {
        loadingIndicator.classList.add('d-none');
        resultsContainer.classList.add('d-none');
        errorContainer.classList.add('d-none');
        noResultsContainer.classList.add('d-none');
    }
    
    function showError(message) {
        hideAllContainers();
        errorMessage.textContent = message;
        errorContainer.classList.remove('d-none');
    }
    
    function displayResults(data) {
        // Clear previous results
        resultsTableBody.innerHTML = '';
        
        // Update summary
        const metadata = data.metadata;
        resultsSummary.innerHTML = `
            Showing ${data.results.length} results for score <strong>${metadata.score}</strong>, 
            group <strong>${metadata.group}</strong>, 
            sector <strong>${metadata.sector}</strong>.
        `;
        
        // Add results to table
        data.results.forEach(result => {
            const row = document.createElement('tr');
            
            // Determine probability class for color coding
            let probabilityClass = '';
            let probabilityDisplay = 'N/A';
            
            if (result.probability !== null) {
                probabilityDisplay = result.probability.toFixed(2) + '%';
                
                if (result.probability >= 75) {
                    probabilityClass = 'probability-high';
                } else if (result.probability >= 40) {
                    probabilityClass = 'probability-medium';
                } else {
                    probabilityClass = 'probability-low';
                }
            } else {
                probabilityClass = 'insufficient-data';
            }
            
            // Format mean and std dev
            const meanDisplay = result.mean !== null ? result.mean.toFixed(2) : 'N/A';
            const stdDevDisplay = result.stdDev !== null ? result.stdDev.toFixed(2) : 'N/A';
            
            row.innerHTML = `
                <td>${result.specialty}</td>
                <td class="${probabilityClass}">${probabilityDisplay}</td>
                <td>${result.status}</td>
                <td>${meanDisplay}</td>
                <td>${stdDevDisplay}</td>
                <td>${result.dataPoints}</td>
            `;
            
            resultsTableBody.appendChild(row);
        });
        
        // Show results container
        resultsContainer.classList.remove('d-none');
    }
});

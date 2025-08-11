document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('upload-form');
    const fileUpload = document.getElementById('file-upload');
    const loadingDiv = document.getElementById('loading');
    const resultDiv = document.getElementById('result');
    const errorDiv = document.getElementById('error');
    const resultImage = document.getElementById('result-image');
    const diseaseName = document.getElementById('disease-name');
    const confidenceSpan = document.getElementById('confidence');
    const confidenceBar = document.getElementById('confidence-bar');
    const tryAgainBtn = document.getElementById('try-again');
    const recommendationContent = document.getElementById('recommendation-content');

    // Disease recommendations mapping
    const recommendations = {
        'Apple - Apple scab': `
            <ul>
                <li>Remove and destroy fallen leaves in autumn to reduce fungal spores.</li>
                <li>Apply fungicides at bud break and during the growing season.</li>
                <li>Improve air circulation by proper pruning.</li>
                <li>Consider planting scab-resistant apple varieties.</li>
            </ul>
        `,
        'Apple - Black rot': `
            <ul>
                <li>Prune out dead or diseased wood, cankers, and mummified fruits.</li>
                <li>Apply fungicides during the growing season, especially after rainy periods.</li>
                <li>Maintain proper tree spacing for good air circulation.</li>
                <li>Remove dropped fruit promptly.</li>
            </ul>
        `,
        'Apple - Cedar apple rust': `
            <ul>
                <li>Remove cedar trees (juniper) within a 1/2 mile radius if possible.</li>
                <li>Apply fungicides in spring when flower buds turn pink.</li>
                <li>Plant rust-resistant apple varieties.</li>
                <li>Maintain good tree health through proper fertilization and watering.</li>
            </ul>
        `,
        'Apple - healthy': `
            <ul>
                <li>Continue regular monitoring for early signs of disease.</li>
                <li>Maintain proper pruning and orchard sanitation.</li>
                <li>Follow a recommended fertilization schedule.</li>
                <li>Ensure adequate watering, especially during dry periods.</li>
            </ul>
        `,
        'Corn - Cercospora leaf spot': `
            <ul>
                <li>Rotate crops with non-host plants for at least one year.</li>
                <li>Apply appropriate fungicides if disease is severe.</li>
                <li>Plant resistant varieties when available.</li>
                <li>Ensure proper field drainage and avoid overhead irrigation.</li>
            </ul>
        `,
        'Corn - Common rust': `
            <ul>
                <li>Plant rust-resistant corn hybrids.</li>
                <li>Apply foliar fungicides in early growth stages if disease pressure is high.</li>
                <li>Practice crop rotation with non-host crops.</li>
                <li>Maintain optimal plant nutrition and avoid excessive nitrogen.</li>
            </ul>
        `,
        'Corn - healthy': `
            <ul>
                <li>Continue regular field monitoring for early disease detection.</li>
                <li>Maintain proper soil fertility and pH.</li>
                <li>Ensure adequate drainage and irrigation.</li>
                <li>Practice crop rotation to prevent disease buildup.</li>
            </ul>
        `,
        'Corn - Northern Leaf Blight': `
            <ul>
                <li>Plant resistant hybrids when available.</li>
                <li>Apply fungicides if disease appears before tasseling.</li>
                <li>Practice crop rotation with non-host crops for at least one year.</li>
                <li>Reduce surface crop residue through tillage where appropriate.</li>
            </ul>
        `,
        'default': `
            <ul>
                <li>Consult with a local extension office or plant pathologist.</li>
                <li>Remove affected plant parts to prevent disease spread.</li>
                <li>Consider appropriate fungicides or treatments based on the specific disease.</li>
                <li>Improve growing conditions including soil health, drainage, and air circulation.</li>
            </ul>
        `
    };

    // Handle form submission
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Check if file is selected
        if (!fileUpload.files[0]) {
            showError('Please select an image file');
            return;
        }

        // Hide previous results and errors
        resultDiv.classList.add('d-none');
        errorDiv.classList.add('d-none');
        
        // Show loading spinner
        loadingDiv.classList.remove('d-none');
        
        // Create form data
        const formData = new FormData();
        formData.append('file', fileUpload.files[0]);
        
        // Send request to server
        fetch('/predict', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // Hide loading spinner
            loadingDiv.classList.add('d-none');
            
            if (data.success) {
                // Display results
                resultImage.src = '/' + data.image_path;
                diseaseName.textContent = data.disease;
                
                // Format confidence to 2 decimal places
                const formattedConfidence = data.confidence.toFixed(2);
                confidenceSpan.textContent = formattedConfidence;
                confidenceBar.style.width = `${data.confidence}%`;
                
                // Set appropriate color for confidence bar
                if (data.confidence > 80) {
                    confidenceBar.className = 'progress-bar bg-success';
                } else if (data.confidence > 60) {
                    confidenceBar.className = 'progress-bar bg-info';
                } else if (data.confidence > 40) {
                    confidenceBar.className = 'progress-bar bg-warning';
                } else {
                    confidenceBar.className = 'progress-bar bg-danger';
                }
                
                // Add disease-specific recommendations
                const recommendationHTML = recommendations[data.disease] || recommendations['default'];
                recommendationContent.innerHTML = recommendationHTML;
                
                // Show results
                resultDiv.classList.remove('d-none');
            } else {
                showError(data.error || 'An error occurred during prediction');
            }
        })
        .catch(error => {
            loadingDiv.classList.add('d-none');
            showError('Network error. Please try again.');
            console.error('Error:', error);
        });
    });
    
    // Try again button
    tryAgainBtn.addEventListener('click', function() {
        resultDiv.classList.add('d-none');
        uploadForm.reset();
    });
    
    // Function to show error message
    function showError(message) {
        errorDiv.textContent = message;
        errorDiv.classList.remove('d-none');
    }
    
    // Preview image before upload
    fileUpload.addEventListener('change', function() {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                // You could add image preview functionality here if desired
            }
            reader.readAsDataURL(file);
        }
    });
});
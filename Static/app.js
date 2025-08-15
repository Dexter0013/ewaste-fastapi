// Application data
const appData = {
  "e_waste_categories": [
    {
      "id": "phone",
      "name": "Smartphones & Mobile Devices",
      "description": "Mobile phones, tablets, smartwatches, and accessories",
      "recycling_info": "Contains valuable materials like gold, silver, and rare earth elements. Take to certified e-waste facility.",
      "environmental_impact": "One smartphone contains 0.034g of gold and other precious metals.",
      "average_lifespan": "2-3 years"
    },
    {
      "id": "laptop",
      "name": "Laptops",
      "description": "Portable computers designed for mobile use",
      "recycling_info": "Contains valuable metals and components. Hard drives require data destruction before recycling.",
      "environmental_impact": "A laptop contains about 2g of silver and 0.1g of gold.",
      "average_lifespan": "4-6 years"
    },
    {
      "id": "monitor",
      "name": "Monitors",
      "description": "CRT, LCD, LED, and OLED displays",
      "recycling_info": "Contains lead and mercury. Requires specialized recycling facilities.",
      "environmental_impact": "Monitors contain 4-5 pounds of lead per unit.",
      "average_lifespan": "7-10 years"
    },
    {
      "id": "Battery",
      "name": "Batteries",
      "description": "Lithium-ion, lead-acid, and other battery types",
      "recycling_info": "Highly toxic if disposed improperly. Requires specialized battery recycling.",
      "environmental_impact": "Lithium-ion batteries can contaminate 40,000 liters of water if landfilled.",
      "average_lifespan": "2-5 years"
    },
    {
      "id": "pcb",
      "name": "Circuit Boards (PCBs)",
      "description": "Printed circuit boards from various electronic devices",
      "recycling_info": "Contains gold, silver, copper, and palladium. Valuable for precious metal recovery.",
      "environmental_impact": "1 ton of PCBs contains more gold than 17 tons of gold ore.",
      "average_lifespan": "Device dependent"
    },
    {
      "id": "cables",
      "name": "Cables & Wires",
      "description": "Power cords, USB cables, and other wiring",
      "recycling_info": "Contains copper and other metals. Can be recycled at e-waste facilities.",
      "environmental_impact": "Improper disposal can lead to soil and water contamination.",
      "average_lifespan": "Varies by type"
    },
    {
      "id": "mouse",
      "name": "Mice & Input Devices",
      "description": "Computer mice, keyboards, and other input devices",
      "recycling_info": "Contains plastics and metals. Can be recycled at e-waste facilities.",
      "environmental_impact": "Improper disposal can lead to soil and water contamination.",
      "average_lifespan": "Varies by type"
    },
    {
      "id": "keyboard",
      "name": "Keyboards",
      "description": "Computer keyboards and other input devices",
      "recycling_info": "Contains plastics and metals. Can be recycled at e-waste facilities.",
      "environmental_impact": "Improper disposal can lead to soil and water contamination.",
      "average_lifespan": "Varies by type"
    }
  ]
};

// Set your FastAPI backend URL here
const API_URL = 'http://localhost:8000/predict'; // Adjust as needed for production

// DOM Elements
let navToggle, navMenu, uploadArea, fileInput, processBtn, clearBtn;
let resultsContainer;

// State
let currentFile = null;

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    // Initialize DOM elements
    initializeDOMElements();
    
    // Initialize components
    initializeNavigation();
    initializeUpload();
    initializeStats();
    populateCategories();
    
    // Setup form submission
    const form = document.getElementById('upload-form');
    form.addEventListener('submit', handleFormSubmit);
    
    console.log('E-Waste Classifier application initialized successfully');
});

// Initialize DOM elements
function initializeDOMElements() {
    navToggle = document.getElementById('nav-toggle');
    navMenu = document.getElementById('nav-menu');
    uploadArea = document.getElementById('upload-area');
    fileInput = document.getElementById('file-input');
    processBtn = document.getElementById('process-btn');
    clearBtn = document.getElementById('clear-btn');
    resultsContainer = document.getElementById('results-container');
}

// Navigation functionality
function initializeNavigation() {
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', () => {
            navToggle.classList.toggle('active');
            navMenu.classList.toggle('active');
        });
    }

    // Handle navigation links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const target = link.getAttribute('href');
            if (target) {
                scrollToSection(target.substring(1));
                
                // Update active state
                document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
                link.classList.add('active');
                
                // Close mobile menu
                if (navToggle && navMenu) {
                    navToggle.classList.remove('active');
                    navMenu.classList.remove('active');
                }
            }
        });
    });
}

// Smooth scroll to section
function scrollToSection(sectionId) {
    const element = document.getElementById(sectionId);
    if (element) {
        const offsetTop = element.offsetTop - 80; // Account for fixed header
        window.scrollTo({
            top: offsetTop,
            behavior: 'smooth'
        });
    }
}

// Statistics animation
function initializeStats() {
    const observerOptions = {
        threshold: 0.5,
        rootMargin: '0px 0px -100px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateStats();
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    const statsSection = document.querySelector('.stats-grid');
    if (statsSection) {
        observer.observe(statsSection);
    }
}

function animateStats() {
    const statNumbers = document.querySelectorAll('.stat-number');
    
    statNumbers.forEach(stat => {
        const target = parseInt(stat.getAttribute('data-target'));
        const duration = 2000; // 2 seconds
        const increment = target / (duration / 16); // 60 FPS
        let current = 0;

        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                stat.textContent = formatNumber(target);
                clearInterval(timer);
            } else {
                stat.textContent = formatNumber(Math.floor(current));
            }
        }, 16);
    });
}

function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(0) + 'K';
    } else {
        return num.toString();
    }
}

// Upload functionality
function initializeUpload() {
    if (!uploadArea || !fileInput) {
        console.error('Upload elements not found');
        return;
    }

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    // Highlight drop area when item is dragged over it
    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, unhighlight, false);
    });


    // Prevent double processing using a flag
    let dropJustHandled = false;

    // Handle dropped files
    uploadArea.addEventListener('drop', (e) => {
        console.log('Drop event fired');
        dropJustHandled = true;
        handleDrop(e);
        // Clear file input so change event doesn't fire after drop
        setTimeout(() => { fileInput.value = ''; }, 0);
    }, false);

    // Handle click to select files
    uploadArea.addEventListener('click', () => fileInput.click());

    // File input change handler
    fileInput.addEventListener('change', (e) => {
        console.log('File input change event fired');
        if (dropJustHandled) {
            dropJustHandled = false;
            console.log('Change event ignored due to recent drop');
            return;
        }
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });

    // Clear button handler
    clearBtn.addEventListener('click', clearFile);

    console.log('Upload functionality initialized');
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function highlight() {
    uploadArea.classList.add('drag-over');
}

function unhighlight() {
    uploadArea.classList.remove('drag-over');
}

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

function handleFile(file) {
    if (!validateFile(file)) return;
    
    currentFile = file;
    processBtn.disabled = false;
    
    // Show preview
    showPreview(file);
    showNotification('Image ready for processing', 'success');
}

function validateFile(file) {
    const maxSize = 200 * 1024 * 1024; // 200MB for videos
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'video/mp4', 'video/webm'];

    if (file.size > maxSize) {
        showNotification('File too large. Maximum size is 200MB.', 'error');
        return false;
    }

    if (!allowedTypes.includes(file.type)) {
        showNotification('Unsupported file type. Please upload JPG, PNG, MP4, or WEBM.', 'error');
        return false;
    }

    return true;
}

function clearFile() {
    currentFile = null;
    fileInput.value = '';
    processBtn.disabled = true;
    resultsContainer.innerHTML = `
        <div class="no-results">
            <i class="fas fa-search"></i>
            <p>No results yet. Upload an image to get started!</p>
        </div>
    `;
    showNotification('Image cleared', 'info');
}

function showPreview(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
        if (file.type.startsWith('image/')) {
            resultsContainer.innerHTML = `
                <img src="${e.target.result}" alt="Preview" class="result-image" style="max-width:600px;display:block;margin:0 auto;">
                <p>Image ready for processing</p>
            `;
        } else if (file.type.startsWith('video/')) {
            resultsContainer.innerHTML = `
                <video controls style="max-width:600px;display:block;margin:0 auto;">
                    <source src="${e.target.result}" type="${file.type}">
                    Your browser does not support the video tag.
                </video>
                <p>Video ready for processing</p>
            `;
        }
    };
    reader.readAsDataURL(file);
}

// Form submission
// Update the handleFormSubmit function to handle video processing
async function handleFormSubmit(e) {
    e.preventDefault();
    
    if (!currentFile) {
        showNotification('Please select a file first', 'warning');
        return;
    }
    
    try {
        // Show appropriate processing message
        if (currentFile.type.startsWith('image/')) {
            resultsContainer.innerHTML = '<div class="processing-animation"><div class="spinner"></div><p>Processing image...</p></div>';
        } else if (currentFile.type.startsWith('video/')) {
            resultsContainer.innerHTML = '<div class="processing-animation"><div class="spinner"></div><p>Processing video... This may take a moment</p></div>';
        }
        
        const formData = new FormData();
        formData.append('file', currentFile);
        
        const response = await fetch(API_URL, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`Server responded with ${response.status}`);
        }
        
        const data = await response.json();
        displayResults(data);
        showNotification('Processing completed!', 'success');
        scrollToSection('results');
    } catch (err) {
        console.error('Error:', err);
        resultsContainer.innerHTML = `
            <div class="error">
                <i class="fas fa-exclamation-circle"></i>
                <p>Error: ${err.message}</p>
            </div>
        `;
        showNotification('Processing failed. Please try again.', 'error');
    }
}

// Update the displayResults function to handle video results
function displayResults(data) {
    let html = '';

    // Show output image or video with bounding boxes
    if (data.type === 'image' && data.image) {
        html += `
        <div style="display: flex; flex-direction: column; align-items: center; margin-bottom: 32px;">
            <img src="data:image/jpeg;base64,${data.image}" alt="Result" class="result-image" style="max-width:600px;width:100%;border-radius:16px;box-shadow:0 4px 24px rgba(0,0,0,0.12);margin-bottom:16px;">
            <div style="font-size:1.1rem;color:#222;font-weight:500;margin-top:16px;">Classification Result</div>
        </div>
        `;

        // Detection Summary (styled like video layout)
        if (data.boxes && data.boxes.length > 0) {
            html += '<div class="video-summary">';
            html += '<h4>Detection Summary</h4>';
            html += '<div class="category-summary-grid">';

            data.boxes.forEach(box => {
                const category = appData.e_waste_categories.find(cat => cat.id.toLowerCase() === box.class_name.toLowerCase()) || 
                                 { name: box.class_name, recycling_info: '', environmental_impact: '' };

                html += `
                    <div class="category-summary-item">
                        <div class="category-summary-header">
                            <span class="category-name">${category.name}</span>
                            <span class="category-count">${(box.confidence * 100).toFixed(1)}%</span>
                        </div>
                        <div class="category-summary-details">
                            <p><strong>Recycling:</strong> ${category.recycling_info}</p>
                            <p><strong>Impact:</strong> ${category.environmental_impact}</p>
                            <p><small>Position: [x: ${box.x}, y: ${box.y}, w: ${box.width}, h: ${box.height}]</small></p>
                        </div>
                    </div>
                `;
            });

            html += '</div></div>'; // close grid and summary
        } else {
            html += '<p>No e-waste items detected in this image.</p>';
        }
    }

    else if (data.type === 'video' && data.video) {
        html += `
        <div style="display: flex; flex-direction: column; align-items: center; margin-bottom: 32px;">
            <video controls autoplay style="max-width:600px;width:100%;border-radius:16px;box-shadow:0 4px 24px rgba(0,0,0,0.12);margin-bottom:16px;">
                <source src="data:video/mp4;base64,${data.video}" type="video/mp4">
                Your browser does not support the video tag.
            </video>
            <div style="font-size:1.1rem;color:#222;font-weight:500;margin-top:16px;">Video Analysis Results (${data.frame_count} frames processed)</div>
        </div>
        `;
        
        // Show video summary statistics
        if (data.frames && data.frames.length > 0) {
            // Count detections per category
            const categoryCounts = {};
            data.frames.forEach(frame => {
                frame.boxes.forEach(box => {
                    const categoryName = box.class_name.toLowerCase();
                    categoryCounts[categoryName] = (categoryCounts[categoryName] || 0) + 1;
                });
            });
            
            // Create summary
            html += '<div class="video-summary">';
            html += '<h4>Detection Summary</h4>';
            
            if (Object.keys(categoryCounts).length > 0) {
                html += '<div class="category-summary-grid">';
                Object.entries(categoryCounts).forEach(([categoryId, count]) => {
                    const category = appData.e_waste_categories.find(cat => cat.id.toLowerCase() === categoryId) || 
                                    { name: categoryId, recycling_info: '', environmental_impact: '' };
                    
                    html += `
                        <div class="category-summary-item">
                            <div class="category-summary-header">
                                <span class="category-name">${category.name}</span>
                                <span class="category-count">${count} detections</span>
                            </div>
                            <div class="category-summary-details">
                                <p><strong>Recycling:</strong> ${category.recycling_info}</p>
                            </div>
                        </div>
                    `;
                });
                html += '</div>';
            } else {
                html += '<p>No e-waste items detected in this video.</p>';
            }
            
            html += '</div>'; // Close video-summary
            
            // Add frame-by-frame details (collapsible)
            html += `
            <div class="frame-details">
                <button class="toggle-frame-details btn btn--secondary">
                    <i class="fas fa-chevron-down"></i>
                    Show Frame-by-Frame Details
                </button>
                <div class="frame-details-content" style="display:none;">
                    <h4>Detailed Frame Analysis</h4>
                    <div class="frame-list">
            `;
            
            data.frames.forEach((frame, frameIndex) => {
                if (frame.boxes.length > 0) {
                    html += `
                        <div class="frame-item">
                            <h5>Frame ${frameIndex + 1}</h5>
                        `;
                    
                    frame.boxes.forEach(box => {
                        const category = appData.e_waste_categories.find(cat => cat.id.toLowerCase() === box.class_name.toLowerCase()) || 
                                        { name: box.class_name, recycling_info: '', environmental_impact: '' };
                        
                        html += `
                            <div class="frame-detection">
                                <span class="detection-category">${category.name}</span>
                                <span class="detection-confidence">${(box.confidence * 100).toFixed(1)}%</span>
                            </div>
                        `;
                    });
                    
                    html += '</div>';
                }
            });
            
            html += `
                    </div>
                </div>
            </div>
            `;
        }
    } 
    else {
        html += '<p>No results to display.</p>';
    }

    resultsContainer.innerHTML = html;
    
    // Add event listener for frame details toggle
    const toggleBtn = resultsContainer.querySelector('.toggle-frame-details');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            const content = resultsContainer.querySelector('.frame-details-content');
            const icon = toggleBtn.querySelector('i');
            if (content.style.display === 'none') {
                content.style.display = 'block';
                icon.classList.remove('fa-chevron-down');
                icon.classList.add('fa-chevron-up');
                toggleBtn.innerHTML = toggleBtn.innerHTML.replace('Show', 'Hide');
            } else {
                content.style.display = 'none';
                icon.classList.remove('fa-chevron-up');
                icon.classList.add('fa-chevron-down');
                toggleBtn.innerHTML = toggleBtn.innerHTML.replace('Hide', 'Show');
            }
        });
    }
}

// Categories population
function populateCategories() {
    const categoriesContainer = document.querySelector('.categories-container');
    if (!categoriesContainer) return;
    
    appData.e_waste_categories.forEach(category => {
        const categoryCard = document.createElement('div');
        categoryCard.className = 'category-card';
        
        categoryCard.innerHTML = `
            <h4>${category.name}</h4>
            <p>${category.description}</p>
            <div class="category-lifespan">Average lifespan: ${category.average_lifespan}</div>
        `;
        
        categoriesContainer.appendChild(categoryCard);
    });
}

// Notification system
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas ${getNotificationIcon(type)}"></i>
            <span>${message}</span>
        </div>
        <button class="notification-close">
            <i class="fas fa-times"></i>
        </button>
    `;

    // Add to document
    document.body.appendChild(notification);

    // Auto remove after 4 seconds
    const autoRemoveTimer = setTimeout(() => {
        removeNotification(notification);
    }, 4000);

    // Manual close
    const closeBtn = notification.querySelector('.notification-close');
    closeBtn.addEventListener('click', () => {
        clearTimeout(autoRemoveTimer);
        removeNotification(notification);
    });
}

function removeNotification(notification) {
    notification.style.animation = 'slideOutRight 0.3s ease';
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 300);
}

function getNotificationIcon(type) {
    switch (type) {
        case 'success': return 'fa-check-circle';
        case 'error': return 'fa-exclamation-circle';
        case 'warning': return 'fa-exclamation-triangle';
        default: return 'fa-info-circle';
    }
}

// Global functions
window.scrollToSection = scrollToSection;
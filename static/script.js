document.addEventListener("DOMContentLoaded", () => {
    // 1. Drag and Drop Functionality
    const dropZone = document.getElementById("dropZone");
    const fileInput = document.getElementById("fileInput");
    const fileInfo = document.getElementById("fileInfo");
    const uploadForm = document.getElementById("uploadForm");
    const loader = document.getElementById("loader");
    const detectBtn = document.getElementById("detectBtn");

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    // Highlight drop zone
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
    });

    // Handle dropped files
    dropZone.addEventListener('drop', (e) => {
        let dt = e.dataTransfer;
        let files = dt.files;
        fileInput.files = files; // Assign files to hidden input
        updateFileInfo(files[0]);
    });

    // Handle browse click files
    fileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            updateFileInfo(this.files[0]);
        }
    });

    function updateFileInfo(file) {
        if (file) {
            fileInfo.innerHTML = `<span class="text-cyan"><i class="fa-solid fa-file-image"></i> ${file.name}</span> Ready for analysis.`;
        }
    }

    // 2. Form Submission & Loading Animation
    uploadForm.addEventListener('submit', (e) => {
        if (fileInput.files.length === 0) {
            e.preventDefault();
            alert("Please upload an image first.");
            return;
        }

        // Show loading state before Flask processes and reloads
        detectBtn.style.display = "none";
        loader.style.display = "block";

        // Let the form submit naturally to the Flask backend
    });

    // 3. Scroll Reveal Animations (Intersection Observer)
    const fadeElements = document.querySelectorAll('.fade-in');
    const observerOptions = {
        threshold: 0.1,
        rootMargin: "0px 0px -50px 0px"
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');

                // Trigger counter animation if it's the stats section
                if (entry.target.classList.contains('stats-section')) {
                    animateCounters();
                }
            }
        });
    }, observerOptions);

    fadeElements.forEach(el => observer.observe(el));

    // 4. Statistics Counter Animation
    let countersAnimated = false;

    function animateCounters() {
        if (countersAnimated) return;
        countersAnimated = true;

        const counters = document.querySelectorAll('.stat-number');
        counters.forEach(counter => {
            const target = parseFloat(counter.getAttribute('data-target'));
            const duration = 2000; // 2 seconds
            const increment = target / (duration / 16); // 60fps
            let current = 0;

            const updateCounter = () => {
                current += increment;
                if (current < target) {
                    // Check if it's a decimal number
                    counter.innerText = target % 1 !== 0 ? current.toFixed(1) : Math.ceil(current);
                    requestAnimationFrame(updateCounter);
                } else {
                    counter.innerText = target;
                }
            };
            updateCounter();
        });
    }

    // 5. Setup result progress bar animation on load if Jinja template generated it
    const resultSection = document.getElementById("resultSection");
    if (resultSection) {
        // Automatically scroll to result
        setTimeout(() => {
            resultSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 300);
    }
});
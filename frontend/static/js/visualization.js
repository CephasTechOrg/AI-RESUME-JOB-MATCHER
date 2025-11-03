let scoresChart = null;

// Enhanced chart creation with better mobile responsiveness
function createScoresChart(scores) {
    const ctx = document.getElementById('scoresChart').getContext('2d');

    // Destroy existing chart if it exists
    if (scoresChart) {
        scoresChart.destroy();
    }

    const labels = Object.keys(scores).map(key =>
        key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    );

    const data = Object.values(scores);

    // Enhanced color coding based on scores
    const backgroundColors = data.map(score => {
        if (score >= 80) return '#10b981'; // Green
        if (score >= 60) return '#f59e0b'; // Yellow
        return '#ef4444'; // Red
    });

    const borderColors = data.map(color => color);

    // Enhanced chart configuration for better mobile experience
    scoresChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Score',
                data: data,
                backgroundColor: backgroundColors,
                borderColor: borderColors,
                borderWidth: 2,
                borderRadius: 8,
                borderSkipped: false,
                barPercentage: 0.7,
                categoryPercentage: 0.8,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: {
                    top: 20,
                    right: 20,
                    bottom: 10,
                    left: 10
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)',
                        drawBorder: false,
                    },
                    ticks: {
                        callback: function (value) {
                            return value + '%';
                        },
                        font: {
                            family: "'Inter', 'Segoe UI', sans-serif",
                            size: window.innerWidth < 768 ? 10 : 12
                        },
                        color: '#64748b',
                        padding: 10,
                    }
                },
                x: {
                    grid: {
                        display: false,
                        drawBorder: false,
                    },
                    ticks: {
                        font: {
                            family: "'Inter', 'Segoe UI', sans-serif",
                            size: window.innerWidth < 768 ? 10 : 12
                        },
                        color: '#64748b',
                        maxRotation: window.innerWidth < 768 ? 45 : 0,
                        padding: 10,
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(37, 99, 235, 0.95)',
                    titleFont: {
                        family: "'Inter', 'Segoe UI', sans-serif",
                        size: 12
                    },
                    bodyFont: {
                        family: "'Inter', 'Segoe UI', sans-serif",
                        size: 11
                    },
                    padding: 12,
                    cornerRadius: 8,
                    displayColors: false,
                    callbacks: {
                        label: function (context) {
                            return `Score: ${context.parsed.y}%`;
                        },
                        title: function (context) {
                            return context[0].label;
                        }
                    }
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeOutQuart'
            },
            interaction: {
                intersect: false,
                mode: 'index',
            }
        }
    });

    // Add resize event listener for better mobile responsiveness
    window.addEventListener('resize', function () {
        if (scoresChart) {
            scoresChart.update();
        }
    });
}
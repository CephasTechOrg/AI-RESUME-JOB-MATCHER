let scoresChart = null;

// Create scores chart
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
    const backgroundColors = data.map(score => {
        if (score >= 80) return '#10b981'; // Green
        if (score >= 60) return '#f59e0b'; // Yellow
        return '#ef4444'; // Red
    });

    scoresChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Score',
                data: data,
                backgroundColor: backgroundColors,
                borderColor: backgroundColors.map(color => color),
                borderWidth: 1,
                borderRadius: 8,
                borderSkipped: false,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            aspectRatio: 2,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function (value) {
                            return value + '%';
                        },
                        font: {
                            family: "'Inter', 'Segoe UI', sans-serif"
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    ticks: {
                        font: {
                            family: "'Inter', 'Segoe UI', sans-serif"
                        }
                    },
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(37, 99, 235, 0.9)',
                    titleFont: {
                        family: "'Inter', 'Segoe UI', sans-serif"
                    },
                    bodyFont: {
                        family: "'Inter', 'Segoe UI', sans-serif"
                    },
                    callbacks: {
                        label: function (context) {
                            return `Score: ${context.parsed.y}%`;
                        }
                    }
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeOutQuart'
            }
        }
    });
}
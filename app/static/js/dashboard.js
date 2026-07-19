document.addEventListener('DOMContentLoaded', function () {
    const dataElement = document.getElementById('review-data');
    if (!dataElement) return;

    let reviewData = [];
    try {
        reviewData = JSON.parse(dataElement.textContent);
    } catch (e) {
        console.error('Error parsing review data:', e);
        return;
    }

    if (reviewData.length === 0) {
        const chartContainer = document.querySelector('.chart-container');
        if (chartContainer) {
            chartContainer.innerHTML = '<div class="text-center py-5 text-muted">No data available yet. Please complete a code review.</div>';
        }
        return;
    }

    // Limit trend chart to last 10 reviews
    const recentData = reviewData.slice(-10);

    const labels = recentData.map((item, index) => item.date || `Review #${index + 1}`);
    const scores = recentData.map(item => item.score);

    const ctx = document.getElementById('scoreTrendChart');
    if (!ctx) return;

    new Chart(ctx.getContext('2d'), {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Overall Quality Score',
                data: scores,
                fill: true,
                backgroundColor: 'rgba(13, 110, 253, 0.05)',
                borderColor: 'rgba(13, 110, 253, 0.8)',
                borderWidth: 3,
                pointBackgroundColor: 'rgba(13, 110, 253, 1)',
                pointBorderColor: '#fff',
                pointHoverRadius: 6,
                pointHoverBackgroundColor: 'rgba(13, 110, 253, 1)',
                pointHoverBorderColor: '#fff',
                pointRadius: 4,
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function (context) {
                            return ` Score: ${context.parsed.y}%`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            family: "'Segoe UI', sans-serif",
                            size: 11
                        }
                    }
                },
                y: {
                    min: 0,
                    max: 100,
                    grid: {
                        color: '#f0f0f0'
                    },
                    ticks: {
                        stepSize: 20,
                        font: {
                            family: "'Segoe UI', sans-serif",
                            size: 11
                        }
                    }
                }
            }
        }
    });
});

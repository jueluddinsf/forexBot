document.addEventListener('DOMContentLoaded', function() {
    // Performance Chart
    const ctx = document.getElementById('performanceChart').getContext('2d');
    const performanceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [], // Will be populated with dates
            datasets: [{
                label: 'Account Balance',
                data: [], // Will be populated with balance history
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: false
                }
            }
        }
    });

    // Function to update chart data
    function updateChartData() {
        fetch('/api/performance')
            .then(response => response.json())
            .then(data => {
                performanceChart.data.labels = data.dates;
                performanceChart.data.datasets[0].data = data.balances;
                performanceChart.update();
            });
    }

    // Update chart initially and every 5 minutes
    updateChartData();
    setInterval(updateChartData, 300000);
});

// Function to close trade
function closeTrade(tradeId) {
    if (confirm('Are you sure you want to close this trade?')) {
        fetch(`/api/close_trade/${tradeId}`, {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Failed to close trade');
            }
        });
    }
}

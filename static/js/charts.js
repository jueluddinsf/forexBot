document.addEventListener('DOMContentLoaded', function() {
    // Performance Chart
    const performanceCtx = document.getElementById('performanceChart').getContext('2d');
    const performanceChart = new Chart(performanceCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Account Balance',
                data: [],
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1,
                fill: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            }
        }
    });

    // P/L Distribution Chart
    const pnlCtx = document.getElementById('pnlDistributionChart').getContext('2d');
    const pnlDistributionChart = new Chart(pnlCtx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Daily P/L Distribution',
                data: [],
                backgroundColor: 'rgba(75, 192, 192, 0.5)',
                borderColor: 'rgb(75, 192, 192)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            }
        }
    });

    // Win Rate Chart
    const winRateCtx = document.getElementById('winRateChart').getContext('2d');
    const winRateChart = new Chart(winRateCtx, {
        type: 'doughnut',
        data: {
            labels: [],
            datasets: [{
                data: [],
                backgroundColor: [
                    'rgba(75, 192, 192, 0.5)',
                    'rgba(255, 99, 132, 0.5)'
                ],
                borderColor: [
                    'rgb(75, 192, 192)',
                    'rgb(255, 99, 132)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                }
            }
        }
    });

    // Risk Chart
    const riskCtx = document.getElementById('riskChart').getContext('2d');
    const riskChart = new Chart(riskCtx, {
        type: 'radar',
        data: {
            labels: ['Market Risk', 'Drawdown Risk', 'Leverage Risk', 'Correlation Risk', 'Volatility Risk'],
            datasets: [{
                label: 'Current Risk Profile',
                data: [],
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgb(75, 192, 192)',
                borderWidth: 2,
                pointBackgroundColor: 'rgb(75, 192, 192)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                }
            },
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        stepSize: 20
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    pointLabels: {
                        font: {
                            size: 12
                        }
                    }
                }
            }
        }
    });

    // Function to update all charts
    function updateCharts() {
        fetch('/api/performance_analytics')
            .then(response => response.json())
            .then(data => {
                // Update Performance Chart
                performanceChart.data.labels = data.performance.dates;
                performanceChart.data.datasets[0].data = data.performance.balances;
                performanceChart.update();

                // Update P/L Distribution Chart
                pnlDistributionChart.data.labels = data.pnl_distribution.labels;
                pnlDistributionChart.data.datasets[0].data = data.pnl_distribution.values;
                pnlDistributionChart.update();

                // Update Win Rate Chart
                winRateChart.data.labels = ['Wins', 'Losses'];
                winRateChart.data.datasets[0].data = [data.win_rate.wins, data.win_rate.losses];
                winRateChart.update();

                // Update Risk Chart
                riskChart.data.datasets[0].data = [
                    data.risk_metrics.market_risk,
                    data.risk_metrics.drawdown_risk,
                    data.risk_metrics.leverage_risk,
                    data.risk_metrics.correlation_risk,
                    data.risk_metrics.volatility_risk
                ];
                riskChart.update();
            });
    }

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

    // Update charts initially and every 5 minutes
    updateCharts();
    setInterval(updateCharts, 300000);
});

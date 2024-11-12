document.addEventListener('DOMContentLoaded', function() {
    // Chart status indicator
    const chartStatus = document.getElementById('chartStatus');
    const lastUpdateTime = document.getElementById('lastUpdateTime');
    
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

    // Enhanced retry configuration
    const MAX_RETRIES = 3;
    const BASE_RETRY_DELAY = 5000; // 5 seconds
    const MAX_RETRY_DELAY = 30000; // 30 seconds
    const ERROR_MESSAGES = {
        404: 'No performance data available yet',
        500: 'Server error occurred while fetching data',
        default: 'Unable to fetch performance data'
    };
    let retryCount = 0;

    // Function to show error message to user
    function showErrorMessage(status, message) {
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger alert-dismissible fade show';
        alertDiv.setAttribute('role', 'alert');
        alertDiv.innerHTML = `
            <strong>Error:</strong> ${message || ERROR_MESSAGES[status] || ERROR_MESSAGES.default}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        // Remove any existing error messages
        document.querySelectorAll('.alert-danger').forEach(el => el.remove());
        
        // Insert the new error message before the charts
        const firstChart = document.querySelector('.chart-container');
        if (firstChart) {
            firstChart.parentNode.insertBefore(alertDiv, firstChart);
        }
    }

    // Function to update chart status
    function updateChartStatus(status, message) {
        if (chartStatus) {
            chartStatus.className = `badge bg-${status}`;
            chartStatus.textContent = message;
        }
    }

    // Function to update all charts with enhanced retry mechanism
    function updateCharts() {
        updateChartStatus('warning', 'Updating...');

        function fetchData() {
            fetch('/api/performance_analytics')
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    try {
                        if (data.error) {
                            throw new Error(data.error);
                        }

                        // Reset retry count on successful fetch
                        retryCount = 0;

                        // Validate and update Performance Chart
                        if (data.performance && Array.isArray(data.performance.dates) && 
                            Array.isArray(data.performance.balances) && 
                            data.performance.dates.length === data.performance.balances.length) {
                            performanceChart.data.labels = data.performance.dates;
                            performanceChart.data.datasets[0].data = data.performance.balances;
                            performanceChart.update();
                        } else {
                            console.warn('Invalid performance data structure');
                        }

                        // Validate and update P/L Distribution Chart
                        if (data.pnl_distribution && Array.isArray(data.pnl_distribution.labels) && 
                            Array.isArray(data.pnl_distribution.values) &&
                            data.pnl_distribution.labels.length === data.pnl_distribution.values.length) {
                            pnlDistributionChart.data.labels = data.pnl_distribution.labels;
                            pnlDistributionChart.data.datasets[0].data = data.pnl_distribution.values;
                            pnlDistributionChart.update();
                        } else {
                            console.warn('Invalid P/L distribution data structure');
                        }

                        // Validate and update Win Rate Chart
                        if (data.win_rate && typeof data.win_rate.wins === 'number' && 
                            typeof data.win_rate.losses === 'number') {
                            winRateChart.data.labels = ['Wins', 'Losses'];
                            winRateChart.data.datasets[0].data = [
                                data.win_rate.wins,
                                data.win_rate.losses
                            ];
                            winRateChart.update();
                        } else {
                            console.warn('Invalid win rate data structure');
                        }

                        // Validate and update Risk Chart
                        if (data.risk_metrics && typeof data.risk_metrics === 'object') {
                            const metrics = data.risk_metrics;
                            const riskData = [
                                metrics.market_risk || 0,
                                metrics.drawdown_risk || 0,
                                metrics.leverage_risk || 0,
                                metrics.correlation_risk || 0,
                                metrics.volatility_risk || 0
                            ];
                            riskChart.data.datasets[0].data = riskData;
                            riskChart.update();
                        } else {
                            console.warn('Invalid risk metrics data structure');
                        }

                        // Update last update time
                        if (lastUpdateTime && data.performance && data.performance.last_update) {
                            try {
                                lastUpdateTime.textContent = new Date(data.performance.last_update).toLocaleString();
                            } catch (e) {
                                console.warn('Error formatting last update time:', e);
                            }
                        }

                        // Update status
                        updateChartStatus('success', 'Updated');
                        
                        // Remove any existing error messages
                        document.querySelectorAll('.alert-danger').forEach(el => el.remove());

                    } catch (error) {
                        console.error('Error processing chart data:', error);
                        handleError('Data processing error', error.message);
                    }
                })
                .catch(error => {
                    console.error('Error fetching performance data:', error);
                    const status = error.response?.status;
                    handleError('Connection error', status);
                });
        }

        function handleError(errorType, status) {
            updateChartStatus('danger', 'Update Failed');
            showErrorMessage(status, ERROR_MESSAGES[status]);

            // Enhanced retry mechanism with exponential backoff
            if (retryCount < MAX_RETRIES) {
                retryCount++;
                const delay = Math.min(BASE_RETRY_DELAY * Math.pow(2, retryCount - 1), MAX_RETRY_DELAY);
                
                updateChartStatus('warning', `Retrying (${retryCount}/${MAX_RETRIES}) in ${delay/1000}s...`);
                
                console.log(`Retrying in ${delay}ms (attempt ${retryCount}/${MAX_RETRIES})`);
                setTimeout(fetchData, delay);
            } else {
                updateChartStatus('danger', 'Update Failed (Max retries)');
                showErrorMessage(status, 'Failed to update after multiple attempts');
                console.error(`Failed to update after ${MAX_RETRIES} attempts`);
                // Reset retry count for next update cycle
                retryCount = 0;
            }
        }

        // Start the fetch process
        fetchData();
    }

    // Function to close trade
    window.closeTrade = function(tradeId) {
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

    // Install pytz for timezone support
    fetch('/api/install_dependencies', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            dependencies: ['pytz']
        })
    });

    // Update charts initially and every minute
    updateCharts();
    setInterval(updateCharts, 60000);
});
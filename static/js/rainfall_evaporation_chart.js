// rainfall_evaporation_chart.js - Dual Axis Chart (Bar + Line combo)
export function rainfall_evaporation_chart(containerId, chartData) {
    let myChart = echarts.init(document.getElementById(containerId));
    
    // Expects 2 datasets: rainfall (bar) and evaporation (line)
    let rainfallData = chartData.datasets[0] ? chartData.datasets[0].values : [];
    let evaporationData = chartData.datasets[1] ? chartData.datasets[1].values : [];
    
    let option = {
        title: {
            text: 'Rainfall vs Evaporation',
            left: 'center',
            textStyle: {
                fontSize: 14,
                fontWeight: 'normal',
                color: '#333'
            }
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'cross',
                crossStyle: {
                    color: '#999'
                }
            }
        },
        legend: {
            data: ['Evaporation', 'Rainfall'],
            bottom: '0%',
            icon: 'circle'
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '12%',
            top: '15%',
            containLabel: true
        },
        xAxis: [
            {
                type: 'category',
                data: chartData.labels,
                axisPointer: {
                    type: 'shadow'
                },
                axisLine: {
                    lineStyle: {
                        color: '#ddd'
                    }
                },
                axisLabel: {
                    color: '#666',
                    fontSize: 10
                }
            }
        ],
        yAxis: [
            {
                type: 'value',
                name: 'Rainfall',
                position: 'left',
                axisLabel: {
                    formatter: '{value}',
                    color: '#666'
                },
                splitLine: {
                    lineStyle: {
                        type: 'dashed',
                        color: '#f0f0f0'
                    }
                }
            },
            {
                type: 'value',
                name: 'Evaporation',
                position: 'right',
                axisLabel: {
                    formatter: '{value}',
                    color: '#666'
                },
                splitLine: {
                    show: false
                }
            }
        ],
        series: [
            {
                name: 'Evaporation',
                type: 'line',
                yAxisIndex: 1,
                data: evaporationData,
                smooth: true,
                showSymbol: true,
                symbolSize: 6,
                lineStyle: {
                    color: '#5470C6',
                    width: 2
                },
                itemStyle: {
                    color: '#5470C6'
                }
            },
            {
                name: 'Rainfall',
                type: 'bar',
                data: rainfallData,
                itemStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: '#7FFF00' },  // Chartreuse green at top
                        { offset: 0.5, color: '#FFD700' }, // Gold in middle
                        { offset: 1, color: '#FF4500' }    // Orange-red at bottom
                    ])
                },
                barMaxWidth: 40,
                barCategoryGap: '40%'
            }
        ]
    };

    myChart.setOption(option);
    
    window.addEventListener('resize', function() {
        myChart.resize();
    });
}
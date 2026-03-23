// confidence_band_chart.js - Confidence Band Chart (Line with Upper/Lower Bounds)
export function confidence_band_chart(containerId, chartData) {
    let myChart = echarts.init(document.getElementById(containerId));
    
    // Main data line
    let mainData = chartData.datasets[0] ? chartData.datasets[0].values : [];
    
    // Calculate confidence bands (±10% as example)
    let upperBound = mainData.map(val => val * 1.1);
    let lowerBound = mainData.map(val => val * 0.9);
    
    let option = {
        title: {
            text: chartData.datasets[0] ? chartData.datasets[0].label : 'Confidence Band',
            subtext: 'Example in Meteorology/Statistics',
            left: 'center',
            textStyle: {
                fontSize: 14,
                fontWeight: 'normal'
            }
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'cross'
            }
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '10%',
            top: '15%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            boundaryGap: false,
            data: chartData.labels,
            axisLine: {
                lineStyle: {
                    color: '#999'
                }
            }
        },
        yAxis: {
            type: 'value',
            axisLine: {
                lineStyle: {
                    color: '#999'
                }
            },
            splitLine: {
                lineStyle: {
                    type: 'dashed',
                    color: '#e0e0e0'
                }
            }
        },
        series: [
            {
                name: 'L',
                type: 'line',
                data: lowerBound,
                lineStyle: {
                    opacity: 0
                },
                stack: 'confidence-band',
                symbol: 'none'
            },
            {
                name: 'U',
                type: 'line',
                data: upperBound.map((val, idx) => val - lowerBound[idx]),
                lineStyle: {
                    opacity: 0
                },
                areaStyle: {
                    color: 'rgba(200, 200, 200, 0.2)'
                },
                stack: 'confidence-band',
                symbol: 'none'
            },
            {
                name: 'Main Line',
                type: 'line',
                data: mainData,
                smooth: true,
                showSymbol: false,
                lineStyle: {
                    width: 2,
                    color: '#333'
                }
            }
        ]
    };

    myChart.setOption(option);
    
    window.addEventListener('resize', function() {
        myChart.resize();
    });
}
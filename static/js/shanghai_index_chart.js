// shanghai_index_chart.js - Stock Index Chart with Moving Averages and Volume
export function shanghai_index_chart(containerId, chartData) {
    let myChart = echarts.init(document.getElementById(containerId));
    
    // Prepare candlestick data
    let candleData = [];
    let volumes = [];
    
    for (let i = 0; i < chartData.labels.length; i++) {
        let open = chartData.datasets[0] ? chartData.datasets[0].values[i] : 0;
        let close = chartData.datasets[1] ? chartData.datasets[1].values[i] : 0;
        let low = chartData.datasets[2] ? chartData.datasets[2].values[i] : 0;
        let high = chartData.datasets[3] ? chartData.datasets[3].values[i] : 0;
        let volume = chartData.datasets[4] ? chartData.datasets[4].values[i] : 0;
        
        candleData.push([open, close, low, high]);
        volumes.push([i, volume, open > close ? 1 : -1]);
    }
    
    // Calculate simple moving averages
    function calculateMA(dayCount, data) {
        let result = [];
        for (let i = 0; i < data.length; i++) {
            if (i < dayCount - 1) {
                result.push('-');
                continue;
            }
            let sum = 0;
            for (let j = 0; j < dayCount; j++) {
                sum += data[i - j][1]; // close price
            }
            result.push((sum / dayCount).toFixed(2));
        }
        return result;
    }
    
    let option = {
        title: {
            text: 'ShangHai Index',
            left: 0
        },
        legend: {
            data: ['K-Line', 'MA5', 'MA10', 'MA20', 'MA30'],
            top: 30
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'cross'
            }
        },
        grid: [
            {
                left: '10%',
                right: '8%',
                height: '50%'
            },
            {
                left: '10%',
                right: '8%',
                top: '65%',
                height: '16%'
            }
        ],
        xAxis: [
            {
                type: 'category',
                data: chartData.labels,
                boundaryGap: false,
                axisLine: { onZero: false },
                splitLine: { show: false },
                min: 'dataMin',
                max: 'dataMax'
            },
            {
                type: 'category',
                gridIndex: 1,
                data: chartData.labels,
                boundaryGap: false,
                axisLine: { onZero: false },
                axisTick: { show: false },
                splitLine: { show: false },
                axisLabel: { show: false },
                min: 'dataMin',
                max: 'dataMax'
            }
        ],
        yAxis: [
            {
                scale: true,
                splitArea: {
                    show: true
                }
            },
            {
                scale: true,
                gridIndex: 1,
                splitNumber: 2,
                axisLabel: { show: false },
                axisLine: { show: false },
                axisTick: { show: false },
                splitLine: { show: false }
            }
        ],
        dataZoom: [
            {
                type: 'inside',
                xAxisIndex: [0, 1],
                start: 70,
                end: 100
            }
        ],
        series: [
            {
                name: 'K-Line',
                type: 'candlestick',
                data: candleData,
                itemStyle: {
                    color: '#ef232a',
                    color0: '#14b143',
                    borderColor: '#ef232a',
                    borderColor0: '#14b143'
                }
            },
            {
                name: 'MA5',
                type: 'line',
                data: calculateMA(5, candleData),
                smooth: true,
                lineStyle: {
                    opacity: 0.5,
                    width: 1
                }
            },
            {
                name: 'MA10',
                type: 'line',
                data: calculateMA(10, candleData),
                smooth: true,
                lineStyle: {
                    opacity: 0.5,
                    width: 1
                }
            },
            {
                name: 'MA20',
                type: 'line',
                data: calculateMA(20, candleData),
                smooth: true,
                lineStyle: {
                    opacity: 0.5,
                    width: 1
                }
            },
            {
                name: 'MA30',
                type: 'line',
                data: calculateMA(30, candleData),
                smooth: true,
                lineStyle: {
                    opacity: 0.5,
                    width: 1
                }
            },
            {
                name: 'Volume',
                type: 'bar',
                xAxisIndex: 1,
                yAxisIndex: 1,
                data: volumes,
                itemStyle: {
                    color: function(params) {
                        return params.data[2] > 0 ? '#ef232a' : '#14b143';
                    }
                }
            }
        ]
    };

    myChart.setOption(option);
    
    window.addEventListener('resize', function() {
        myChart.resize();
    });
}
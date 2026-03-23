// candlestick_brush_chart.js - Candlestick Chart with Brush Selection and Volume
export function candlestick_brush_chart(containerId, chartData) {
    let myChart = echarts.init(document.getElementById(containerId));
    
    // Prepare candlestick and volume data
    let candleData = [];
    let volumeData = [];
    
    for (let i = 0; i < chartData.labels.length; i++) {
        let open = chartData.datasets[0] ? chartData.datasets[0].values[i] : 0;
        let close = chartData.datasets[1] ? chartData.datasets[1].values[i] : 0;
        let low = chartData.datasets[2] ? chartData.datasets[2].values[i] : 0;
        let high = chartData.datasets[3] ? chartData.datasets[3].values[i] : 0;
        let volume = chartData.datasets[4] ? chartData.datasets[4].values[i] : Math.random() * 1000;
        
        candleData.push([open, close, low, high]);
        volumeData.push(volume);
    }
    
    // Calculate moving averages
    function calculateMA(dayCount, data) {
        let result = [];
        for (let i = 0; i < data.length; i++) {
            if (i < dayCount - 1) {
                result.push('-');
                continue;
            }
            let sum = 0;
            for (let j = 0; j < dayCount; j++) {
                sum += data[i - j][1];
            }
            result.push((sum / dayCount).toFixed(2));
        }
        return result;
    }
    
    let option = {
        title: {
            text: 'Candlestick Brush',
            left: 0
        },
        legend: {
            data: ['K-Line', 'MA5', 'MA10', 'MA20', 'MA30'],
            top: 30,
            textStyle: {
                fontSize: 10
            }
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
                start: 40,
                end: 70
            },
            {
                show: true,
                xAxisIndex: [0, 1],
                type: 'slider',
                bottom: '2%',
                start: 40,
                end: 70
            }
        ],
        brush: {
            xAxisIndex: 'all',
            brushLink: 'all',
            outOfBrush: {
                colorAlpha: 0.1
            }
        },
        series: [
            {
                name: 'K-Line',
                type: 'candlestick',
                data: candleData,
                itemStyle: {
                    color: '#00da3c',
                    color0: '#ec0000',
                    borderColor: '#00da3c',
                    borderColor0: '#ec0000'
                }
            },
            {
                name: 'MA5',
                type: 'line',
                data: calculateMA(5, candleData),
                smooth: true,
                lineStyle: {
                    opacity: 0.6,
                    width: 1
                }
            },
            {
                name: 'MA10',
                type: 'line',
                data: calculateMA(10, candleData),
                smooth: true,
                lineStyle: {
                    opacity: 0.6,
                    width: 1
                }
            },
            {
                name: 'MA20',
                type: 'line',
                data: calculateMA(20, candleData),
                smooth: true,
                lineStyle: {
                    opacity: 0.6,
                    width: 1
                }
            },
            {
                name: 'MA30',
                type: 'line',
                data: calculateMA(30, candleData),
                smooth: true,
                lineStyle: {
                    opacity: 0.6,
                    width: 1
                }
            },
            {
                name: 'Volume',
                type: 'bar',
                xAxisIndex: 1,
                yAxisIndex: 1,
                data: volumeData,
                itemStyle: {
                    color: function(params) {
                        let dataIndex = params.dataIndex;
                        let isRise = candleData[dataIndex] && candleData[dataIndex][1] >= candleData[dataIndex][0];
                        return isRise ? '#00da3c' : '#ec0000';
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
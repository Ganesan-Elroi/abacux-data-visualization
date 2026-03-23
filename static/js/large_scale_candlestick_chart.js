// large_scale_candlestick_chart.js - Large Scale Candlestick with Data Amount Display
export function large_scale_candlestick_chart(containerId, chartData) {
    let myChart = echarts.init(document.getElementById(containerId));
    
    // Prepare candlestick data
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
    
    // Calculate data amount for display
    let dataAmount = chartData.labels.length;
    
    let option = {
        title: {
            text: `Data Amount: ${dataAmount.toLocaleString()}`,
            right: '10%',
            top: '5%',
            textStyle: {
                fontSize: 12,
                fontWeight: 'normal',
                color: '#666'
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
                left: '5%',
                right: '5%',
                height: '55%',
                top: '10%'
            },
            {
                left: '5%',
                right: '5%',
                top: '68%',
                height: '20%'
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
                max: 'dataMax',
                axisPointer: {
                    z: 100
                }
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
                    show: false
                },
                splitLine: {
                    lineStyle: {
                        color: '#f0f0f0'
                    }
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
                start: 80,
                end: 100
            },
            {
                show: true,
                xAxisIndex: [0, 1],
                type: 'slider',
                bottom: '5%',
                start: 80,
                end: 100,
                height: 20
            }
        ],
        series: [
            {
                name: 'Candlestick',
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
                name: 'Volume',
                type: 'bar',
                xAxisIndex: 1,
                yAxisIndex: 1,
                data: volumeData,
                itemStyle: {
                    color: function(params) {
                        let dataIndex = params.dataIndex;
                        let isRise = candleData[dataIndex] && candleData[dataIndex][1] >= candleData[dataIndex][0];
                        return isRise ? 'rgba(0, 218, 60, 0.5)' : 'rgba(236, 0, 0, 0.5)';
                    }
                },
                barMaxWidth: 5
            }
        ]
    };

    myChart.setOption(option);
    
    window.addEventListener('resize', function() {
        myChart.resize();
    });
}
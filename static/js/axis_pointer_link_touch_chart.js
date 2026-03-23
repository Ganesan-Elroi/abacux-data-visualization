// axis_pointer_link_touch_chart.js - Multiple Charts with Linked Axis Pointer
export function axis_pointer_link_touch_chart(containerId, chartData) {
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
    
    let option = {
        title: {
            text: 'Axis Pointer Link and Touch',
            left: 'center',
            textStyle: {
                fontSize: 14
            }
        },
        axisPointer: {
            link: [
                {
                    xAxisIndex: 'all'
                }
            ],
            label: {
                backgroundColor: '#777'
            }
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'cross'
            },
            backgroundColor: 'rgba(245, 245, 245, 0.9)',
            borderWidth: 1,
            borderColor: '#ccc',
            padding: 10,
            textStyle: {
                color: '#000'
            }
        },
        grid: [
            {
                left: '10%',
                right: '8%',
                height: '50%',
                top: '12%'
            },
            {
                left: '10%',
                right: '8%',
                top: '67%',
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
                max: 'dataMax',
                axisPointer: {
                    z: 100,
                    label: {
                        show: true
                    }
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
                max: 'dataMax',
                axisPointer: {
                    label: {
                        show: true
                    }
                }
            }
        ],
        yAxis: [
            {
                scale: true,
                axisPointer: {
                    label: {
                        show: true
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
                start: 70,
                end: 100
            },
            {
                show: true,
                xAxisIndex: [0, 1],
                type: 'slider',
                bottom: '1%',
                start: 70,
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
                    color: '#ef232a',
                    color0: '#14b143',
                    borderColor: '#ef232a',
                    borderColor0: '#14b143'
                },
                emphasis: {
                    itemStyle: {
                        borderWidth: 2
                    }
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
                        return isRise ? 'rgba(239, 35, 42, 0.5)' : 'rgba(20, 177, 67, 0.5)';
                    }
                },
                barMaxWidth: 8
            }
        ]
    };

    myChart.setOption(option);
    
    window.addEventListener('resize', function() {
        myChart.resize();
    });
}
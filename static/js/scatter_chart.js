// scatter_chart.js - Scatter Plot for correlation analysis
export function scatter_chart(containerId, chartData) {
    let myChart = echarts.init(document.getElementById(containerId));
    
    // Prepare scatter data - expects 2 value columns
    let scatterData = [];
    for (let i = 0; i < chartData.labels.length; i++) {
        let xValue = chartData.datasets[0] ? chartData.datasets[0].values[i] : 0;
        let yValue = chartData.datasets[1] ? chartData.datasets[1].values[i] : 0;
        scatterData.push([xValue, yValue, chartData.labels[i]]);
    }
    
    let option = {
        tooltip: {
            trigger: 'item',
            formatter: function(params) {
                return `${params.value[2]}<br/>
                        ${chartData.datasets[0].label}: ${params.value[0]}<br/>
                        ${chartData.datasets[1].label}: ${params.value[1]}`;
            }
        },
        grid: {
            left: '3%',
            right: '7%',
            bottom: '10%',
            containLabel: true
        },
        xAxis: {
            type: 'value',
            name: chartData.datasets[0] ? chartData.datasets[0].label : 'X',
            splitLine: {
                lineStyle: {
                    type: 'dashed'
                }
            }
        },
        yAxis: {
            type: 'value',
            name: chartData.datasets[1] ? chartData.datasets[1].label : 'Y',
            splitLine: {
                lineStyle: {
                    type: 'dashed'
                }
            }
        },
        series: [{
            name: 'Correlation',
            type: 'scatter',
            symbolSize: 20,
            data: scatterData,
            itemStyle: {
                color: new echarts.graphic.RadialGradient(0.5, 0.5, 1, [
                    { offset: 0, color: '#188df0' },
                    { offset: 1, color: '#83bff6' }
                ]),
                shadowBlur: 10,
                shadowColor: 'rgba(25, 100, 150, 0.5)',
                shadowOffsetY: 5
            },
            emphasis: {
                itemStyle: {
                    shadowBlur: 20,
                    shadowColor: 'rgba(25, 100, 150, 0.8)'
                }
            }
        }]
    };

    myChart.setOption(option);
    
    window.addEventListener('resize', function() {
        myChart.resize();
    });
}
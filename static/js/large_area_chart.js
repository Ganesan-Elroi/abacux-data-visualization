// large_area_chart.js - Large Scale Area Chart with Gradient
export function large_area_chart(containerId, chartData) {
    let myChart = echarts.init(document.getElementById(containerId));
    
    // Create gradient area with pink/coral colors
    let option = {
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'cross',
                label: {
                    backgroundColor: '#6a7985'
                }
            }
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '10%',
            top: '5%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            boundaryGap: false,
            data: chartData.labels,
            axisLabel: {
                fontSize: 10,
                color: '#666'
            },
            axisLine: {
                lineStyle: {
                    color: '#ddd'
                }
            }
        },
        yAxis: {
            type: 'value',
            axisLabel: {
                fontSize: 10,
                color: '#666'
            },
            splitLine: {
                lineStyle: {
                    color: '#f0f0f0'
                }
            }
        },
        series: chartData.datasets.map((ds, index) => {
            return {
                name: ds.label,
                type: 'line',
                smooth: true,
                showSymbol: false,
                lineStyle: {
                    width: 0
                },
                areaStyle: {
                    opacity: 0.8,
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        {
                            offset: 0,
                            color: 'rgba(255, 99, 132, 0.8)'
                        },
                        {
                            offset: 0.5,
                            color: 'rgba(255, 159, 64, 0.5)'
                        },
                        {
                            offset: 1,
                            color: 'rgba(255, 205, 86, 0.2)'
                        }
                    ])
                },
                data: ds.values
            };
        })
    };

    myChart.setOption(option);
    
    window.addEventListener('resize', function() {
        myChart.resize();
    });
}
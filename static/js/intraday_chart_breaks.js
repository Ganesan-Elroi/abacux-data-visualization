// intraday_chart_breaks.js - Intraday Chart with Market Break Periods
export function intraday_chart_breaks(containerId, chartData) {
    let myChart = echarts.init(document.getElementById(containerId));
    
    // Prepare line data
    let lineData = chartData.datasets[0] ? chartData.datasets[0].values : [];
    
    let option = {
        title: {
            text: 'Intraday Chart with Breaks',
            left: 0,
            textStyle: {
                fontSize: 14,
                fontWeight: 'normal'
            }
        },
        tooltip: {
            trigger: 'axis',
            position: function(pt) {
                return [pt[0], '10%'];
            }
        },
        grid: {
            left: '5%',
            right: '5%',
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
            boundaryGap: [0, '100%'],
            splitLine: {
                lineStyle: {
                    type: 'dashed',
                    color: '#e0e0e0'
                }
            }
        },
        dataZoom: [
            {
                type: 'inside',
                start: 0,
                end: 100
            }
        ],
        series: [
            {
                name: 'Price',
                type: 'line',
                smooth: true,
                symbol: 'none',
                lineStyle: {
                    color: '#5470c6',
                    width: 2
                },
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        {
                            offset: 0,
                            color: 'rgba(84, 112, 198, 0.3)'
                        },
                        {
                            offset: 1,
                            color: 'rgba(84, 112, 198, 0.05)'
                        }
                    ])
                },
                data: lineData
            }
        ]
    };

    myChart.setOption(option);
    
    window.addEventListener('resize', function() {
        myChart.resize();
    });
}
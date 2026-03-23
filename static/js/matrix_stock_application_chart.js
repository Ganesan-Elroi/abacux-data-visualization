// matrix_stock_application_chart.js - Multi-Stock Comparison Chart with Volume
export function matrix_stock_application_chart(containerId, chartData) {
    let myChart = echarts.init(document.getElementById(containerId));
    
    // Legend data for multiple stocks
    let legendData = chartData.datasets.slice(0, -1).map(ds => ds.label);
    
    // Color scheme for different stocks
    let colors = ['#c23531', '#2f4554', '#61a0a8', '#d48265', '#91c7ae', '#749f83', '#ca8622', '#bda29a'];
    
    let option = {
        title: {
            text: 'Matrix Stock Application',
            left: 0,
            textStyle: {
                fontSize: 14
            }
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'cross',
                animation: false,
                label: {
                    backgroundColor: '#505765'
                }
            }
        },
        legend: {
            data: legendData,
            left: 'center',
            top: 25,
            textStyle: {
                fontSize: 10
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
                start: 60,
                end: 100
            },
            {
                show: true,
                xAxisIndex: [0, 1],
                type: 'slider',
                bottom: '2%',
                start: 60,
                end: 100
            }
        ],
        series: [
            // Stock price lines
            ...chartData.datasets.slice(0, -1).map((ds, index) => ({
                name: ds.label,
                type: 'line',
                data: ds.values,
                smooth: true,
                showSymbol: false,
                lineStyle: {
                    width: 1.5,
                    color: colors[index % colors.length]
                }
            })),
            // Volume bars
            {
                name: 'Volume',
                type: 'bar',
                xAxisIndex: 1,
                yAxisIndex: 1,
                data: chartData.datasets[chartData.datasets.length - 1] ? 
                      chartData.datasets[chartData.datasets.length - 1].values : [],
                itemStyle: {
                    color: function(params) {
                        return params.dataIndex % 2 === 0 ? 
                               'rgba(236, 0, 0, 0.4)' : 'rgba(0, 218, 60, 0.4)';
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
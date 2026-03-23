// multiple_axes_chart.js - Chart with multiple Y-axes for different value ranges
export function multiple_axes_chart(containerId, chartData) {
    let myChart = echarts.init(document.getElementById(containerId));
    
    // Colors for different datasets
    let colors = ['#5470C6', '#91CC75', '#EE6666'];
    
    // Build series with different y-axis indices
    let series = chartData.datasets.map((ds, index) => {
        return {
            name: ds.label,
            type: 'line',
            yAxisIndex: index < 2 ? index : 1, // Max 2 y-axes
            smooth: true,
            data: ds.values,
            itemStyle: {
                color: colors[index % colors.length]
            }
        };
    });
    
    // Build y-axes dynamically
    let yAxes = [];
    let numAxes = Math.min(chartData.datasets.length, 2); // Max 2 axes
    
    for (let i = 0; i < numAxes; i++) {
        yAxes.push({
            type: 'value',
            name: chartData.datasets[i].label,
            position: i === 0 ? 'left' : 'right',
            alignTicks: true,
            axisLine: {
                show: true,
                lineStyle: {
                    color: colors[i]
                }
            },
            axisLabel: {
                formatter: '{value}'
            }
        });
    }
    
    let option = {
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'cross'
            }
        },
        legend: {
            data: chartData.datasets.map(ds => ds.label),
            bottom: '0%'
        },
        grid: {
            left: '3%',
            right: '10%',
            bottom: '10%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            boundaryGap: false,
            data: chartData.labels
        },
        yAxis: yAxes,
        series: series
    };

    myChart.setOption(option);
    
    window.addEventListener('resize', function() {
        myChart.resize();
    });
}
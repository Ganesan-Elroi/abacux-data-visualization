// area_chart.js - Stacked Area Chart with smooth gradients
export function area_chart(containerId, chartData) {
    let myChart = echarts.init(document.getElementById(containerId));
    
    // Beautiful gradient color schemes
    let gradientColors = [
        { start: 'rgba(255, 99, 132, 0.7)', end: 'rgba(255, 99, 132, 0.1)' },
        { start: 'rgba(54, 162, 235, 0.7)', end: 'rgba(54, 162, 235, 0.1)' },
        { start: 'rgba(255, 206, 86, 0.7)', end: 'rgba(255, 206, 86, 0.1)' },
        { start: 'rgba(75, 192, 192, 0.7)', end: 'rgba(75, 192, 192, 0.1)' },
        { start: 'rgba(153, 102, 255, 0.7)', end: 'rgba(153, 102, 255, 0.1)' }
    ];
    
    let series = chartData.datasets.map((ds, index) => {
        let colorScheme = gradientColors[index % gradientColors.length];
        return {
            name: ds.label,
            type: 'line',
            smooth: true,
            stack: 'Total',
            areaStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: colorScheme.start },
                    { offset: 1, color: colorScheme.end }
                ])
            },
            emphasis: {
                focus: 'series'
            },
            data: ds.values
        };
    });

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
        legend: {
            data: chartData.datasets.map(ds => ds.label),
            bottom: '0%',
            icon: 'circle'
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '10%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            boundaryGap: false,
            data: chartData.labels
        },
        yAxis: {
            type: 'value'
        },
        series: series
    };

    myChart.setOption(option);
    
    window.addEventListener('resize', function() {
        myChart.resize();
    });
}
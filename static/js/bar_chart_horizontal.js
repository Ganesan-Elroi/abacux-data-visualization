// bar_chart_horizontal.js
export function bar_chart_horizontal(containerId, chartData) {
    let myChart = echarts.init(document.getElementById(containerId));
    
    // Premium Gradient Colors for Bars (Horizontal orientation)
    let gradientColors = [
        ['#83bff6', '#188df0', '#188df0'],
        ['#00FF87', '#60EFFF', '#60EFFF'],
        ['#F6D365', '#FDA085', '#FDA085'],
        ['#84fab0', '#8fd3f4', '#8fd3f4'],
        ['#fccb90', '#d57eeb', '#d57eeb']
    ];
    
    let series = chartData.datasets.map((ds, index) => {
        let colors = gradientColors[index % gradientColors.length];
        return {
            name: ds.label,
            type: 'bar',
            barWidth: '40%',
            showBackground: true,
            backgroundStyle: {
                color: 'rgba(180, 180, 180, 0.1)',
                borderRadius: [0, 10, 10, 0]
            },
            itemStyle: {
                color: new echarts.graphic.LinearGradient(1, 0, 0, 0, [
                    { offset: 0, color: colors[0] },
                    { offset: 0.5, color: colors[1] },
                    { offset: 1, color: colors[2] }
                ]),
                borderRadius: [0, 10, 10, 0]
            },
            emphasis: {
                itemStyle: {
                    color: new echarts.graphic.LinearGradient(1, 0, 0, 0, [
                        { offset: 0, color: colors[1] },
                        { offset: 0.7, color: colors[1] },
                        { offset: 1, color: colors[0] }
                    ])
                }
            },
            data: ds.values
        };
    });

    let option = {
        tooltip: { 
            trigger: 'axis',
            axisPointer: { type: 'shadow' }
        },
        legend: { 
            show: chartData.datasets.length > 1,
            icon: 'circle',
            bottom: '0%'
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '10%',
            containLabel: true
        },
        xAxis: {
            type: 'value'
        },
        yAxis: {
            type: 'category',
            data: chartData.labels,
            axisTick: { alignWithLabel: true }
        },
        series: series
    };

    myChart.setOption(option);
    
    window.addEventListener('resize', function() {
        myChart.resize();
    });
}
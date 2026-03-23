// bar_chart_clickable.js
export function bar_chart_clickable(containerId, chartData) {
    let myChart = echarts.init(document.getElementById(containerId));
    
    // Dynamic array for values
    let dataValues = chartData.datasets[0] ? chartData.datasets[0].values : [];
    
    // Calculate shadows based on maximum value for depth effect
    let maxVal = Math.max(...dataValues);
    let dataShadow = dataValues.map(() => maxVal * 1.05); // 5% higher than max
    
    let option = {
        title: {
            text: 'Feature Sample: Gradient Color, Shadow, Click Zoom',
            subtext: chartData.datasets[0] ? chartData.datasets[0].label : '',
            left: 'center'
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: { type: 'shadow' }
        },
        xAxis: {
            data: chartData.labels,
            axisLabel: {
                inside: true,
                color: '#fff'
            },
            axisTick: { show: false },
            axisLine: { show: false },
            z: 10
        },
        yAxis: {
            axisLine: { show: false },
            axisTick: { show: false },
            axisLabel: { color: '#999' }
        },
        dataZoom: [
            {
                type: 'inside'
            }
        ],
        series: [
            {
                // For shadow background
                type: 'bar',
                showBackground: true,
                itemStyle: {
                    color: 'rgba(0,0,0,0.05)'
                },
                barGap: '-100%',
                barCategoryGap: '40%',
                data: dataShadow,
                animation: false
            },
            {
                type: 'bar',
                itemStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: '#83bff6' },
                        { offset: 0.5, color: '#188df0' },
                        { offset: 1, color: '#188df0' }
                    ])
                },
                emphasis: {
                    itemStyle: {
                        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                            { offset: 0, color: '#2378f7' },
                            { offset: 0.7, color: '#2378f7' },
                            { offset: 1, color: '#83bff6' }
                        ])
                    }
                },
                data: dataValues
            }
        ]
    };

    myChart.setOption(option);
    
    // Click interaction to trigger dataZoom feature
    const zoomSize = 6;
    myChart.on('click', function (params) {
        myChart.dispatchAction({
            type: 'dataZoom',
            startValue: chartData.labels[Math.max(params.dataIndex - zoomSize / 2, 0)],
            endValue: chartData.labels[Math.min(params.dataIndex + zoomSize / 2, chartData.labels.length - 1)]
        });
    });
    
    window.addEventListener('resize', function() {
        myChart.resize();
    });
}

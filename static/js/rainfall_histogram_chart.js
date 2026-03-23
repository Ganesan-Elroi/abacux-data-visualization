// rainfall_histogram_chart.js - Distribution histogram with gradient
export function rainfall_histogram_chart(containerId, chartData) {
    let myChart = echarts.init(document.getElementById(containerId));
    
    let option = {
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'shadow'
            }
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '10%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            data: chartData.labels,
            axisTick: {
                alignWithLabel: true
            }
        },
        yAxis: {
            type: 'value'
        },
        series: chartData.datasets.map((ds, index) => {
            return {
                name: ds.label,
                type: 'bar',
                barWidth: '60%',
                data: ds.values,
                itemStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: '#2af598' },
                        { offset: 0.5, color: '#009efd' },
                        { offset: 1, color: '#5468ff' }
                    ])
                },
                emphasis: {
                    itemStyle: {
                        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                            { offset: 0, color: '#5468ff' },
                            { offset: 0.5, color: '#009efd' },
                            { offset: 1, color: '#2af598' }
                        ])
                    }
                }
            };
        })
    };

    myChart.setOption(option);
    
    window.addEventListener('resize', function() {
        myChart.resize();
    });
}
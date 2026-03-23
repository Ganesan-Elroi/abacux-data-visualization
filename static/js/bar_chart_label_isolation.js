// bar_chart_label_isolation.js
// Grouped bar chart where each bar displays an isolated label
// showing its own value + series name (e.g. "320  Forest").
// Labels are rotated 90° inside the bar — purely ECharts config, no HTML injection.

export function bar_chart_label_isolation(containerId, chartData) {
    let myChart = echarts.init(document.getElementById(containerId));

    let colorsList = [
        '#5470c6', '#91cc75', '#fac858', '#ee6666',
        '#73c0de', '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc'
    ];

    let series = chartData.datasets.map((ds, index) => {
        return {
            name: ds.label,
            type: 'bar',
            barMaxWidth: 60,
            label: {
                show: true,
                rotate: 90,
                align: 'left',
                verticalAlign: 'middle',
                position: 'insideBottom',
                distance: 10,
                color: '#fff',
                fontSize: 12,
                fontWeight: 'bold',
                // "label isolation" — each bar independently shows its value + its own series name
                formatter: function (params) {
                    return params.value + '  ' + ds.label;
                }
            },
            emphasis: {
                focus: 'series'
            },
            data: ds.values,
            itemStyle: {
                color: colorsList[index % colorsList.length]
            }
        };
    });

    let option = {
        tooltip: {
            trigger: 'axis',
            axisPointer: { type: 'shadow' }
        },
        legend: {
            show: chartData.datasets.length > 1,
            bottom: 0,
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
            data: chartData.labels,
            axisTick: { alignWithLabel: true }
        },
        yAxis: {
            type: 'value',
            splitLine: { lineStyle: { type: 'dashed' } }
        },
        series: series
    };

    myChart.setOption(option);

    window.addEventListener('resize', function () {
        myChart.resize();
    });
}
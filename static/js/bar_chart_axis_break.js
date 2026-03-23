// bar_chart_axis_break.js
export function bar_chart_axis_break(containerId, chartData) {
    let myChart = echarts.init(document.getElementById(containerId));
    
    // Default ECharts colors
    let colorsList = ["#5470c6","#91cc75","#fac858","#ee6666","#73c0de","#3ba272","#fc8452","#9a60b4","#ea7ccc"];
    
    // We determine a pseudo "break point" by finding the max value, and breaking the Y axis
    // into two chunks: 0 to Max*0.2, and Max*0.7 to Max*1.1
    let maxVal = 0;
    chartData.datasets.forEach(ds => {
        let localMax = Math.max(...ds.values);
        if (localMax > maxVal) maxVal = localMax;
    });
    
    // Fallback if maxVal is too small or zero
    if (maxVal < 10) { maxVal = 100; }
    
    let breakBottom = Math.floor(maxVal * 0.2);
    let breakTop = Math.floor(maxVal * 0.7);
    let maxLimit = Math.ceil(maxVal * 1.05);

    let series = chartData.datasets.map((ds, index) => {
        return {
            name: ds.label,
            type: 'bar',
            data: ds.values,
            barMaxWidth: 60,
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
            data: chartData.datasets.map(ds => ds.label),
            bottom: 0
        },
        grid: [
            // Top grid (above break)
            {
                left: '5%',
                right: '5%',
                bottom: '55%',
                top: '10%',
                containLabel: true
            },
            // Bottom grid (below break)
            {
                left: '5%',
                right: '5%',
                top: '55%',
                bottom: '10%',
                containLabel: true
            }
        ],
        xAxis: [
            {
                type: 'category',
                data: chartData.labels,
                gridIndex: 0,
                axisLabel: { show: false },
                axisTick: { show: false },
                axisLine: { show: false }
            },
            {
                type: 'category',
                data: chartData.labels,
                gridIndex: 1
            }
        ],
        yAxis: [
            {
                type: 'value',
                gridIndex: 0,
                min: breakTop,
                max: maxLimit,
                axisLabel: {
                    formatter: function (value) {
                        return value >= 1000 ? (value / 1000) + 'k' : value;
                    }
                }
            },
            {
                type: 'value',
                gridIndex: 1,
                min: 0,
                max: breakBottom,
                splitLine: { show: false },
                axisLabel: {
                    formatter: function (value) {
                        return value >= 1000 ? (value / 1000) + 'k' : value;
                    }
                }
            }
        ],
        series: series.map(s => {
            // Duplicate series for top and bottom grids
            return [
                { ...s, xAxisIndex: 0, yAxisIndex: 0 },
                { ...s, xAxisIndex: 1, yAxisIndex: 1 }
            ];
        }).flat()
    };

    myChart.setOption(option);
    
    window.addEventListener('resize', function() {
        myChart.resize();
    });
}

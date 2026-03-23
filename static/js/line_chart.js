// line_chart.js
export function line_chart(containerId, chartData) {
    let myChart = echarts.init(document.getElementById(containerId));
    
    // Gradient colors for a beautiful stacked area effect
    let gradientColors = [
        ['#80FFA5', '#00DDFF'],
        ['#00DDFF', '#77BFFF'],
        ['#37A2FF', '#FF0087'],
        ['#FF0087', '#FFBF00'],
        ['#FFBF00', '#80FFA5']
    ];
    let fallbackColors = ["#4e79a7", "#f28e2b", "#e15759"];
    
    let series = chartData.datasets.map((ds, index) => {
        let colors = gradientColors[index % gradientColors.length];
        return {
            name: ds.label,
            type: 'line',
            stack: 'Total', // Stacked area feature
            smooth: true,
            lineStyle: {
                width: 0 // Hide the line stroke itself for pure area
            },
            showSymbol: false,
            areaStyle: {
                opacity: 0.8,
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: colors[0] },
                    { offset: 1, color: colors[1] }
                ])
            },
            emphasis: {
                focus: 'series'
            },
            data: ds.values
        };
    });

    let option = {
        color: ['#80FFA5', '#00DDFF', '#37A2FF', '#FF0087', '#FFBF00'],
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
            show: chartData.datasets.length > 1,
            icon: 'circle' // Cleaner look
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        xAxis: [
            {
                type: 'category',
                boundaryGap: false,
                data: chartData.labels
            }
        ],
        yAxis: [
            {
                type: 'value'
            }
        ],
        series: series
    };

    myChart.setOption(option);
    
    window.addEventListener('resize', function() {
        myChart.resize();
    });
}
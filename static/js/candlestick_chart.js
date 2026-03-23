// candlestick_chart.js
export function candlestick_chart(containerId, chartData) {
    let myChart = echarts.init(document.getElementById(containerId));
    
    // Candlestick expects [open, close, lowest, highest]
    let seriesData = [];
    for (let i = 0; i < chartData.labels.length; i++) {
        let open = chartData.datasets[0] ? chartData.datasets[0].values[i] : 0;
        let close = chartData.datasets[1] ? chartData.datasets[1].values[i] : open;
        let lowest = chartData.datasets[2] ? chartData.datasets[2].values[i] : (Math.min(open, close) * 0.95);
        let highest = chartData.datasets[3] ? chartData.datasets[3].values[i] : (Math.max(open, close) * 1.05);
        
        seriesData.push([open, close, lowest, highest]);
    }

    let option = {
        tooltip: {
            trigger: 'axis',
            axisPointer: { type: 'cross' }
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
            boundaryGap: true,
            axisTick: { alignWithLabel: true }
        },
        yAxis: {
            type: 'value',
            scale: true
        },
        series: [
            {
                name: 'Candlestick',
                type: 'candlestick',
                data: seriesData,
                itemStyle: {
                    color: '#ec0000',
                    color0: '#00da3c',
                    borderColor: '#8A0000',
                    borderColor0: '#008F28'
                }
            }
        ]
    };

    myChart.setOption(option);
    
    window.addEventListener('resize', function() {
        myChart.resize();
    });
}

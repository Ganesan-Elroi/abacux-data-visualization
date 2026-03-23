// ohlc_chart.js - OHLC (Open-High-Low-Close) Chart with Volume
export function ohlc_chart(containerId, chartData) {
    let myChart = echarts.init(document.getElementById(containerId));
    
    // Prepare OHLC data [open, close, low, high]
    let ohlcData = [];
    for (let i = 0; i < chartData.labels.length; i++) {
        let open = chartData.datasets[0] ? chartData.datasets[0].values[i] : 0;
        let close = chartData.datasets[1] ? chartData.datasets[1].values[i] : 0;
        let low = chartData.datasets[2] ? chartData.datasets[2].values[i] : 0;
        let high = chartData.datasets[3] ? chartData.datasets[3].values[i] : 0;
        ohlcData.push([open, close, low, high]);
    }
    
    let option = {
        title: {
            text: 'OHLC Chart',
            left: 0,
            textStyle: {
                fontSize: 14
            }
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'cross'
            }
        },
        grid: {
            left: '10%',
            right: '10%',
            bottom: '15%'
        },
        xAxis: {
            type: 'category',
            data: chartData.labels,
            boundaryGap: false,
            axisLine: { onZero: false },
            splitLine: { show: false },
            min: 'dataMin',
            max: 'dataMax'
        },
        yAxis: {
            scale: true,
            splitArea: {
                show: true
            }
        },
        dataZoom: [
            {
                type: 'inside',
                start: 50,
                end: 100
            },
            {
                show: true,
                type: 'slider',
                bottom: '5%',
                start: 50,
                end: 100
            }
        ],
        series: [
            {
                name: 'OHLC',
                type: 'candlestick',
                data: ohlcData,
                itemStyle: {
                    color: '#00da3c',
                    color0: '#ec0000',
                    borderColor: '#00da3c',
                    borderColor0: '#ec0000'
                }
            }
        ]
    };

    myChart.setOption(option);
    
    window.addEventListener('resize', function() {
        myChart.resize();
    });
}
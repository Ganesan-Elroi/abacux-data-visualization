// beijing_aqi_chart.js - Beijing AQI Mixed Chart (Bar + Line + Calendar Axis)
export function beijing_aqi_chart(containerId, chartData) {
    let myChart = echarts.init(document.getElementById(containerId));
    
    // Expects multiple datasets for AQI components
    // PM2.5, PM10, SO2, NO2, CO, O3
    let datasets = chartData.datasets;
    
    let option = {
        title: {
            text: 'Beijing AQI',
            left: 'center',
            textStyle: {
                fontSize: 14,
                fontWeight: 'normal'
            }
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'cross'
            }
        },
        legend: {
            data: datasets.map(ds => ds.label),
            bottom: '0%',
            textStyle: {
                fontSize: 10
            }
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '15%',
            top: '15%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            boundaryGap: true,
            data: chartData.labels,
            axisLabel: {
                rotate: 45,
                fontSize: 9
            }
        },
        yAxis: {
            type: 'value',
            name: 'AQI',
            axisLabel: {
                formatter: '{value}'
            }
        },
        series: datasets.map((ds, index) => {
            // Alternate between bar and line for visual variety
            let isBar = index % 2 === 0;
            
            let colorScheme = [
                '#EE6666', '#FAC858', '#73C0DE', 
                '#5470C6', '#91CC75', '#EA7CCC'
            ];
            
            if (isBar) {
                return {
                    name: ds.label,
                    type: 'bar',
                    data: ds.values,
                    barMaxWidth: 15,
                    itemStyle: {
                        color: colorScheme[index % colorScheme.length],
                        opacity: 0.7
                    }
                };
            } else {
                return {
                    name: ds.label,
                    type: 'line',
                    data: ds.values,
                    smooth: true,
                    showSymbol: false,
                    lineStyle: {
                        width: 2,
                        color: colorScheme[index % colorScheme.length]
                    }
                };
            }
        })
    };

    myChart.setOption(option);
    
    window.addEventListener('resize', function() {
        myChart.resize();
    });
}
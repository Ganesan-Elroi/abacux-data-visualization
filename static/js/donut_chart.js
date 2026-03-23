// donut_chart.js
export function donut_chart(containerId, chartData) {
    let myChart = echarts.init(document.getElementById(containerId));
    
    // Vibrant professional color palette
    let colorsList = [
        '#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', 
        '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc'
    ];
    
    let dataMap = chartData.labels.map((label, i) => {
        return {
            name: label,
            value: chartData.datasets[0].values[i]
        };
    });

    let option = {
        tooltip: { 
            trigger: 'item',
            formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: { 
            orient: 'vertical', 
            right: '5%', 
            top: 'middle',
            icon: 'circle'
        },
        color: colorsList,
        series: [
            {
                name: chartData.datasets[0].label || 'Value',
                type: 'pie',
                radius: ['45%', '75%'],
                center: ['40%', '50%'],
                // Modern ECharts 6.0+ Doughnut styling
                padAngle: 5,
                itemStyle: {
                    borderRadius: 10
                },
                label: {
                    show: true,
                    // Minimalistic label styling
                    formatter: '{b}\n{d}%',
                    color: '#444'
                },
                labelLine: {
                    length: 15,
                    length2: 10,
                    smooth: 0.2
                },
                data: dataMap
            }
        ]
    };

    myChart.setOption(option);
    
    window.addEventListener('resize', function() {
        myChart.resize();
    });
}
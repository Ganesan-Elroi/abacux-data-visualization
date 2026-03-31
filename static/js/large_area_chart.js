// large_area_chart.js - Large Scale Area Chart with Gradient + Data Zoom
export function large_area_chart(containerId, chartData) {
    let myChart = echarts.init(document.getElementById(containerId));
    
    // Determine initial zoom level based on data size
    let endPercent = 100;
    const dataLength = chartData.labels ? chartData.labels.length : 0;
    
    if (dataLength > 1000) {
        endPercent = 10; // Show 10% for very large datasets
    } else if (dataLength > 500) {
        endPercent = 20; // Show 20% for large datasets
    } else if (dataLength > 100) {
        endPercent = 50; // Show 50% for medium datasets
    }
    
    // Create gradient area with pink/coral colors
    let option = {
        tooltip: {
            trigger: 'axis',
            position: function (pt) {
                return [pt[0], '10%'];
            },
            axisPointer: {
                type: 'cross',
                label: {
                    backgroundColor: '#6a7985'
                }
            }
        },
        // Add toolbox for zoom controls and save image
        toolbox: {
            feature: {
                dataZoom: {
                    yAxisIndex: 'none',
                    title: {
                        zoom: 'Area Zoom',
                        back: 'Reset Zoom'
                    }
                },
                restore: {
                    title: 'Restore'
                },
                saveAsImage: {
                    title: 'Save as Image'
                }
            },
            right: '5%',
            top: '2%'
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '15%', // Increased to make room for dataZoom slider
            top: '10%',    // Increased to make room for toolbox
            containLabel: true
        },
        xAxis: {
            type: 'category',
            boundaryGap: false,
            data: chartData.labels,
            axisLabel: {
                fontSize: 10,
                color: '#666',
                rotate: dataLength > 50 ? 45 : 0 // Rotate labels for large datasets
            },
            axisLine: {
                lineStyle: {
                    color: '#ddd'
                }
            }
        },
        yAxis: {
            type: 'value',
            boundaryGap: [0, '5%'],
            axisLabel: {
                fontSize: 10,
                color: '#666'
            },
            splitLine: {
                lineStyle: {
                    color: '#f0f0f0'
                }
            }
        },
        // Add data zoom controls
        dataZoom: [
            {
                // Inside zoom (mouse wheel / pinch)
                type: 'inside',
                start: 0,
                end: endPercent,
                zoomOnMouseWheel: true,
                moveOnMouseMove: true,
                moveOnMouseWheel: true
            },
            {
                // Slider at bottom
                type: 'slider',
                start: 0,
                end: endPercent,
                height: 25,
                bottom: '5%',
                handleStyle: {
                    color: '#ff6384',
                    borderColor: '#ff6384'
                },
                moveHandleStyle: {
                    color: '#ff9f40'
                },
                textStyle: {
                    fontSize: 10,
                    color: '#666'
                },
                borderColor: '#ddd',
                fillerColor: 'rgba(255, 99, 132, 0.2)',
                handleIcon: 'path://M10.7,11.9v-1.3H9.3v1.3c-4.9,0.3-8.8,4.4-8.8,9.4c0,5,3.9,9.1,8.8,9.4v1.3h1.3v-1.3c4.9-0.3,8.8-4.4,8.8-9.4C19.5,16.3,15.6,12.2,10.7,11.9z M13.3,24.4H6.7V23h6.6V24.4z M13.3,19.6H6.7v-1.4h6.6V19.6z'
            }
        ],
        series: chartData.datasets.map((ds, index) => {
            return {
                name: ds.label,
                type: 'line',
                smooth: true,
                showSymbol: false, // No symbols for better performance
                sampling: 'lttb',  // Largest-Triangle-Three-Buckets sampling
                lineStyle: {
                    width: 0
                },
                areaStyle: {
                    opacity: 0.8,
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        {
                            offset: 0,
                            color: 'rgba(255, 99, 132, 0.8)'
                        },
                        {
                            offset: 0.5,
                            color: 'rgba(255, 159, 64, 0.5)'
                        },
                        {
                            offset: 1,
                            color: 'rgba(255, 205, 86, 0.2)'
                        }
                    ])
                },
                emphasis: {
                    focus: 'series'
                },
                data: ds.values
            };
        }),
        // Disable animation for very large datasets (better performance)
        animation: dataLength < 1000
    };

    myChart.setOption(option);
    
    window.addEventListener('resize', function() {
        myChart.resize();
    });
    
    // Log performance info for debugging
    if (dataLength > 500) {
        console.log(`📊 Large Area Chart: Rendering ${dataLength} data points with zoom enabled`);
    }
}
// chart-engine.js
// Central registry of all available chart handlers
// Import your chart functions (assuming they are in separate files)

import { bar_chart_vertical } from './bar_chart_vertical.js';
import { bar_chart_horizontal } from './bar_chart_horizontal.js';
import { donut_chart } from './donut_chart.js';
import { line_chart } from './line_chart.js';
import { area_chart } from './area_chart.js';
import { large_area_chart } from './large_area_chart.js';
import { scatter_chart } from './scatter_chart.js';
import { rainfall_evaporation_chart } from './rainfall_evaporation_chart.js';
import { beijing_aqi_chart } from './beijing_aqi_chart.js';
import { confidence_band_chart } from './confidence_band_chart.js';
import { bar_chart_clickable } from './bar_chart_clickable.js';

import { candlestick_chart } from './candlestick_chart.js';
import { ohlc_chart } from './ohlc_chart.js';
import { multiple_axes_chart } from './multiple_axes_chart.js';
import { matrix_stock_application_chart } from './matrix_stock_application_chart.js';
import { large_scale_candlestick_chart } from './large_scale_candlestick_chart.js';
import { intraday_chart_breaks } from './intraday_chart_breaks.js';
import { shanghai_index_chart } from './shanghai_index_chart.js';
import { rainfall_histogram_chart } from './rainfall_histogram_chart.js';

import { axis_pointer_link_touch_chart } from './axis_pointer_link_touch_chart.js';
import { candlestick_brush_chart } from './candlestick_brush_chart.js';
import { bar_chart_label_isolation } from './bar_chart_label_isolation.js';

// ────────────────────────────────────────────────

const chartHandlers = {
    // Core / most common charts
    bar_chart_vertical:               bar_chart_vertical,
    bar_chart_horizontal:             bar_chart_horizontal,
    donut_chart:                      donut_chart,
    line_chart:                       line_chart,
    area_chart:                       area_chart,
    large_area_chart:                 large_area_chart,
    scatter_chart:                    scatter_chart,

    // Financial / stock charts
    candlestick_chart:                candlestick_chart,
    ohlc_chart:                       ohlc_chart,
    large_scale_candlestick_chart:    large_scale_candlestick_chart,
    candlestick_brush_chart:          candlestick_brush_chart,
    intraday_chart_breaks:            intraday_chart_breaks,
    matrix_stock_application_chart:   matrix_stock_application_chart,
    shanghai_index_chart:             shanghai_index_chart,
    beijing_aqi_chart:                beijing_aqi_chart,

    // Special / advanced charts
    rainfall_evaporation_chart:       rainfall_evaporation_chart,
    rainfall_histogram_chart:         rainfall_histogram_chart,
    confidence_band_chart:            confidence_band_chart,
    multiple_axes_chart:              multiple_axes_chart,
    bar_chart_clickable:              bar_chart_clickable,
    bar_chart_label_isolation:        bar_chart_label_isolation,

    // Axis / interaction helpers
    axis_pointer_link_touch_chart:    axis_pointer_link_touch_chart,
};

export default chartHandlers;


function renderChart(type, containerId, chartData) {
    const normalizedType = normalizeChartType(type);

    const handler = chartHandlers[normalizedType];

    if (!handler) {
        console.warn("Unknown chart type:", type);
        return chartHandlers["bar_chart_vertical"](containerId, chartData);
    }

    handler(containerId, chartData);
}

function normalizeChartType(type) {
    const map = {
        // Core
        bar_v:                      "bar_chart_vertical",
        bar_h:                      "bar_chart_horizontal",
        donut:                      "donut_chart",
        line:                       "line_chart",
        area:                       "area_chart",
        large_area:                 "large_area_chart",
        scatter:                    "scatter_chart",

        // Special
        rainfall_evaporation:       "rainfall_evaporation_chart",
        beijing_aqi:                "beijing_aqi_chart",
        confidence_band:            "confidence_band_chart",
        bar_clickable:              "bar_chart_clickable",

        // ✅ NEW — all likely aliases the LLM might return
        bar_label_isolation:        "bar_chart_label_isolation",
        bar_label:                  "bar_chart_label_isolation",
        label_isolation:            "bar_chart_label_isolation",

        // Financial
        candlestick:                "candlestick_chart",
        ohlc:                       "ohlc_chart",
        large_scale_candlestick:    "large_scale_candlestick_chart",
        intraday_chart_breaks:      "intraday_chart_breaks",
        matrix_stock_application:   "matrix_stock_application_chart",
        shanghai_index:             "shanghai_index_chart",

        // Other
        rainfall_histogram:         "rainfall_histogram_chart",
        multiple_axes:              "multiple_axes_chart",
        axis_pointer_link_touch:    "axis_pointer_link_touch_chart",
    };

    return map[type] || type;
}

// ✅ export it
export { renderChart };

// optional global
window.renderChart = renderChart;

// ────────────────────────────────────────────────
export function isChartSupported(type) {
    return !!chartHandlers[type];
}

export function getAllChartTypes() {
    return Object.keys(chartHandlers);
}
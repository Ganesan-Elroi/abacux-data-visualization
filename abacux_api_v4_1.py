import os
import json
from flask import Flask, render_template, request, jsonify
from google import genai
from dotenv import load_dotenv
import json

load_dotenv()

app = Flask(__name__)
client = genai.Client(api_key=os.getenv("GEMINI-API-KEY"))


def analyze_data_for_charts(db_results, user_prompt=""):
    """
    Analyzes the first 5 rows of DB results and returns chart configurations.
    
    Args:
        db_results: List of dictionaries containing database query results
        user_prompt: Optional user instruction for chart preferences
        
    Returns:
        List of chart configurations with label_key, value_keys, and chart_type
    """
    if not db_results or len(db_results) == 0:
        return []
    
    # Get first 5 rows as sample
    sample_data = db_results[:5]
    all_columns = list(sample_data[0].keys())
    
    sample_json = json.dumps(sample_data, default=str, indent=2)
    
    prompt = f"""
        You are a data visualization expert specializing in Apache ECharts.

        Given the following sample of database query results (first 5 rows shown):
        {sample_json}

        User instruction / goal:
        "{user_prompt if user_prompt else 'No specific instructions provided. Create the most useful, clear and diverse visualizations possible.'}"

        Most datasets are BUSINESS / OPERATIONAL data (sales, orders, invoices, customers, payments, inventory, shipments, etc.).
        Only VERY RARELY will you see true stock market OHLC data (open, close, high, low, volume).

        CRITICAL VARIETY & DIVERSITY RULES – YOU MUST FOLLOW THESE:

        1. You MUST create MAXIMUM VARIETY of insights. Do NOT generate 2–3 charts that show almost the same thing.
        Forbidden: three distribution charts of the same measure (e.g. grand total by city + by status + by product — all as bar/donut).

        2. Use COMPLETELY DIFFERENT grouping columns (label_key) for each chart whenever possible.
        Good diversity examples:
        - Chart 1: group by product / customer / category
        - Chart 2: group by payment_status / delivery_status / order_status
        - Chart 3: group by shipping_city / region / customer
        - Chart 4: no grouping (label_key = ""), show totals or multiple metrics comparison

        3. If there is ANY date/datetime column (order_date, invoice_date, payment_date, created_at, etc.):
        → AT LEAST ONE CHART MUST BE TIME-BASED (use that date column on x-axis, label_key = "").
        Preferred time-based types: large_area, line, area, confidence_band

        4. AT LEAST ONE CHART MUST HAVE label_key = "" (no category grouping) — show overall totals, multiple metrics side-by-side, or time trend.

        5. If there are ≥2 numeric columns that might be related → include AT LEAST ONE scatter chart
        (examples: quantity vs grand_total, paid_amount vs grand_total, tax_amount vs subtotal, revenue vs count)

        6. When ≥3 numeric columns exist → include at least one multi-metric chart:
        multiple_y_axes, beijing_aqi, line, area (stacked), rainfall_evaporation

        7. Try to avoid reusing the same column across charts when possible — but ALLOW reuse when needed for better insights.
        Prioritize variety of insights over strict non-reuse.

        8. NEVER use columns like "order_id", "invoice_no", "id", "row_id" or any pure sequence/primary key.

        9. ONLY use columns that actually exist in the sample data.

        PREFERRED CHART TYPES FOR BUSINESS DATA (use these first in most cases):

        - bar_v          – vertical bars for category comparison
        - bar_h          – horizontal bars for long category names
        - donut          – composition / percentage breakdown
        - large_area     – beautiful single-metric trend over time
        - area           – stacked or cumulative trends
        - line           – multiple metrics over time or categories
        - scatter        – correlation / relationship between two numbers
        - rainfall_evaporation  – dual-axis bar + line (different scales)

        Advanced / multi-metric charts (when they fit well):
        - beijing_aqi, multiple_y_axes, confidence_band, bar_race (rankings)

        Financial candlestick family — ONLY if columns clearly represent OHLC + volume.

        NUMERIC & STRUCTURE GUIDELINES:

        IF the data contains a date/datetime column:
        → Chart 1: time-based (large_area / line / area), label_key = ""
        → Chart 2: bar_v / bar_h using important category + key numeric
        → Chart 3: donut / scatter / multiple_y_axes using different dimension

        IF 4+ numeric columns:
        → Chart 1: multiple_y_axes / beijing_aqi / area (multiple numerics)
        → Chart 2: scatter (two related numerics)
        → Chart 3: bar_v / bar_h / donut with different grouping

        IF 2–3 numeric columns:
        → Chart 1: rainfall_evaporation / scatter / line / area
        → Chart 2: bar_v / bar_h using different category
        → Chart 3: donut / large_area (if time) / bar_clickable

        IF 1 numeric column:
        → Chart 1: large_area (if time-based) or bar_v / bar_h
        → Chart 2: donut or bar_race (if ranking makes sense)

        MANDATORY OUTPUT FORMAT:
        Return ONLY a valid JSON array — nothing else — no explanation, no markdown, no code fences:

        [
        {{
            "label_key": "category_column_or_empty_string",
            "value_keys": ["numeric_col1", "numeric_col2"],
            "chart_type": "bar_v"
        }},
        {{
            "label_key": "different_category",
            "value_keys": ["numeric_col3"],
            "chart_type": "donut"
        }},
        {{
            "label_key": "",
            "value_keys": ["quantity", "grand_total"],
            "chart_type": "scatter"
        }}
        ]

        Notes:
        - label_key can be empty string "" when: time-series (date on x-axis), multi-metric comparison without grouping, or single aggregated view
        - value_keys must be real existing column names
        - Use DIFFERENT chart_type for each entry
        """
    
    
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        llm_response = response.text.strip()
        
        # Remove markdown formatting if present
        if llm_response.startswith("```json"):
            llm_response = llm_response.replace("```json", "").replace("```", "").strip()
        elif llm_response.startswith("```"):
            llm_response = llm_response.replace("```", "").strip()
        
        parsed = json.loads(llm_response)
        if not isinstance(parsed, list):
            parsed = [parsed]
        
        # Validate and normalize chart configurations
        validated_charts = []
        for chart_config in parsed:
            l_key = chart_config.get("label_key", "")
            v_keys = chart_config.get("value_keys", [])
            
            # Handle legacy format
            if not v_keys and "value_key" in chart_config:
                if isinstance(chart_config["value_key"], list):
                    v_keys = chart_config["value_key"]
                else:
                    v_keys = [chart_config["value_key"]]
            
            # Validate columns exist
            if l_key not in all_columns:
                continue
            
            valid_v_keys = [vk for vk in v_keys if vk in all_columns]
            if not valid_v_keys:
                continue
            
            # Normalize chart type
            c_type_raw = chart_config.get("chart_type", "bar_v").lower()
            
            # Basic charts
            if c_type_raw in ["pie", "doughnut", "donut"]:
                c_type = "donut"
            elif c_type_raw in ["bar", "column", "bar_v", "vertical"]:
                c_type = "bar_v"
            elif c_type_raw in ["bar_h", "horizontal"]:
                c_type = "bar_h"
            
            # Line and area charts
            elif c_type_raw in ["line", "multi_line"]:
                c_type = "line"
            elif c_type_raw in ["area", "gradient_area", "stacked_area"]:
                c_type = "area"
            elif c_type_raw in ["large_area", "area_large", "pink_area"]:
                c_type = "large_area"
            
            # Financial charts - candlestick family
            elif c_type_raw in ["candlestick", "candle", "ohlc"]:
                c_type = "candlestick"
            elif c_type_raw in ["basic_candlestick", "simple_candlestick"]:
                c_type = "basic_candlestick"
            elif c_type_raw in ["ohlc", "ohlc_chart"]:
                c_type = "ohlc"
            elif c_type_raw in ["shanghai_index", "stock_index", "ma_chart"]:
                c_type = "shanghai_index"
            elif c_type_raw in ["large_scale_candlestick", "large_candlestick"]:
                c_type = "large_scale_candlestick"
            elif c_type_raw in ["candlestick_brush", "brush_selection"]:
                c_type = "candlestick_brush"
            elif c_type_raw in ["matrix_stock", "multi_stock", "stock_comparison"]:
                c_type = "matrix_stock"
            elif c_type_raw in ["axis_pointer_link", "linked_pointer"]:
                c_type = "axis_pointer_link"
            elif c_type_raw in ["intraday_chart_breaks", "intraday", "realtime"]:
                c_type = "intraday_chart_breaks"
            
            # Interactive and special charts
            elif c_type_raw == "bar_axis_break":
                c_type = "bar_axis_break"
            elif c_type_raw in ["bar_clickable", "interactive_bar"]:
                c_type = "bar_clickable"
            elif c_type_raw in ["scatter", "scatter_plot"]:
                c_type = "scatter"
            
            # Dual-axis and multi-metric charts
            elif c_type_raw in ["rainfall_evaporation", "dual_axis", "combo_chart"]:
                c_type = "rainfall_evaporation"
            elif c_type_raw in ["beijing_aqi", "multi_metric", "mixed_chart", "aqi"]:
                c_type = "beijing_aqi"
            elif c_type_raw in ["multiple_y_axes", "dual_y_axis", "multi_axis"]:
                c_type = "multiple_y_axes"
            
            # Statistical and animated charts
            elif c_type_raw in ["confidence_band", "confidence", "statistical"]:
                c_type = "confidence_band"
            elif c_type_raw in ["animation_delay", "animated_bar", "staggered"]:
                c_type = "animation_delay"
            elif c_type_raw in ["bar_race", "race", "ranking"]:
                c_type = "bar_race"
            elif c_type_raw in ["weather_statistics", "stacked_bar", "composition"]:
                c_type = "weather_statistics"
            
            # Fallback
            else:
                print("[INFO]:  Fall back : bar_v  chart-type")
                c_type = "bar_v"
            
            validated_charts.append({
                "label_key": l_key,
                "value_keys": valid_v_keys,
                "chart_type": c_type
            })
        
        # Ensure at least 2 charts
        if len(validated_charts) < 2:
            # Add fallback charts if needed
            print("[INFO]: Fall back after validate chart ")
            numeric_cols = []
            categorical_cols = []
            
            for col in all_columns:
                sample_val = sample_data[0].get(col)
                if isinstance(sample_val, (int, float)) or (isinstance(sample_val, str) and sample_val.replace('.', '', 1).isdigit()):
                    numeric_cols.append(col)
                else:
                    categorical_cols.append(col)
            
            # Add even stronger fallback
            if len(validated_charts) == 0 and len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
                validated_charts.append({
                    "label_key": categorical_cols[0],
                    "value_keys": [numeric_cols[0]],
                    "chart_type": "bar_v"
                })
            if len(validated_charts) <= 1 and len(numeric_cols) >= 1:
                # Status or simple metric distribution
                status_like_cols = [c for c in all_columns if "status" in c.lower() or "type" in c.lower()]
                if status_like_cols:
                    validated_charts.append({
                        "label_key": status_like_cols[0],
                        "value_keys": [numeric_cols[0]],
                        "chart_type": "donut"
                    })
        
        return validated_charts[:3]  # Maximum 3 charts
        
    except Exception as e:
        print(f"Error in analyze_data_for_charts: {e}")
        
        # Fallback: try to return at least 2 basic charts
        numeric_cols = []
        categorical_cols = []
        
        for col in all_columns:
            try:
                sample_val = sample_data[0].get(col)
                if isinstance(sample_val, (int, float)) or (isinstance(sample_val, str) and sample_val.replace('.', '', 1).replace('-', '', 1).isdigit()):
                    numeric_cols.append(col)
                else:
                    categorical_cols.append(col)
            except:
                categorical_cols.append(col)
        
        fallback_charts = []
        if categorical_cols and numeric_cols:
            fallback_charts.append({
                "label_key": categorical_cols[0],
                "value_keys": [numeric_cols[0]],
                "chart_type": "bar_v"
            })
            
            if len(categorical_cols) > 1 and len(numeric_cols) > 1:
                fallback_charts.append({
                    "label_key": categorical_cols[1],
                    "value_keys": [numeric_cols[1]],
                    "chart_type": "donut"
                })
            elif len(numeric_cols) > 1:
                fallback_charts.append({
                    "label_key": categorical_cols[0],
                    "value_keys": [numeric_cols[1]],
                    "chart_type": "bar_h"
                })
        
        return fallback_charts


@app.route("/api/analyze-charts", methods=["POST"])
def analyze_charts():
    """
    API endpoint to analyze DB results and return chart configurations.
    
    Expected payload:
    {
        "db_result": [...],  # Array of database result objects
        "user_prompt": ""    # Optional user instruction
    }
    
    Returns:
    {
        "status": 1,
        "msg": "success",
        "chart_data": [...]  # Array of chart configurations
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": 0,
                "msg": "No data provided",
                "chart_data": []
            }), 400
        
        db_results = data.get("db_result", [])
        user_prompt = data.get("user_prompt", "")
        
        if not db_results or not isinstance(db_results, list):
            return jsonify({
                "status": 0,
                "msg": "Invalid or empty db_result",
                "chart_data": []
            }), 400
        
        # Analyze data and get chart configurations
        chart_data = analyze_data_for_charts(db_results, user_prompt)
        
        if not chart_data:
            return jsonify({
                "status": 0,
                "msg": "Could not generate chart configurations",
                "chart_data": []
            }), 500
        
        return jsonify({
            "status": 1,
            "msg": "success",
            "chart_data": chart_data
        })
        
    except Exception as e:
        print(f"Error in /api/analyze-charts: {e}")
        return jsonify({
            "status": 0,
            "msg": f"Internal server error: {str(e)}",
            "chart_data": []
        }), 500


@app.route("/api/health", methods=["GET"])
def health_check():
    """Simple health check endpoint"""
    return jsonify({
        "status": 1,
        "msg": "API is running"
    })

@app.route("/demo/ui", methods=["GET"])
@app.route("/", methods=["GET"])
def DemoUI():
    return render_template("demo_frontend.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5012, debug=True)
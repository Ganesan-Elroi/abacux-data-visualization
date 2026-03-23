import os
import json
from flask import Flask, request, jsonify, render_template
from google import genai
from dotenv import load_dotenv

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
Given the following sample of database query results (up to 5 rows):
{sample_json}

The user has provided the following instruction:
"{user_prompt if user_prompt else 'No specific instructions provided.'}"

Analyze this data and identify MINIMUM 2 and MAXIMUM 3 different, meaningful ways to chart this data.

CRITICAL RULES:
1. DO NOT REUSE ANY COLUMN ACROSS CHARTS. Each chart must use completely unique column combinations.
2. NEVER use "invoice_no", "id", or any sequence number columns for label_key or value_key.
3. ONLY choose columns that exist in the sample data provided above.
4. You MUST use DIFFERENT chart types for each chart - VARIETY IS MANDATORY!
5. PRIORITIZE advanced chart types - AVOID bar_v and bar_h unless absolutely necessary.

AVAILABLE CHART TYPES - DECISION TREE:

Step 1: Count numeric columns in the data.
Step 2: Look at the data structure and follow these EXACT rules:

IF you have 6+ numeric columns:
  → Chart 1: "beijing_aqi" using 4-6 numeric columns (mixed bars + lines)
  → Chart 2: "candlestick" using 4 different numeric columns [col1, col2, col3, col4]
  → Chart 3: "scatter" using 2 remaining numeric columns

ELSE IF you have 4-5 numeric columns:
  → Chart 1: "candlestick" using 4 numeric columns as [value_key_1, value_key_2, value_key_3, value_key_4]
  → Chart 2: "scatter" using 2 different numeric columns
  → Chart 3: "donut" using 1 remaining numeric column

ELSE IF you have 3 numeric columns:
  → Chart 1: "area" using all 3 numeric columns together (multi-area chart)
  → Chart 2: "scatter" using 2 numeric columns
  → Chart 3: "bar_clickable" using 1 remaining numeric column

ELSE IF you have 2 numeric columns:
  → Chart 1: "rainfall_evaporation" using both numeric columns (dual-axis: bar + line)
  → Chart 2: "scatter" using both numeric columns (X vs Y correlation)
  → (Optional Chart 3: "large_area" using 1 numeric column for trend)

ELSE IF you have 1 numeric column:
  → Chart 1: "large_area" for beautiful trend visualization
  → Chart 2: "donut" for distribution
  
SPECIAL CASES:
- If data has DATE column + 1 numeric → Use "large_area" or "confidence_band"
- If data has DATE column + 2 numeric → Use "rainfall_evaporation"
- If data has DATE column + 3+ numeric → Use "area" or "beijing_aqi"
  
CHART TYPE DETAILS:

1. "candlestick" - Financial candlestick chart (OHLC)
   - REQUIRES: EXACTLY 4 value_keys [open, close, low, high]
   - Example: ["sales", "paid", "with_tax", "without_tax"]
   - USE WHEN: You have 4+ numeric columns available
   - PRIORITY: HIGH - Use this when 4 numeric columns exist!

2. "scatter" - Scatter Plot for correlation
   - REQUIRES: EXACTLY 2 value_keys [x_metric, y_metric]
   - Example: ["sales", "with_tax"] to show correlation
   - USE WHEN: You want to show relationship between 2 metrics
   - PRIORITY: HIGH

3. "large_area" - Large gradient area chart (pink/coral gradient)
   - REQUIRES: 1+ value_keys
   - Example: ["sales"] over time
   - USE WHEN: Single metric time series, large dataset
   - PRIORITY: HIGH - Beautiful for trends!

4. "area" - Stacked Area Chart (multi-color gradients)
   - REQUIRES: 2+ value_keys
   - Example: ["sales", "paid", "with_tax"]
   - USE WHEN: Showing cumulative or comparative trends
   - PRIORITY: HIGH

5. "rainfall_evaporation" - Dual-axis combo (bar + line)
   - REQUIRES: EXACTLY 2 value_keys (first=bar, second=line)
   - Example: ["sales", "paid"]
   - USE WHEN: Comparing 2 metrics with different scales
   - PRIORITY: MEDIUM - Great for dual metrics!

6. "beijing_aqi" - Multi-metric mixed chart (bars + lines)
   - REQUIRES: 4-6 value_keys
   - Example: ["sales", "paid", "with_tax", "without_tax", "sales_person"]
   - USE WHEN: Need to compare 4+ different metrics
   - PRIORITY: MEDIUM

7. "line" - Multi-line chart with gradients
   - REQUIRES: 2+ value_keys
   - Example: ["sales", "paid", "with_tax"]
   - USE WHEN: Comparing multiple metrics across categories
   - PRIORITY: MEDIUM

8. "donut" - Pie/Donut Chart
   - REQUIRES: exactly 1 value_key
   - Example: ["paid"] grouped by sales_person
   - USE WHEN: Showing distribution or percentages
   - PRIORITY: LOW

9. "bar_clickable" - Interactive zoomable bar
   - REQUIRES: exactly 1 value_key
   - Example: ["sales"] by customer
   - USE WHEN: Single metric needs interactive exploration
   - PRIORITY: LOW

10. "confidence_band" - Line with confidence bounds
   - REQUIRES: 1 value_key
   - Example: ["sales"] with statistical bounds
   - USE WHEN: Statistical data, forecasting
   - PRIORITY: MEDIUM

11. "bar_axis_break" - Bar with Y-axis break
   - REQUIRES: 1+ value_keys
   - USE WHEN: One value is 5x+ larger than others
   - PRIORITY: LOW

12. "bar_v" - AVOID UNLESS NO OTHER OPTION
13. "bar_h" - AVOID UNLESS NO OTHER OPTION

MANDATORY VARIETY RULE:
Each of your 2-3 charts MUST use DIFFERENT chart types. For example:
✓ GOOD: [candlestick, scatter, donut]
✓ GOOD: [area, scatter, bar_clickable]
✗ BAD: [bar_v, bar_h, donut]
✗ BAD: [donut, donut, bar_v]

Return ONLY a valid JSON array (no markdown formatting):
[
  {{
    "label_key": "column_name",
    "value_keys": ["col1", "col2"],
    "chart_type": "scatter"
  }},
  {{
    "label_key": "different_column",
    "value_keys": ["col3"],
    "chart_type": "donut"
  }}
]
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
            
            if c_type_raw in ["pie", "doughnut", "donut"]:
                c_type = "donut"
            elif c_type_raw in ["bar", "column", "bar_v", "vertical"]:
                c_type = "bar_v"
            elif c_type_raw in ["bar_h", "horizontal"]:
                c_type = "bar_h"
            elif c_type_raw in ["line", "multi_line"]:
                c_type = "line"
            elif c_type_raw in ["area", "gradient_area", "stacked_area"]:
                c_type = "area"
            elif c_type_raw in ["large_area", "area_large", "pink_area"]:
                c_type = "large_area"
            elif c_type_raw in ["candlestick", "candle", "ohlc"]:
                c_type = "candlestick"
            elif c_type_raw == "bar_axis_break":
                c_type = "bar_axis_break"
            elif c_type_raw in ["bar_clickable", "interactive_bar"]:
                c_type = "bar_clickable"
            elif c_type_raw in ["scatter", "scatter_plot"]:
                c_type = "scatter"
            elif c_type_raw in ["rainfall_evaporation", "dual_axis", "combo_chart"]:
                c_type = "rainfall_evaporation"
            elif c_type_raw in ["beijing_aqi", "multi_metric", "mixed_chart", "aqi"]:
                c_type = "beijing_aqi"
            elif c_type_raw in ["confidence_band", "confidence", "statistical"]:
                c_type = "confidence_band"
            else:
                c_type = "bar_v"
            
            validated_charts.append({
                "label_key": l_key,
                "value_keys": valid_v_keys,
                "chart_type": c_type
            })
        
        # Ensure at least 2 charts
        if len(validated_charts) < 2:
            # Add fallback charts if needed
            numeric_cols = []
            categorical_cols = []
            
            for col in all_columns:
                sample_val = sample_data[0].get(col)
                if isinstance(sample_val, (int, float)) or (isinstance(sample_val, str) and sample_val.replace('.', '', 1).isdigit()):
                    numeric_cols.append(col)
                else:
                    categorical_cols.append(col)
            
            if len(validated_charts) == 0 and categorical_cols and numeric_cols:
                validated_charts.append({
                    "label_key": categorical_cols[0],
                    "value_keys": [numeric_cols[0]],
                    "chart_type": "bar_v"
                })
            
            if len(validated_charts) == 1 and len(categorical_cols) > 1 and len(numeric_cols) > 1:
                validated_charts.append({
                    "label_key": categorical_cols[1] if len(categorical_cols) > 1 else categorical_cols[0],
                    "value_keys": [numeric_cols[1]] if len(numeric_cols) > 1 else [numeric_cols[0]],
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
    return render_template("demo_frontend_v3.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5012, debug=True)
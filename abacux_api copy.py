import os
import json
from flask import Flask, request, jsonify,render_template
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
You are a data visualization expert.
Given the following sample of database query results (up to 5 rows):
{sample_json}

The user has provided the following instruction:
"{user_prompt if user_prompt else 'No specific instructions provided.'}"

Analyze this data and identify MINIMUM 2 and MAXIMUM 3 different, meaningful ways to chart this data.

CRITICAL RULES:
1. DO NOT REUSE ANY COLUMN ACROSS CHARTS. Each chart must use completely unique column combinations.
2. NEVER use "invoice_no", "id", or any sequence number columns for label_key or value_key.
3. ONLY choose columns that exist in the sample data provided above.
4. For each chart, identify:
   - label_key: Best column for X-axis/categories (typically names, dates, categories)
   - value_keys: Array of numeric columns for Y-axis/values
5. Choose the most appropriate chart_type from the following options:

AVAILABLE CHART TYPES:
1. "line" - Gradient Stacked Area chart for tracking multiple metrics over time
   - REQUIRES: 2+ value_keys
   - Best for: time series data with multiple numeric metrics
   
2. "donut" - Pie Chart with padding for percentage breakdowns
   - REQUIRES: exactly 1 value_key
   - Best for: showing distribution of a single metric across categories
   
3. "bar_v" - Vertical Bar Chart
   - Standard comparison chart
   
4. "bar_h" - Horizontal Bar Chart
   - Good when category labels are long (e.g., customer names)
   
5. "candlestick" - Financial candlestick chart
   - REQUIRES: EXACTLY 4 value_keys in order [Open, Close, Lowest, Highest]
   - Use approximations if exact financial columns don't exist
   
6. "bar_axis_break" - Bar chart with Y-axis break
   - Use when there's an extreme outlier (one value much larger than others)
   
7. "bar_clickable" - Interactive, zoomable bar chart
   - REQUIRES: exactly 1 value_key
   - Best for single metric comparisons across many categories

STRATEGY:
- Prioritize advanced chart types (candlestick, line, donut, bar_axis_break, bar_clickable) over basic bars
- Use dates/timestamps for line charts when available
- Use categorical fields (names, status, branch) for donut/bar charts
- Look for numeric fields like: total, balance, amount, paid, converted_total, etc.

Return ONLY a valid JSON array (no markdown formatting):
[
  {{
    "label_key": "column_name",
    "value_keys": ["column_name1", "column_name2"],
    "chart_type": "chart_type"
  }},
  {{
    "label_key": "different_column",
    "value_keys": ["different_value_column"],
    "chart_type": "chart_type"
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
            elif c_type_raw in ["line", "area"]:
                c_type = "line"
            elif c_type_raw in ["candlestick", "candle"]:
                c_type = "candlestick"
            elif c_type_raw == "bar_axis_break":
                c_type = "bar_axis_break"
            elif c_type_raw == "bar_clickable":
                c_type = "bar_clickable"
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


@app.route("/demo/ui", methods=["GET"])
@app.route("/", methods=["GET"])
def DemoUI():
    return render_template("demo_frontend.html")

@app.route("/api/health", methods=["GET"])
def health_check():
    """Simple health check endpoint"""
    return jsonify({
        "status": 1,
        "msg": "API is running"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5012, debug=True)
import os
import json
import random
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from google import genai
from dotenv import load_dotenv
import traceback
import re

load_dotenv()

app = Flask(__name__)
client = genai.Client(api_key=os.getenv("GEMINI-API-KEY"))


# ========================================================================
# SMART COLUMN TYPE DETECTION
# ========================================================================

def safe_parse_json(llm_response):
    if not llm_response:
        raise ValueError("Empty LLM response")

    text = llm_response.strip()

    # Remove markdown
    text = re.sub(r"```json", "", text)
    text = re.sub(r"```", "", text)

    # Extract JSON array
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if match:
        text = match.group(0)

    return json.loads(text)

def is_date(value):
    """Check if value looks like a date"""
    if value is None:
        return False
    
    if isinstance(value, datetime):
        return True
    
    if not isinstance(value, str):
        return False
    
    # Common date patterns
    date_patterns = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S"
    ]
    
    for pattern in date_patterns:
        try:
            datetime.strptime(value.split('.')[0].replace('Z', ''), pattern)
            return True
        except:
            continue
    
    # ISO format check
    try:
        datetime.fromisoformat(value.replace("Z", ""))
        return True
    except:
        return False


def detect_column_types(data):
    """
    Detect column types with cardinality awareness.
    
    Returns dict with column types:
    - numeric: numbers (suitable for value_keys)
    - date: date/datetime (suitable for time-series)
    - category: low cardinality text (suitable for label_key)
    - high_cardinality: high cardinality text (NOT suitable for label_key)
    - id: likely an ID column (should be ignored)
    """
    if not data or len(data) == 0:
        return {}
    
    column_types = {}
    column_unique_counts = {}
    
    # Use larger sample for type detection (up to 50 rows)
    sample_size = min(50, len(data))
    sample = data[:sample_size]
    
    first_row = sample[0]
    
    for col in first_row.keys():
        # Collect non-null values
        values = [row.get(col) for row in sample if row.get(col) is not None]
        
        if not values:
            column_types[col] = "unknown"
            continue
        
        unique_values = set(str(v) for v in values)
        column_unique_counts[col] = len(unique_values)
        
        numeric_count = 0
        date_count = 0
        
        # Check each value
        for val in values:
            # Numeric check
            if isinstance(val, (int, float)):
                numeric_count += 1
            elif isinstance(val, str):
                # Try to parse as number
                try:
                    float(val.replace(',', ''))
                    numeric_count += 1
                except:
                    pass
            
            # Date check
            if is_date(val):
                date_count += 1
        
        total = len(values)
        
        # Check if column name suggests it's an ID
        col_lower = col.lower()
        if any(keyword in col_lower for keyword in ['_id', 'id_', 'uuid', 'key']):
            column_types[col] = "id"
        
        # Numeric columns
        elif numeric_count > total * 0.6:
            column_types[col] = "numeric"
        
        # Date columns
        elif date_count > total * 0.6:
            column_types[col] = "date"
        
        # Categorical columns - check cardinality
        else:
            cardinality_ratio = column_unique_counts[col] / total
            
            # High cardinality (likely names, descriptions, IDs)
            if cardinality_ratio > 0.7 or column_unique_counts[col] > 20:
                column_types[col] = "high_cardinality"
            else:
                column_types[col] = "category"
    
    return column_types


def get_smart_sample(db_results, sample_size=8):
    """
    Get a smart sample that includes:
    - Top rows (recent data)
    - Random rows (diversity)
    
    This ensures LLM sees varied data, not just the first few rows.
    """
    if len(db_results) <= sample_size:
        return db_results
    
    # Take first 3 rows (usually most recent)
    top_rows = db_results[:3]
    
    # Take random rows from the rest
    remaining = db_results[3:]
    random_count = min(sample_size - 3, len(remaining))
    
    if random_count > 0:
        random_rows = random.sample(remaining, random_count)
    else:
        random_rows = []
    
    return top_rows + random_rows


# ========================================================================
# CHART CONFIG VALIDATION
# ========================================================================

def validate_chart_config(config, sample_row, column_types):
    """
    Validate if chart configuration is compatible with data structure.
    """
    chart_type = config.get('chart_type', '')
    value_keys = config.get('value_keys', [])
    label_key = config.get('label_key', '')
    
    available_cols = set(sample_row.keys())
    
    # Check if label_key exists and is suitable
    if label_key:
        if label_key not in available_cols:
            return False, f"Label key '{label_key}' not found in data"
        
        # Check if label is high cardinality or ID (should not be used)
        col_type = column_types.get(label_key, "")
        if col_type in ["high_cardinality", "id"]:
            return False, f"Label key '{label_key}' has too many unique values (type: {col_type})"
    
    # Check if all value_keys exist and are numeric
    for vk in value_keys:
        if vk not in available_cols:
            return False, f"Value key '{vk}' not found in data"
        
        col_type = column_types.get(vk, "")
        if col_type not in ["numeric"]:
            return False, f"Value key '{vk}' is not numeric (type: {col_type})"
    
    # Chart-specific validation
    if chart_type in ['candlestick', 'candlestick_brush', 'ohlc']:
        required = {'open', 'high', 'low', 'close'}
        if not required.issubset(set(value_keys)):
            return False, f"{chart_type} requires open, high, low, close columns"
    
    elif chart_type == 'scatter':
        if len(value_keys) < 2:
            return False, "Scatter chart requires at least 2 numeric columns"
    
    elif chart_type in ['rainfall_evaporation', 'beijing_aqi', 'multiple_y_axes']:
        if len(value_keys) < 2:
            return False, f"{chart_type} requires at least 2 value columns"
    
    return True, "Valid"


# ========================================================================
# USER SUGGESTION HANDLING
# ========================================================================

def clean_column_name(col_name):
    """Remove 'table_' prefix from column names if present"""
    if col_name.startswith('table_'):
        return col_name[6:]  # Remove 'table_' prefix
    return col_name


def find_best_column_match(suggested_col, available_cols, column_types):
    """Find the best matching column from available columns"""
    cleaned_suggested = clean_column_name(suggested_col)
    
    # Direct match (after cleaning)
    if cleaned_suggested in available_cols:
        return cleaned_suggested, None
    
    # Partial match
    for col in available_cols:
        if cleaned_suggested.lower() in col.lower() or col.lower() in cleaned_suggested.lower():
            return col, f"Used '{col}' (closest match to '{suggested_col}')"
    
    return None, None


def validate_user_suggestion(user_suggestion, db_results):
    """
    Validate and process user suggestions.
    Returns list of chart configs with messages explaining any changes.
    """
    if not user_suggestion or not isinstance(user_suggestion, dict):
        return None
    
    suggested_charts = user_suggestion.get('chart', [])
    suggested_columns = user_suggestion.get('columns', [])
    
    if not suggested_charts or not suggested_columns:
        return None
    
    # Ensure both are lists
    if not isinstance(suggested_charts, list):
        suggested_charts = [suggested_charts]
    if not isinstance(suggested_columns, list):
        suggested_columns = [suggested_columns]
    
    sample_data = get_smart_sample(db_results, sample_size=8)
    column_types = detect_column_types(db_results)
    available_cols = list(sample_data[0].keys())
    
    numeric_cols = [col for col, ctype in column_types.items() if ctype == "numeric"]
    category_cols = [col for col, ctype in column_types.items() if ctype == "category"]
    date_cols = [col for col, ctype in column_types.items() if ctype == "date"]
    
    chart_configs = []
    
    # Process each chart type
    for chart_type in suggested_charts:
        normalized_chart = normalize_chart_type(chart_type)
        chart_message = None
        selected_columns = []
        label_key = ""
        
        # Map suggested columns to actual columns
        mapped_columns = []
        for suggested_col in suggested_columns:
            matched_col, message = find_best_column_match(suggested_col, available_cols, column_types)
            if matched_col:
                mapped_columns.append((matched_col, message))
        
        # Determine what type of columns this chart needs
        chart_needs_numeric = normalized_chart in ['bar_v', 'bar_h', 'line', 'area', 'large_area', 
                                                     'scatter', 'rainfall_evaporation', 'multiple_axes', 
                                                     'confidence_band', 'donut']
        chart_needs_category = normalized_chart in ['bar_v', 'bar_h', 'donut', 'line', 'area']
        
        # Separate mapped columns by type
        mapped_numeric = [(col, msg) for col, msg in mapped_columns if column_types.get(col) == "numeric"]
        mapped_category = [(col, msg) for col, msg in mapped_columns if column_types.get(col) == "category"]
        mapped_date = [(col, msg) for col, msg in mapped_columns if column_types.get(col) == "date"]
        
        # Build chart configuration based on chart type requirements
        if chart_needs_numeric and chart_needs_category:
            # Charts like bar_v, bar_h, donut need both category (label) and numeric (values)
            
            # Try to use mapped category columns for label
            if mapped_category:
                label_key = mapped_category[0][0]
                if mapped_category[0][1]:
                    chart_message = mapped_category[0][1]
            elif mapped_date:
                # Use date as label if no category
                label_key = mapped_date[0][0]
                if mapped_date[0][1]:
                    chart_message = mapped_date[0][1]
            elif category_cols:
                # Fallback to available category
                label_key = category_cols[0]
                chart_message = f"Used '{label_key}' as label (no suitable category column in your selection)"
            
            # Use mapped numeric columns for values
            if mapped_numeric:
                selected_columns = [col for col, msg in mapped_numeric]
                if not chart_message and any(msg for col, msg in mapped_numeric):
                    chart_message = "; ".join([msg for col, msg in mapped_numeric if msg])
            elif numeric_cols:
                # Fallback to available numeric
                selected_columns = [numeric_cols[0]]
                chart_message = f"Used '{numeric_cols[0]}' (no suitable numeric column in your selection)"
        
        elif chart_needs_numeric:
            # Charts that only need numeric values (like scatter needs 2+ numeric)
            if mapped_numeric:
                selected_columns = [col for col, msg in mapped_numeric]
                if any(msg for col, msg in mapped_numeric):
                    chart_message = "; ".join([msg for col, msg in mapped_numeric if msg])
            elif numeric_cols:
                # Fallback
                selected_columns = numeric_cols[:2] if normalized_chart == 'scatter' else [numeric_cols[0]]
                chart_message = f"Used {', '.join(selected_columns)} (no suitable numeric columns in your selection)"
            
            # For scatter, ensure we have at least 2 numeric columns
            if normalized_chart == 'scatter' and len(selected_columns) < 2:
                if len(numeric_cols) >= 2:
                    selected_columns = numeric_cols[:2]
                    chart_message = f"Scatter chart requires 2 numeric columns. Used '{selected_columns[0]}' and '{selected_columns[1]}'"
        
        # Skip if we couldn't find appropriate columns
        if not selected_columns and not label_key:
            chart_message = f"Could not find suitable columns for {chart_type} chart from your selection"
            continue
        
        # Create chart config
        config = {
            "label_key": label_key,
            "value_keys": selected_columns if selected_columns else [],
            "chart_type": normalized_chart
        }
        
        # Add message if there were any substitutions or issues
        if chart_message:
            config["chart_message"] = chart_message
        
        # Validate the config
        is_valid, validation_msg = validate_chart_config(config, sample_data[0], column_types)
        
        if is_valid:
            chart_configs.append(config)
        else:
            # Try to fix common issues
            if "not numeric" in validation_msg and numeric_cols:
                config["value_keys"] = [numeric_cols[0]]
                config["chart_message"] = f"Selected column was not numeric. Used '{numeric_cols[0]}' instead"
                chart_configs.append(config)
            elif "too many unique values" in validation_msg and category_cols:
                config["label_key"] = category_cols[0]
                config["chart_message"] = f"Selected label had too many unique values. Used '{category_cols[0]}' instead"
                is_valid_retry, _ = validate_chart_config(config, sample_data[0], column_types)
                if is_valid_retry:
                    chart_configs.append(config)
    
    return chart_configs if chart_configs else None


# ========================================================================
# LLM CHART ANALYSIS
# ========================================================================

def analyze_data_for_charts(db_results, user_prompt="", user_suggestion=None):
    if not db_results:
        return []
    
    # If user provided suggestions, try to use them first
    if user_suggestion:
        user_charts = validate_user_suggestion(user_suggestion, db_results)
        if user_charts:
            print(f"[INFO] Using user-suggested charts: {len(user_charts)} charts")
            return user_charts

    sample_data = get_smart_sample(db_results, sample_size=8)
    column_types = detect_column_types(db_results)

    all_columns = list(sample_data[0].keys())

    numeric_cols = [col for col, c in column_types.items() if c == "numeric"]
    date_cols = [col for col, c in column_types.items() if c == "date"]
    category_cols = [col for col, c in column_types.items() if c == "category"]
    high_card_cols = [col for col, c in column_types.items() if c == "high_cardinality"]

    column_info_text = "\n".join([f"- {col}: {ctype}" for col, ctype in column_types.items()])
    sample_json = json.dumps(sample_data, default=str, indent=2)

    # ✅ OPTIMIZED PROMPT
    prompt = f"""
You are an expert data visualization assistant using Apache ECharts.

Your goal:
Create meaningful, insightful, and varied charts.

COLUMN TYPES:
{column_info_text}

COLUMN GROUPS:
- Numeric: {numeric_cols}
- Date: {date_cols}
- Category: {category_cols}
- High Cardinality (DO NOT USE): {high_card_cols}

SAMPLE DATA:
{sample_json}

USER GOAL:
"{user_prompt if user_prompt else 'Generate useful insights'}"

===========================
GUIDELINES
===========================

- Choose charts based on insight, not fixed rules
- Avoid repeating same chart unless needed
- Use advanced charts when useful

Available chart types:
bar_v, bar_h, donut, line, area, large_area,
scatter, rainfall_evaporation, multiple_axes,
confidence_band, beijing_aqi

===========================
IMPORTANT
===========================

Return ONLY valid JSON.
No explanation. No markdown.

===========================
FORMAT
===========================

[
  {{
    "label_key": "column_or_empty",
    "value_keys": ["numeric_column"],
    "chart_type": "bar_v"
  }}
]
"""

    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )

        llm_response = response.text.strip()

        print("\n🔍 RAW LLM RESPONSE:\n", llm_response)

        # ✅ SAFE PARSING
        parsed = safe_parse_json(llm_response)

        if not isinstance(parsed, list):
            parsed = [parsed]

        validated_charts = []

        for chart_config in parsed:
            label_key = chart_config.get("label_key", "")
            value_keys = chart_config.get("value_keys", [])
            chart_type = normalize_chart_type(chart_config.get("chart_type", ""))

            if not value_keys:
                continue

            if label_key and label_key not in all_columns:
                continue

            valid_values = [vk for vk in value_keys if vk in all_columns]
            if not valid_values:
                continue

            config = {
                "label_key": label_key,
                "value_keys": valid_values,
                "chart_type": chart_type
            }

            is_valid, _ = validate_chart_config(config, sample_data[0], column_types)

            if is_valid:
                validated_charts.append(config)

        # ✅ Minimal fallback
        if not validated_charts:
            return create_fallback_charts(numeric_cols, category_cols, sample_data)

        print(f"[SUCCESS] Generated {len(validated_charts)} charts")

        return validated_charts

    except Exception as e:
        print("❌ ERROR:", e)
        return create_fallback_charts(numeric_cols, category_cols, sample_data)
    

def normalize_chart_type(c_type_raw):
    if not c_type_raw:
        return "bar_v"

    c = c_type_raw.lower()

    mapping = {
        "pie": "donut",
        "doughnut": "donut",

        "bar": "bar_v",
        "column": "bar_v",
        "vertical": "bar_v",

        "horizontal": "bar_h",

        "line": "line",
        "area": "area",
        "large_area": "large_area",

        "scatter": "scatter",

        "candlestick": "candlestick",
        "ohlc": "ohlc",

        "rainfall_evaporation": "rainfall_evaporation",
        "beijing_aqi": "beijing_aqi",

        "multiple_axes": "multiple_axes",
        "multiple_y_axes": "multiple_axes",

        "confidence_band": "confidence_band",

        "bar_clickable": "bar_clickable"
    }

    return mapping.get(c, c)   # ✅ DO NOT fallback to bar_v

def add_fallback_charts(existing_charts, numeric_cols, category_cols, sample_data):
    """Add fallback charts if not enough valid charts were generated"""
    if len(existing_charts) == 0 and category_cols and numeric_cols:
        existing_charts.append({
            "label_key": category_cols[0],
            "value_keys": [numeric_cols[0]],
            "chart_type": "bar_v"
        })
    
    if len(existing_charts) <= 1 and numeric_cols:
        if len(category_cols) > 1:
            existing_charts.append({
                "label_key": category_cols[1] if len(category_cols) > 1 else category_cols[0],
                "value_keys": [numeric_cols[0]],
                "chart_type": "donut"
            })
        elif len(category_cols) == 1:
            existing_charts.append({
                "label_key": category_cols[0],
                "value_keys": [numeric_cols[0]],
                "chart_type": "donut"
            })
    
    return existing_charts


def create_fallback_charts(numeric_cols, category_cols, sample_data):
    """Create basic fallback charts when everything else fails"""
    fallback_charts = []
    
    if category_cols and numeric_cols:
        fallback_charts.append({
            "label_key": category_cols[0],
            "value_keys": [numeric_cols[0]],
            "chart_type": "bar_v"
        })
        
        if len(category_cols) > 1:
            fallback_charts.append({
                "label_key": category_cols[1],
                "value_keys": [numeric_cols[0]],
                "chart_type": "donut"
            })
    
    return fallback_charts

# ========================================================================
# FLASK ROUTES
# ========================================================================

@app.route("/api/analyze-charts", methods=["POST"])
def analyze_charts():
    """
    API endpoint to analyze DB results and return chart configurations.
    """
    try:
        data = request.get_json()
        print(f"[INFO]: Received Payload:  {data}")
        
        if not data:
            return jsonify({
                "status": 0,
                "msg": "No data provided",
                "chart_data": []
            }), 400
        
        db_results = data.get("db_result", [])
        user_prompt = data.get("user_prompt", "")
        user_suggestion = data.get("user_suggestion", None)
        
        if not db_results or not isinstance(db_results, list):
            return jsonify({
                "status": 0,
                "msg": "Invalid or empty db_result",
                "chart_data": []
            }), 400
        
        if len(db_results) == 0:
            return jsonify({
                "status": 0,
                "msg": "Empty db_result array",
                "chart_data": []
            }), 400
        
        # Analyze data and get chart configurations
        chart_data = analyze_data_for_charts(db_results, user_prompt, user_suggestion)
        print(chart_data)
        
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
        import traceback
        print(traceback.print_exc())
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
        "msg": "API is running",
        "version": "3.0-production-ready"
    })


@app.route("/demo/ui", methods=["GET"])
@app.route("/", methods=["GET"])
def demo_ui():
    return render_template("demo_frontend.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5012, debug=True)
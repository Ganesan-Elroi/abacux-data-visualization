# abacux_app.py
import os
import json
import psycopg2
from flask import Flask, render_template, request
from google import genai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
client = genai.Client(api_key=os.getenv("GEMINI-API-KEY"))


def get_db_connection():
    try:
        conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        database=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
        )

        
        return conn
    except Exception as e:
        return str(e)


def generate_where_clause(user_prompt):
    if not user_prompt:
        return ""
        
    prompt = f"""
You are a SQL expert assistant for a PostgreSQL database.
The user wants to filter a sales dashboard with this prompt: "{user_prompt}"

The underlying SQL query selects some of these columns from various tables with aliases:
- si (sales_invoices): grand_total, gross_total, invoice_date, paid_status
- u (users): u.name as created_user
- c (customers): c.customer_name, c.contact_no_one as customer_mobile
- v (vendors): v.vendor_name, v.contact_no_one as vendor_mobile
- e (employee): e.employee_name
- isr (invoice_sales_receipts): total_received

Return ONLY a valid PostgreSQL WHERE clause condition that represents the user's filter.
DO NOT include the word "WHERE" or "AND". Return ONLY the condition.
If the prompt has nothing to do with filtering data, return an empty string.
DO NOT format as code block, just text.

CRITICAL INSTRUCTIONS:
1. ONLY filter based on EXACTLY what the user prompt says. 
2. DO NOT hallucinate filters for random names, dates, or terms.
3. Treat each prompt as a completely independent request. Do not remember previous users, names, or values from your context history.
"""
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        condition = response.text.replace("```sql", "").replace("```", "").strip()
        # Strip leading WHERE or AND if LLM accidentally includes it
        if condition.lower().startswith("where "):
            condition = condition[6:].strip()
        if condition.lower().startswith("and "):
            condition = condition[4:].strip()
            
        return condition
    except Exception as e:
        print(f"Error generating WHERE clause: {e}")
        return ""

def run_query(extra_where=""):
    conn = get_db_connection()
    if isinstance(conn, str):
        return conn
    cursor = conn.cursor()

#     db_query = """
#        SELECT 
#     -- si.id,
#     si.invoice_date,
#     si.invoice_no,
#     c.display_name AS customer_display_name,
#     CONCAT(c.salutation, ' ', c.customer_name, ' ', c.last_name) AS customer_name,
#     -- si.payment_due_date,
#     si.grand_total,
#     si.gross_total,
#     si.paid_status,
#     -- si.invoice_type,
# 	CASE 
#         WHEN si.employee_advance_type = 0 
#         THEN SUM(isr.receipt_amount) 
#         ELSE si.grand_total 
#     END AS totalpaid,
#     CASE 
#         WHEN si.employee_advance_type = 0 
#         THEN si.grand_total - SUM(isr.receipt_amount) 
#         ELSE 0 
#     END AS balance,
#     -- si.created_by,
#     -- si.tag_id,
#    --  si.branch_id,
#     -- si.invoice_prefix,
#     -- si.email_id,
#     si.tax_info,
#     -- si.commission_status,
#     -- c.contact_no_one,
#     -- c.contact_no_two,
#     si.created_at,
#     si.updated_at
#     -- si.is_cancelled,
#     -- CONCAT(v.salutation, ' ', v.vendor_name, ' ', v.last_name) AS vendor_name,
#     -- ah.account_holder_type_id,
#     -- v.contact_no_one AS vcontact_no_one,
#     -- v.contact_no_two AS vcontact_no_two,
#     -- v.display_name AS vendor_display_name,
#     -- c.gstin_no AS cgstin_no,
#     -- v.gstin_no AS vgstin_no,
#     -- si.eway_bill_no,
#     -- si.irn_no,
#     -- si.einvoice_status,
#     -- si.einvoice_json,
#     -- si.eway_bill_pdf,
#     -- si.eway_bill_valid_upto,
#     -- si.motor_vehicle_no,
#     -- si.delivery_challan_id,
#     -- si.is_non_journal,
#     -- si.recurring_sales_invoice_id,
#     -- ah.id AS account_holder_id,
#     -- si.currency_conversion_rate,
#     -- v.currency_id AS vendor_currency_id,
#     -- c.currency_id AS customer_currency_id,
#     -- si.approved_config,
#     -- v.gst_treatment_id AS vendor_gst_treatment,
#     -- c.gst_treatment_id AS customer_gst_treatment,
#     -- sb.id AS shipping_bill_id,
#     -- si.invoice_rating,
#     -- si.invoice_rated_through,
#     -- si.si_sequence_format_value
#     -- e.employee_name,
#     -- e.contact_no AS econtact_no,
#     -- si.employee_advance_type
 
# FROM sales_invoices si
 
# LEFT JOIN invoice_sales_receipts isr
#     ON isr.invoice_id = si.id
 
# LEFT JOIN users u
#     ON u.id = si.created_by
 
# LEFT JOIN account_holders ah
#     ON ah.id = si.customer_id
 
# LEFT JOIN vendors v
#     ON v.account_holder_id = ah.id
 
# LEFT JOIN customers c
#     ON c.account_holder_id = ah.id
 
# LEFT JOIN employee e
#     ON e.account_holder_id = ah.id
 
# LEFT JOIN shipping_bills sb
#     ON sb.sales_invoice_id = si.id
    db_query = f"""
    SELECT 

    si.grand_total,

    si.gross_total,

    si.invoice_date,

    si.paid_status,

    CASE 

        WHEN si.paid_status = 0 THEN 'Unpaid'

        WHEN si.paid_status = 1 THEN 'Paid'

        ELSE 'Unknown'

    END AS paid_status_text,
 
    si.si_sequence_format_value,

    u.name AS created_user,
 
    c.customer_name,

    c.contact_no_one AS customer_mobile,
 
    v.vendor_name,

    v.contact_no_one AS vendor_mobile,
 
    e.employee_name,
 
    COALESCE(isr.total_received, 0) AS total_received,
 
    (si.grand_total - COALESCE(isr.total_received, 0)) AS balance_amount
 
FROM sales_invoices si
 
LEFT JOIN users u 

    ON u.id = si.created_by
 
LEFT JOIN account_holders ah 

    ON ah.id = si.customer_id
 
LEFT JOIN vendors v 

    ON v.account_holder_id = ah.id
 
LEFT JOIN customers c 

    ON c.account_holder_id = ah.id
 
LEFT JOIN employee e 

    ON e.id = si.assignee_id
 
LEFT JOIN (

    SELECT 

        invoice_id, 

        SUM(receipt_amount) AS total_received

    FROM invoice_sales_receipts

    GROUP BY invoice_id

) isr 

    ON isr.invoice_id = si.id
 
LEFT JOIN employee_advances ea 

    ON ea.id = si.employee_advance_id 

    AND si.employee_advance_type = 1
 
LEFT JOIN laborwages_advances la 

    ON la.id = si.employee_advance_id 

    AND si.employee_advance_type = 2
 
WHERE 

    si.is_deleted = 0

    AND si.is_draft != 1

    AND si.invoice_prefix != 'OP'

    AND si.branch_id IN (4, 57)

    AND si.invoice_date BETWEEN '2025-12-01' AND '2026-03-17'
"""

    if extra_where:
        db_query += f"\n    AND ({extra_where})"
        
    db_query += """
ORDER BY 

    si.id DESC;
 
    """
    print(f"Final Query: {db_query}")
    cursor.execute(db_query)

    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    results = []
    for row in rows:
        results.append(dict(zip(columns, row)))

    return results

def main():
    try:
        db_results = run_query()
        print(db_results)
        return ""
    except Exception as e:
        return str(e)
    
@app.route("/")
def index():
    user_prompt = request.args.get("user_prompt", "").strip()
    
    # 1. Ask Gemini to write a WHERE clause based on the prompt
    extra_where = generate_where_clause(user_prompt)
    if extra_where:
        print(f"Injected SQL Condition: {extra_where}")
    
    # 2. Run the actual DB query with the dynamic filter
    db_results = run_query(extra_where)

    if not db_results:
        return "No Data Found matching the criteria."

    all_columns = list(db_results[0].keys())
    
    selected_columns = request.args.getlist("columns")
    
    # Define columns to evaluate: user selection, or fallback to all columns on initial load
    eval_columns = selected_columns if selected_columns else all_columns
    
    # Filter sample data to only include the specific columns
    sample_data = []
    for row in db_results[:5]:
        filtered_row = {k: v for k, v in row.items() if k in eval_columns}
        sample_data.append(filtered_row)
        
    sample_json = json.dumps(sample_data, default=str)

    prompt = f"""
You are a data evaluation assistant.
Given the following sample of 5 rows from a database query, featuring ONLY the specific columns the user selected:
{sample_json}

The user has provided the following specific instruction for how they want the charts:
"{user_prompt if user_prompt else 'No specific instructions provided.'}"
(If there is a valid instruction above, you MUST prioritize it highly to decide what chart types and which columns from the sample data to compare!)

Identify up to 3 different, meaningful ways to chart this data.
CRITICAL: DO NOT REUSE ANY COLUMN ACROSS CHARTS. 
If a column is used as a `label_key` or `value_key` in Chart 1, IT MUST NOT BE USED in Chart 2 or Chart 3. All 3 charts MUST use completely unique column combinations.
(e.g., if Chart 1 uses "customer_display_name", Chart 2 must use something else like "invoice_date").
CRITICAL: NEVER choose the column "invoice_no" for either `label_key` or `value_key` in any chart. This is a sequence number, not an analytical dimension!
CRITICAL: You are ONLY allowed to choose columns that are actively present in the sample JSON provided above!

For each chart, identify the best column to use as the "label" (typically a name, category, or date) and the best column(s) to use as the numeric "value".
CRITICAL: DO NOT REUSE ANY COLUMN ACROSS CHARTS. All 3 charts MUST use completely unique column combinations.

IMPORTANT: We have implemented highly optimized, beautiful Apache ECharts for the frontend. You MUST choose from ONLY the following 7 available "chart_type" values:
1. "line" - (Gradient Stacked Area) Use when tracking multiple numeric metrics over time (e.g., date vs gross_total and total_received). MUST provide 2+ value_keys.
2. "donut" - (Pie Chart with padAngle) Use for simple percentage breakdowns of a single metric across categories. MUST provide exactly 1 value_key.
3. "bar_v" - (Vertical Bar) Standard comparison chart.
4. "bar_h" - (Horizontal Bar) Good when category labels are long (e.g., customer names).
5. "candlestick" - Use for financial data if 4 values exist. MUST provide EXACTLY 4 value_keys in order: [Open, Close, Lowest, Highest]. Use approximations like [grand_total, gross_total, total_received, balance_amount] if exact financial columns don't exist.
6. "bar_axis_break" - Use when there is an extreme outlier in the data (one value is MASSIVELY larger than the others). This allows the chart to split the Y-axis.
7. "bar_clickable" - Use for an interactive, zoomable bar chart. Best for single metric comparisons across many categories. MUST provide exactly 1 value_key.

CRITICAL REQUIREMENT: To show off our beautiful codebase, you SHOULD attempt to use the advanced types ("bar_axis_break", "bar_clickable", "candlestick", "line", "donut") instead of just standard bars!

Return ONLY a valid JSON array of objects in this format exactly without markdown formatting:
[
  {{
    "label_key": "column_name",
    "value_keys": ["column_name1", "column_name2", "column_name3"],
    "chart_type": "chart_type"
  }}
]
"""
    
    parsed = []
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        llm_response = response.text.strip()
        
        # Remove markdown ticks if present
        if llm_response.startswith("```json"):
            llm_response = llm_response.replace("```json", "").replace("```", "").strip()
        elif llm_response.startswith("```"):
            llm_response = llm_response.replace("```", "").strip()

        parsed = json.loads(llm_response)
        if not isinstance(parsed, list):
            parsed = [parsed]
            
        print("LLM Detected Output:", parsed)
            
    except Exception as e:
        print(f"Error extracting columns from LLM: {e}")
        # fallback to the defaults already set
        fallback_l = eval_columns[0] if len(eval_columns) > 0 else all_columns[0]
        fallback_v = eval_columns[1] if len(eval_columns) > 1 else (eval_columns[0] if len(eval_columns) > 0 else all_columns[1])
        parsed = [{"label_key": fallback_l, "value_keys": [fallback_v], "chart_type": "bar_v"}]

    charts_list = []
    for c in parsed:
        l_key = c.get("label_key", eval_columns[0] if eval_columns else all_columns[0])
        v_keys = c.get("value_keys", [])
        
        # Handle fallback if old prompt format is accidentally used by LLM
        if not v_keys and "value_key" in c:
            if isinstance(c["value_key"], list):
                v_keys = c["value_key"]
            else:
                v_keys = [c["value_key"]]
        if not v_keys:
            v_keys = [eval_columns[1] if len(eval_columns) > 1 else eval_columns[0]]
        
        # Validate existence
        if l_key not in eval_columns: l_key = eval_columns[0] if eval_columns else all_columns[0]
        valid_v_keys = [vk for vk in v_keys if vk in eval_columns]
        if not valid_v_keys: valid_v_keys = [eval_columns[1] if len(eval_columns) > 1 else eval_columns[0]]
        
        c_type_raw = c.get("chart_type", "bar_v").lower()
        
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
            c_type = "bar_v" # Default fallback
            
        labels = []
        aggregated_data = {}
        
        for row in db_results:
            # Handle potential None values smoothly and convert to string for labels
            lbl = str(row[l_key]) if row.get(l_key) is not None else "Unknown"
            
            if lbl not in aggregated_data:
                aggregated_data[lbl] = {vk: 0.0 for vk in valid_v_keys}
                labels.append(lbl)
                
            for vk in valid_v_keys:
                val = float(row[vk]) if row.get(vk) is not None else 0.0
                aggregated_data[lbl][vk] += val

        datasets = []
        for vk in valid_v_keys:
            values = [aggregated_data[lbl][vk] for lbl in labels]
            datasets.append({
                "label": vk,
                "values": values
            })
        
        charts_list.append({
            "label_key": l_key,
            "value_keys": valid_v_keys,
            "chart_type": c_type,
            "labels": labels,
            "datasets": datasets
        })

    return render_template(
        "abacux_index.html",
        charts_list=json.dumps(charts_list, default=str),
        all_columns=all_columns,
        selected_columns=selected_columns,
        user_prompt=user_prompt
    )


if __name__ == "__main__":
    # # get_db_connection()
    # main()

    app.run(host="0.0.0.0", port=5011, debug=True)
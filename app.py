import os
import json
from flask import Flask, render_template
from google import genai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

client = genai.Client(api_key=os.getenv("GEMINI-API-KEY"))

@app.route("/")
def index():

    db_results = [
        {"category": "Cloud Fees", "value": 450},
        {"category": "Compute", "value": 1200},
        {"category": "Storage", "value": 300},
        {"category": "Bandwidth", "value": 150}
    ]

    data_json = json.dumps(db_results)

    prompt = f"""
You are a data visualization assistant.

Dataset:
{data_json}

Return ONLY a valid Chart.js configuration JSON.
Choose the best chart type (bar, line, doughnut).

Example format:

{{
"type":"bar",
"data":{{
"labels":["A","B"],
"datasets":[{{"label":"Values","data":[10,20]}}]
}}
}}
"""

    response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=prompt
    )

    chart_config_text = response.text.strip()

    try:
        chart_config = json.loads(chart_config_text)
    except:
        chart_config = {
            "type": "bar",
            "data": {
                "labels": [x["category"] for x in db_results],
                "datasets": [{
                    "label": "Cost",
                    "data": [x["value"] for x in db_results]
                }]
            }
        }

    return render_template("index.html", chart_config=chart_config)


if __name__ == "__main__":
    app.run(port=5007, debug=True)
import json
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
@app.route("/index" , methods =["GET"])
def index():
    chart_type = request.values.get("chart_type") or "bar_h"

    db_results = [
        {"category": "Cloud Fees", "value": 450},
        {"category": "Compute", "value": 1200},
        {"category": "Storage", "value": 300},
        {"category": "Bandwidth", "value": 150},
        {"category": "GPU", "value": 200},
        {"category": "AI API", "value": 180}
    ]

    label_key = list(db_results[0].keys())[0]
    value_key = list(db_results[0].keys())[1]

    labels = [x[label_key] for x in db_results]
    values = [x[value_key] for x in db_results]

    chart_data = {
        "labels": labels,
        "values": values
    }

    # chart_type = "donut"   # change to: bar_v , bar_h , line

    return render_template(
        "index_v2.html",
        chart_data=json.dumps(chart_data),
        chart_type=chart_type
    )

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5009)
import json
from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index():

    # Simulated DB JSON (dynamic structure)
    db_results = [
        {"category": "Cloud Fees", "value": 450},
        {"category": "Compute", "value": 1200},
        {"category": "Storage", "value": 300},
        {"category": "Bandwidth", "value": 150},
        {"category": "GPU", "value": 200},
        {"category": "AI API", "value": 180},
    ]

    # Detect column names dynamically
    keys = list(db_results[0].keys())

    label_key = keys[0]
    value_key = keys[1]

    labels = [row[label_key] for row in db_results]
    values = [row[value_key] for row in db_results]

    chart_data = {
        "labels": labels,
        "values": values
    }

    return render_template(
        "index_v1.html",
        chart_data=json.dumps(chart_data)
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5008, debug=True)
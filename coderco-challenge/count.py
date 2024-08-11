from flask import Flask, render_template_string, redirect, url_for
import redis
import random
from datetime import datetime, timedelta
import json

app = Flask(__name__)
r = redis.Redis(host='redis', port=6379)

# Personalized Milestones and Quotes
milestones = {
    100: "Milestone: 100 Visits! This marks the day I decided to change my career to tech.",
    500: "Milestone: 500 Visits! The day I landed my first job as a developer!",
    1000: "Milestone: 1000 Visits! This one goes out to the day I started my journey with CoderCo!"
}

personal_quotes = [
    "The only way to do great work is to love what you do. - Steve Jobs",
    "Success is not final, failure is not fatal: It is the courage to continue that counts. - Winston Churchill",
    "You miss 100% of the shots you don’t take. - Wayne Gretzky",
    "Do or do not, there is no try. - Yoda",
    "CoderCo: Where dreams take code!"
]

# Base HTML template with enhanced logo placement and gradient background
base_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.0.1/chart.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.js"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.css" />
    <style>
        body {
            background: linear-gradient(135deg, #242F46, #FF775C);
            color: white;
            font-family: Arial, sans-serif;
            padding: 50px 0;
        }
        .container {
            background-color: #ffffff;
            color: #333;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
            margin-bottom: 20px;
        }
        .btn-primary {
            background-color: #FF775C;
            border: none;
        }
        .btn-primary:hover {
            background-color: #ff5c42;
        }
        .btn-danger {
            background-color: #FF775C;
            border: none;
        }
        .btn-danger:hover {
            background-color: #ff5c42;
        }
        .btn-secondary {
            background-color: #242F46;
            color: #FFFFFF;
            border: 1px solid #FF775C;
        }
        .btn-secondary:hover {
            background-color: #ff5c42;
            color: #FFFFFF;
        }
        .btn-container {
            margin-top: 30px;
        }
        #visitMap {
            height: 300px;
            margin-top: 20px;
            border-radius: 10px;
        }
        #visitChart {
            margin-top: 20px;
        }
        .logo {
            width: 100px;
            margin-bottom: 20px;
        }
        .milestone {
            margin-top: 20px;
            font-style: italic;
            color: #FF775C;
        }
    </style>
</head>
<body>
    <div class="container text-center">
        <img src="{{ url_for('static', filename='logo.png') }}" alt="CoderCo Logo" class="logo">
        <h1>{{ title }}</h1>
        <p class="lead">{{ message }}</p>

        {% if show_quote %}
        <p class="quote"><em>"{{ quote }}"</em></p>
        {% endif %}

        {% if show_milestone %}
        <p class="milestone">{{ milestone }}</p>
        {% endif %}

        {% if show_map %}
        <div id="visitMap"></div>
        <script>
            var map = L.map('visitMap').setView([51.505, -0.09], 2);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                maxZoom: 18,
                attribution: '© OpenStreetMap'
            }).addTo(map);

            var markers = {{ markers|tojson }};
            markers.forEach(function(marker) {
                L.marker(marker).addTo(map);
            });
        </script>
        {% endif %}

        {% if show_chart %}
        <canvas id="visitChart"></canvas>
        <script>
            var ctx = document.getElementById('visitChart').getContext('2d');
            var visitChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: {{ labels|tojson }},
                    datasets: [{
                        label: 'Daily Visits',
                        data: {{ data|tojson }},
                        borderColor: '#FF775C',
                        borderWidth: 2,
                        fill: false
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        </script>
        {% endif %}

        <div class="btn-container">
            {% if show_count_button %}
            <a href="{{ url_for('count') }}" class="btn btn-primary">{{ count_button_text }}</a>
            {% endif %}
            {% if show_reset_button %}
            <a href="{{ url_for('reset') }}" class="btn btn-danger">{{ reset_button_text }}</a>
            {% endif %}
            <a href="{{ url_for('welcome') }}" class="btn btn-secondary">Home</a>
        </div>
    </div>
</body>
</html>
"""

@app.route('/count')
def count():
    count = r.incr('visits')
    today = datetime.now().strftime('%Y-%m-%d')
    r.hincrby('daily_visits', today, 1)

    # Get a random quote
    quote = random.choice(personal_quotes)

    # Check for milestone
    milestone = milestones.get(count, None)

    # Update visit map
    marker = [random.uniform(-90, 90), random.uniform(-180, 180)]  # Random location for example purposes
    markers = json.loads(r.get('visit_markers') or '[]')
    markers.append(marker)
    r.set('visit_markers', json.dumps(markers))

    return render_template_string(base_template, 
                                  title="Visit Count", 
                                  message=f"This page has been visited {count} times.",
                                  show_reset_button=True,
                                  reset_button_text="Reset Counter",
                                  show_quote=True,
                                  quote=quote,
                                  show_milestone=milestone is not None,
                                  milestone=milestone,
                                  show_map=True,
                                  markers=markers,
                                  show_chart=True,
                                  labels=get_chart_labels(),
                                  data=get_chart_data())

@app.route('/reset')
def reset():
    r.set('visits', 0)
    r.delete('visit_markers')
    r.delete('daily_visits')
    return redirect(url_for('count'))

@app.route('/')
def welcome():
    return render_template_string(base_template, 
                                  title="Welcome to VisitTracker Pro by CoderCo!", 
                                  message="Track your visits with ease. Click the button below to see how many times you've visited this page.",
                                  show_count_button=True, 
                                  count_button_text="View Visit Count")

# Helper function to get chart labels (dates)
def get_chart_labels():
    labels = []
    for i in range(7):
        labels.append((datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d'))
    return labels[::-1]

# Helper function to get chart data (daily visits)
def get_chart_data():
    labels = get_chart_labels()
    data = []
    for label in labels:
        data.append(int(r.hget('daily_visits', label) or 0))
    return data

@app.route('/about')
def about():
    about_text = """
    Welcome to VisitTracker Pro by CoderCo, an application born out of a journey through self-discovery and personal growth. 
    This app isn't just about tracking visits; it's a reflection of milestones, challenges, and the successes that have shaped my journey as a developer.
    Each feature in this app represents a chapter in my story, from the decision to change careers to landing my first job, and finally starting my journey with CoderCo.
    I hope this app inspires you to reflect on your own journey, and to celebrate each step you take along the way.
    """
    return render_template_string(base_template, 
                                  title="About VisitTracker Pro", 
                                  message=about_text,
                                  show_count_button=False)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5002)

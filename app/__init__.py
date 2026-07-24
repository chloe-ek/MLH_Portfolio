import os, datetime, pymysql, psutil
from peewee import *
from flask import Flask, render_template, request
from dotenv import load_dotenv
from playhouse.shortcuts import model_to_dict

load_dotenv()
app = Flask(__name__)

mydb = MySQLDatabase(os.getenv("MYSQL_DATABASE"),
              user=os.getenv("MYSQL_USER"),
              password=os.getenv("MYSQL_PASSWORD"),
              host=os.getenv("MYSQL_HOST"),
              port=3306)

class TimelinePost(Model):
    name = CharField()
    email = CharField()
    content = TextField()
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = mydb

pymysql.install_as_MySQLdb()

mydb.connect()
mydb.create_tables([TimelinePost])


pages = [
    {"name": "Experience", "url": "/#experience"},
    {"name": "Education", "url": "/#education"},
    {"name": "Certifications", "url": "/#certifications"},
    {"name": "Hobbies", "url": "/hobbies"},
    {"name": "Status", "url": "/status"},
]

hobbies = [
    {
        "name": "Hiking",
        "image": "hiking.jpg",
        "description": "Love exploring trails and being out in nature."
    },
    {
        "name": "Baking",
        "image": "baking.jpg",
        "description": "Nothing beats the smell of freshly baked cookies!"
    },
    {
        "name": "Travel",
        "image": "travel.jpg",
        "description": "love visiting new cities, trying local food, and exploring new places."
    }
]

@app.route('/')
def index():
    about = {
        "name": "Chloe Kwon ",
        "bio": "MLH Fellow on Meta's Production Engineering track. I build and break things to understand how systems stay alive under pressure. Focused on cloud infrastructure, observability, and reliability engineering."
    }
    experiences = [
        {
            "company": "Meta X MLH Fellowship",
            "role": "Production Engineering Fellow",
            "duration": "Jun 2026 – Present",
            "location": "Remote"
        },
        {
            "company": "Brats and Bavaria",
            "role": "Freelance Full-Stack Developer",
            "duration": "May 2025 – Present",
            "location": "Vancouver, BC"
        },
        {
            "company": "Byte Camp",
            "role": "Software Developer",
            "duration": "Sep 2025 – Dec 2025",
            "location": "Vancouver, BC"
        }
    ]
    education = [
        {
            "school": "British Columbia Institute of Technology (BCIT)",
            "degree": "Diploma in Computer Systems Technology",
            "years": "Jan 2024 – Dec 2025"
        }
    ]
    certifications = [
        {
            "name": "AWS Certified Solutions Architect – Associate",
            "credential": "SAA-C03",
            "issued": "Jun 25th, 2026"
        }
    ]

    return render_template('index.html', title="MLH Fellow", url=os.getenv("URL"),
                           about=about, experiences=experiences, education=education,
                           certifications=certifications, 
                           hobbies=hobbies, pages=pages)

@app.route('/hobbies')
def hobbies_page():
    return render_template('hobbies.html', title="Hobbies", hobbies=hobbies, pages=pages)


@app.route('/api/timeline_post', methods=['POST'])
def post_time_line_post():
    name = request.form['name']
    email = request.form['email']
    content = request.form['content']
    timeline_post = TimelinePost.create(name=name, email=email, content=content)
    return model_to_dict(timeline_post)

@app.route('/api/timeline_post', methods=['GET'])
def get_time_line_post():
    return {
        'timeline_posts': [
            model_to_dict(p)
            for p in TimelinePost.select().order_by(TimelinePost.created_at.desc())
        ]
    }

@app.route('/timeline')
def timeline():
    return render_template('timeline.html', title="Timeline")


def _bytes_to_gb(num_bytes):
    return round(num_bytes / (1024 ** 3), 2)


@app.route('/api/system_status')
def system_status():
    cpu_percent = psutil.cpu_percent(interval=0.2)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    try:
        mydb.execute_sql('SELECT 1')
        db_status = 'ok'
    except Exception:
        db_status = 'error'

    return {
        'db': db_status,
        'timestamp': datetime.datetime.now().isoformat(),
        'cpu': {
            'percent': cpu_percent,
            'cores': psutil.cpu_count(),
        },
        'memory': {
            'percent': memory.percent,
            'used_gb': _bytes_to_gb(memory.total - memory.available),
            'total_gb': _bytes_to_gb(memory.total),
        },
        'disk': {
            'percent': disk.percent,
            'used_gb': _bytes_to_gb(disk.used),
            'total_gb': _bytes_to_gb(disk.used + disk.free),
        },
    }


@app.route('/status')
def status_page():
    return render_template('status.html', title="Server Status", pages=pages)
📌 Event Management API (Django REST Framework)

A simple API for creating events, managing RSVPs, and adding reviews. Supports JWT authentication, permissions, and public/private event access.

🚀 Features

Create, update, delete events (organizer only)

Public & private events with invited users

RSVP system: Going / Maybe / Not Going

Reviews with 1–5 star rating

JWT authentication

Search, filter, pagination

🛠️ Tech Stack

Django 4+

Django REST Framework

SimpleJWT

SQLite

⚙️ Setup
git clone <repo-url>
cd event_api
python -m venv venv
venv\Scripts\activate      # or source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver


API runs at:
http://127.0.0.1:8000/

🔑 Authentication (JWT)

Get Token

POST /api/token/


Use Token

Authorization: Bearer <access_token>

📚 Main Endpoints
Events

GET /api/events/ – List events

POST /api/events/ – Create event

GET /api/events/{id}/ – Event details

PUT /api/events/{id}/ – Update (organizer)

DELETE /api/events/{id}/ – Delete (organizer)

RSVP

POST /api/events/{id}/rsvp/

PATCH /api/events/{event_id}/rsvp/{user_id}/

Reviews

GET /api/events/{id}/reviews/


POST /api/events/{id}/reviews/

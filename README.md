# Klub

Klub is a school assistance app that puts courses, documents, and AI help in one place.
It uses the Ecole Directe (Mon ENT) ecosystem to retrieve student data (homework and grades), then adds AI tools to help with study and revision.

## Tech Stack

- Frontend: Angular 17 (+ Tailwind CSS)
- Backend: Flask (Python 3.11)
- AI: Groq API
- Deployment: Docker + Nginx

## Quick Start (Docker)

1. Create `backend/.env` from `backend/exemple.env`.
2. Fill these variables in `backend/.env`:
	- `GROQ_API_KEY`
	- `SECRET_KEY`
	- `ACCESS_CODE`
3. Start the app:

```bash
docker-compose up --build
```

4. Open:
	- Frontend: `http://localhost:4200`
	- Backend health check: `http://localhost:5000/api/health`

## Run Without Docker

### Frontend

```bash
cd frontend
npm install
npm start
```

### Backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```

## Authentication

- Login route: `POST /api/auth/login` with JSON body: `{ "code": "<ACCESS_CODE>" }`
- Most `/api/*` routes require an authenticated session.
- Public routes: `/api/auth/login` and `/api/health`

## Main API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/cours` | `GET`, `POST` | List or create course files |
| `/api/cours/<matiere>/<nom>` | `DELETE` | Delete a course file |
| `/api/flash-cards` | `GET`, `POST` | List or create flash-card sets |
| `/api/devoirs` | `GET` | Get homework data |
| `/api/notes` | `GET` | Get grades |
| `/api/notes/commentaire` | `GET` | Generate AI grade comment |
| `/api/chat_devoirs` | `POST` | AI help for homework |
| `/api/cours/chat` | `POST` | AI chat using a selected course |
| `/api/chat/global` | `POST` | General AI chat with tools |
| `/api/ocr` | `POST` | OCR from images and save as a course |

## Production Notes

- Use `docker-compose.prod.yml` for production.
- Services are bound to `127.0.0.1` in prod compose.
- Frontend Nginx production config includes HTTP Basic Auth.

## License

GNU GPL v3 (see `LICENSE`).

# Developer Guidance System

The Developer Guidance System is a backend platform designed to help users become better developers through personalized learning roadmaps, adaptive task management, and intelligent feedback. It leverages AI to generate tailored content and integrates with external APIs for enhanced resources.

## Key Features

- **User Registration**: Register with interests, age, and daily learning time
- **Personalized Roadmap Generation**: AI-powered creation of step-by-step learning plans
- **Task Generation**: Daily tasks generated for each roadmap step
- **Sources Integration**: Each task is enriched with relevant learning resources via an external sources API
- **Progress Tracking**: Monitor task completion and learning progress
- **Adaptive Learning**: System adapts to user performance and failures
- **Failure Handling**: Intelligent reassignment and support for incomplete tasks

## Setup Instructions

1. **Install Dependencies**
   ```bash
   pip install -e .
   ```

2. **Environment Variables**
   Create a `.env` file in the project root:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   GOOGLE_API_KEY=your_google_api_key_here
   # Optional: Set the sources API endpoint
   SOURCES_API_URL=http://your-sources-api-url/get-sources
   ```

3. **Database Migration**
   Run Alembic migrations to set up the database schema:
   ```bash
   alembic upgrade head
   ```

4. **Start the Application**
   ```bash
   python main.py
   ```

5. **API Documentation**
   Access interactive docs at: [http://localhost:8000/docs](http://localhost:8000/docs)

## Docker Usage

You can run the entire stack without installing Python locally using Docker.

### 1. Build & Run

```bash
docker compose up --build
```

Then visit: http://localhost:8000/docs

### 2. Environment Variables

Pass API keys either via an `.env` file (same directory as `docker-compose.yml`) or inline:

```bash
GROQ_API_KEY=your_key GOOGLE_API_KEY=your_key docker compose up --build
```

Example `.env` file:
```
GROQ_API_KEY=your_groq_api_key
GOOGLE_API_KEY=your_google_api_key
DATABASE_URL=sqlite:///./hackathon.db
```

### 3. Automatic Migrations

The container entrypoint runs:
```
alembic upgrade head
```
before starting `uvicorn`, ensuring the database schema is always up to date.

### 4. Development (Live Reload)

For iterative development, uncomment the `volumes` section in `docker-compose.yml` to mount the source code. Note: mounting the project root will override the pre-built virtual environment. If that happens, exec into the container and run `uv sync --locked` again.

### 5. One-off Migration Command

You can run only migrations using the `migrate` profile:
```bash
docker compose run --build migrate
```

### 6. Clean Up

```bash
docker compose down -v
```

This stops containers and removes anonymous volumes.

---

### Troubleshooting

- If dependencies change, rebuild with `--build`.
- Override the database (e.g., Postgres) by setting `DATABASE_URL` and adding the appropriate driver package to `pyproject.toml`.
- Healthcheck failures: run `docker compose logs app` to inspect startup issues.


## API Endpoints Overview

### User Management
- `POST /api/register` — Register a new user
- `GET /api/user/{user_id}` — Retrieve user details

### Roadmap Management
- `POST /api/roadmap/generate` — Generate a personalized roadmap
- `GET /api/roadmap/{user_id}` — Get the active roadmap for a user
- `POST /api/roadmap/regenerate/{user_id}` — Regenerate roadmap and tasks

### Task Management
- `POST /api/tasks/generate/{user_id}` — Generate tasks for the current roadmap step
- `GET /api/tasks/{user_id}` — Retrieve all active tasks for a user
- `POST /api/tasks/complete/{user_id}` — Mark tasks as completed
- `POST /api/tasks/failure/{user_id}` — Report task failures and reassign

## Database Schema Overview

- **Users**: Stores user profile and preferences
- **Roadmaps**: Stores generated learning plans
- **Tasks**: Stores individual learning tasks and their sources
- **TaskFailures**: Stores failure events for adaptive learning

## System Workflow

1. User registers and provides interests, age, and time availability
2. System generates a personalized roadmap using AI
3. User requests daily tasks for the current roadmap step
4. Each task is enriched with sources from the external API
5. User completes tasks or reports failures
6. System adapts future tasks and roadmap steps based on user progress

## Technology Stack

- **FastAPI** — Web API framework
- **SQLAlchemy** — ORM for database management
- **SQLite** — Default database (can be swapped)
- **LangChain Groq** — AI-powered roadmap and task generation
- **Pydantic** — Data validation and serialization
- **Alembic** — Database migrations
- **Requests** — External API integration for sources

## Customization & Extensibility

- **Sources API**: Integrate with any external API to provide resources for each task. Configure the endpoint via the `SOURCES_API_URL` environment variable.
- **AI Model**: Swap or extend the AI integration for roadmap and task generation as needed.

## Getting Help

For questions, issues, or contributions, please open an issue or contact the maintainer.

### Roadmap Management
- `POST /api/roadmap/generate` - Generate a new roadmap
- `GET /api/roadmap/{user_id}` - Get active roadmap
- `POST /api/roadmap/regenerate/{user_id}` - Regenerate roadmap

### Task Management
- `POST /api/tasks/generate/{user_id}` - Generate tasks
- `GET /api/tasks/{user_id}` - Get user tasks
- `POST /api/tasks/complete/{user_id}` - Complete tasks
- `POST /api/tasks/failure/{user_id}` - Handle task failures

## Database Schema

- **Users**: Store user information and preferences
- **Roadmaps**: Store generated learning roadmaps
- **Tasks**: Store individual learning tasks
- **TaskFailures**: Store failure reasons for learning improvement

## Flow

1. User registers with interests and time availability
2. System generates personalized roadmap using AI
3. User requests tasks for current roadmap step
4. User completes tasks or reports failures
5. System adapts based on completion/failure patterns
6. Process continues with progressive learning

## Technology Stack

- **FastAPI**: Web framework
- **SQLAlchemy**: ORM
- **SQLite**: Database
- **LangChain Groq**: AI integration
- **Pydantic**: Data validation

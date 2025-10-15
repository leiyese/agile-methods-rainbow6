# Development Setup Guide

This guide will help you get the project running locally using Docker Compose.

## Prerequisites

Before you start, make sure you have installed:
- [Git](https://git-scm.com/downloads)
- [Docker Desktop](https://www.docker.com/products/docker-desktop) (includes Docker Compose)

### Verify Installation
Open your terminal/command prompt and run:
```bash
docker --version
docker-compose --version
```

## Step-by-Step Setup

### 1. Clone the Repository
```bash
git clone https://github.com/leiyese/agile-methods-rainbow6.git
cd agile-methods-rainbow6
```

### 2. Set Up Environment Variables
Create your environment file by copying the example:

**On Windows (PowerShell):**
```powershell
Copy-Item "env example" .env
```

**On Windows (Command Prompt):**
```cmd
copy "env example" .env
```

**On Mac/Linux:**
```bash
cp "env example" .env
```

Then edit the `.env` file and fill in the empty values. Here are **example values for local development only**:
```bash
POSTGRES_DB=agile_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_local_password_here
```

⚠️ **Important Notes:**
- These are **placeholder values for local development only**
- Use strong, unique passwords even for local development
- Never commit your `.env` file to version control (it's already in `.gitignore`)
- For production, use secure, randomly generated passwords

### 3. Start the Application
Run this command from the project root directory:
```bash
docker-compose up
```

**What this does:**
- Builds and starts the Flask backend (Python API)
- Builds and starts the React frontend (Web UI)  
- Starts a PostgreSQL database with pgvector extension
- Creates necessary Docker volumes for data persistence

### 4. Wait for Everything to Start
The first run will take longer as Docker needs to:
- Download base images (Node.js, Python, PostgreSQL)
- Install all dependencies
- Build the applications

You'll know everything is ready when you see:
```
backend-1   | * Running on all addresses (0.0.0.0)
backend-1   | * Running on http://127.0.0.1:8001
frontend-1  | Local:   http://localhost:5173/
postgres-1  | database system is ready to accept connections
```

### 5. Access the Application
Once everything is running, you can access:
- **Frontend (React UI)**: http://localhost:5173
- **Backend API**: http://localhost:8001
- **Database**: localhost:5432 (if you need direct database access)

## Common Commands

### Start in Background (Detached Mode)
```bash
docker-compose up -d
```

### View Logs
```bash
# View all logs
docker-compose logs

# View logs for specific service
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres

# Follow logs in real-time
docker-compose logs -f
```

### Stop the Application
```bash
docker-compose down
```

### Rebuild After Code Changes
If you make changes to Docker files or dependencies:
```bash
docker-compose down
docker-compose build
docker-compose up
```

### Clean Restart (Remove Volumes)
If you want to start fresh and remove all data:
```bash
docker-compose down -v
docker-compose up
```

## Troubleshooting

### Port Already in Use
If you see errors like "port 8001 is already in use":
1. Stop any other applications using those ports
2. Or modify the ports in `docker-compose.yml`

### Database Connection Issues
- Make sure your `.env` file has the correct database credentials
- Verify all environment variables are filled in (no empty values)
- Try a clean restart: `docker-compose down -v && docker-compose up`

### Build Failures
- Make sure Docker Desktop is running
- Try rebuilding: `docker-compose build --no-cache`
- Check if you have enough disk space

### File Changes Not Reflecting
The setup uses volume mounts, so your code changes should appear immediately:
- **Backend**: Changes to Python files will trigger auto-reload
- **Frontend**: Changes to React files will trigger hot reload
- If changes don't appear, try restarting the specific service

## Development Workflow

### Making Backend Changes
1. Edit files in the `backend/` directory
2. Flask will automatically reload (you'll see restart messages in logs)
3. Test your changes at http://localhost:8001

### Making Frontend Changes  
1. Edit files in the `frontend/` directory
2. Vite will automatically reload the browser
3. Test your changes at http://localhost:5173

### Database Access
If you need to access the PostgreSQL database directly:
```bash
# Connect to the database container
docker-compose exec postgres psql -U [your_username] -d [your_database_name]

# Or use a GUI tool like pgAdmin with:
# Host: localhost
# Port: 5432  
# Username: (whatever you set in .env)
# Password: (whatever you set in .env)
# Database: (whatever you set in .env)
```

## Security Best Practices

- ✅ **DO**: Use strong passwords even for local development
- ✅ **DO**: Keep your `.env` file private (never commit it)
- ✅ **DO**: Use different credentials for different environments
- ❌ **DON'T**: Share your `.env` file in chat or email
- ❌ **DON'T**: Use production credentials for local development

## Need Help?

- Check the logs: `docker-compose logs`
- Restart services: `docker-compose restart [service-name]`
- Ask the team in our project channel
- Check Docker Desktop dashboard for container status

## Quick Reference

| Command | Purpose |
|---------|---------|
| `docker-compose up` | Start all services |
| `docker-compose up -d` | Start in background |
| `docker-compose down` | Stop all services |
| `docker-compose logs -f` | View live logs |
| `docker-compose build` | Rebuild containers |
| `docker-compose restart backend` | Restart specific service |

Happy coding! 🚀

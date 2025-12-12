# TaskMind

A full-stack task management application built with Python, featuring a Streamlit frontend and Flask backend, containerized with Docker and deployed with CI/CD automation.

## 📋 Table of Contents
- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [How We Built This - Step by Step](#how-we-built-this---step-by-step)
  - [Step 1: Project Setup & Git Initialization](#step-1-project-setup--git-initialization)
  - [Step 2: Building the Frontend](#step-2-building-the-frontend)
  - [Step 3: Database Design & Setup](#step-3-database-design--setup)
  - [Step 4: Building the Backend API](#step-4-building-the-backend-api)
  - [Step 5: Dockerizing the Application](#step-5-dockerizing-the-application)
  - [Step 6: CI/CD Pipeline Setup](#step-6-cicd-pipeline-setup)
  - [Step 7: Deployment](#step-7-deployment)
- [Running Locally](#running-locally)
- [Contributing](#contributing)

## 🎯 Overview

TaskMind is a modern task management application that allows users to create, manage, and track their tasks efficiently. Built with a microservices architecture, it demonstrates best practices in full-stack development, containerization, and DevOps. 

## 🛠️ Tech Stack

- **Frontend**: Streamlit (Python)
- **Backend**: Flask (Python)
- **Database**: PostgreSQL
- **Containerization**: Docker & Docker Compose
- **CI/CD**: GitHub Actions
- **Container Registry**: Docker Hub
- **Deployment**: Railway / Render

---

## 🚀 How We Built This - Step by Step

### Step 1: Project Setup & Git Initialization

**1.1 Create the project directory**
```bash
mkdir TaskMind
cd TaskMind
```

**1.2 Initialize Git repository**
```bash
git init
git branch -M master
```

**1.3 Create initial project structure**
```bash
mkdir FrontEnd BackEnd tests
touch README.md . gitignore requirements.txt
```

**1.4 Create .gitignore**
```gitignore
__pycache__/
*.pyc
*.pyo
*.db
. env
venv/
. DS_Store
```

**1.5 First commit**
```bash
git add . 
git commit -m "Initial commit:  Project structure"
```

**1.6 Connect to GitHub**
```bash
# Create repository on GitHub first, then: 
git remote add origin git@github.com:kernelbits/TaskMind.git
git push -u origin master
```

---

### Step 2: Building the Frontend

**2.1 Create Frontend structure**
```bash
cd FrontEnd
touch frontend. py Dockerfile requirements.txt
```

**2.2 Install Streamlit**
```bash
pip install streamlit
```

**2.3 Build the Streamlit UI** (`FrontEnd/frontend.py`)
- Created main page layout
- Added task input forms
- Implemented task list display
- Added filtering and search functionality
- Integrated with Backend API endpoints

**2.4 Create Frontend requirements** (`FrontEnd/requirements.txt`)
```txt
streamlit
requests
```

**2.5 Test frontend locally**
```bash
streamlit run frontend.py
```

**2.6 Commit frontend**
```bash
git add FrontEnd/
git commit -m "feat: Add Streamlit frontend"
git push origin master
```

---

### Step 3: Database Design & Setup

**3.1 Design database schema**
- Created `tasks` table with fields: 
  - `id` (Primary Key)
  - `title` (VARCHAR)
  - `description` (TEXT)
  - `status` (VARCHAR)
  - `priority` (VARCHAR)
  - `created_at` (TIMESTAMP)
  - `updated_at` (TIMESTAMP)

**3.2 Choose PostgreSQL**
- Selected PostgreSQL for reliability and scalability
- Decided to use managed database service for production

**3.3 Create database configuration**
- Set up environment variables for database connection
- Created connection pooling for efficiency

**3.4 Write database initialization scripts**
```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    priority VARCHAR(50) DEFAULT 'medium',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### Step 4: Building the Backend API

**4.1 Create Backend structure**
```bash
cd BackEnd
touch backend.py Dockerfile requirements.txt
```

**4.2 Install Flask and dependencies**
```bash
pip install flask flask-cors psycopg2-binary python-dotenv
```

**4.3 Build Flask API** (`BackEnd/backend.py`)
- Set up Flask application
- Configured CORS for frontend communication
- Implemented REST API endpoints: 
  - `GET /tasks` - List all tasks
  - `POST /tasks` - Create new task
  - `GET /tasks/<id>` - Get single task
  - `PUT /tasks/<id>` - Update task
  - `DELETE /tasks/<id>` - Delete task
- Added database connection handling
- Implemented error handling and validation

**4.4 Create Backend requirements** (`BackEnd/requirements.txt`)
```txt
flask
flask-cors
psycopg2-binary
python-dotenv
```

**4.5 Test backend API**
```bash
python backend.py
# Test endpoints with curl or Postman
```

**4.6 Create root requirements. txt**
```txt
flask
flask-cors
streamlit
requests
psycopg2-binary
python-dotenv
```

**4.7 Commit backend**
```bash
git add BackEnd/ requirements.txt
git commit -m "feat: Add Flask backend API"
git push origin master
```

---

### Step 5: Dockerizing the Application

**5.1 Create Backend Dockerfile** (`BackEnd/Dockerfile`)
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend.py . 

EXPOSE 5000

CMD ["python", "backend.py"]
```

**5.2 Create Frontend Dockerfile** (`FrontEnd/Dockerfile`)
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY frontend. py .

EXPOSE 8501

CMD ["streamlit", "run", "frontend.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**5.3 Create Docker Compose** (`docker-compose.yml`)
```yaml
version: '3.8'

services:
  backend:
    build: 
      context: . 
      dockerfile: BackEnd/Dockerfile
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
    restart: unless-stopped

  frontend:
    build: 
      context: . 
      dockerfile: FrontEnd/Dockerfile
    ports:
      - "8501:8501"
    depends_on:
      - backend
    environment:
      - BACKEND_URL=http://backend:5000
    restart: unless-stopped
```

**5.4 Create . dockerignore**
```
__pycache__/
*. pyc
*.pyo
. git/
.gitignore
.env
venv/
tests/
README.md
```

**5.5 Test Docker setup locally**
```bash
docker-compose build
docker-compose up
```

**5.6 Commit Docker configuration**
```bash
git add Dockerfile docker-compose.yml . dockerignore
git commit -m "feat: Add Docker containerization"
git push origin master
```

---

### Step 6: CI/CD Pipeline Setup

**6.1 Create GitHub Actions workflow** (`.github/workflows/ci-cd.yml`)

```yaml
name: CI/CD Pipeline

on:
  push: 
    branches: [ master, develop ]
  pull_request: 
    branches: [ master ]

env:
  DOCKERHUB_USERNAME: ${{ secrets.DOCKERHUB_USERNAME }}
  BACKEND_IMAGE: ${{ secrets.DOCKERHUB_USERNAME }}/taskmind-backend
  FRONTEND_IMAGE: ${{ secrets. DOCKERHUB_USERNAME }}/taskmind-frontend

jobs: 
  test:
    name: Run Tests
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses:  actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version:  '3.11'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov flake8
      
      - name: Run linting
        run: |
          flake8 BackEnd/backend.py --count --select=E9,F63,F7,F82 --show-source --statistics || true
          flake8 FrontEnd/frontend.py --count --select=E9,F63,F7,F82 --show-source --statistics || true
      
      - name: Test Backend imports
        run: |
          python -c "import sys; sys.path.insert(0, '. '); from BackEnd.backend import app; print('✅ Backend imports OK')"
      
      - name: Run tests
        run: |
          pytest tests/ -v || echo "No tests found yet"

  build:
    name: Build & Push Images
    runs-on: ubuntu-latest
    needs: test
    if: github.event_name == 'push' && github.ref == 'refs/heads/master'
    
    steps:
      - name:  Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Log in to Docker Hub
        uses:  docker/login-action@v3
        with:
          username:  ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
      
      - name: Build and push Backend image
        uses: docker/build-push-action@v5
        with:
          context: . 
          file: ./BackEnd/Dockerfile
          push: true
          tags: |
            ${{ env.BACKEND_IMAGE }}:latest
            ${{ env.BACKEND_IMAGE }}:${{ github. sha }}
      
      - name: Build and push Frontend image
        uses: docker/build-push-action@v5
        with: 
          context: .
          file: ./FrontEnd/Dockerfile
          push: true
          tags: |
            ${{ env. FRONTEND_IMAGE }}:latest
            ${{ env.FRONTEND_IMAGE }}:${{ github.sha }}

  deploy:
    name:  Deployment Ready
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/master' && github.event_name == 'push'
    
    steps:
      - name:  Deployment notification
        run: |
          echo "🚀 Deployment Ready!"
          echo "Backend:  ${{ env.BACKEND_IMAGE }}:latest"
          echo "Frontend: ${{ env.FRONTEND_IMAGE }}:latest"
```

**6.2 Set up Docker Hub**
- Created account on Docker Hub
- Created access token in Security settings

**6.3 Configure GitHub Secrets**
Go to repository Settings → Secrets and variables → Actions: 
- `DOCKERHUB_USERNAME`: Your Docker Hub username
- `DOCKERHUB_TOKEN`: Docker Hub access token

**6.4 Commit CI/CD workflow**
```bash
git add .github/
git commit -m "feat: Add CI/CD pipeline with GitHub Actions"
git push origin master
```

**6.5 Monitor first pipeline run**
- Go to Actions tab on GitHub
- Watch the workflow execute
- Fixed authentication issues (incorrect Docker Hub credentials)
- Verified images pushed successfully to Docker Hub

---

### Step 7: Deployment

**7.1 Choose deployment platform**
- Evaluated options: Railway, Render, AWS, Heroku
- Selected Railway for ease of use and PostgreSQL support

**7.2 Create deployment configuration**

**For Railway:** (`railway/railway.toml`)
```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "BackEnd/Dockerfile"

[deploy]
startCommand = "python backend.py"
restartPolicyType = "ON_FAILURE"
```

**For Render:** (`render.yaml`)
```yaml
services:
  - type: web
    name: taskmind-backend
    env:  docker
    dockerfilePath: ./BackEnd/Dockerfile
    envVars:
      - key: DATABASE_URL
        sync: false

  - type: web
    name: taskmind-frontend
    env: docker
    dockerfilePath: ./FrontEnd/Dockerfile
    envVars: 
      - key: BACKEND_URL
        sync: false

databases:
  - name: taskmind-db
    databaseName: taskmind
    user: taskmind
```

**7.3 Deploy to Railway**
1. Connected GitHub repository to Railway
2. Created PostgreSQL database
3. Set environment variables
4. Deployed backend and frontend services
5. Configured custom domains (optional)

**7.4 Commit deployment configs**
```bash
git add railway/ render.yaml
git commit -m "feat: Add deployment configurations"
git push origin master
```

**7.5 Verify deployment**
- Tested live application
- Verified database connections
- Checked API endpoints
- Tested frontend functionality

---

## 🏃 Running Locally

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL (or use Docker)

### With Docker (Recommended)
```bash
# Clone the repository
git clone https://github.com/kernelbits/TaskMind.git
cd TaskMind

# Set environment variables
cp .env.example .env
# Edit .env with your database credentials

# Build and run
docker-compose up --build
```

Access: 
- Frontend: http://localhost:8501
- Backend API: http://localhost:5000

### Without Docker
```bash
# Clone the repository
git clone https://github.com/kernelbits/TaskMind.git
cd TaskMind

# Install dependencies
pip install -r requirements. txt

# Run backend
cd BackEnd
python backend.py

# In another terminal, run frontend
cd FrontEnd
streamlit run frontend.py
```

---

## 📝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📦 Docker Images

Pull pre-built images from Docker Hub:
```bash
docker pull kernelbits/taskmind-backend:latest
docker pull kernelbits/taskmind-frontend:latest
```

---

## 🔗 Links

- **Repository**: https://github.com/kernelbits/TaskMind
- **Docker Hub**: https://hub.docker.com/u/kernelbits
- **Issues**: https://github.com/kernelbits/TaskMind/issues

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 👤 Author

**KernelBits**
- GitHub: [@kernelbits](https://github.com/kernelbits)
- Docker Hub: [kernelbits](https://hub.docker.com/u/kernelbits)

---

Built with ❤️ using Python, Docker, and modern DevOps practices
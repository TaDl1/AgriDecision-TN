# Setup Guide: AgriDecision-TN

## Project Overview
**AgriDecision-TN** is a smart agricultural decision-support platform designed for farmers in Tunisia. At its core, the platform is structured around the **Tunisian Agricultural Calendar (Calendrier Agraire)**, ensuring that advice on crop selection, financial planning, and risk management is perfectly synchronized with local seasonal cycles, regional benchmarks, and real-time weather conditions.

## Prerequisites

### Software
- **Python 3.9+**: Backend runtime.
- **Node.js 18.x+**: Frontend development environment.
- **npm or yarn**: Package managers for frontend dependencies.
- **SQLite**: (Built-in with Python) Local database for development.

### Tools & Extensions (Recommended)
- **VS Code**: Recommended IDE.
- **Python Extension**: For IntelliSense and linting.
- **ESLint & Prettier**: For frontend code formatting.
- **Tailwind CSS IntelliSense**: For rapid UI development.
- **Postman or Insomnia**: For API testing (Insomnia collection available in `/insomnia`).

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd AgriDecision-TN
```

### 2. Backend Setup
Navigate to the `backend` directory and set up a virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Frontend Setup
Navigate to the `frontend` directory and install dependencies:
```bash
cd ../frontend
npm install
```

## Configuration

### Environment Variables
1. Copy the `.env.example` from the root to both `backend` and `frontend` folders (or create specific ones):
   - **Backend**: Create a `.env` in `/backend`.
   - **Frontend**: Create a `.env.development` in `/frontend`.

2. Key Variables to Configure:
   - `SECRET_KEY`: A secure string for Flask sessions.
   - `DATABASE_URL`: Defaults to `sqlite:///data/agridecision.db`.
   - `OPENWEATHER_API_KEY`: Required for real-time weather features.
   - `OPENAI_API_KEY`: Required for smart summary interpretations.

## Running the Project

### Start the Backend
```bash
cd backend
python app.py
```
The backend API will run on `http://localhost:5000`.

### Start the Frontend
```bash
cd frontend
npm run dev
```
The frontend will be accessible at `http://localhost:5173`.

## Key Features & Commands

### 📚 API Documentation & Evaluation
- **Interactive Docs**: Visit **`http://localhost:5000/apidocs`** after starting the backend to test endpoints via Swagger.
- **Project Evaluation**: See **`academic_project_evaluation.md`** in the root directory for a comprehensive software engineering audit of the platform.

### 🧪 Testing
Run the comprehensive test suite, including edge-case verification:
```bash
cd backend
pytest tests/test_edge_cases_simple.py
```

### 🚀 CI/CD Pipeline
The project includes a GitHub Actions workflow (`.github/workflows/deploy.yml`) that:
- Triggers on push to `main`.
- Runs all unit and integration tests.
- Deploys automatically to the configured VPS via SSH.

## AI-Assisted Workflow (GitHub Copilot)
This project is optimized for an AI-assisted workflow using **GitHub Copilot**. 
- **Boilerplate**: Use Copilot to generate SQLAlchemy models and React components quickly.
- **Testing**: Generate `pytest` cases for backend services and `vitest` for frontend components.
- **Refactoring**: Leverage Copilot Chat to refactor complex analytical logic (e.g., AES calculations).
- **Documentation**: Copilot helps maintain the `history.log` and API documentation by summarizing recent changes.

---
*For deployment instructions, please refer to [DEPLOYMENT.md](file:///d:/AgriDecision-TN/DEPLOYMENT.md).*
*Detailed interaction audit can be found in [history.log](file:///d:/AgriDecision-TN/history.log).*

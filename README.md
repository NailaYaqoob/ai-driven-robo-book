# Physical AI & Humanoid Robotics Interactive Textbook

A comprehensive, interactive textbook for learning Physical AI and Humanoid Robotics, featuring a 13-week curriculum with integrated RAG chatbot, personalization engine, and Urdu translation.

## 🎯 Features

- **📚 Complete 13-Week Curriculum**: From ROS 2 fundamentals to autonomous humanoid development
- **🤖 AI-Powered Chatbot**: Ask questions and get contextual answers with source citations
- **👤 Personalized Learning**: Adapt content based on your role (Student/Educator/Professional) and skill level
- **🌐 Urdu Translation**: Full RTL translation with technical accuracy
- **📱 Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **♿ Accessibility**: WCAG 2.1 Level AA compliant

## 🏗️ Project Structure

```
ai-driven-robo-book/
├── website/              # Docusaurus frontend
│   ├── docs/            # Textbook content (MDX)
│   ├── src/             # React components, hooks, context
│   └── static/          # Images, diagrams, PDFs
├── backend/             # FastAPI backend
│   ├── app/             # Application code
│   │   ├── api/         # API routes
│   │   ├── services/    # Business logic (RAG, auth, translation)
│   │   ├── models/      # Database models
│   │   └── schemas/     # Pydantic schemas
│   ├── tests/           # Backend tests
│   └── alembic/         # Database migrations
└── specs/               # Project specifications and planning
```

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.11+
- **Git**

### Frontend Setup (Docusaurus)

```bash
cd website
npm install
npm start
```

The site will open at `http://localhost:3000`

### Backend Setup (FastAPI)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your API keys (OpenAI, Neon, Qdrant)

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API documentation available at `http://localhost:8000/docs`

## 📖 Curriculum Overview

### Module 1: ROS 2 Fundamentals (Weeks 3-5)
- Architecture and design patterns
- Nodes, topics, services, and actions
- Building and managing packages
- Launch files and parameters

### Module 2: Robot Simulation (Weeks 6-7)
- Gazebo environment setup
- URDF and SDF modeling
- Physics simulation
- Unity visualization

### Module 3: NVIDIA Isaac Platform (Weeks 8-10)
- Isaac SDK and Sim
- Perception and manipulation pipelines
- Reinforcement learning for robotics
- Sim-to-real transfer

### Module 4: Humanoid Development (Weeks 11-13)
- Kinematics and dynamics
- Bipedal locomotion
- Manipulation and grasping
- Conversational AI integration

## 🛠️ Technology Stack

**Frontend**
- Docusaurus 3.x (React-based static site generator)
- TypeScript
- MDX for interactive content

**Backend**
- FastAPI (Python async web framework)
- OpenAI API (embeddings & chat completions)
- Qdrant (vector database)
- Neon Serverless Postgres
- Better-Auth (authentication)

**Deployment**
- Vercel (frontend) — https://ai-driven-robo-book.vercel.app
- Railway (backend) — https://ai-driven-robo-book-production.up.railway.app

## 🚢 Deployment

> Full guide: [DEPLOYMENT.md](DEPLOYMENT.md) · Quick start: [QUICKSTART-DEPLOY.md](QUICKSTART-DEPLOY.md)

### Vercel (Frontend)

The frontend is automatically deployed to **Vercel** on every push to the `main`
branch (preview deploys for other branches/PRs).

**Setup Instructions:**

1. **Import the repo** at https://vercel.com/new and set **Root Directory** to
   `website`. Build settings come from `website/vercel.json`.

2. **Set the backend URL** in Vercel → Settings → Environment Variables (this is
   what connects the frontend to the API):
   ```bash
   REACT_APP_API_URL=https://ai-driven-robo-book-production.up.railway.app
   ```
   Redeploy after adding it — env vars only apply to new builds.

3. **Deploy** by pushing to `main`:
   ```bash
   git add .
   git commit -m "Deploy frontend"
   git push origin main
   ```

4. **Access your site**: https://ai-driven-robo-book.vercel.app

**Local Build Test:**
```bash
cd website
npm ci
REACT_APP_API_URL=https://ai-driven-robo-book-production.up.railway.app npm run build
npm run serve  # Test production build locally
```

### Backend Deployment (Railway)

The backend FastAPI service deploys to Railway:

1. Install Railway CLI: `npm install -g @railway/cli`
2. Login: `railway login`
3. Link project: `railway link`
4. Deploy: `railway up`

**Environment Variables** (set in Railway dashboard):
- `OPENAI_API_KEY`
- `NEON_DATABASE_URL`
- `QDRANT_URL`
- `QDRANT_API_KEY`
- `BETTER_AUTH_SECRET`
- `JWT_SECRET_KEY`

## 🧪 Testing

### Frontend Tests
```bash
cd website
npm run typecheck
npm run lint
npm run build  # Validates links during build
```

### Backend Tests
```bash
cd backend
pytest
pytest --cov=app --cov-report=html  # With coverage
```

## 📝 Development Workflow

### Adding New Content

1. Create MDX file in `website/docs/` (e.g., `website/docs/02-ros2-fundamentals/week-04-sensors.mdx`)
2. Add frontmatter:
   ```yaml
   ---
   title: Week 4 - Robot Sensors
   description: Understanding sensor integration in ROS 2
   sidebar_position: 4
   ---
   ```
3. Test locally: `npm start`
4. Re-embed content for chatbot: `python backend/scripts/embed_content.py --file path/to/new/file.mdx`

### Translating Content

```bash
python backend/scripts/translate_to_urdu.py \
  --input website/docs/02-ros2-fundamentals/ \
  --output website/i18n/ur/docusaurus-plugin-content-docs/current/02-ros2-fundamentals/
```

## 🤝 Contributing

This project follows Spec-Driven Development (SDD) using the Spec-Kit Plus workflow:

1. **Constitution** (`.specify/memory/constitution.md`) - Project principles and standards
2. **Specification** (`specs/001-textbook-content/spec.md`) - Feature requirements
3. **Plan** (`specs/001-textbook-content/plan.md`) - Implementation architecture
4. **Tasks** (`specs/001-textbook-content/tasks.md`) - Dependency-ordered task list

See [CLAUDE.md](./CLAUDE.md) for detailed development guidelines.

## 📚 Documentation

- **Specification**: [specs/001-textbook-content/spec.md](specs/001-textbook-content/spec.md)
- **Implementation Plan**: [specs/001-textbook-content/plan.md](specs/001-textbook-content/plan.md)
- **Tasks**: [specs/001-textbook-content/tasks.md](specs/001-textbook-content/tasks.md)
- **Quickstart Guide**: [specs/001-textbook-content/quickstart.md](specs/001-textbook-content/quickstart.md)
- **API Contracts**: [specs/001-textbook-content/contracts/rag-api.yaml](specs/001-textbook-content/contracts/rag-api.yaml)

## 🔐 Environment Variables

### Frontend (`website/.env`)
```bash
REACT_APP_API_URL=http://localhost:8000
REACT_APP_BETTER_AUTH_CLIENT_ID=your_client_id
```

### Backend (`backend/.env`)
```bash
OPENAI_API_KEY=sk-proj-...
NEON_DATABASE_URL=postgresql://...
QDRANT_URL=https://...
QDRANT_API_KEY=...
BETTER_AUTH_SECRET=...
JWT_SECRET_KEY=...
```

Generate secrets with: `openssl rand -hex 32`

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Curriculum based on "Hackathon I: Physical AI & Humanoid Robotics Textbook"
- Built using Docusaurus, FastAPI, OpenAI, Qdrant, and Better-Auth
- Generated with Claude Code following Spec-Kit Plus methodology

---

**Version**: 1.0.0
**Last Updated**: 2025-12-12
**Maintained By**: Claude Code Agent System

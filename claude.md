# English Learning Agent - AI-Powered English Exam Preparation System

## Project Overview

This is an intelligent agent-based application designed to help users prepare for English proficiency exams including:
- Postgraduate Entrance Examination (考研)
- CET-4 (四级)
- CET-6 (六级)
- College Entrance Examination (高考)

The system combines Large Language Model (LLM) capabilities with personalized learning progress tracking to provide an adaptive and interactive learning experience.

## Technology Stack

### Backend
- **Framework**: Python with FastAPI (async support)
- **AI/ML**: LangChain v1.0 with agent architecture
- **LLM Providers**: DeepSeek, GLM4 (configurable)
- **Database**: PostgreSQL + SQLAlchemy async ORM + Alembic migrations
- **Memory Algorithm**: SM-2 spaced repetition with full implementation
- **Authentication**: JWT token-based auth with password hashing
- **Testing**: pytest with 30 comprehensive tests (100% pass rate)

### Frontend
- **Framework**: Flutter (Dart)
- **State Management**: Provider/GetX
- **UI Components**: Material Design
- **Platform Support**: Cross-platform (mobile & desktop)

### Development Environment
- **Backend**: WSL2 (Windows Subsystem for Linux 2)
- **Frontend**: Windows PowerShell development environment
- **Version Control**: Git

## Project Architecture

```
english-learning-agent/
├── README.md                    # Basic project overview
├── AGENT_GUIDE.md              # Comprehensive agent usage guide
├── QUICKSTART.md               # Setup and quick start instructions
├── CHANGELOG.md                # Version history
├── claude.md                   # Development notes
├── run_tests.sh                # Test runner script
├── backend/                    # FastAPI backend server
│   ├── app/
│   │   ├── main.py             # FastAPI application entry point
│   │   ├── api/
│   │   │   └── chat.py         # Chat/Agent API endpoints
│   │   ├── agents/             # AI agent implementation
│   │   │   ├── english_learning_agent.py  # Main LangChain agent
│   │   │   ├── llm_providers.py # LLM provider management
│   │   │   └── tools/          # Learning tools
│   │   │       └── learning_tools.py  # 9 specialized learning tools
│   │   ├── config/             # Configuration management
│   │   │   └── settings.py     # Environment variables and settings
│   │   ├── database.py         # Database connection and session management
│   │   ├── models.py           # SQLAlchemy database models
│   │   ├── schemas.py          # Pydantic request/response models
│   │   ├── security.py         # JWT and password utilities
│   │   ├── dependencies.py     # Dependency injection functions
│   │   └── __init__.py
│   ├── alembic/                # Database migration files
│   ├── tests/                  # Test suite (30 tests, 100% pass rate)
│   │   ├── conftest.py         # Test configuration and fixtures
│   │   ├── test_english_learning_agent.py  # Agent testing
│   │   ├── test_main_apis.py   # API endpoint testing
│   │   └── test_study.py       # Learning algorithm testing
│   └── venv/                   # Python virtual environment
├── frontend/                    # Flutter mobile application
│   ├── lib/
│   │   ├── main.dart           # Flutter app entry point
│   │   ├── screens/           # App screens
│   │   │   ├── login_screen.dart  # Authentication interface
│   │   │   └── chat_screen.dart    # Main chat interface
│   │   └── services/          # Business logic
│   │       └── api_service.dart    # API client and state management
│   ├── pubspec.yaml           # Dependencies and project configuration
│   └── .dart_tool/            # Flutter build artifacts
```

## Core Features

### 1. User Authentication & Management
- User registration and login
- Profile management
- Learning preferences configuration

### 2. Multi-Exam Support
Each exam type (考研, 四级, 六级, 高考) has:
- Independent progress tracking
- Specialized vocabulary sets
- Tailored learning paths
- Exam-specific features

### 3. AI-Powered Learning Agent
- **Emma**: Professional English learning AI assistant
- **LangChain v1.0 Architecture**: Modern agent framework with tool calling
- **9 Learning Tools**: Dictionary search, exercises, grammar explanations, etc.
- **Context Management**: Maintains conversation history and learning progress
- **Multi-Provider Support**: DeepSeek, GLM4 LLM integration

### 4. Vocabulary Learning System
**Current Status: UI-Only Implementation**
- **Frontend Interface**: Complete button-based navigation for vocabulary learning
- **Backend Integration**: Tool calling not activated - currently only chat with LLM
- **Data Persistence**: No learning progress or user performance tracking in database
- **Planned Features**: Personalized learning plans, SM-2 spaced repetition, progress analytics

### 5. Interactive Question Types
- Meaning discrimination (词义辨析)
- Fill-in-the-blank spelling (挖空拼写)
- Complete word spelling (整个单词拼写)
- Dictation exercises (听写)
- Configurable question type preferences

### 6. Adaptive Learning
- Dynamic difficulty adjustment
- Real-time progress evaluation
- Contextual AI assistance during exercises
- Skip/regenerate question functionality

## Current Development Status

### ✅ Completed (Production-Ready Features)
- **Backend API**: Complete FastAPI server with async support
- **Database Integration**: PostgreSQL + SQLAlchemy with SM-2 algorithm
- **Authentication System**: JWT-based user registration and login
- **AI Agent System**: LangChain v1.0 agent with 9 learning tools (configured but not activated)
- **LLM Integration**: DeepSeek and GLM4 provider support
- **Testing Suite**: 30 comprehensive tests with 100% pass rate
- **Flutter Frontend**: Login and chat interfaces fully functional
- **API Integration**: Complete frontend-backend communication
- **UI Framework**: Complete chat-based interface with interactive navigation buttons

### 🔄 Recent Updates (December 2025)
- **LangChain v1.0 Modernization**: Updated to official `create_agent` pattern
- **Agent Architecture**: Proper tool calling and state management (tools configured but not activated)
- **Frontend UI Revolution**: Complete chat-based interface with smart button navigation
- **User Experience Optimization**: Dynamic button updates without chat bubble spam
- **AIMessage Response Fix**: Resolved LangChain v1.0 response parsing issues
- **Test Coverage**: Comprehensive testing of all major components
- **Documentation**: Complete setup guides and API documentation

### 📋 Short-Term Goals (Critical Next Steps)
1. **Activate Agent Tool Calling**: Enable Emma to actually use the 9 configured learning tools
2. **Implement Learning Data Storage**: Create database tables for user progress, word mastery, and learning history
3. **Vocabulary Learning Backend**: Implement actual word review, new word learning, and progress assessment functions
4. **Database Integration**: Connect UI button actions to real learning operations and data persistence
5. **Context Management**: Ensure user learning history is properly maintained as LLM context

## Technical Implementation Details

### LangChain v1.0 Agent Architecture
The project now uses the official LangChain v1.0 pattern with modern agent setup:

```python
# Current implementation (v1.0 compliant)
from langchain.agents import create_agent

agent = create_agent(
    llm,                    # DeepSeek or GLM4
    learning_tools,         # 9 specialized tools
    system_prompt=emma_prompt  # Emma's teaching personality
)

# Agent invocation
response = agent.invoke({
    "messages": [{"role": "user", "content": user_input}]
})
```

### 2. Cross-Platform Development Environment
**Problem**: Backend runs in WSL2 while frontend runs on Windows, creating integration challenges.

**Solutions**:
- Configure WSL2 network access for Windows
- Use proper IP addressing for API endpoints
- Implement CORS policies for cross-origin requests
- Consider containerization for easier deployment

## Development Guidelines

### Code Standards
- **Backend**: Follow PEP 8 Python style guidelines
- **Frontend**: Use effective Dart/Flutter conventions
- **API**: RESTful design principles with proper HTTP status codes
- **Testing**: Minimum 80% code coverage requirement

### LLM Agent Best Practices
- Use structured prompts for consistent responses
- Implement proper error handling and fallback mechanisms
- Cache frequently used vocabulary data
- Maintain conversation context efficiently
- Use LangSmith for agent debugging and optimization

### Database Guidelines
- Use SQLAlchemy ORM for database operations
- Implement proper transaction management
- Design scalable schemas for user growth
- Regular database backups and migration scripts

### Frontend Development
- Implement responsive design for multiple screen sizes
- Use proper state management patterns
- Handle network connectivity issues gracefully
- Implement loading states and error handling

## API Design Principles

### Core Endpoints Structure
```
# Authentication
POST /users/                     # User registration
POST /token                      # User authentication (JWT)

# Chat & Agent
POST /chat/                      # Send message to AI agent
GET  /chat/history              # Get conversation history
POST /chat/clear                # Clear conversation history
GET  /chat/agent-info           # Get agent information
POST /chat/update-context       # Update user context
GET  /chat/tools                # Get available learning tools

# Study Features
POST /study/progress            # Create learning record
GET  /study/needs-review        # Get words for review
POST /study/review              # Update word progress (SM-2)
GET  /books/                    # Get vocabulary books
GET  /books/{id}/words          # Get words from specific book

# Health Checks
GET  /                          # Root endpoint
GET  /health                    # Basic health check
GET  /health/db                 # Database connection test
```

### Response Format Standard
```json
{
  "success": true,
  "data": {},
  "message": "Operation completed successfully",
  "timestamp": "2025-12-05T12:00:00Z"
}
```

## Testing Strategy

### Backend Tests (Current Coverage: 30 tests, 100% pass rate)
- **Agent Testing** (13 tests): LangChain v1.0 agent behavior, tool calling, conversation management
- **API Testing** (15 tests): All endpoints, authentication, CRUD operations, error handling
- **Algorithm Testing** (4 tests): SM-2 spaced repetition logic and edge cases
- **Database Testing**: In-memory SQLite for fast, isolated tests
- **Mock Strategy**: Comprehensive mocking for external services and LLM responses

### Test Execution
```bash
# Run all tests
./run_tests.sh
# Or directly with pytest
cd backend && pytest tests/ -v
```

### Frontend Tests
- Widget testing for UI components (planned)
- Integration testing for user flows (planned)
- API service testing with mock responses (planned)
- Performance testing for chat interface (planned)

## Future Roadmap

### Phase 2 Features (Planned)
- **Listening Comprehension**: Audio-based exercises
- **Speaking Practice**: Voice recognition and feedback
- **Mock Exams**: Full-length practice tests
- **Analytics Dashboard**: Detailed progress insights
- **Social Features**: Study groups and competitions

### Technical Improvements
- LangGraph integration for complex agent workflows
- Microservices architecture for scalability
- Real-time collaboration features
- Offline mode capabilities
- Mobile app optimization

## Configuration Requirements

### Development Setup
1. **Backend** (WSL2):
   - Python 3.9+
   - PostgreSQL/SQLite database
   - OpenAI API key or alternative LLM
   - Redis for caching (optional)

2. **Frontend** (Windows):
   - Flutter SDK 3.0+
   - Dart SDK compatible with Flutter
   - Android Studio / VS Code with Flutter plugins

### Environment Variables
```bash
# Backend (required for LLM integration)
DEEPSEEK_API_KEY=your_deepseek_api_key
GLM4_API_KEY=your_glm4_key
GLM4_API_BASE=your_glm4_endpoint
DEFAULT_LLM_PROVIDER=deepseek

# Backend (database & security)
DATABASE_URL=postgresql://user:pass@localhost/dbname
SECRET_KEY=your_jwt_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Development Settings
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Frontend
API_BASE_URL=http://localhost:8000
```

## Contributing Guidelines

1. **Branch Management**: Use feature branches for new development
2. **Commit Messages**: Follow conventional commit format
3. **Code Review**: All changes must be reviewed before merging
4. **Testing**: Ensure all tests pass before deployment
5. **Documentation**: Update relevant documentation for API changes

## Security Considerations

- Implement proper authentication and authorization
- Sanitize all user inputs to prevent injection attacks
- Use HTTPS for all API communications
- Implement rate limiting for API endpoints
- Regular security audits and dependency updates

## Performance Optimization

### Backend
- Implement database query optimization
- Use caching for frequently accessed vocabulary data
- Optimize LLM API calls with proper batching
- Monitor and log API response times

### Frontend
- Implement lazy loading for vocabulary lists
- Use efficient state management patterns
- Optimize image and asset loading
- Monitor app startup time and memory usage

---

**Last Updated**: 2025-12-06
**Version**: 1.0.0-alpha
**Status**: Active Development (UI Complete, Backend Tools Pending)
# Contributing to BananaLecture

First off, thank you for considering contributing to BananaLecture! It's people like you that make this project great. Your contributions help us improve the project and make it more useful for everyone!

## Code of Conduct

This project and everyone participating in it is governed by the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior.

## How Can I Contribute?

We welcome contributions of all kinds, including:
- 🐛 Bug fixes
- 📝 Improvements to existing features or documentation
- 🔧 New feature development

### Reporting Bugs or Suggesting Enhancements

Before creating a new issue, please **ensure one does not already exist** by searching on GitHub under Issues.

- If you're reporting a bug, please include a **title and clear description**, as much relevant information as possible, and a **code sample** or an **executable test case** demonstrating the expected behavior that is not occurring.
- If you're suggesting an enhancement, clearly state the enhancement you are proposing and why it would be a good addition to the project.

## Development Setup

To get started with development, you'll need to set up your environment.

### Backend Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ChengJiale150/BananaLecture.git
    cd BananaLecture
    ```

2.  **Install dependencies:**
    ```bash
    cd backend
    uv sync
    ```

3.  **Configure environment variables:**
    ```bash
    cp ../.env.example ../.env
    # Edit .env file with your API keys and configuration
    ```

4.  **Start the backend server:**
    ```bash
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```

### Frontend Setup

1.  **Install dependencies:**
    ```bash
    cd frontend
    npm install
    ```

2.  **Start the frontend development server:**
    ```bash
    npm run dev
    ```

### Docker Setup (Optional)

If you prefer to use Docker for development:

```bash
docker-compose build
```

## Making Changes

1. **Create a new branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes:**
   - Follow the project's coding conventions
   - Write clear commit messages
   - Test your changes thoroughly

3. **Run tests:**
   ```bash
   # Backend tests
   cd backend
   pytest
   
   # Frontend tests
   cd frontend
   npm run lint
   ```

4. **Build the project:**
   ```bash
   # Backend build
   cd backend
   python -m build
   
   # Frontend build
   cd frontend
   npm run build
   ```

## Pull Request Process

1.  Once you are satisfied with your changes and tests, commit your code.
2.  Push your branch to your fork and attach with detailed description of the changes you made.
3.  Open a pull request to the `main` branch of the original repository.

We look forward to your contributions!

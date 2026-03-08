# Contributing to DevOps Observability Stack

Thank you for your interest in contributing to the DevOps Observability Stack! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Bugs

- Use the [GitHub Issues](https://github.com/harishgedi/devops-observability-stack/issues) page
- Provide detailed information about the bug
- Include steps to reproduce the issue
- Add screenshots if applicable
- Specify your environment (OS, Docker version, etc.)

### Suggesting Features

- Open an issue with the "enhancement" label
- Describe the feature in detail
- Explain the use case and benefits
- Provide examples of how the feature would work

### Submitting Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 🛠️ Development Setup

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- Git

### Setup Steps

```bash
# Clone your fork
git clone https://github.com/yourusername/devops-observability-stack.git
cd devops-observability-stack

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Run production tests
python test_production.py

# Run performance benchmarks
python generate_performance_report.py
```

### Code Quality

```bash
# Run linting
flake8 src/ tests/
black src/ tests/
isort src/ tests/

# Run type checking
mypy src/ --ignore-missing-imports

# Run security checks
bandit -r src/
```

## 📝 Coding Standards

### Python Code Style

- Follow PEP 8 guidelines
- Use Black for code formatting
- Use isort for import sorting
- Add type hints for all functions
- Write comprehensive docstrings

### Documentation

- Update README.md for user-facing changes
- Add inline comments for complex logic
- Update API documentation for new endpoints
- Include examples in documentation

### Testing

- Write unit tests for all new functions
- Add integration tests for new features
- Ensure test coverage above 80%
- Use descriptive test names

## 🏗️ Project Structure

```
devops-observability-stack/
├── src/                    # Source code
│   └── monitoring_service.py
├── config/                 # Configuration files
│   ├── prometheus.yml
│   ├── alertmanager.yml
│   └── alert_rules.yml
├── tests/                  # Test files
├── dashboards/             # Grafana dashboards
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile             # Docker image definition
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

## 🚀 Release Process

1. Update version numbers in code
2. Update CHANGELOG.md
3. Create a release tag
4. Build and publish Docker images
5. Update documentation

## 📋 Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] All tests pass
- [ ] New tests added
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
```

## 🎯 Areas for Contribution

### High Priority

- [ ] Additional Grafana dashboards
- [ ] More alert rules
- [ ] Kubernetes deployment manifests
- [ ] Performance optimizations

### Medium Priority

- [ ] Additional exporters (MySQL, Redis, etc.)
- [ ] Custom visualizations
- [ ] Enhanced documentation
- [ ] More test coverage

### Low Priority

- [ ] UI improvements
- [ ] Additional integrations
- [ ] Mobile responsiveness
- [ ] Internationalization

## 📞 Getting Help

- Create an issue for questions
- Join our discussions
- Check existing documentation
- Review similar projects for inspiration

## 📜 Code of Conduct

Be respectful, inclusive, and professional. We welcome contributors from all backgrounds and experience levels.

---

Thank you for contributing to the DevOps Observability Stack! 🚀

# Contributing to A2A Approvals Extension

Thank you for your interest in contributing to the A2A Approvals Extension! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone.

## How to Contribute

### Reporting Bugs

1. Check the [issue tracker](https://github.com/awickham10/a2a-python-approvals-extension/issues) to see if the bug has already been reported
2. If not, create a new issue using the bug report template
3. Provide as much detail as possible:
   - Clear description of the bug
   - Steps to reproduce
   - Expected vs actual behavior
   - Code samples
   - Environment details (OS, Python version, package version)

### Suggesting Features

1. Check existing issues to see if the feature has been suggested
2. Create a new issue using the feature request template
3. Clearly describe:
   - The problem you're trying to solve
   - Your proposed solution
   - Any alternatives you've considered
   - Example API usage if applicable

### Contributing Code

1. **Fork the repository**
   ```bash
   git clone https://github.com/awickham10/a2a-python-approvals-extension.git
   cd a2a-python-approvals-extension
   ```

2. **Set up development environment**
   ```bash
   # Install uv if you haven't already
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Install dependencies
   uv sync --all-extras --dev
   ```

3. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Make your changes**
   - Write clear, readable code
   - Follow the existing code style
   - Add type hints to all functions
   - Write docstrings for public APIs
   - Update documentation if needed

5. **Add tests**
   - Write tests for any new functionality
   - Ensure existing tests still pass
   - Aim for high test coverage

6. **Run quality checks**
   ```bash
   # Run tests
   uv run pytest

   # Check test coverage
   uv run pytest --cov=a2a_approvals --cov-report=term

   # Type checking
   uv run mypy src tests

   # Linting and formatting
   uv run ruff check src tests
   uv run ruff format src tests
   ```

7. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```

   Use conventional commit messages:
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation changes
   - `test:` for test additions/changes
   - `refactor:` for code refactoring
   - `chore:` for maintenance tasks

8. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

9. **Create a Pull Request**
   - Go to the original repository on GitHub
   - Click "New Pull Request"
   - Select your fork and branch
   - Fill out the PR template with details about your changes
   - Link any related issues

## Development Guidelines

### Code Style

- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Keep lines under 100 characters
- Use meaningful variable and function names
- Write docstrings for all public APIs

### Testing

- Write unit tests for all new functionality
- Use pytest fixtures for common test setups
- Mock external dependencies
- Test edge cases and error conditions
- Aim for >90% test coverage

### Documentation

- Update README.md if adding new features
- Add docstrings to all public functions and classes
- Include usage examples for new functionality
- Update CHANGELOG.md following Keep a Changelog format

### Type Checking

- All code must pass mypy strict mode
- Add type hints to all functions
- Use proper generic types where applicable
- Avoid using `Any` unless absolutely necessary

## Project Structure

```
a2a-python-approvals-extension/
├── .github/
│   ├── workflows/         # GitHub Actions workflows
│   └── ISSUE_TEMPLATE/    # Issue templates
├── src/
│   └── a2a_approvals/     # Main package
│       ├── __init__.py
│       ├── approvals.py   # Core implementation
│       └── py.typed       # Type hint marker
├── tests/                 # Test suite
│   ├── __init__.py
│   └── test_approvals.py
├── examples/              # Usage examples
├── pyproject.toml         # Package configuration
├── README.md
├── CHANGELOG.md
├── CONTRIBUTING.md
└── LICENSE
```

## Release Process

Releases are automated through GitHub Actions:

1. Version bumps are determined by commit messages or manual workflow dispatch
2. The release workflow updates version numbers and CHANGELOG
3. A new GitHub release is created
4. The package is automatically published to PyPI

## Getting Help

- Check the [documentation](https://github.com/awickham10/a2a-python-approvals-extension#readme)
- Look at [existing issues](https://github.com/awickham10/a2a-python-approvals-extension/issues)
- Review the [examples](./examples) directory
- Open a new issue if you're stuck

## Recognition

Contributors will be recognized in:
- GitHub's contributor list
- Release notes for significant contributions

Thank you for contributing!

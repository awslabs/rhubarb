# Testing Guide

## Overview

This document outlines the testing strategy, coverage requirements, and procedures for the Rhubarb framework.

## Test Structure

```
tests/
├── test_basic_functionality.py    # Core API tests
├── test_doc_analysis.py           # DocAnalysis unit tests  
├── test_video_analysis.py         # VideoAnalysis unit tests
├── test_doc_classification.py     # DocClassification unit tests
├── test_integration.py            # AWS integration tests
├── test_rhubarb_extractions.py    # Existing extraction tests
└── test_file_converter.py         # File conversion tests
```

## Running Tests

### Local Development
```bash
# Install test dependencies
pip install pytest pytest-cov pytest-mock moto

# Run all tests
pytest

# Run with coverage
pytest --cov=rhubarb --cov-report=html

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m slow          # Long-running tests
```

### CI/CD Pipeline
Tests run automatically on:
- Pull requests to main branch
- Pushes to main branch
- Scheduled weekly runs

## Coverage Requirements

- **Minimum Coverage**: 30% (current: 41%)
- **Target Coverage**: 80%
- **Critical Paths**: 90%+ coverage required for:
  - Core analysis functions
  - Error handling
  - Security-sensitive code

## Test Categories

### Unit Tests
- Test individual components in isolation
- Mock external dependencies (AWS services, file I/O)
- Fast execution (< 1 second per test)

### Integration Tests
- Test AWS service integration using moto mocking
- Verify S3 file handling
- Test end-to-end workflows

### Security Tests
- Automated security scanning with Bandit
- Dependency vulnerability checks with Safety
- Input validation testing

## Test Data

Test files located in:
- `tests/test_docs/` - Sample documents for testing
- `cookbooks/test_docs/` - Additional test documents

## Mocking Strategy

- **AWS Services**: Use moto for S3, Bedrock mocking
- **File I/O**: Use temporary files with pytest fixtures
- **External APIs**: Mock HTTP calls and responses

## Continuous Integration

GitHub Actions workflows:
- `.github/workflows/security-scan.yml` - Security scanning
- `.github/workflows/publish-to-pypi.yml` - Package publishing

## Adding New Tests

1. Follow naming convention: `test_*.py`
2. Use descriptive test names: `test_feature_scenario_expected_result`
3. Include docstrings explaining test purpose
4. Add appropriate markers (`@pytest.mark.unit`, etc.)
5. Mock external dependencies
6. Assert both positive and negative cases

## Test Maintenance

- Review test coverage monthly
- Update tests when adding new features
- Remove obsolete tests when refactoring
- Keep test data current and relevant

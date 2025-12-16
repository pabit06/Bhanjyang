# Integration Tests

This directory contains integration tests for the Bhanjyang Cooperative project.

## Structure

- `test_integration.py` - Main integration tests
- `conftest.py` - Pytest configuration and shared fixtures

## Running Tests

### Run all integration tests:
```bash
pytest tests/
```

### Run specific test file:
```bash
pytest tests/test_integration.py
```

### Run with coverage:
```bash
pytest tests/ --cov=apps --cov-report=html
```

## Test Categories

1. **Page Load Tests** - Verify pages load without errors
2. **Form Submission Tests** - Test form submissions end-to-end
3. **API Integration Tests** - Test API endpoints
4. **Cross-App Integration** - Test interactions between apps

## Adding New Tests

When adding new integration tests:

1. Create test classes that group related tests
2. Use descriptive test method names
3. Use fixtures from `conftest.py` for common setup
4. Mark tests with appropriate pytest markers (`@pytest.mark.django_db`)

## Best Practices

- Test user flows, not just individual components
- Use realistic test data
- Clean up after tests (use fixtures)
- Test both success and error cases
- Keep tests independent and isolated


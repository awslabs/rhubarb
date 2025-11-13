# Security Policy

## Overview

This document outlines the security practices, vulnerability management, and compliance measures for the Rhubarb framework.

## Security Scanning

### Automated Security Checks

The project uses multiple security scanning tools:

1. **Bandit** - Static security analysis for Python
2. **Safety** - Dependency vulnerability scanning  
3. **Semgrep** - Advanced static analysis (planned)

### Running Security Scans

```bash
# Install security tools
pip install bandit safety

# Run Bandit scan
bandit -r src/ -f txt

# Run Safety check
safety scan

# Generate reports
bandit -r src/ -f json -o security-report.json
```

### CI/CD Security Pipeline

Security scans run automatically:
- On every pull request
- Weekly scheduled scans
- Before releases

Configuration: `.github/workflows/security-scan.yml`

## Vulnerability Management

### Current Security Issues

As of last scan:
- **Medium**: Hardcoded temp directory usage (`/tmp`)
- **Low**: Standard random generator for backoff (non-cryptographic use)
- **Info**: Pip version vulnerability (upgrade recommended)

### Remediation Process

1. **Critical/High**: Fix within 24 hours
2. **Medium**: Fix within 1 week  
3. **Low**: Fix in next release cycle
4. **Info**: Address during regular maintenance

### Reporting Vulnerabilities

Please report security vulnerabilities to:
- Email: rhubarb-security@amazon.com
- Follow responsible disclosure practices
- Do not create public issues for security vulnerabilities

## Security Best Practices

### Input Validation
- All user inputs are validated
- File paths are sanitized
- S3 paths are validated against expected patterns

### AWS Security
- Use IAM roles with least privilege
- Enable AWS CloudTrail for API logging
- Rotate access keys regularly
- Use VPC endpoints where possible

### Data Handling
- No sensitive data logged
- Temporary files cleaned up automatically
- Memory cleared after processing sensitive content

### Dependencies
- Regular dependency updates
- Vulnerability scanning of all dependencies
- Pin dependency versions for reproducible builds

## Compliance

### Standards Adherence
- OWASP Top 10 guidelines
- AWS Security Best Practices
- Python Security Guidelines (PEP 578)

### Audit Trail
- All security scans logged
- Vulnerability remediation tracked
- Security policy changes documented

## Configuration

### Bandit Configuration
File: `.bandit`
- Excludes test directories
- Skips non-security related checks
- Configured for Python security best practices

### Safety Configuration
- Scans all dependencies
- Checks against known vulnerability databases
- Generates machine-readable reports

## Security Contacts

- **Security Team**: rhubarb-security@amazon.com
- **Maintainers**: rhubarb-developers@amazon.com
- **AWS Security**: aws-security@amazon.com

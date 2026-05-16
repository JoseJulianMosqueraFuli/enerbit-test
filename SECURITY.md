# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

We take the security of this project seriously. If you discover a security vulnerability, please follow these steps:

1. **DO NOT** open a public GitHub issue
2. Email us directly at [your-email@example.com]
3. Include as much information as possible:
   - Type of vulnerability
   - Full path of source file(s)
   - Location of affected code
   - Special configuration required to reproduce
   - Step-by-step instructions to reproduce
   - Proof-of-concept or exploit code (if possible)
   - Impact of the issue

## Response Timeline

- **Initial response**: Within 48 hours
- **Status update**: Within 7 days
- **Fix released**: Within 30 days (depending on severity)

## Security Measures

This project implements the following security measures:

### Automated Scans (GitHub Actions)

- **SAST**: Bandit static analysis on every PR
- **Dependency scanning**: pip-audit + Safety check weekly
- **Secret scanning**: Gitleaks on every push
- **CodeQL**: Semantic code analysis for vulnerabilities
- **Container scanning**: Trivy for Docker images and filesystem
- **Dockerfile linting**: Hadolint for best practices
- **Dependency review**: Blocks PRs with vulnerable dependencies

### Manual Reviews

- All PRs require code review
- Security-sensitive changes require additional review
- Dependencies are updated weekly via Dependabot

## Best Practices

- Never commit secrets or credentials
- Use environment variables for sensitive configuration
- Keep dependencies up to date
- Run `make security` locally before pushing

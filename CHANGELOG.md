# Changelog

All notable changes to Em-Cubed will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Multi-surface intelligent task planner skill demonstrating orchestration
- Hy fuzzy logic engine with symbolic computation and AI patterns
- Prolog logic solver with constraint satisfaction and reasoning
- Python calculator skill with mathematical operations and testing
- Comprehensive API documentation with interactive OpenAPI docs
- CONTRIBUTING.md with development guidelines and code standards
- Extensive README.md with usage examples and surface references

### Changed
- Enhanced Python surface security with asteval (replacing unsafe eval)
- Improved Prolog surface query execution and error handling
- Added structured logging with structlog throughout codebase
- Consolidated dependencies to single pyproject.toml source of truth
- Updated all test imports to use proper em_cubed package structure

### Fixed
- HTTPException handling in API endpoints
- Prolog tag extraction regex for proper predicate matching
- Python surface error handling with asteval exceptions
- Integration test async execution patterns

## [0.1.0] - 2026-04-28

### Added
- Initial multi-surface framework architecture
- Core execution surfaces: Python, Prolog, Hy, Janus (placeholder)
- Skill indexing and search with multi-surface scoring
- REST API with FastAPI for skill execution
- Basic testing infrastructure
- Project structure and configuration

### Security
- Safe Python execution via asteval
- Input validation on all API endpoints
- Restricted execution environments

### Documentation
- Basic README with setup instructions
- API endpoint documentation
- Surface reference guides

---

## Release Process

### Pre-release Checklist
- [ ] All tests passing (54/54)
- [ ] Code coverage ≥76%
- [ ] Ruff linting clean
- [ ] MyPy type checking clean
- [ ] Documentation complete
- [ ] CHANGELOG.md updated
- [ ] Version updated in pyproject.toml
- [ ] Release notes prepared

### Release Steps
1. Update version in `pyproject.toml`
2. Update CHANGELOG.md with release notes
3. Commit changes: `git commit -m "release: v0.2.0"`
4. Create git tag: `git tag -a v0.2.0 -m "Release v0.2.0"`
5. Push to GitHub: `git push origin master --tags`
6. Create GitHub release with release notes
7. Optionally publish to PyPI: `python -m build && twine upload dist/*`

### Version Format
Em-Cubed follows [Semantic Versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH**
- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

### Release Types
- **Alpha/Beta**: Pre-release versions (e.g., `0.2.0-alpha.1`)
- **Release Candidate**: Final testing (e.g., `0.2.0-rc.1`)
- **Stable**: Production ready (e.g., `0.2.0`)

---

## Development Milestones

### Completed ✅
- **Month 1**: Code consolidation and stabilization
- **Month 2**: Testing & Quality (54 tests, 76% coverage)
- **Month 3**: Documentation & Polish (4 example skills, comprehensive docs)

### Future Releases
- **v0.3.0**: Additional surfaces (JavaScript, SQL, Shell)
- **v0.4.0**: Web UI and skill marketplace
- **v0.5.0**: Performance optimizations and enterprise features
- **v1.0.0**: Production-ready multi-surface framework

---

## Contributors

- **SpectreDeath**: Project creator and maintainer
- **Community**: Bug reports, feature requests, and contributions welcome!

For more information about contributing, see [CONTRIBUTING.md](CONTRIBUTING.md).
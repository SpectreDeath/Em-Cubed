# Em-Cubed Troubleshooting Guide

This guide helps you diagnose and resolve common issues when working with Em-Cubed.

## Common Issues and Solutions

### Installation and Setup

#### Dependency Installation Fails
**Symptoms:** Errors when running `pip install -e .` or `pip install -r requirements.txt`
**Solutions:**
- Ensure you have Python 3.9+ installed
- Update pip: `python -m pip install --upgrade pip`
- For psutil installation issues on Windows: Install Visual C++ Build Tools or use `pip install --only-binary :all: psutil`
- For Z3 solver installation: `pip install z3-solver` may require additional dependencies on Linux

#### Plugin Discovery Issues
**Symptoms:** Surfaces not loading or "Surface not available" errors
**Solutions:**
- Run `em3 surfaces` to see which surfaces are registered and their availability
- Check that required dependencies for specific surfaces are installed:
  - Python surface: Built-in (no extra deps)
  - Prolog surface: `pip install pyswip`
  - Hy surface: `pip install hy`
  - Z3 surface: `pip install z3-solver`
  - Datalog surface: `pip install pydatalog`
  - Janus surface: `pip install pyjanus` (optional)
  - SQLite surface: Built-in (no extra deps)
  - QuickJS surface: `pip install pyquickjs`

### Execution Issues

#### Skill Execution Fails with "No surface code block found"
**Symptoms:** When running a skill, you get an error like "No python code block found in skill_id"
**Solutions:**
- Verify the skill has a code block for the surface you're trying to use
- SKILL.md files should contain code blocks like:
  ```python
  # Your Python code here
  ```
  ```prolog
  % Your Prolog code here
  ```
- Check that the surface name in the code block matches exactly (case-insensitive)
- Ensure there are no extra spaces or characters in the language identifier

#### Skill Execution Times Out
**Symptoms:** Execution takes longer than the default 30-second timeout
**Solutions:**
- Increase timeout using the `--timeout` flag or `EM_CUBED_TIMEOUT` environment variable
- Optimize your skill code to reduce execution time
- For infinite loops, add proper termination conditions
- Consider using iterative approaches instead of recursive ones for deep computations

#### Memory Limit Exceeded
**Symptoms:** Errors about exceeding memory limits during execution
**Solutions:**
- Increase memory limit using the `memory_limit_mb` parameter in BenchmarkConfig
- Optimize memory usage in your skill code
- Process large data in chunks rather than loading everything into memory
- Consider using surfaces better suited for memory-intensive tasks (e.g., SQLite for large datasets)

### API and CLI Issues

#### API Returns 401 Unauthorized
**Symptoms:** API requests return 401 errors
**Solutions:**
- If `EM_CUBED_API_KEY` is set, you must provide the `X-API-Key` header with your requests
- Get the API key from your environment variables
- To disable authentication, unset `EM_CUBED_API_KEY`

#### CLI Commands Not Found
**Symptoms:** `em3` command not recognized
**Solutions:**
- Ensure the package is installed in development mode: `pip install -e .`
- Verify that the scripts directory is in your PATH
- Try running `python -m em_cubed.api.main` directly as an alternative

#### Search Returns No Results
**Symptoms:** Search queries return empty results
**Solutions:**
- Ensure skills have been indexed: run `em3 index`
- Check that your query matches skill descriptions, names, or triggers
- Try broader search terms or use the API directly to debug
- Verify the Whoosh index is properly built and accessible

### Development Issues

#### Tests Fail After Code Changes
**Symptoms:** Previously passing tests now fail
**Solutions:**
- Run `pytest -v` to see detailed failure messages
- Check if you've changed interfaces that tests depend on
- Update tests to match new interfaces if intentional changes were made
- Run `ruff check .` to ensure code style compliance
- Run `mypy .` to check for type errors

#### Type Checking Errors
**Symptoms:** MyPy reports type errors
**Solutions:**
- Add proper type annotations to function signatures and variables
- Import required types from typing module
- Use `# type: ignore` comments only as a last resort for legitimate false positives
- Check that you're using compatible versions of dependencies

#### Linting Errors
**Symptoms:** Ruff reports linting errors
**Solutions:**
- Run `ruff check --fix .` to automatically fix fixable errors
- Manually fix remaining errors according to Ruff guidelines
- Common issues: unused imports (F401), line length (E501), blank lines (E302)
- Follow the project's coding standards in existing files as examples

### Performance Issues

#### Slow Skill Execution
**Symptoms:** Skills take longer than expected to execute
**Solutions:**
- Profile your code to identify bottlenecks
- Consider using different surfaces for different tasks (e.g., Prolog for logical queries, Python for heavy computation)
- Implement caching for expensive operations that are repeated
- Use vectorized operations where possible (NumPy for numerical work)
- Consider using the Shared Substrate feature for zero-copy data exchange between surfaces

#### High Memory Usage
**Symptoms:** Execution consumes excessive memory
**Solutions:**
- Use generators and iterators instead of lists for large datasets
- Clear references to large objects when no longer needed
- Consider using surfaces with better memory characteristics for your workload
- Profile memory usage with tools like memory_profiler

#### Slow Startup Time
**Symptoms:** Long initialization time when starting Em-Cubed
**Solutions:**
- The PluginManager uses lazy loading for heavy surfaces (Z3, Datalog) by default
- Only the surfaces you actually use will be initialized
- To further improve startup time, avoid importing heavy modules at the top level of your skills
- Consider initializing surfaces only when needed in your application code

## Getting Help

If you've tried the solutions above and are still experiencing issues:

1. Check the project's issue tracker: https://github.com/Kilo-Org/kilocode/issues
2. Search for similar problems in closed issues
3. When reporting a new issue, include:
   - Em-Cubed version (`em3 --version`)
   - Python version and platform
   - Steps to reproduce the issue
   - Relevant error messages and logs
   - Minimal reproducible example if possible

## Debugging Tips

### Enabling Verbose Logging
Set the environment variable `EM_CUBED_LOG_LEVEL=DEBUG` to get detailed logs.

### Tracing Skill Execution
Use the `--trace` flag with `em3 run` to see detailed execution traces including:
- Surface selection
- Context passing
- Execution timing
- Memory usage

### Checking Surface Availability
Run `em3 surfaces` to see which surfaces are available and their load status.

### Validating Skill Format
Use `em3 skill-info <skill_id>` to check if a skill is properly formatted and accessible.
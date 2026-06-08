# Contributing to Social Manipulation Detector Agent

## Getting Started

```bash
git clone https://github.com/social-manipulation-detector-agent/smda.git
cd smda
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
cp .env.example .env
```

## Project Structure

```
src/
├── api/           # FastAPI application, routes, schemas, dependencies
├── analyzer/      # 6-stage analysis pipeline modules
├── patterns/      # Tactic taxonomy + prompt library
├── graph/         # Neo4j bot network operations
├── crawler/       # Research paper crawler
├── extension/     # Browser extension (Chrome/Firefox MV3)
scripts/           # Automation scripts
data/              # Pattern YAMLs, few-shot examples, research cache
prompts/           # LLM prompt templates
docker/            # Dockerfiles and configs
```

## Development

```bash
# Start API server
python -m src.api.main

# Start Celery worker
celery -A src.worker worker --loglevel=info

# Run tests
pytest tests/ -v --cov=src

# Lint
ruff check src/ scripts/

# Type check
mypy src/
```

## Adding a New Platform

1. Create client in `src/api/platforms/your_platform.py`
2. Add to `src/api/platforms/__init__.py`
3. Create DOM injector in `src/extension/injectors/your_platform.js`
4. Add content script entry to `src/extension/manifest.json`
5. Add `host_permissions` entry in manifest

## Adding a New Language

1. Create `data/few_shot_examples/{lang}_examples.json` with 10+ labeled examples
2. Create `data/manipulation_patterns/{LANG}_patterns.yaml` with language-specific phrases
3. Add to `MultilingualHandler.LANG_CONFIG` in `src/analyzer/multilingual.py`
4. Add language code to `supported_languages` in `src/config.py`

## Adding a New Tactic

1. Add to `TACTICS` dict in `src/patterns/tactic_taxonomy.py`
2. Add to appropriate YAML file in `data/manipulation_patterns/`
3. Add to prompt template in `prompts/manipulation_scoring.md`
4. Add few-shot examples in `data/few_shot_examples/`

## Code Standards

- Python 3.11+ with type annotations
- FastAPI async handlers
- Pydantic v2 for all schemas
- Dataclasses for internal data flow
- Lazy-loading for HuggingFace models
- All LLM calls at `temperature=0` for reproducibility

## Pull Requests

1. Fork and create a feature branch
2. Add tests for new functionality
3. Update relevant YAML pattern files if adding tactics
4. Update `CHANGELOG.md`
5. Ensure `ruff check` and `mypy` pass
6. Submit PR with description of changes

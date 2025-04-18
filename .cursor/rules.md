# Cursor Rules for drive-api Monorepo

## General Structure
- This repository contains two main applications:
  - **frontend/**: Angular 16+ app for Google Cloud Next '25 Content Management System UI
  - **backend/**: FastAPI app for the Conference Content Management System API

---

## Frontend (Angular)
- **Location:** `frontend/`
- **Entry Point:** `src/main.ts`
- **App Root:** `src/app/`
- **Key Feature Folders:**
  - `features/content-management`: Content CRUD, schema, upload, review
  - `features/home`: Dashboard
  - `features/ai-features`: AI-powered features
  - `features/search`: Search UI
  - `shared/`: Shared models, UI, and utilities
  - `core/`: Core services, API, auth, models
- **Styling:** SCSS, Tailwind, Angular Material (custom theme)
- **Testing:** Jasmine/Karma, specs in `src/**/*.spec.ts`
- **Scripts:** Use `npm run start` for dev, `npm run build` for prod
- **TypeScript:** Strict mode enabled, see `tsconfig.json`
- **Ignore:** `dist/`, `node_modules/`, `.angular/`, `.env*`, `.vscode/`, `*.log`

### Cursor Navigation
- Use `src/app/features/` for feature-driven development
- Use `src/app/shared/` for reusable code
- Use `src/app/core/` for singleton services and app-wide logic
- UI components are in `components/` subfolders
- Models are in `models/` subfolders
- Services are in `services/` subfolders

### Code Quality
- Follow Angular and Google Material best practices
- Use RxJS for async flows
- Prefer Observables over Promises in services
- Use SCSS modules for component styles
- Use Angular CLI for generating new components/services
- Use strict typing everywhere
- Write unit tests for all components and services
- Use pre-commit hooks for formatting and linting if desired

### Tailwind CSS Rules
- Use Tailwind utility classes for layout, spacing, color, and typography where possible.
- Prefer Tailwind classes over custom SCSS for common UI patterns (e.g., flex, grid, margin, padding, text, bg, border).
- Use SCSS only for complex or reusable styles that cannot be easily expressed with Tailwind.
- Use `@apply` in SCSS for grouping Tailwind utilities in component stylesheets if needed.
- Keep Tailwind configuration in `tailwind.config.js` and extend only as necessary for the design system.
- Use the `prose` class for rich text content (e.g., markdown rendering) to apply sensible defaults.
- Avoid duplicating styles between Tailwind and Angular Material; use one system per component where possible.
- Use responsive and dark mode variants (`sm:`, `md:`, `lg:`, `dark:`, etc.) for adaptive design.
- Purge unused Tailwind classes via the Angular build pipeline (see `tailwind.config.js` and `angular.json`).
- Document any custom Tailwind plugins or theme extensions in the README or `tailwind.config.js`.

---

## Backend (FastAPI)
- **Location:** `backend/`
- **Entry Point:** `main.py`
- **App Root:** `app/`
- **Key Folders:**
  - `api/endpoints/`: Route handlers (auth, content, drive, rag, etc.)
  - `core/`: Config, logging, auth utils
  - `db/`: Firestore client
  - `models/`: Data models (Pydantic)
  - `repositories/`: Data access layer
  - `services/`: Business logic
  - `schemas/`: Pydantic schemas
  - `tests/`: Unit/integration tests
- **Config:** Use `.env` for secrets and environment variables
- **Testing:** Pytest, config in `pytest.ini` and `pyproject.toml`
- **Linting/Formatting:** Black, Flake8, isort, mypy, ruff (see `.pre-commit-config.yaml`)
- **Ignore:** `venv/`, `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.env*`, `uploads/`, `dist/`, `build/`, `*.log`, `*.egg-info/`

### Cursor Navigation
- Use `app/api/endpoints/` for API routes
- Use `app/services/` for business logic
- Use `app/repositories/` for DB access
- Use `app/models/` and `app/schemas/` for data models
- Use `tests/` for all test code

### Code Quality
- Follow FastAPI and Pydantic best practices
- Use type hints everywhere
- Use dependency injection for services
- Write unit and integration tests for all endpoints and services
- Use pre-commit hooks for formatting, linting, and type checking
- Use structured logging (see `app/core/logging.py`)

---

## Monorepo Conventions
- Keep frontend and backend code separate
- Use consistent naming and folder structure across both apps
- Document all public APIs and components
- Use `.gitignore` in both apps to avoid committing build, env, and secret files
- Use README.md in each app for onboarding and documentation
- Use pre-commit hooks for code quality (see backend for example)

---

## Cursor Tips
- Use semantic search to find features, services, or endpoints
- Use fuzzy file search for quick navigation
- Use code actions to refactor or generate new code following the above structure
- When in doubt, check the relevant README.md for each app

---

_Last updated: 2024-06-09_

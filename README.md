# FastAPI User CRUD Manager

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white) ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

Full-stack CRUD app with Pydantic validation & auto-delete if credit score < 100.

**Live Demo:** (add Render/Fly.io link here)

## Features
- Create / Read / Update / Delete users
- Username-based lookup
- Auto-delete low credit score users
- Modern glassmorphism UI (2025 style)

## Tech Stack
- FastAPI
- Pydantic
- Jinja2 + Tailwind CSS

## Quick Start
```bash
pip install fastapi uvicorn
uvicorn main_app:app --reload

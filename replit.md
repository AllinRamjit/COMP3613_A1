# Flask MVC Template - Replit Setup

## Overview
This is a Flask MVC web application template that provides user authentication, route management, and administrative features. The application follows the Model-View-Controller pattern and includes features for managing users, streets, routes, and delivery requests.

## Current State (September 25, 2025)
- Successfully imported and configured for Replit environment
- Python 3.11 with all dependencies installed 
- SQLite database initialized with proper schema
- Flask development server running on 0.0.0.0:5000
- Deployment configuration set up for production

## Recent Changes
- Fixed SQLAlchemy relationship issues in models (Route and User class references)
- Configured Flask development server for Replit proxy compatibility
- Set up autoscale deployment with gunicorn for production
- All dependencies successfully installed via pip

## Technology Stack
- **Backend**: Flask 2.3.3 with SQLAlchemy, JWT authentication
- **Database**: SQLite (development), PostgreSQL (production ready)
- **Frontend**: HTML templates with Jinja2, CSS, JavaScript
- **Admin**: Flask-Admin interface
- **Testing**: pytest, mocha, chai, puppeteer for E2E testing

## Project Architecture
```
App/
├── controllers/     # Business logic and user management
├── models/         # Database models (User, Street, Route, Request)
├── views/          # Route handlers and view logic
├── templates/      # HTML templates
├── static/         # CSS, JS, and static assets
└── tests/          # Unit and integration tests
```

## Key Features
- User authentication with role-based access (drivers, residents)
- Street and route management system
- Request/delivery tracking system
- Administrative dashboard
- JWT token-based authentication
- Migration support with Flask-Migrate

## Development Workflow
- Flask development server configured for host 0.0.0.0:5000
- Debug mode enabled for development
- Database automatically initialized with sample data
- Hot reloading enabled

## Deployment
- Production deployment configured with autoscale
- Uses gunicorn WSGI server for production
- Build process installs all requirements.txt dependencies
- Environment variables configured for production database connection

## User Preferences
- Prefers working Flask applications over documentation
- Focus on functionality and working code
- Minimal configuration needed for quick setup
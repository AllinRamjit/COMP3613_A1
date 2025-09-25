![Tests](https://github.com/uwidcit/flaskmvc/actions/workflows/dev.yml/badge.svg)

# Flask MVC Template
A template for flask applications structured in the Model View Controller pattern [Demo](https://dcit-flaskmvc.herokuapp.com/). [Postman Collection](https://documenter.getpostman.com/view/583570/2s83zcTnEJ)


# Dependencies
* Python3/pip3
* Packages listed in requirements.txt

# Installing Dependencies
```bash
$ pip install -r requirements.txt
```

# Configuration Management


Configuration information such as the database url/port, credentials, API keys etc are to be supplied to the application. However, it is bad practice to stage production information in publicly visible repositories.
Instead, all config is provided by a config file or via [environment variables](https://linuxize.com/post/how-to-set-and-list-environment-variables-in-linux/).

## In Development

When running the project in a development environment (such as gitpod) the app is configured via default_config.py file in the App folder. By default, the config for development uses a sqlite database.

default_config.py
```python
SQLALCHEMY_DATABASE_URI = "sqlite:///temp-database.db"
SECRET_KEY = "secret key"
JWT_ACCESS_TOKEN_EXPIRES = 7
ENV = "DEVELOPMENT"
```

These values would be imported and added to the app in load_config() function in config.py

config.py
```python
# must be updated to inlude addtional secrets/ api keys & use a gitignored custom-config file instad
def load_config():
    config = {'ENV': os.environ.get('ENV', 'DEVELOPMENT')}
    delta = 7
    if config['ENV'] == "DEVELOPMENT":
        from .default_config import JWT_ACCESS_TOKEN_EXPIRES, SQLALCHEMY_DATABASE_URI, SECRET_KEY
        config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
        config['SECRET_KEY'] = SECRET_KEY
        delta = JWT_ACCESS_TOKEN_EXPIRES
...
```

## In Production

When deploying your application to production/staging you must pass
in configuration information via environment tab of your render project's dashboard.

![perms](./images/fig1.png)

# Flask CLI Commands

The application provides a comprehensive set of CLI commands for managing the delivery/transportation system. All commands are executed through the Flask CLI using `wsgi.py`.

## Command Structure

Commands are organized into groups for better organization:

```bash
export FLASK_APP=wsgi.py
flask <group> <command> [options]
```

## Database Management

### Initialize Database
Initialize and seed the database with default data:
```bash
flask init
```

### Import Test Data
Import comprehensive test data from JSON file:
```bash
# Import test data (preserves existing data)
flask user import-test-data

# Clear existing data and import fresh
flask user import-test-data --clear

# Import from custom file
flask user import-test-data --file my_data.json
```

## User Management Commands

All user management commands use the `flask user` prefix:

### Create Users
Create users with different roles:
```bash
# Create a driver
flask user create alice alicepass --role driver

# Create a resident with street assignment
flask user create john johnpass --role resident --street-id 1
```

### List Users
Display users in different formats:
```bash
# List users (object format)
flask user list

# List users in JSON format
flask user list json
```

### Manage Streets
Add and manage street locations:
```bash
# Add a new street
flask user add-street --name "Main Street"

# Update user's street assignment
flask user update-user-street --user_id 2 --street_id 1
```

## Route Management Commands

### Schedule Routes
Create delivery routes for drivers:
```bash
# Schedule a route for a driver
flask user schedule-route --driver_id 3 --street_id 1 --time "2025-09-26T09:00:00"
```

### List Routes
View scheduled routes with optional filtering:
```bash
# List all routes
flask user list-routes

# List routes by status
flask user list-routes --status scheduled
flask user list-routes --status "on the way"
flask user list-routes --status arrived
flask user list-routes --status completed
flask user list-routes --status cancelled
```

### Route Lifecycle Management
Control route progression through different states:
```bash
# Start a scheduled route
flask user start-route --route_id 1

# Mark driver as arrived at destination
flask user arrive --route_id 1

# Complete a route
flask user complete-route --route_id 1

# Cancel a route
flask user cancel-route --route_id 2

# Manually set route status
flask user set-route-status --route_id 1 --status "on the way"
```

## Request Management Commands

### Create Stop Requests
Residents can request stops on routes:
```bash
# Create a stop request
flask user request-stop --resident_id 2 --route_id 1 --quantity 3 --notes "Need groceries"
```

### Manage Requests
Drivers can manage incoming requests:
```bash
# Accept a request
flask user manage-requests --request_id 1 --action accept

# Decline a request
flask user manage-requests --request_id 1 --action decline

# Mark request as fulfilled
flask user manage-requests --request_id 1 --action fulfill

# Cancel a request
flask user manage-requests --request_id 1 --action cancel
```

### View Requests
List stops and view resident inboxes:
```bash
# List all stops for a route
flask user list-stops --route_id 1

# View resident's inbox (upcoming routes on their street)
flask user view-inbox --resident_id 2
```

## Driver Operations Commands

### Location and Status Management
Track driver locations and check status:
```bash
# Update driver's GPS location
flask user update-location --driver_id 3 --lat 40.7128 --lng -74.0060

# Check driver's current status and upcoming routes
flask user driver-status --driver_id 3
```

## Testing Commands

### Run Test Suite
Execute automated tests:
```bash
# Run all user-related tests
flask test user

# Run only unit tests
flask test user unit

# Run only integration tests
flask test user int
```

## Command Examples Workflow

Here's a complete workflow example demonstrating the system:

```bash
# 1. Initialize database
flask init

# 2. Import comprehensive test data
flask user import-test-data --clear

# 3. Check imported users
flask user list

# 4. View all scheduled routes
flask user list-routes

# 5. Start a route
flask user start-route --route_id 1

# 6. Update driver location
flask user update-location --driver_id 1 --lat 40.7580 --lng -73.9855

# 7. Mark arrival
flask user arrive --route_id 1

# 8. Create a stop request
flask user request-stop --resident_id 5 --route_id 1 --quantity 2 --notes "Emergency supplies"

# 9. Accept the request
flask user manage-requests --request_id 1 --action accept

# 10. Complete the route
flask user complete-route --route_id 1

# 11. Check driver status
flask user driver-status --driver_id 1
```

## Command Reference Quick Guide

| Category | Command | Purpose |
|----------|---------|---------|
| **Database** | `flask init` | Initialize database |
| **Data** | `flask user import-test-data` | Import test data |
| **Users** | `flask user create` | Create new user |
| **Users** | `flask user list` | List all users |
| **Streets** | `flask user add-street` | Add new street |
| **Streets** | `flask user update-user-street` | Update user's street assignment |
| **Routes** | `flask user schedule-route` | Schedule new route |
| **Routes** | `flask user list-routes` | View all routes |
| **Routes** | `flask user start-route` | Start route |
| **Routes** | `flask user arrive` | Mark arrival |
| **Routes** | `flask user complete-route` | Complete route |
| **Routes** | `flask user cancel-route` | Cancel route |
| **Routes** | `flask user set-route-status` | Set route status manually |
| **Requests** | `flask user request-stop` | Create stop request |
| **Requests** | `flask user manage-requests` | Handle requests |
| **Requests** | `flask user list-stops` | View route stops |
| **Requests** | `flask user view-inbox` | View resident inbox |
| **Drivers** | `flask user driver-status` | Check driver status |
| **Drivers** | `flask user update-location` | Update GPS location |
| **Testing** | `flask test user` | Run test suite |

All commands include built-in help. Use `--help` with any command to see detailed options:
```bash
flask user --help
flask user create --help
flask user schedule-route --help
```


# Running the Project

_For development run the serve command (what you execute):_
```bash
$ flask run
```

_For production using gunicorn (what the production server executes):_
```bash
$ gunicorn wsgi:app
```

# Deploying
You can deploy your version of this app to render by clicking on the "Deploy to Render" link above.

# Initializing the Database
When connecting the project to a fresh empty database ensure the appropriate configuration is set then file then run the following command. This must also be executed once when running the app on heroku by opening the heroku console, executing bash and running the command in the dyno.

```bash
$ flask init
```

# Database Migrations
If changes to the models are made, the database must be'migrated' so that it can be synced with the new models.
Then execute following commands using manage.py. More info [here](https://flask-migrate.readthedocs.io/en/latest/)

```bash
$ flask db init
$ flask db migrate
$ flask db upgrade
$ flask db --help
```

# Testing

## Unit & Integration
Unit and Integration tests are created in the App/test. You can then create commands to run them. Look at the unit test command in wsgi.py for example

```python
@test.command("user", help="Run User tests")
@click.argument("type", default="all")
def user_tests_command(type):
    if type == "unit":
        sys.exit(pytest.main(["-k", "UserUnitTests"]))
    elif type == "int":
        sys.exit(pytest.main(["-k", "UserIntegrationTests"]))
    else:
        sys.exit(pytest.main(["-k", "User"]))
```

You can then execute all user tests as follows

```bash
$ flask test user
```

You can also supply "unit" or "int" at the end of the comand to execute only unit or integration tests.

You can run all application tests with the following command

```bash
$ pytest
```

## Test Coverage

You can generate a report on your test coverage via the following command

```bash
$ coverage report
```

You can also generate a detailed html report in a directory named htmlcov with the following comand

```bash
$ coverage html
```

# Troubleshooting

## Views 404ing

If your newly created views are returning 404 ensure that they are added to the list in main.py.

```python
from App.views import (
    user_views,
    index_views
)

# New views must be imported and added to this list
views = [
    user_views,
    index_views
]
```

## Cannot Update Workflow file

If you are running into errors in gitpod when updateding your github actions file, ensure your [github permissions](https://gitpod.io/integrations) in gitpod has workflow enabled ![perms](./images/gitperms.png)

## Database Issues

If you are adding models you may need to migrate the database with the commands given in the previous database migration section. Alternateively you can delete you database file.

import click, pytest, sys, json
from flask.cli import with_appcontext, AppGroup
from datetime import datetime
from typing import Optional



from App.database import db, get_migrate
from App.models.user import User
from App.models.street import Street
from App.models.request import Request
from App.models.routes import Route
from App.main import create_app

from App.main import create_app
from App.controllers import ( create_user, get_all_users_json, get_all_users, initialize )


# This commands file allow you to create convenient CLI commands for testing controllers

app = create_app()
migrate = get_migrate(app)

#Functions to be used in commands#
def parse_time(iso_string):
    """Convert ISO formatted string to datetime object."""
    try:
        return datetime.fromisoformat(iso_string)
    except Exception:
        print("Invalid datetime format. Use ISO format.")

def get_user(user_id: int, user_role:Optional[str] = None):
    user = User.query.get(user_id)
    if not user:
        print(f"User {user_id} not found")
        return None
    if user_role and user.role != user_role:
        print(f"User {user.id} is not a {user_role}. They are {user.role}")
        return None
    return user

def get_street(street_id: int):
    street = Street.query.get(street_id)
    if not street:
        print(f"Street {street_id} not found")
    return street

def get_route(route_id: int):
    route = Route.query.get(route_id)
    if not route:
        print(f"Route {route_id} not found")
    return route

# This command creates and initializes the database
@app.cli.command("init", help="Creates and initializes the database")
def init():
    initialize()
    print('database intialized')

'''
User Commands
'''

# Commands can be organized using groups

# create a group, it would be the first argument of the comand
# eg : flask user <command>
user_cli = AppGroup('user', help='User object commands') 

# Then define the command and any parameters and annotate it with the group (@)
@user_cli.command("create", help="Creates a user")
@click.argument("username", default="rob")
@click.argument("password", default="robpass")
@click.option("--role", required=True, type=click.Choice(['driver', 'resident'], case_sensitive=False), help="Role of the user")
@click.option("--street-id", required=False, default=None, help="Street id of the resident user")
def create_user_command(username, password, role, street_id):
    if role == 'resident' and street_id is None:
        print("Resident users must have a street_id. You can add street_id later using the update-user-street command")
        return
    
    if street_id is not None:
        street = get_street(street_id)
        if not street:
            print(f"Street with id {street_id} not found")
            return
        u = User(username=username, password=password, role=role, street_id=street.id)
        db.session.add(u)
        db.session.commit()
        print(f'User {u.username} created with id {u.id} and street {street.name}')
    else:
        # Create user without street (for drivers, etc.)
        u = User(username=username, password=password, role=role, street_id=None)
        db.session.add(u)
        db.session.commit()
        print(f'User {u.username} created with id {u.id} and role {role}')

# this command will be : flask user create bob bobpass

@user_cli.command("list", help="Lists users in the database")
@click.argument("format", default="string")
def list_user_command(format):
    if format == 'string':
        print(get_all_users())
    else:
        print(get_all_users_json())

app.cli.add_command(user_cli) # add the group to the cli

'''
Test Commands
'''

test = AppGroup('test', help='Testing commands') 

@test.command("user", help="Run User tests")
@click.argument("type", default="all")
def user_tests_command(type):
    if type == "unit":
        sys.exit(pytest.main(["-k", "UserUnitTests"]))
    elif type == "int":
        sys.exit(pytest.main(["-k", "UserIntegrationTests"]))
    else:
        sys.exit(pytest.main(["-k", "App"]))
    

app.cli.add_command(test)

@user_cli.command("add-street", help="Add streets to the database")
@click.option("--name", required=True, help= "Unique Street Name")
def add_street(name):
    if Street.query.filter_by(name=name).first():
        print(f'Street {name} already exists')
    s = Street(name=name)
    db.session.add(s)
    db.session.commit()
    print(f'Street {s.name} created with id {s.id}')

@user_cli.command("update-user-street", help="Update a user's street")
@click.option("--user_id", required=True, type=int, help="ID of the user to update")
@click.option("--street_id", required=True, type=int, help="ID of the street to assign to the user")
def update_user_street(user_id, street_id):
    try:
        user = get_user(user_id, 'resident')
        if not user:
            return
        street = get_street(street_id)
        if not street:
            return
        user.street_id = street.id
        db.session.commit()
        print(f'User {user.username} updated with street {street.name}')
    except ValueError as e:
        print("Oops there was an error 1:", e)

@user_cli.command("schedule-route", help="Schedule drivers for their routes")
@click.option("--driver_id", required=True, type=int, help="ID of the driver to schedule")
@click.option("--street_id", required=True, type=int, help="ID of the street to assign to the driver")
@click.option("--time", required=True, type=str, help="Scheduled time in ISO format (YYYY-MM-DDTHH:MM:SS)")
def schedule_route(driver_id, street_id, time):
    try:
        driver = get_user(driver_id, 'driver')
        street = get_street(street_id)
        if not driver or not street:
            return
        route_time = parse_time(time)
        # Create a new route instead of modifying the driver
        route = Route(driver_id=driver.id, street_id=street.id, scheduled_time=route_time, status='scheduled')
        db.session.add(route)
        db.session.commit()
        print(f'Driver {driver.username} scheduled for street {street.name} at {route_time}')
    except Exception as e:
        print("Oops there was an error 2:", e)

@user_cli.command("list-routes", help="List all routes")
@click.option("--status", type=click.Choice(["scheduled", "on the way", "arrived", "completed", "cancelled"]), default=None)
def list_routes(status):
    q = Route.query
    if status:
        q = q.filter(Route.status == status)
    routes = q.order_by(Route.scheduled_time.asc()).all()
    if not routes:
        if status:
            print(f"No routes found with status '{status}'.")
        else:
            print("No routes found.")
        return
    for route in routes:
        street = Street.query.get(route.street_id)
        driver = User.query.get(route.driver_id)
        print(f"Route ID: {route.id}, Driver: {driver.username}, Street: {street.name}, Scheduled Time: {route.scheduled_time.isoformat()}, Status: {route.status}")


@user_cli.command("view-inbox", help="List all requests")
@click.option("--resident_id", required=False, type=int, help="Filter requests by resident ID")
def view_inbox(resident_id):
    resident = get_user(resident_id, user_role="resident")
    if not resident:
        return
    if not resident.street_id:
        print(f"Resident {resident.username} does not have a street assigned.")
        return
    time_now = datetime.utcnow()
    routes = Route.query.filter(Route.street_id == resident.street_id, Route.scheduled_time >= time_now).order_by(Route.scheduled_time.asc()).all()
    if not routes:
        print(f"No routes scheduled for resident {resident.username}'s street.")
        return
    street = Street.query.get(resident.street_id)
    print(f"Route(s) scheduled for street {street.name}:")
    for r in routes:
        print(f"Driver Name: {r.driver_id}, Status: {r.status}, Scheduled Time: {r.scheduled_time.isoformat()})")

@user_cli.command("request-stop", help="Request a stop")
@click.option("--resident_id", required=True, type=int, help="ID of the resident making the request")
@click.option("--route_id", required=True, type=int, help="ID of the route request the stop")
@click.option("--quantity", required=True, type=int, help="Quantity of items to request")
@click.option("--notes", required=False, type=str, default="", help="Additional notes for the request")
def request_stop(resident_id,route_id, quantity, notes):
    try:
        resident = get_user(resident_id, user_role="resident")
        route = get_route(route_id)
        if route.status not in ["scheduled", "on the way"]:
            print(f"Cannot request a stop for route {route.id} with status {route.status}.")
            return
        request = Request(resident_id=resident.id, route_id=route.id, quantity=quantity, notes=notes)
        db.session.add(request)
        db.session.commit()
        print(f"Request {request.id} created for resident {resident.username} on route {route.id}.")
    except ValueError as e:
        print("Oops there was an error 3:", e)

@user_cli.command("manage-requests", help="Manage requests for a driver")
@click.option("--request_id", required=True, type=int, help="ID of the request to manage")
@click.option("--action", required=True, type=click.Choice(['accept','decline', 'fulfill','cancel'], case_sensitive=False), help="Action to perform on the request")
def manage_requests(request_id, action):
    stop_request = Request.query.get(request_id)
    if not stop_request:
        print(f"Request {request_id} not found.")
        return
    old = stop_request.status
    mapping = {"accept": "on the way", "decline": "available", "fulfill": "completed", "cancel": "cancelled"}
    stop_request.status = mapping[action]
    db.session.commit()
    print(f"Request {request_id} status changed from {old} to {stop_request.status}.")

@user_cli.command("driver-status", help="Update driver status and location")
@click.option("--driver_id", required=True, type=int, help="ID of the driver to update")
def driver_status(driver_id):
    driver = get_user(driver_id, user_role="driver")
    if not driver:
        return
    
    curr_time = datetime.utcnow()
    next_request = Route.query.filter(Route.scheduled_time >= curr_time, Route.status == 'scheduled').order_by(Route.scheduled_time.asc()).first()
    current_request = Route.query.filter(Route.driver_id == driver.id, Route.status.in_(["on the way", "arrived"])).first()

    if current_request:
        street = Street.query.get(current_request.street_id)
        print(f"Current Route: ID = {current_request.id} on {street.name} scheduled for {current_request.scheduled_time.isoformat()} with status {current_request.status}.")
    else:
        print(f"No current deliveries.")
    if next_request and next_request.driver_id == driver.id and (not current_request or next_request.id != current_request.id):
        street = Street.query.get(next_request.street_id)
        print(f"Next Request: Driver {driver.username} is scheduled to go to street {street.name} at {next_request.scheduled_time.isoformat()}.")
    elif not current_request:
        print(f"No upcoming deliveries.")

@user_cli.command("update-location", help="Update driver location")
@click.option("--driver_id", required=True, type=int, help="ID of the Driver to update")
@click.option("--lat", required=True, type=float, help="Current latitude of the driver")
@click.option("--lng", required=True, type=float, help="Current longitude of the driver")
def update_location(driver_id, lat, lng):
    driver = get_user(driver_id, user_role="driver")
    if not driver:
        return
    route = Route.query.filter(Route.driver_id == driver.id, Route.status.in_(["on the way", "arrived"])).order_by(Route.scheduled_time.asc()).first()
    if not route:
        print(f"Driver {driver.username} does not have an active route to update location for.")
        return
    route.current_lat = lat
    route.current_lng = lng
    db.session.commit()
    print(f"Driver {driver.username} location updated to lat: {lat}, lng: {lng} for route {route.id}.")


@user_cli.command("set-route-status", help="Set route status")
@click.option("--route_id", required=True, type=int, help="ID of the route to update")
@click.option("--status", required=True, type=click.Choice(["scheduled", "on the way", "arrived", "completed", "cancelled"], case_sensitive=False), help="New status of the route")
def set_driver_status(route_id, status):
    route = get_route(route_id)
    old_status = route.status
    route.status = status
    db.session.commit()
    print(f"Route {route.id} status changed from {old_status} to {route.status}.")


@user_cli.command("start-route", help="Start a driver's route")
@click.option("--route_id", required=True, type=int, help="ID of the route to start")
def start_route(route_id):
    route = get_route(route_id)
    if route.status != "scheduled":
        print(f"Cannot start route {route.id} with status {route.status}.")
        return
    route.status = "on the way"
    db.session.commit()
    print(f"Route {route.id} started. Status changed to 'on the way'.")


@user_cli.command("arrive", help="Mark a driver as arrived at their destination")
@click.option("--route_id", required=True, type=int, help="ID of the route to mark as arrived")
def arrive(route_id):
    route = get_route(route_id)
    if route.status != "on the way":
        print(f"Cannot mark route {route.id} as arrived with status {route.status}.")
        return
    route.status = "arrived"
    db.session.commit()
    print(f"Route {route.id} marked as arrived. Status changed to 'arrived'.")

@user_cli.command("complete-route", help="Complete a driver's route")
@click.option("--route_id", required=True, type=int, help="ID of the route to complete")
def complete_route(route_id):
    route = get_route(route_id)
    if route.status != "arrived":
        print(f"Cannot complete route {route.id} with status {route.status}.")
        return
    route.status = "completed"
    db.session.commit()
    print(f"Route {route.id} completed. Status changed to 'completed'.")

@user_cli.command("cancel-route", help="Cancel a driver's route")
@click.option("--route_id", required=True, type=int, help="ID of the route to cancel")
def cancel_route(route_id):
    route = get_route(route_id)
    if route.status in ["completed", "cancelled"]:
        print(f"Cannot cancel route {route.id} with status {route.status}.")
        return
    route.status = "cancelled"
    db.session.commit()
    print(f"Route {route.id} cancelled. Status changed to 'cancelled'.")

@user_cli.command("list-stops", help="List all stops for a route")
@click.option("--route_id", required=True, type=int, help="ID of the route to list stops for")
def list_stops(route_id):
    route = get_route(route_id)
    requests = Request.query.filter(Request.route_id == route.id).order_by(Request.created_at.asc()).all()
    if not requests:
        print(f"No stops found for route {route.id}.")
        return
    print(f"Stops for Route {route.id}:")
    for req in requests:
        resident = User.query.get(req.resident_id)
        print(f"Request ID: {req.id}, Resident: {resident.username}, Quantity: {req.quantity}, Notes: {req.notes}, Status: {req.status}, Created At: {req.created_at.isoformat()}")


@user_cli.command("import-test-data", help="Import test data from JSON file")
@click.option("--file", default="test_data.json", help="Path to the JSON test data file")
@click.option("--clear", is_flag=True, help="Clear existing data before importing")
def import_test_data(file, clear):
    """Import comprehensive test data from a JSON file."""
    try:
        # Read the JSON file
        with open(file, 'r') as f:
            data = json.load(f)
        
        if clear:
            print("Clearing existing data...")
            # Clear existing data in reverse dependency order
            Request.query.delete()
            Route.query.delete()
            User.query.delete()
            Street.query.delete()
            db.session.commit()
            print("Existing data cleared.")
        
        print("Importing test data...")
        
        # Import streets first
        street_map = {}
        for street_data in data.get('streets', []):
            existing_street = Street.query.filter_by(name=street_data['name']).first()
            if not existing_street:
                street = Street(name=street_data['name'])
                db.session.add(street)
                db.session.flush()  # To get the ID
                street_map[street_data['name']] = street.id
                print(f"Created street: {street.name} (ID: {street.id})")
            else:
                street_map[street_data['name']] = existing_street.id
                print(f"Street already exists: {existing_street.name} (ID: {existing_street.id})")
        
        db.session.commit()
        
        # Import users
        user_map = {}
        for user_data in data.get('users', []):
            existing_user = User.query.filter_by(username=user_data['username']).first()
            if not existing_user:
                street_id = None
                if user_data.get('street_name'):
                    street_id = street_map.get(user_data['street_name'])
                elif user_data.get('street_id'):
                    street_id = user_data['street_id']
                
                user = User(
                    username=user_data['username'],
                    password=user_data['password'],
                    role=user_data['role'],
                    street_id=street_id
                )
                db.session.add(user)
                db.session.flush()  # To get the ID
                user_map[user_data['username']] = user.id
                street_name = user_data.get('street_name', 'None')
                print(f"Created user: {user.username} ({user.role}) - Street: {street_name}")
            else:
                user_map[user_data['username']] = existing_user.id
                print(f"User already exists: {existing_user.username}")
        
        db.session.commit()
        
        # Import routes
        route_map = {}
        for route_data in data.get('routes', []):
            driver_id = user_map.get(route_data['driver_username'])
            street_id = street_map.get(route_data['street_name'])
            
            if driver_id and street_id:
                scheduled_time = datetime.fromisoformat(route_data['scheduled_time'])
                
                # Create unique route key including scheduled time to handle multiple routes per driver/street
                route_key = f"{route_data['driver_username']}_{route_data['street_name']}_{route_data['scheduled_time']}"
                
                # Check if route already exists
                existing_route = Route.query.filter_by(
                    driver_id=driver_id,
                    street_id=street_id,
                    scheduled_time=scheduled_time
                ).first()
                
                if not existing_route:
                    route = Route(
                        driver_id=driver_id,
                        street_id=street_id,
                        scheduled_time=scheduled_time,
                        status=route_data['status']
                    )
                    db.session.add(route)
                    db.session.flush()  # To get the ID
                    route_map[route_key] = route.id
                    print(f"Created route: Driver {route_data['driver_username']} -> {route_data['street_name']} at {scheduled_time}")
                else:
                    route_map[route_key] = existing_route.id
                    print(f"Route already exists: {route_data['driver_username']} -> {route_data['street_name']} at {scheduled_time}")
            else:
                print(f"Skipping route - missing driver or street: {route_data}")
        
        db.session.commit()
        
        # Import requests
        for request_data in data.get('requests', []):
            resident_id = user_map.get(request_data['resident_username'])
            
            # Use the exact scheduled time from the request if provided, otherwise find the first matching route
            if 'route_scheduled_time' in request_data:
                # Direct mapping using the specific scheduled time
                route_key = f"{request_data['route_driver']}_{request_data['route_street']}_{request_data['route_scheduled_time']}"
                route_id = route_map.get(route_key)
                
                if not route_id:
                    print(f"Error: No route found for exact match: {request_data['route_driver']} -> {request_data['route_street']} at {request_data['route_scheduled_time']}")
                    route_id = None
            else:
                # Legacy support: find routes by driver and street, but warn if multiple exist
                matching_routes = []
                for route_data in data.get('routes', []):
                    if (route_data['driver_username'] == request_data['route_driver'] and 
                        route_data['street_name'] == request_data['route_street']):
                        matching_routes.append(route_data)
                
                if len(matching_routes) == 0:
                    print(f"Error: No matching route found for request: {request_data['resident_username']} -> {request_data['route_driver']} on {request_data['route_street']}")
                    route_id = None
                elif len(matching_routes) > 1:
                    print(f"Warning: Multiple routes found for {request_data['route_driver']} -> {request_data['route_street']}. Add 'route_scheduled_time' to request for deterministic matching. Using first route.")
                    route_key = f"{request_data['route_driver']}_{request_data['route_street']}_{matching_routes[0]['scheduled_time']}"
                    route_id = route_map.get(route_key)
                else:
                    # Single route found, use it
                    route_key = f"{request_data['route_driver']}_{request_data['route_street']}_{matching_routes[0]['scheduled_time']}"
                    route_id = route_map.get(route_key)
            
            if resident_id and route_id:
                # Check if request already exists
                existing_request = Request.query.filter_by(
                    resident_id=resident_id,
                    route_id=route_id
                ).first()
                
                if not existing_request:
                    request = Request(
                        resident_id=resident_id,
                        route_id=route_id,
                        quantity=request_data['quantity'],
                        notes=request_data['notes'],
                        status=request_data['status']
                    )
                    db.session.add(request)
                    print(f"Created request: {request_data['resident_username']} -> Route {route_id} (Qty: {request_data['quantity']})")
                else:
                    print(f"Request already exists: {request_data['resident_username']} -> Route {route_id}")
            else:
                print(f"Skipping request - missing resident or route: {request_data}")
        
        db.session.commit()
        
        # Print summary
        print("\n=== Import Summary ===")
        print(f"Streets: {Street.query.count()}")
        print(f"Users: {User.query.count()}")
        print(f"Routes: {Route.query.count()}")
        print(f"Requests: {Request.query.count()}")
        print("Test data import completed successfully!")
        
    except FileNotFoundError:
        print(f"Error: File '{file}' not found.")
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in '{file}': {e}")
    except Exception as e:
        print(f"Error importing test data: {e}")
        db.session.rollback()


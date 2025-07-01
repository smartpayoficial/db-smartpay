import pytest
import uuid
import random
from httpx import AsyncClient

# --- Action Endpoints --- #

@pytest.fixture(scope="function")
async def action(client: AsyncClient, device, user):
    """Fixture to create and clean up an action for testing."""
    action_data = {
        "device_id": device["id"],
        "applied_by_id": user["id"],
        "action": "locate",
        "description": "A test action"
    }
    response = await client.post("/api/v1/actions/", json=action_data)
    assert response.status_code == 201
    created_action = response.json()
    
    yield created_action
    
    # Cleanup
    delete_response = await client.delete(f"/api/v1/actions/{created_action['action_id']}/")
    assert delete_response.status_code in [200, 404]

async def test_create_action(action):
    """Tests POST /actions/ endpoint by using the action fixture."""
    assert "action_id" in action
    assert action["action"] == "locate"

async def test_get_all_actions(client: AsyncClient):
    """Tests GET /actions/ endpoint."""
    response = await client.get("/api/v1/actions/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

async def test_get_action_by_id(client: AsyncClient, action):
    """Tests GET /actions/{action_id}/ endpoint."""
    response = await client.get(f"/api/v1/actions/{action['action_id']}/")
    assert response.status_code == 200
    assert response.json()["action_id"] == action["action_id"]

async def test_update_action(client: AsyncClient, action):
    """Tests PATCH /actions/{action_id}/ endpoint."""
    update_data = {"state": "completed"}
    response = await client.patch(f"/api/v1/actions/{action['action_id']}/", json=update_data)
    assert response.status_code == 200
    assert response.json()["state"] == "completed"

async def test_delete_action(client: AsyncClient, action):
    """Tests DELETE /actions/{action_id}/ endpoint."""
    response = await client.delete(f"/api/v1/actions/{action['action_id']}/")
    assert response.status_code == 200
    assert response.json()["deleted"] is True

    # Verify it's gone
    get_response = await client.get(f"/api/v1/actions/{action['action_id']}/")
    assert get_response.status_code == 404

# --- Authentication Endpoints --- #

@pytest.fixture(scope="function")
async def authentication(client: AsyncClient):
    """Fixture to create and clean up an authentication for testing."""
    unique_id = uuid.uuid4()
    auth_data = {
        "username": f"testuser_{unique_id}",
        "password": "a_secure_password",
        "email": f"test_{unique_id}@example.com",
    }
    response = await client.post("/api/v1/auth/", json=auth_data)
    assert response.status_code == 201
    created_auth = response.json()
    
    yield created_auth
    
    # Cleanup
    auth_id = created_auth["authentication_id"]
    delete_response = await client.delete(f"/api/v1/auth/{auth_id}/")
    assert delete_response.status_code in [204, 404]

async def test_create_authentication(authentication):
    """Tests POST /auth/ endpoint by using the authentication fixture."""
    assert "authentication_id" in authentication
    assert "username" in authentication

async def test_get_all_authentications(client: AsyncClient):
    """Tests GET /auth/ endpoint."""
    response = await client.get("/api/v1/auth/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

async def test_get_authentication_by_id(client: AsyncClient, authentication):
    """Tests GET /auth/{auth_id}/ endpoint."""
    auth_id = authentication["authentication_id"]
    response = await client.get(f"/api/v1/auth/{auth_id}/")
    assert response.status_code == 200
    assert response.json()["authentication_id"] == auth_id

async def test_update_authentication(client: AsyncClient, authentication):
    """Tests PATCH /auth/{auth_id}/ endpoint."""
    auth_id = authentication["authentication_id"]
    update_data = {"password": "a_new_secure_password"}
    response = await client.patch(f"/api/v1/auth/{auth_id}/", json=update_data)
    assert response.status_code == 204

async def test_delete_authentication(client: AsyncClient, authentication):
    """Tests DELETE /auth/{auth_id}/ endpoint."""
    auth_id = authentication["authentication_id"]
    response = await client.delete(f"/api/v1/auth/{auth_id}/")
    assert response.status_code == 204

    # Verify it's gone
    get_response = await client.get(f"/api/v1/auth/{auth_id}/")
    assert get_response.status_code == 404

# --- City Endpoints --- #

@pytest.fixture(scope="function")
async def city(client: AsyncClient, region):
    """Fixture to create and clean up a city for testing."""
    city_data = {
        "name": f"Test City {uuid.uuid4()}",
        "region_id": region["id"]
    }
    response = await client.post("/api/v1/cities/", json=city_data)
    assert response.status_code == 201
    created_city = response.json()
    
    yield created_city
    
    # Cleanup
    delete_response = await client.delete(f"/api/v1/cities/{created_city['id']}/")
    assert delete_response.status_code in [204, 404]

async def test_create_city(city):
    """Tests POST /cities/ endpoint by using the city fixture."""
    assert "id" in city
    assert "name" in city
    assert city["region"]["id"] is not None

async def test_get_all_cities(client: AsyncClient):
    """Tests GET /cities/ endpoint."""
    response = await client.get("/api/v1/cities/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

async def test_get_city_by_id(client: AsyncClient, city):
    """Tests GET /cities/{city_id}/ endpoint."""
    response = await client.get(f"/api/v1/cities/{city['id']}/")
    assert response.status_code == 200
    assert response.json()["id"] == city["id"]

async def test_update_city(client: AsyncClient, city):
    """Tests PATCH /cities/{city_id}/ endpoint."""
    update_data = {"name": f"Updated City {uuid.uuid4()}"}
    response = await client.patch(f"/api/v1/cities/{city['id']}/", json=update_data)
    assert response.status_code == 200
    assert response.json()["name"] == update_data["name"]

async def test_delete_city(client: AsyncClient, city):
    """Tests DELETE /cities/{city_id}/ endpoint."""
    response = await client.delete(f"/api/v1/cities/{city['id']}/")
    assert response.status_code == 204

    # Verify it's gone
    get_response = await client.get(f"/api/v1/cities/{city['id']}/")
    assert get_response.status_code == 404

# --- Configuration Endpoints --- #

@pytest.fixture(scope="function")
async def configuration(client: AsyncClient):
    """Fixture to create and clean up a configuration for testing."""
    config_data = {
        "key": f"test_config_{uuid.uuid4()}",
        "value": "test_value"
    }
    # Note: The router prefix was corrected to /configuration/ (singular)
    response = await client.post("/api/v1/configuration/", json=config_data)
    assert response.status_code == 201
    created_config = response.json()
    
    yield created_config
    
    # Cleanup
    config_id = created_config["id"]
    delete_response = await client.delete(f"/api/v1/configuration/{config_id}/")
    assert delete_response.status_code in [204, 404]

async def test_create_configuration(configuration):
    """Tests POST /configuration/ endpoint by using the configuration fixture."""
    assert "id" in configuration
    assert "key" in configuration

async def test_get_all_configurations(client: AsyncClient):
    """Tests GET /configuration/ endpoint."""
    response = await client.get("/api/v1/configuration/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

async def test_get_configuration_by_id(client: AsyncClient, configuration):
    """Tests GET /configuration/{configuration_id}/ endpoint."""
    config_id = configuration["id"]
    response = await client.get(f"/api/v1/configuration/{config_id}/")
    assert response.status_code == 200
    assert response.json()["id"] == config_id

async def test_update_configuration(client: AsyncClient, configuration):
    """Tests PATCH /configuration/{configuration_id}/ endpoint."""
    config_id = configuration["id"]
    update_data = {"value": "new_test_value"}
    response = await client.patch(f"/api/v1/configuration/{config_id}/", json=update_data)
    assert response.status_code == 204

async def test_delete_configuration(client: AsyncClient, configuration):
    """Tests DELETE /configuration/{configuration_id}/ endpoint."""
    config_id = configuration["id"]
    response = await client.delete(f"/api/v1/configuration/{config_id}/")
    assert response.status_code == 204

    # Verify it's gone
    get_response = await client.get(f"/api/v1/configuration/{config_id}/")
    assert get_response.status_code == 404

# --- Country Endpoints --- #

@pytest.fixture(scope="function")
async def country(client: AsyncClient):
    """Fixture to create and clean up a country for testing."""
    country_data = {
        "name": f"Test Country {uuid.uuid4()}",
        "code": f"{random.randint(100, 999)}",
        "prefix": f"+{random.randint(1, 99)}"
    }
    response = await client.post("/api/v1/countries/", json=country_data)
    assert response.status_code == 201
    created_country = response.json()
    
    yield created_country
    
    # Cleanup
    delete_response = await client.delete(f"/api/v1/countries/{created_country['id']}/")
    assert delete_response.status_code in [204, 404]

async def test_create_country(country):
    """Tests POST /countries/ endpoint by using the country fixture."""
    assert "id" in country
    assert "name" in country
    assert "code" in country

async def test_get_all_countries(client: AsyncClient):
    """Tests GET /countries/ endpoint."""
    response = await client.get("/api/v1/countries/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

async def test_get_country_by_id(client: AsyncClient, country):
    """Tests GET /countries/{country_id}/ endpoint."""
    response = await client.get(f"/api/v1/countries/{country['id']}/")
    assert response.status_code == 200
    assert response.json()["id"] == country["id"]

async def test_update_country(client: AsyncClient, country):
    """Tests PATCH /countries/{country_id}/ endpoint."""
    update_data = {"name": f"Updated Country {uuid.uuid4()}"}
    response = await client.patch(f"/api/v1/countries/{country['id']}/", json=update_data)
    assert response.status_code == 200
    assert response.json()["name"] == update_data["name"]

async def test_delete_country(client: AsyncClient, country):
    """Tests DELETE /countries/{country_id}/ endpoint."""
    response = await client.delete(f"/api/v1/countries/{country['id']}/")
    assert response.status_code == 204

    # Verify it's gone
    get_response = await client.get(f"/api/v1/countries/{country['id']}/")
    assert get_response.status_code == 404

# --- Device Endpoints --- #

@pytest.fixture(scope="function")
async def device(client: AsyncClient, enrolment):
    """Fixture to create and clean up a device for testing."""
    device_data = {
        "serial_number": f"SN-{uuid.uuid4()}",
        "enrolment_id": enrolment["id"]
    }
    response = await client.post("/api/v1/devices/", json=device_data)
    assert response.status_code == 201
    created_device = response.json()
    
    yield created_device
    
    # Cleanup
    delete_response = await client.delete(f"/api/v1/devices/{created_device['id']}/")
    assert delete_response.status_code in [204, 404]

async def test_create_device(device):
    """Tests POST /devices/ endpoint by using the device fixture."""
    assert "id" in device
    assert "serial_number" in device
    assert device["enrolment"]["id"] is not None

async def test_get_all_devices(client: AsyncClient):
    """Tests GET /devices/ endpoint."""
    response = await client.get("/api/v1/devices/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

async def test_get_device_by_id(client: AsyncClient, device):
    """Tests GET /devices/{device_id}/ endpoint."""
    response = await client.get(f"/api/v1/devices/{device['id']}/")
    assert response.status_code == 200
    assert response.json()["id"] == device["id"]

async def test_update_device(client: AsyncClient, device):
    """Tests PATCH /devices/{device_id} endpoint."""
    update_data = {"serial_number": f"SN-UPDATED-{uuid.uuid4()}"}
    update_response = await client.patch(f"/api/v1/devices/{device['id']}/", json=update_data)
    assert update_response.status_code == 200
    updated_device = update_response.json()
    assert updated_device["serial_number"] == update_data["serial_number"]

    get_response = await client.get(f"/api/v1/devices/{device['id']}/")
    assert get_response.status_code == 200
    get_device = get_response.json()
    assert get_device["serial_number"] == update_data["serial_number"]

async def test_delete_device(client: AsyncClient, device):
    """Tests DELETE /devices/{device_id}/ endpoint."""
    device_id = device["id"]
    response = await client.delete(f"/api/v1/devices/{device_id}/")
    assert response.status_code == 204

    # Verify it's gone
    get_response = await client.get(f"/api/v1/devices/{device_id}/")
    assert get_response.status_code == 404

# --- Enrolment Endpoints --- #

@pytest.fixture(scope="function")
async def enrolment(client: AsyncClient, plan, city, role):
    """Fixture to create and clean up an enrolment and its dependencies for testing."""
    # --- Create User ---
    user_data = {
        "username": f"test_user_{uuid.uuid4().hex[:6]}", "password": "a_secure_password",
        "email": f"user_{uuid.uuid4().hex[:6]}@example.com", "dni": f"{uuid.uuid4().int % 100000000}",
        "first_name": "Test", "last_name": "User", "role_id": role["id"], "city_id": city["id"]
    }
    user_response = await client.post("/api/v1/users/", json=user_data)
    assert user_response.status_code == 201
    created_user = user_response.json()

    # --- Create Vendor (another user) ---
    vendor_data = {
        "username": f"test_vendor_{uuid.uuid4().hex[:6]}", "password": "a_secure_password",
        "email": f"vendor_{uuid.uuid4().hex[:6]}@example.com", "dni": f"{uuid.uuid4().int % 100000000}",
        "first_name": "Test", "last_name": "Vendor", "role_id": role["id"], "city_id": city["id"]
    }
    vendor_response = await client.post("/api/v1/users/", json=vendor_data)
    assert vendor_response.status_code == 201
    created_vendor = vendor_response.json()

    # --- Create Enrolment ---
    enrolment_data = {
        "user_id": created_user["id"],
        "vendor_id": created_vendor["id"],
        "plan_id": plan["id"],
        "city_id": city["id"]
    }
    response = await client.post("/api/v1/enrolments/", json=enrolment_data)
    assert response.status_code == 201
    created_enrolment = response.json()
    
    yield created_enrolment
    
    # Cleanup
    await client.delete(f"/api/v1/enrolments/{created_enrolment['id']}/")
    await client.delete(f"/api/v1/users/{created_user['id']}/")
    await client.delete(f"/api/v1/users/{created_vendor['id']}/")

async def test_create_enrolment(enrolment):
    """Tests POST /enrolments/ endpoint by using the enrolment fixture."""
    assert "id" in enrolment
    assert "user" in enrolment
    assert "vendor" in enrolment

async def test_get_all_enrolments(client: AsyncClient):
    """Tests GET /enrolments/ endpoint."""
    response = await client.get("/api/v1/enrolments/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

async def test_get_enrolment_by_id(client: AsyncClient, enrolment):
    """Tests GET /enrolments/{enrolment_id}/ endpoint."""
    response = await client.get(f"/api/v1/enrolments/{enrolment['id']}/")
    assert response.status_code == 200
    assert response.json()["id"] == enrolment["id"]

async def test_update_enrolment(client: AsyncClient, enrolment):
    """Tests PATCH /enrolments/{enrolment_id}/ endpoint."""
    update_data = {"state": "INACTIVE"}
    response = await client.patch(f"/api/v1/enrolments/{enrolment['id']}/", json=update_data)
    assert response.status_code == 200
    assert response.json()["state"] == "INACTIVE"

async def test_delete_enrolment(client: AsyncClient, enrolment):
    """Tests DELETE /enrolments/{enrolment_id}/ endpoint."""
    response = await client.delete(f"/api/v1/enrolments/{enrolment['id']}/")
    assert response.status_code == 204

    # Verify it's gone
    get_response = await client.get(f"/api/v1/enrolments/{enrolment['id']}/")
    assert get_response.status_code == 404

# --- Factory Reset Protection Endpoints --- #

@pytest.fixture(scope="function")
async def frp(client: AsyncClient, device):
    """Fixture to create and clean up a Factory Reset Protection for testing."""
    frp_data = {
        "account_id": f"acc_{uuid.uuid4()}",
        "device_id": device["id"],
    }
    response = await client.post("/api/v1/factoryResetProtection/", json=frp_data)
    assert response.status_code == 201
    created_frp = response.json()
    
    yield created_frp
    
    # Cleanup
    frp_id = created_frp["id"]
    await client.delete(f"/api/v1/factoryResetProtection/{frp_id}/")

async def test_create_factory_reset_protection(frp):
    """Tests POST /factoryResetProtection/ endpoint."""
    assert "id" in frp
    assert "account_id" in frp

async def test_get_all_factory_reset_protections(client: AsyncClient):
    """Tests GET /factoryResetProtection/ endpoint."""
    response = await client.get("/api/v1/factoryResetProtection/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

async def test_get_frp_by_id(client: AsyncClient, frp):
    """Tests GET /factoryResetProtection/{factory_reset_protection_id}/ endpoint."""
    frp_id = frp["id"]
    response = await client.get(f"/api/v1/factoryResetProtection/{frp_id}/")
    assert response.status_code == 200
    assert response.json()["id"] == frp_id

async def test_get_frp_by_account_id(client: AsyncClient, frp):
    """Tests GET /factoryResetProtection/accountId/{account_id}/ endpoint."""
    account_id = frp["account_id"]
    response = await client.get(f"/api/v1/factoryResetProtection/accountId/{account_id}/")
    assert response.status_code == 200
    assert response.json()["account_id"] == account_id

async def test_update_frp(client: AsyncClient, frp):
    """Tests PATCH /factoryResetProtection/{factory_reset_protection_id}/ endpoint."""
    frp_id = frp["id"]
    update_data = {"device_id": f"dev_updated_{uuid.uuid4()}"}
    response = await client.patch(f"/api/v1/factoryResetProtection/{frp_id}/", json=update_data)
    assert response.status_code == 204

async def test_delete_frp(client: AsyncClient, frp):
    """Tests DELETE /factoryResetProtection/{factory_reset_protection_id}/ endpoint."""
    frp_id = frp["id"]
    response = await client.delete(f"/api/v1/factoryResetProtection/{frp_id}/")
    assert response.status_code == 204

    # Verify it's gone
    get_response = await client.get(f"/api/v1/factoryResetProtection/{frp_id}/")
    assert get_response.status_code == 404

# --- Internal Auth Endpoints --- #

INTERNAL_HEADERS = {"X-Internal-Request": "true"}

@pytest.fixture(scope="function")
async def internal_user(client: AsyncClient):
    """Fixture to create an internal user for testing."""
    username = f"internal_user_{uuid.uuid4().hex[:6]}"
    password = "internal_password"
    user_data = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "dni": f"{uuid.uuid4().int % 100000000}",
        "first_name": "Internal",
        "last_name": "User",
        "role_id": None,
        "city_id": None
    }
    async with AsyncClient(app=app, base_url="http://test", headers=INTERNAL_HEADERS) as internal_client:
        response = await internal_client.post("/api/v1/users/", json=user_data)
        assert response.status_code == 201
        created_user = response.json()
        created_user['password'] = password  # Add password for verification tests
        yield created_user

        # No cleanup needed as internal users might not be deletable through API

async def test_create_internal_user(internal_user):
    """Tests POST /users/ (internal) endpoint."""
    assert "id" in internal_user
    assert internal_user["username"].startswith("internal_user")

async def test_get_user_by_username(client: AsyncClient, internal_user):
    """Tests GET /users/by-username/{username}/ endpoint."""
    username = internal_user["username"]
    async with AsyncClient(app=app, base_url="http://test", headers=INTERNAL_HEADERS) as internal_client:
        response = await internal_client.get(f"/api/v1/users/by-username/{username}/")
        assert response.status_code == 200
        assert response.json()["username"] == username

async def test_verify_credentials(client: AsyncClient, internal_user):
    """Tests POST /auth/verify/ endpoint."""
    creds = {"username": internal_user["username"], "password": internal_user["password"]}
    async with AsyncClient(app=app, base_url="http://test", headers=INTERNAL_HEADERS) as internal_client:
        response = await internal_client.post("/api/v1/auth/verify/", json=creds)
        assert response.status_code == 200
        response_json = response.json()
        assert response_json["valid"] is True
        assert response_json["user"]["username"] == internal_user["username"]

async def test_verify_credentials_invalid(client: AsyncClient):
    """Tests POST /auth/verify/ with invalid credentials."""
    creds = {"username": "nonexistentuser", "password": "wrongpassword"}
    async with AsyncClient(app=app, base_url="http://test", headers=INTERNAL_HEADERS) as internal_client:
        response = await internal_client.post("/api/v1/auth/verify/", json=creds)
        assert response.status_code == 200
        response_json = response.json()
        assert response_json["valid"] is False
        assert response_json["user"] is None

async def test_internal_endpoint_fails_without_header(client: AsyncClient):
    """Tests that internal endpoints are not accessible without the header."""
    response = await client.get("/api/v1/users/by-username/someuser/")
    assert response.status_code == 403

# --- Location Endpoints --- #

@pytest.fixture(scope="function")
async def location(client: AsyncClient, device):
    """Fixture to create and clean up a location for testing."""
    location_data = {
        "latitude": 10.0,
        "longitude": 20.0,
        "device_id": device["id"]
    }
    response = await client.post("/api/v1/locations/", json=location_data)
    assert response.status_code == 201
    created_location = response.json()
    
    yield created_location
    
    # Cleanup
    await client.delete(f"/api/v1/locations/{created_location['id']}/")

async def test_create_location(location):
    """Tests POST /locations/ endpoint."""
    assert "id" in location
    assert "device_id" in location

async def test_get_all_locations(client: AsyncClient):
    """Tests GET /locations/ endpoint."""
    response = await client.get("/api/v1/locations/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

async def test_get_location_by_id(client: AsyncClient, location):
    """Tests GET /locations/{location_id}/ endpoint."""
    response = await client.get(f"/api/v1/locations/{location['id']}/")
    assert response.status_code == 200
    assert response.json()["id"] == location["id"]

async def test_get_location_by_device_id(client: AsyncClient, location):
    """Tests GET /locations/device/{device_id}/ endpoint."""
    device_id = location["device_id"]
    response = await client.get(f"/api/v1/locations/device/{device_id}/")
    assert response.status_code == 200
    assert response.json()["device_id"] == device_id

async def test_update_location(client: AsyncClient, location):
    """Tests PATCH /locations/{location_id}/ endpoint."""
    update_data = {"latitude": 15.0}
    response = await client.patch(f"/api/v1/locations/{location['id']}/", json=update_data)
    assert response.status_code == 204

async def test_delete_location(client: AsyncClient, location):
    """Tests DELETE /locations/{location_id}/ endpoint."""
    location_id = location["id"]
    response = await client.delete(f"/api/v1/locations/{location_id}/")
    assert response.status_code == 204

    # Verify it's gone
    get_response = await client.get(f"/api/v1/locations/{location_id}/")
    assert get_response.status_code == 404

# --- Payment Endpoints --- #

@pytest.fixture(scope="function")
async def payment(client: AsyncClient, plan):
    """Fixture to create and clean up a payment for testing."""
    payment_data = {
        "amount": 100.50,
        "state": "completed",
        "plan_id": plan["id"]
    }
    response = await client.post("/api/v1/payments/", json=payment_data)
    assert response.status_code == 201
    created_payment = response.json()
    
    yield created_payment
    
    # Cleanup
    await client.delete(f"/api/v1/payments/{created_payment['id']}/")

async def test_create_payment(payment):
    """Tests POST /payments/ endpoint."""
    assert "id" in payment
    assert payment["state"] == "completed"

async def test_get_all_payments(client: AsyncClient):
    """Tests GET /payments/ endpoint."""
    response = await client.get("/api/v1/payments/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

async def test_get_payment_by_id(client: AsyncClient, payment):
    """Tests GET /payments/{payment_id}/ endpoint."""
    response = await client.get(f"/api/v1/payments/{payment['id']}/")
    assert response.status_code == 200
    assert response.json()["id"] == payment["id"]

async def test_update_payment(client: AsyncClient, payment):
    """Tests PATCH /payments/{payment_id}/ endpoint."""
    update_data = {"state": "refunded"}
    response = await client.patch(f"/api/v1/payments/{payment['id']}/", json=update_data)
    assert response.status_code == 200
    assert response.json()["state"] == "refunded"

async def test_delete_payment(client: AsyncClient, payment):
    """Tests DELETE /payments/{payment_id}/ endpoint."""
    payment_id = payment["id"]
    response = await client.delete(f"/api/v1/payments/{payment_id}/")
    assert response.status_code == 204

    # Verify it's gone
    get_response = await client.get(f"/api/v1/payments/{payment_id}/")
    assert get_response.status_code == 404

# --- Plan Endpoints --- #

@pytest.fixture(scope="function")
async def plan(client: AsyncClient):
    """Fixture to create and clean up a plan for testing."""
    plan_data = {
        "name": f"Test Plan {uuid.uuid4().hex[:6]}",
        "description": "A plan for testing",
        "price": 99.99,
        "duration_days": 30
    }
    response = await client.post("/api/v1/plans/", json=plan_data)
    assert response.status_code == 201
    created_plan = response.json()
    
    yield created_plan
    
    # Cleanup
    delete_response = await client.delete(f"/api/v1/plans/{created_plan['id']}/")
    assert delete_response.status_code in [204, 404]

async def test_create_plan(plan):
    """Tests POST /plans/ endpoint by using the plan fixture."""
    assert "id" in plan
    assert "name" in plan

async def test_get_all_plans(client: AsyncClient):
    """Tests GET /plans/ endpoint."""
    response = await client.get("/api/v1/plans/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

async def test_get_plan_by_id(client: AsyncClient, plan):
    """Tests GET /plans/{plan_id}/ endpoint."""
    response = await client.get(f"/api/v1/plans/{plan['id']}/")
    assert response.status_code == 200
    assert response.json()["id"] == plan["id"]

async def test_update_plan(client: AsyncClient, plan):
    """Tests PATCH /plans/{plan_id}/ endpoint."""
    update_data = {"price": 129.99}
    response = await client.patch(f"/api/v1/plans/{plan['id']}/", json=update_data)
    assert response.status_code == 200
    assert response.json()["price"] == 129.99

async def test_delete_plan(client: AsyncClient, plan):
    """Tests DELETE /plans/{plan_id}/ endpoint."""
    plan_id = plan["id"]
    response = await client.delete(f"/api/v1/plans/{plan_id}/")
    assert response.status_code == 204

    # Verify it's gone
    get_response = await client.get(f"/api/v1/plans/{plan_id}/")
    assert get_response.status_code == 404

# --- Region Endpoints --- #

@pytest.fixture(scope="function")
async def region(client: AsyncClient, country):
    """Fixture to create and clean up a region for testing."""
    region_data = {
        "name": f"Test Region {uuid.uuid4().hex[:6]}",
        "country_id": country["id"]
    }
    response = await client.post("/api/v1/regions/", json=region_data)
    assert response.status_code == 201
    created_region = response.json()
    
    yield created_region
    
    # Cleanup
    delete_response = await client.delete(f"/api/v1/regions/{created_region['id']}/")
    assert delete_response.status_code in [204, 404]

async def test_create_region(region):
    """Tests POST /regions/ endpoint by using the region fixture."""
    assert "id" in region
    assert "name" in region
    assert region["country"]["id"] is not None

async def test_get_all_regions(client: AsyncClient):
    """Tests GET /regions/ endpoint."""
    response = await client.get("/api/v1/regions/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

async def test_get_region_by_id(client: AsyncClient, region):
    """Tests GET /regions/{region_id}/ endpoint."""
    response = await client.get(f"/api/v1/regions/{region['id']}/")
    assert response.status_code == 200
    assert response.json()["id"] == region["id"]

async def test_update_region(client: AsyncClient, region):
    """Tests PATCH /regions/{region_id}/ endpoint."""
    update_data = {"name": f"Updated Region {uuid.uuid4().hex[:6]}"}
    response = await client.patch(f"/api/v1/regions/{region['id']}/", json=update_data)
    assert response.status_code == 200
    assert response.json()["name"] == update_data["name"]

async def test_delete_region(client: AsyncClient, region):
    """Tests DELETE /regions/{region_id}/ endpoint."""
    response = await client.delete(f"/api/v1/regions/{region['id']}/")
    assert response.status_code == 204

    # Verify it's gone
    get_response = await client.get(f"/api/v1/regions/{region['id']}/")
    assert get_response.status_code == 404

# --- Role Endpoints --- #

@pytest.fixture(scope="function")
async def role(client: AsyncClient):
    """Fixture to create and clean up a role for testing."""
    role_data = {
        "name": f"Test Role {uuid.uuid4().hex[:6]}",
        "description": "A role for testing"
    }
    response = await client.post("/api/v1/roles/", json=role_data)
    assert response.status_code == 201
    created_role = response.json()
    
    yield created_role
    
    # Cleanup
    delete_response = await client.delete(f"/api/v1/roles/{created_role['id']}/")
    assert delete_response.status_code in [204, 404]

async def test_create_role(role):
    """Tests POST /roles/ endpoint by using the role fixture."""
    assert "id" in role
    assert "name" in role

async def test_get_all_roles(client: AsyncClient):
    """Tests GET /roles/ endpoint."""
    response = await client.get("/api/v1/roles/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

async def test_get_role_by_id(client: AsyncClient, role):
    """Tests GET /roles/{role_id}/ endpoint."""
    response = await client.get(f"/api/v1/roles/{role['id']}/")
    assert response.status_code == 200
    assert response.json()["id"] == role["id"]

async def test_update_role(client: AsyncClient, role):
    """Tests PATCH /roles/{role_id}/ endpoint."""
    update_data = {"description": "An updated test role description"}
    response = await client.patch(f"/api/v1/roles/{role['id']}/", json=update_data)
    assert response.status_code == 200
    assert response.json()["description"] == update_data["description"]

async def test_delete_role(client: AsyncClient, role):
    """Tests DELETE /roles/{role_id}/ endpoint."""
    response = await client.delete(f"/api/v1/roles/{role['id']}/")
    assert response.status_code == 204

    # Verify it's gone
    get_response = await client.get(f"/api/v1/roles/{role['id']}/")
    assert get_response.status_code == 404

# --- SIM Endpoints --- #

@pytest.fixture(scope="function")
async def sim(client: AsyncClient, device):
    """Fixture to create and clean up a SIM for testing."""
    sim_data = {
        "device_id": device["id"],
        "icc_id": f"890123456789012345{random.randint(0, 9)}",
        "slot_index": "1",
        "operator": "Test Operator",
        "number": f"555-{uuid.uuid4().int % 1000000}",
    }
    response = await client.post("/api/v1/sims/", json=sim_data)
    assert response.status_code == 201
    created_sim = response.json()
    
    yield created_sim
    
    # Cleanup
    delete_response = await client.delete(f"/api/v1/sims/{created_sim['id']}/")
    assert delete_response.status_code in [204, 404]

async def test_create_sim(sim):
    """Tests POST /sims/ endpoint by using the sim fixture."""
    assert "id" in sim
    assert sim["device"]["id"] is not None

async def test_get_all_sims(client: AsyncClient):
    """Tests GET /sims/ endpoint."""
    response = await client.get("/api/v1/sims/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

async def test_get_sim_by_id(client: AsyncClient, sim):
    """Tests GET /sims/{sim_id}/ endpoint."""
    response = await client.get(f"/api/v1/sims/{sim['id']}/")
    assert response.status_code == 200
    assert response.json()["id"] == sim["id"]

async def test_update_sim(client: AsyncClient, sim):
    """Tests PATCH /sims/{sim_id}/ endpoint."""
    update_data = {"state": "inactive"}
    response = await client.patch(f"/api/v1/sims/{sim['id']}/", json=update_data)
    assert response.status_code == 200
    assert response.json()["state"] == update_data["state"]

async def test_delete_sim(client: AsyncClient, sim):
    """Tests DELETE /sims/{sim_id}/ endpoint."""
    response = await client.delete(f"/api/v1/sims/{sim['id']}/")
    assert response.status_code == 204

    # Verify it's gone
    get_response = await client.get(f"/api/v1/sims/{sim['id']}/")
    assert get_response.status_code == 404

# --- User Endpoints --- #

@pytest.fixture(scope="function")
async def user(client: AsyncClient, city, role):
    """Fixture to create and clean up a user for testing."""
    user_data = {
        "username": f"test_user_{uuid.uuid4().hex[:6]}",
        "password": "a_secure_password",
        "email": f"user_{uuid.uuid4().hex[:6]}@example.com",
        "dni": f"{uuid.uuid4().int % 100000000}",
        "first_name": "Test",
        "last_name": "User",
        "role_id": role["id"],
        "city_id": city["id"]
    }
    response = await client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 201
    created_user = response.json()
    
    yield created_user
    
    # Cleanup
    delete_response = await client.delete(f"/api/v1/users/{created_user['id']}/")
    assert delete_response.status_code in [204, 404]

async def test_create_user(user):
    """Tests POST /users/ endpoint by using the user fixture."""
    assert "id" in user
    assert "username" in user
    assert user["role"]["id"] is not None
    assert user["city"]["id"] is not None

async def test_get_all_users(client: AsyncClient):
    """Tests GET /users/ endpoint."""
    response = await client.get("/api/v1/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

async def test_get_user_by_id(client: AsyncClient, user):
    """Tests GET /users/{user_id}/ endpoint."""
    response = await client.get(f"/api/v1/users/{user['id']}/")
    assert response.status_code == 200
    assert response.json()["id"] == user["id"]

async def test_update_user(client: AsyncClient, user):
    """Tests PATCH /users/{user_id}/ endpoint."""
    update_data = {"first_name": f"Updated_{uuid.uuid4().hex[:4]}"}
    response = await client.patch(f"/api/v1/users/{user['id']}/", json=update_data)
    assert response.status_code == 200
    assert response.json()["first_name"] == update_data["first_name"]

async def test_delete_user(client: AsyncClient, user):
    """Tests DELETE /users/{user_id}/ endpoint."""
    response = await client.delete(f"/api/v1/users/{user['id']}/")
    assert response.status_code == 204

    # Verify it's gone
    get_response = await client.get(f"/api/v1/users/{user['id']}/")
    assert get_response.status_code == 404

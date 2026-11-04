import app as app_module


def test_home_page_loads():
    client = app_module.app.test_client()
    response = client.get("/")
    assert response.status_code == 200


def test_admin_page_loads():
    client = app_module.app.test_client()
    response = client.get("/admin")
    assert response.status_code == 200

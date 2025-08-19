from fastapi import status

def test_get_user(client, admin_user, override_get_current_user):
    response = client.get(f"/user/{admin_user.id}")
    assert response.status_code == 200
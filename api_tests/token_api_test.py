import json

from conftest import auth_headers, requires_env


@requires_env("API_TOKEN")
def test__create_token(base_url, session, token_name, bucket_name):
    """Should create a token"""
    resp = session.post(f'{base_url}/b/{bucket_name}')
    assert resp.status_code == 200

    permissions = {
        "full_access": True,
        "read": [bucket_name],
        "write": [bucket_name],
    }

    resp = session.post(f'{base_url}/tokens/{token_name}', json=permissions)
    assert resp.status_code == 200
    assert resp.headers['content-type'] == "application/json"
    assert "token-" in json.loads(resp.content)["value"]


@requires_env("API_TOKEN")
def test__create_token_exist(base_url, session, token_name):
    """Should return 409 if a token already exists"""
    permissions = {}

    resp = session.post(f'{base_url}/tokens/{token_name}', json=permissions)
    assert resp.status_code == 200
    resp = session.post(f'{base_url}/tokens/{token_name}', json={})
    assert resp.status_code == 409
    assert resp.headers["x-reduct-error"] == f"Token '{token_name}' already exists"


@requires_env("API_TOKEN")
def test__creat_token_with_full_access(base_url, session, token_name, token_without_permissions):
    """Needs full access to create a token"""
    permissions = {}

    resp = session.post(f'{base_url}/tokens/{token_name}', json=permissions, headers=auth_headers(''))
    assert resp.status_code == 401

    resp = session.post(f'{base_url}/tokens/{token_name}', json=permissions,
                        headers=auth_headers(token_without_permissions))
    assert resp.status_code == 403
    assert resp.headers["x-reduct-error"] == "Token doesn't have full access"


@requires_env("API_TOKEN")
def test__list_tokens(base_url, session, token_name):
    """Should list all tokens"""
    permissions = {}

    resp = session.post(f'{base_url}/tokens/{token_name}', json=permissions)
    assert resp.status_code == 200

    resp = session.get(f'{base_url}/tokens')
    assert resp.status_code == 200
    assert resp.headers['content-type'] == "application/json"
    assert token_name in [t["name"] for t in json.loads(resp.content)["tokens"]]


@requires_env("API_TOKEN")
def test__list_token_with_full_access(base_url, session, token_without_permissions):
    """Needs full access to list tokens"""
    resp = session.get(f'{base_url}/tokens', headers=auth_headers(''))
    assert resp.status_code == 401

    resp = session.get(f'{base_url}/tokens', headers=auth_headers(token_without_permissions))
    assert resp.status_code == 403
    assert resp.headers["x-reduct-error"] == "Token doesn't have full access"


@requires_env("API_TOKEN")
def test__get_token(base_url, session, bucket_name, token_name):
    """Should show a token name and permissions"""
    resp = session.post(f'{base_url}/b/{bucket_name}')
    assert resp.status_code == 200

    permissions = {
        "full_access": True,
        "read": [bucket_name],
        "write": [bucket_name],
    }

    resp = session.post(f'{base_url}/tokens/{token_name}', json=permissions)
    assert resp.status_code == 200
    created_at = json.loads(resp.content)["created_at"]

    resp = session.get(f'{base_url}/tokens/{token_name}')
    assert resp.status_code == 200
    assert resp.headers['content-type'] == "application/json"
    assert json.loads(resp.content) == {
        "name": token_name,
        "created_at": created_at,
        "value": "",
        "permissions": permissions,
    }


@requires_env("API_TOKEN")
def test__get_token_not_found(base_url, session):
    """Should return 404 if a token does not exist"""
    resp = session.get(f'{base_url}/tokens/token-not-found')
    assert resp.status_code == 404
    assert resp.headers["x-reduct-error"] == "Token 'token-not-found' doesn't exist"


@requires_env("API_TOKEN")
def test__get_token_with_full_access(base_url, session, token_without_permissions):
    """Needs full access to get a token"""
    resp = session.get(f'{base_url}/tokens/token-name', headers=auth_headers(''))
    assert resp.status_code == 401

    resp = session.get(f'{base_url}/tokens/token-name', headers=auth_headers(token_without_permissions))
    assert resp.status_code == 403
    assert resp.headers["x-reduct-error"] == "Token doesn't have full access"


@requires_env("API_TOKEN")
def test__delete_token(base_url, session, token_name):
    """Should delete a token"""
    permissions = {}

    resp = session.post(f'{base_url}/tokens/{token_name}', json=permissions)
    assert resp.status_code == 200

    resp = session.delete(f'{base_url}/tokens/{token_name}')
    assert resp.status_code == 200

    resp = session.get(f'{base_url}/tokens')
    assert resp.status_code == 200
    assert token_name not in [t["name"] for t in json.loads(resp.content)["tokens"]]


@requires_env("API_TOKEN")
def test__delete_token_not_found(base_url, session):
    """Should return 404 if a token does not exist"""
    resp = session.delete(f'{base_url}/tokens/token-not-found')
    assert resp.status_code == 404
    assert resp.headers["x-reduct-error"] == "Token 'token-not-found' doesn't exist"


@requires_env("API_TOKEN")
def test__delete_token_with_full_access(base_url, session, token_without_permissions):
    """Needs full access to delete a token"""
    resp = session.delete(f'{base_url}/tokens/token-name', headers=auth_headers(''))
    assert resp.status_code == 401

    resp = session.delete(f'{base_url}/tokens/token-name', headers=auth_headers(token_without_permissions))
    assert resp.status_code == 403
    assert resp.headers["x-reduct-error"] == "Token doesn't have full access"

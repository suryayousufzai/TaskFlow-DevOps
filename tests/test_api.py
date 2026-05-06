import pytest
import json
from app import create_app, db


@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


# ── HEALTH ──────────────────────────────────────────────────────
def test_health(client):
    r = client.get('/api/health')
    assert r.status_code == 200
    assert r.get_json()['status'] == 'ok'


# ── CREATE ──────────────────────────────────────────────────────
def test_create_task(client):
    r = client.post('/api/tasks', json={'title': 'Buy milk'})
    assert r.status_code == 201
    data = r.get_json()
    assert data['title'] == 'Buy milk'
    assert data['completed'] is False
    assert data['priority'] == 'medium'


def test_create_task_no_title(client):
    r = client.post('/api/tasks', json={'description': 'oops'})
    assert r.status_code == 400


def test_create_task_empty_title(client):
    r = client.post('/api/tasks', json={'title': '   '})
    assert r.status_code == 400


def test_create_task_with_all_fields(client):
    r = client.post('/api/tasks', json={
        'title': 'Submit report',
        'description': 'Q3 report',
        'priority': 'high',
        'category': 'work',
        'due_date': '2025-12-31T23:59:00',
    })
    assert r.status_code == 201
    data = r.get_json()
    assert data['priority'] == 'high'
    assert data['category'] == 'work'


# ── READ ──────────────────────────────────────────────────────
def test_get_tasks_empty(client):
    r = client.get('/api/tasks')
    assert r.status_code == 200
    assert r.get_json() == []


def test_get_tasks(client):
    client.post('/api/tasks', json={'title': 'Task A'})
    client.post('/api/tasks', json={'title': 'Task B'})
    r = client.get('/api/tasks')
    assert len(r.get_json()) == 2


def test_get_single_task(client):
    c = client.post('/api/tasks', json={'title': 'Find me'})
    task_id = c.get_json()['id']
    r = client.get(f'/api/tasks/{task_id}')
    assert r.status_code == 200
    assert r.get_json()['title'] == 'Find me'


def test_get_nonexistent_task(client):
    r = client.get('/api/tasks/9999')
    assert r.status_code == 404


# ── UPDATE ──────────────────────────────────────────────────────
def test_update_task(client):
    c = client.post('/api/tasks', json={'title': 'Old title'})
    task_id = c.get_json()['id']
    r = client.put(f'/api/tasks/{task_id}', json={'title': 'New title', 'priority': 'high'})
    assert r.status_code == 200
    data = r.get_json()
    assert data['title'] == 'New title'
    assert data['priority'] == 'high'


def test_update_bad_priority(client):
    c = client.post('/api/tasks', json={'title': 'Task'})
    task_id = c.get_json()['id']
    r = client.put(f'/api/tasks/{task_id}', json={'priority': 'urgent'})
    assert r.status_code == 400


# ── TOGGLE ──────────────────────────────────────────────────────
def test_toggle_task(client):
    c = client.post('/api/tasks', json={'title': 'Toggle me'})
    task_id = c.get_json()['id']
    r = client.patch(f'/api/tasks/{task_id}/toggle')
    assert r.get_json()['completed'] is True
    r2 = client.patch(f'/api/tasks/{task_id}/toggle')
    assert r2.get_json()['completed'] is False


# ── DELETE ──────────────────────────────────────────────────────
def test_delete_task(client):
    c = client.post('/api/tasks', json={'title': 'Delete me'})
    task_id = c.get_json()['id']
    r = client.delete(f'/api/tasks/{task_id}')
    assert r.status_code == 200
    r2 = client.get(f'/api/tasks/{task_id}')
    assert r2.status_code == 404


# ── STATS ──────────────────────────────────────────────────────
def test_stats(client):
    client.post('/api/tasks', json={'title': 'T1', 'priority': 'high'})
    client.post('/api/tasks', json={'title': 'T2', 'priority': 'low'})
    t3 = client.post('/api/tasks', json={'title': 'T3'}).get_json()
    client.patch(f'/api/tasks/{t3["id"]}/toggle')  # complete one

    r = client.get('/api/stats')
    assert r.status_code == 200
    data = r.get_json()
    assert data['total'] == 3
    assert data['completed'] == 1
    assert data['pending'] == 2
    assert data['completion_rate'] == 33.3


# ── FILTER ──────────────────────────────────────────────────────
def test_filter_by_priority(client):
    client.post('/api/tasks', json={'title': 'H', 'priority': 'high'})
    client.post('/api/tasks', json={'title': 'L', 'priority': 'low'})
    r = client.get('/api/tasks?priority=high')
    assert len(r.get_json()) == 1
    assert r.get_json()[0]['priority'] == 'high'

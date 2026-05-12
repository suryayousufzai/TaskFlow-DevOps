# app/api.py
# all the API routes live here
# these return JSON data (not HTML pages)
# the frontend javascript calls these to get/create/update/delete tasks

from flask import Blueprint, jsonify, request
from app import db
from app.models import Task
from datetime import datetime

api = Blueprint('api', __name__)


# small helper function so i don't repeat jsonify({'error': ...}) everywhere
def error(msg, code=400):
    return jsonify({'error': msg}), code


# GET /api/tasks
# returns all tasks, with optional filters via query params
# example: /api/tasks?priority=high&completed=false
@api.route('/tasks', methods=['GET'])
def get_tasks():
    # read optional filter params from the url
    priority  = request.args.get('priority')
    category  = request.args.get('category')
    completed = request.args.get('completed')

    # start with all tasks, then narrow down based on filters
    query = Task.query
    if priority:
        query = query.filter_by(priority=priority)
    if category:
        query = query.filter_by(category=category)
    if completed is not None:
        # the url param comes in as a string so i need to convert it to bool
        query = query.filter_by(completed=(completed.lower() == 'true'))

    # sort newest first
    tasks = query.order_by(Task.created_at.desc()).all()
    return jsonify([t.to_dict() for t in tasks])


# GET /api/tasks/<id>
# returns a single task by id
# get_or_404 automatically returns a 404 error if the task doesn't exist
@api.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = Task.query.get_or_404(task_id)
    return jsonify(task.to_dict())


# POST /api/tasks
# creates a new task
# expects JSON in the request body with at least a "title"
@api.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()

    # make sure they actually sent a title
    if not data or not data.get('title', '').strip():
        return error('Title is required')

    # parse the due date if they sent one
    due = None
    if data.get('due_date'):
        try:
            due = datetime.fromisoformat(data['due_date'])
        except ValueError:
            return error('Invalid due_date format. Use ISO 8601.')

    # create the task object and save it to the database
    task = Task(
        title=data['title'].strip(),
        description=data.get('description', ''),
        priority=data.get('priority', 'medium'),
        category=data.get('category', 'general'),
        due_date=due,
    )
    db.session.add(task)
    db.session.commit()

    # 201 means "created" - slightly different from the usual 200 "ok"
    return jsonify(task.to_dict()), 201


# PUT /api/tasks/<id>
# updates an existing task - only updates the fields that are sent
@api.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()

    if not data:
        return error('No data provided')

    # only update fields that were actually included in the request
    # i check each one individually so partial updates work fine
    if 'title' in data:
        if not data['title'].strip():
            return error('Title cannot be empty')
        task.title = data['title'].strip()

    if 'description' in data:
        task.description = data['description']

    if 'completed' in data:
        task.completed = bool(data['completed'])

    if 'priority' in data:
        if data['priority'] not in ('low', 'medium', 'high'):
            return error('Priority must be low, medium, or high')
        task.priority = data['priority']

    if 'category' in data:
        task.category = data['category']

    if 'due_date' in data:
        if data['due_date']:
            try:
                task.due_date = datetime.fromisoformat(data['due_date'])
            except ValueError:
                return error('Invalid due_date format')
        else:
            task.due_date = None  # allow clearing the due date by sending null

    db.session.commit()
    return jsonify(task.to_dict())


# DELETE /api/tasks/<id>
# deletes a task permanently
@api.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': f'task {task_id} deleted'}), 200


# PATCH /api/tasks/<id>/toggle
# flips the completed status without needing to send the full task
# much easier than doing a full PUT just to check/uncheck a task
@api.route('/tasks/<int:task_id>/toggle', methods=['PATCH'])
def toggle_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed = not task.completed  # flip it
    db.session.commit()
    return jsonify(task.to_dict())


# GET /api/stats
# returns some summary numbers about all the tasks
# used by the dashboard on the frontend
@api.route('/stats', methods=['GET'])
def get_stats():
    total     = Task.query.count()
    completed = Task.query.filter_by(completed=True).count()
    pending   = total - completed

    # count pending tasks grouped by priority
    by_priority = {
        p: Task.query.filter_by(priority=p, completed=False).count()
        for p in ('low', 'medium', 'high')
    }

    # count tasks grouped by category
    categories = db.session.query(Task.category, db.func.count(Task.id)) \
        .group_by(Task.category).all()

    return jsonify({
        'total':           total,
        'completed':       completed,
        'pending':         pending,
        'completion_rate': round((completed / total * 100), 1) if total else 0,
        'by_priority':     by_priority,
        'by_category':     {c: n for c, n in categories},
    })


# GET /api/health
# just a simple check to confirm the api is running
# docker and the ci pipeline use this to know the app started up correctly
@api.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'service': 'taskflow-api'})

from flask import Blueprint, jsonify, request
from app import db
from app.models import Task
from datetime import datetime

api = Blueprint('api', __name__)


def error(msg, code=400):
    return jsonify({'error': msg}), code


@api.route('/tasks', methods=['GET'])
def get_tasks():
    priority = request.args.get('priority')
    category = request.args.get('category')
    completed = request.args.get('completed')

    query = Task.query
    if priority:
        query = query.filter_by(priority=priority)
    if category:
        query = query.filter_by(category=category)
    if completed is not None:
        query = query.filter_by(completed=(completed.lower() == 'true'))

    tasks = query.order_by(Task.created_at.desc()).all()
    return jsonify([t.to_dict() for t in tasks])


@api.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = Task.query.get_or_404(task_id)
    return jsonify(task.to_dict())


@api.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    if not data or not data.get('title', '').strip():
        return error('Title is required')

    due = None
    if data.get('due_date'):
        try:
            due = datetime.fromisoformat(data['due_date'])
        except ValueError:
            return error('Invalid due_date format. Use ISO 8601.')

    task = Task(
        title=data['title'].strip(),
        description=data.get('description', ''),
        priority=data.get('priority', 'medium'),
        category=data.get('category', 'general'),
        due_date=due,
    )
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201


@api.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    if not data:
        return error('No data provided')

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
            task.due_date = None

    db.session.commit()
    return jsonify(task.to_dict())


@api.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': f'Task {task_id} deleted'}), 200


@api.route('/tasks/<int:task_id>/toggle', methods=['PATCH'])
def toggle_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed = not task.completed
    db.session.commit()
    return jsonify(task.to_dict())


@api.route('/stats', methods=['GET'])
def get_stats():
    total = Task.query.count()
    completed = Task.query.filter_by(completed=True).count()
    pending = total - completed
    by_priority = {
        p: Task.query.filter_by(priority=p, completed=False).count()
        for p in ('low', 'medium', 'high')
    }
    categories = db.session.query(Task.category, db.func.count(Task.id))\
        .group_by(Task.category).all()
    return jsonify({
        'total': total,
        'completed': completed,
        'pending': pending,
        'completion_rate': round((completed / total * 100), 1) if total else 0,
        'by_priority': by_priority,
        'by_category': {c: n for c, n in categories},
    })


@api.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'service': 'taskflow-api'})

# app/models.py
# Database models - defines the structure of our database tables
# SQLAlchemy lets us work with the database using Python classes
# instead of writing raw SQL queries

from app import db
from datetime import datetime, timezone


class Task(db.Model):
    """
    Task model - represents one task/to-do item in the database.
    Each attribute here becomes a column in the 'tasks' table.
    """
    __tablename__ = 'tasks'

    # primary key - auto increments for each new task
    id = db.Column(db.Integer, primary_key=True)

    # main task fields
    title       = db.Column(db.String(200), nullable=False)   # required field
    description = db.Column(db.Text, default='')              # optional extra info
    completed   = db.Column(db.Boolean, default=False)        # done or not done

    # priority can be 'low', 'medium', or 'high'
    priority = db.Column(db.String(10), default='medium')

    # category like 'work', 'personal', 'school' etc.
    category = db.Column(db.String(50), default='general')

    # optional due date for the task
    due_date = db.Column(db.DateTime, nullable=True)

    # timestamps - set automatically when created or updated
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self):
        """
        Convert this task object to a plain dictionary.
        This is needed because Flask can't return Python objects as JSON directly.
        """
        return {
            'id':          self.id,
            'title':       self.title,
            'description': self.description,
            'completed':   self.completed,
            'priority':    self.priority,
            'category':    self.category,
            # convert datetime to string (ISO format) for JSON
            'due_date':    self.due_date.isoformat() if self.due_date else None,
            'created_at':  self.created_at.isoformat() if self.created_at else None,
            'updated_at':  self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        # this is just for debugging - shows up when you print a Task object
        return f'<Task {self.id}: {self.title}>'

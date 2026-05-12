# app/models.py
# this file defines what the database looks like
# each class = one table, each attribute = one column
# sqlalchemy lets me work with the database using python objects
# so i don't have to write raw SQL (which is nice)

from app import db
from datetime import datetime, timezone


class Task(db.Model):
    __tablename__ = 'tasks'

    # every row needs a unique id, sqlalchemy handles the auto-increment for me
    id = db.Column(db.Integer, primary_key=True)

    # the actual task data
    title       = db.Column(db.String(200), nullable=False)  # required, can't be empty
    description = db.Column(db.Text, default='')             # optional, defaults to empty string
    completed   = db.Column(db.Boolean, default=False)       # starts as not done

    # priority is one of: 'low', 'medium', 'high'
    priority = db.Column(db.String(10), default='medium')

    # category like 'work', 'personal', 'school', whatever the user wants
    category = db.Column(db.String(50), default='general')

    # due date is optional, so nullable=True
    due_date = db.Column(db.DateTime, nullable=True)

    # these timestamps get set automatically - i don't have to do it manually
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)  # updates every time i save the row
    )

    def to_dict(self):
        # flask can't turn python objects into JSON automatically
        # so i convert the task to a plain dictionary first
        # also need to convert datetime objects to strings for JSON
        return {
            'id':          self.id,
            'title':       self.title,
            'description': self.description,
            'completed':   self.completed,
            'priority':    self.priority,
            'category':    self.category,
            'due_date':    self.due_date.isoformat() if self.due_date else None,
            'created_at':  self.created_at.isoformat() if self.created_at else None,
            'updated_at':  self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        # just for debugging - makes print(task) show something useful
        return f'<Task {self.id}: {self.title}>'

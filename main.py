import argparse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, Student, Group, Teacher, Subject, Grade

engine = create_engine('postgresql://postgres:password@localhost:5432/base_hw_06')
Session = sessionmaker(bind=engine)
session = Session()

def create_record(model, **kwargs):
    record = model(**kwargs)
    session.add(record)
    session.commit()
    print(f"Created {model.__name__} with id {record.id}")

def list_records(model):
    records = session.query(model).all()
    for record in records:
        print(record.__dict__)

def update_record(model, id, **kwargs):
    record = session.query(model).filter_by(id=id).first()
    if record:
        for key, value in kwargs.items():
            setattr(record, key, value)
        session.commit()
        print(f"Updated {model.__name__} with id {id}")
    else:
        print(f"{model.__name__} with id {id} not found")

def remove_record(model, id):
    record = session.query(model).filter_by(id=id).first()
    if record:
        session.delete(record)
        session.commit()
        print(f"Removed {model.__name__} with id {id}")
    else:
        print(f"{model.__name__} with id {id} not found")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CRUD operations')
    parser.add_argument('-a', '--action', choices=['create', 'list', 'update', 'remove'], required=True)
    parser.add_argument('-m', '--model', choices=['Student', 'Group', 'Teacher', 'Subject', 'Grade'], required=True)
    parser.add_argument('--id', type=int)
    parser.add_argument('-n', '--name', type=str)

    args = parser.parse_args()

    model_mapping = {
        'Student': Student,
        'Group': Group,
        'Teacher': Teacher,
        'Subject': Subject,
        'Grade': Grade,
    }

    model = model_mapping[args.model]

    if args.action == 'create':
        create_record(model, name=args.name)
    elif args.action == 'list':
        list_records(model)
    elif args.action == 'update':
        update_record(model, args.id, name=args.name)
    elif args.action == 'remove':
        remove_record(model, args.id)

    session.close()
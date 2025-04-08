from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import random

from models import Base, Student, Group, Teacher, Subject, Grade

engine = create_engine('postgresql://postgres:mysecretpassword@localhost:5432/postgres')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

fake = Faker('uk_UA')  # Use Ukrainian locale for names and other data

groups = [Group(name=f'Група {chr(ord("А") + i)}-{random.randint(100, 103)}') for i in range(3)]
session.add_all(groups)
session.commit()

teachers = [Teacher(name=fake.name()) for _ in range(random.randint(3, 5))]
session.add_all(teachers)
session.commit()

subjects = []
subject_names = [
    "Математика", "Фізика", "Хімія", "Інформатика", "Історія України",
    "Англійська мова", "Література", "Біологія"
]
selected_subjects = random.sample(subject_names, random.randint(5, 8))
for subject_name in selected_subjects:
    subjects.append(Subject(name=subject_name, teacher_id=random.choice(teachers).id))
session.add_all(subjects)
session.commit()

students = [Student(name=fake.name()) for _ in range(random.randint(30, 50))]
session.add_all(students)
session.commit()

for student in students:
    num_grades = random.randint(10, 20)
    assigned_subjects = random.sample(subjects, random.randint(3, len(subjects)))
    for _ in range(num_grades):
        subject = random.choice(assigned_subjects)
        grade = Grade(
            student_id=student.id,
            subject_id=subject.id,
            grade=random.randint(60, 100),
            date_received=fake.date_between(start_date='-1y', end_date='today')
        )
        session.add(grade)
    student.groups.append(random.choice(groups))

session.commit()
session.close()
from sqlalchemy import create_engine, func, desc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from models import Student, Group, Teacher, Subject, Grade

engine = create_engine('postgresql://postgres:mysecretpassword@localhost:5432/postgres')
Session = sessionmaker(bind=engine)
session = Session()

def select_1():
    """Знайти 5 студентів із найбільшим середнім балом з усіх предметів."""
    return session.query(Student.name, func.avg(Grade.grade).label('average_grade')) \
        .join(Grade).group_by(Student.id).order_by(desc('average_grade')).limit(5).all()

def select_2(subject_name):
    """Знайти студента із найвищим середнім балом з певного предмета."""
    return session.query(Student.name, func.avg(Grade.grade).label('average_grade')) \
        .join(Grade).join(Subject).filter(Subject.name == subject_name).group_by(Student.id).order_by(desc('average_grade')).first()

def select_3(subject_name):
    """Знайти середній бал у групах з певного предмета."""
    return session.query(Group.name, func.avg(Grade.grade).label('average_grade')) \
        .join(Student).join(Grade).join(Subject).filter(Subject.name == subject_name).group_by(Group.id).all()

def select_4():
    """Знайти середній бал на потоці (по всій таблиці оцінок)."""
    return session.query(func.avg(Grade.grade).label('average_grade')).scalar()

def select_5(teacher_name):
    """Знайти які курси читає певний викладач."""
    return session.query(Subject.name).join(Teacher).filter(Teacher.name == teacher_name).all()

def select_6(group_name):
    """Знайти список студентів у певній групі."""
    return session.query(Student.name).join(Student.groups).join(Group).filter(Group.name == group_name).all()

def select_7(group_name, subject_name):
    """Знайти оцінки студентів у окремій групі з певного предмета."""
    return session.query(Student.name, Grade.grade).join(Student.groups).join(Group).join(Grade).join(Subject) \
        .filter(Group.name == group_name, Subject.name == subject_name).all()

def select_8(teacher_name):
    """Знайти середній бал, який ставить певний викладач зі своїх предметів."""
    return session.query(func.avg(Grade.grade).label('average_grade')) \
        .join(Subject).join(Teacher).filter(Teacher.name == teacher_name).scalar()

def select_9(student_name):
    """Знайти список курсів, які відвідує певний студент."""
    return session.query(Subject.name).join(Grade).join(Student).filter(Student.name == student_name).distinct().all()

def select_10(student_name, teacher_name):
    """Список курсів, які певному студенту читає певний викладач."""
    return session.query(Subject.name).join(Grade).join(Student).join(Subject).join(Teacher) \
        .filter(Student.name == student_name, Teacher.name == teacher_name).distinct().all()

# Додаткові запити
def select_11(teacher_name, student_name):
    """Середній бал, який певний викладач ставить певному студентові."""
    return session.query(func.avg(Grade.grade).label('average_grade')) \
        .join(Subject).join(Teacher).join(Student).filter(Teacher.name == teacher_name, Student.name == student_name).scalar()

def select_12(group_name, subject_name):
    """Оцінки студентів у певній групі з певного предмета на останньому занятті."""
    subquery = session.query(func.max(Grade.date_received).label('max_date')) \
        .join(Student).join(Student.groups).join(Group) \
        .filter(Group.name == group_name, Grade.subject_id == Subject.id) \
        .group_by(Grade.subject_id).scalar_subquery()
    return session.query(Student.name, Grade.grade, Grade.date_received, Subject.name) \
        .join(Student).join(Student.groups).join(Group).join(Subject).join(Grade) \
        .filter(Group.name == group_name, Subject.name == subject_name, Grade.date_received == subquery).all()

if __name__ == '__main__':
    print("Топ 5 студентів за середнім балом:")
    for student, avg_grade in select_1():
        print(f"{student}: {avg_grade:.2f}")

    print("\nСтудент з найвищим середнім балом з математики:")
    result_2 = select_2("Математика")
    if result_2:
        print(f"{result_2.name}: {result_2.average_grade:.2f}")
    else:
        print("Предмет Математика не знайдено.")

    print("\nСередній бал у групах з фізики:")
    for group, avg_grade in select_3("Фізика"):
        print(f"{group}: {avg_grade:.2f}")

    print("\nСередній бал на потоці:")
    avg_overall = select_4()
    if avg_overall is not None:
        print(f"{avg_overall:.2f}")
    else:
        print("Немає оцінок у базі даних.")

    teacher_name = session.query(Teacher.name).first()
    if teacher_name:
        print(f"\nКурси, які читає {teacher_name[0]}:")
        for subject in select_5(teacher_name[0]):
            print(subject.name)

    group_name = session.query(Group.name).first()
    if group_name:
        print(f"\nСтуденти в групі {group_name[0]}:")
        for student in select_6(group_name[0]):
            print(student.name)

    if group_name and "Інформатика" in [sub.name for sub in session.query(Subject).all()]:
        print(f"\nОцінки студентів у групі {group_name[0]} з інформатики:")
        for student, grade in select_7(group_name[0], "Інформатика"):
            print(f"{student}: {grade}")

    if teacher_name:
        avg_teacher_grade = select_8(teacher_name[0])
        if avg_teacher_grade is not None:
            print(f"\nСередній бал, який ставить {teacher_name[0]}: {avg_teacher_grade:.2f}")

    student_name = session.query(Student.name).first()
    if student_name:
        print(f"\nКурси, які відвідує {student_name[0]}:")
        for subject in select_9(student_name[0]):
            print(subject.name)

    if student_name and teacher_name:
        print(f"\nКурси, які {student_name[0]} читає {teacher_name[0]}:")
        for subject in select_10(student_name[0], teacher_name[0]):
            print(subject.name)

    if teacher_name and student_name:
        avg_teacher_student_grade = select_11(teacher_name[0], student_name[0])
        if avg_teacher_student_grade is not None:
            print(f"\nСередній бал, який {teacher_name[0]} ставить {student_name[0]}: {avg_teacher_student_grade:.2f}")

    if group_name and "Хімія" in [sub.name for sub in session.query(Subject).all()]:
        print(f"\nОцінки студентів у групі {group_name[0]} з хімії на останньому занятті:")
        for student, grade, date, subject in select_12(group_name[0], "Хімія"):
            print(f"{student}: {grade} ({date.strftime('%Y-%m-%d')}) - {subject}")

    session.close()
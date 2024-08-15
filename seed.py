import uuid
from faker import Faker
from datetime import datetime, timedelta
from app import app, db
from models import (ExamCategory, User, Exams, SubCategory, Subscription, Topic, 
                    UserExamResult, Question)
import bcrypt

fake = Faker()

def seed_database():
    print('Deleting existing data...')
    UserExamResult.query.delete()
    Question.query.delete()
    Exams.query.delete()
    Topic.query.delete()
    SubCategory.query.delete()
    ExamCategory.query.delete()
    Subscription.query.delete()
    User.query.delete()
    db.session.commit()

    # Exam Categories
    exam_categories = []
    for _ in range(5):
        exam_category = ExamCategory(
            id=uuid.uuid4(),
            name=fake.unique.word(),
            description=fake.text()
        )
        exam_categories.append(exam_category)
        db.session.add(exam_category)

    db.session.commit()

    # Users
    users = []
    # Admin user
    print('Adding admin user...')
    admin_password = '123'
    hashed_admin_password = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt())
    admin = User(
        id=uuid.uuid4(),
        username='steve',
        email='steve@gmail.com',
        password=hashed_admin_password.decode('utf-8'),
        confirmed_email=True,
        role='admin',
        referral_code=str(uuid.uuid4()),
        created_at=datetime.utcnow()
    )
    users.append(admin)
    db.session.add(admin)

    # Regular users
    print('Adding users...')
    for _ in range(10):
        password = fake.password()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user = User(
            id=uuid.uuid4(),
            username=fake.unique.user_name(),
            email=fake.unique.email(),
            password=hashed_password.decode('utf-8'),
            confirmed_email=fake.boolean(),
            role='user',
            referral_code=str(uuid.uuid4()),
            created_at=datetime.utcnow()
        )
        users.append(user)
        db.session.add(user)

    db.session.commit()

    # Subcategories
    print('Adding subcategories...')
    subcategories = []
    for category in exam_categories:
        for _ in range(3):
            sub_category = SubCategory(
                id=uuid.uuid4(),
                name=fake.unique.word(),
                exam_category_id=category.id
            )
            subcategories.append(sub_category)
            db.session.add(sub_category)

    db.session.commit()

    # Topics
    print('Adding topics...')
    topics = []
    used_topic_names = set()
    for subcategory in subcategories:
        for _ in range(2):
            while True:
                name = fake.unique.word()
                if name not in used_topic_names:
                    used_topic_names.add(name)
                    break
            
            topic = Topic(
                id=uuid.uuid4(),
                name=name,
                sub_category_id=subcategory.id
            )
            topics.append(topic)
            db.session.add(topic)

    db.session.commit()

    # Exams
    exams = []
    print('Adding exams...')
    for _ in range(10):
        exam = Exams(
            id=uuid.uuid4(),
            exam_name=fake.unique.word(),
            category=fake.word(),
            subcategory=fake.word(),
            createdBy=fake.name(),
            createdOn=fake.date_time_this_year().strftime("%Y-%m-%d %H:%M:%S"),
            exam_duration=fake.random_int(min=30, max=180),
            examiner_id=fake.random.choice([u.id for u in users])
        )
        exams.append(exam)
        db.session.add(exam)

    db.session.commit()

    # Questions
    print('Adding question...')
    for exam in exams:
        for _ in range(5):
            question = Question(
                id=uuid.uuid4(),
                question_text=fake.sentence(),
                choice1=fake.word(),
                choice2=fake.word(),
                choice3=fake.word(),
                choice4=fake.word(),
                isChoice=fake.boolean(),
                answer=fake.word(),
                exam_id=exam.id,
                topic_id=fake.random.choice([t.id for t in topics]) if topics else None
            )
            db.session.add(question)

    db.session.commit()

    # Subscriptions
    print('Adding subscriptions....')
    for user in users:
        subscription = Subscription(
            id=uuid.uuid4(),
            type=fake.word(),
            amount=fake.pyfloat(min_value=10, max_value=1000, right_digits=2),
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=365),
            user_id=user.id
        )
        db.session.add(subscription)

    db.session.commit()

    # User Exam Results
    print('Adding user-exam results ...')
    for user in users:
        user_exam_result = UserExamResult(
            id=uuid.uuid4(),
            user_id=user.id,
            exam_id=fake.random.choice([e.id for e in exams]),
            grade=fake.pyfloat(min_value=0, max_value=100, right_digits=2)
        )
        db.session.add(user_exam_result)

    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        print("Seeding database...")
        seed_database()
        print("Database seeding completed.")
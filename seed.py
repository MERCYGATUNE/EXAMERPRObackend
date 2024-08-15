import uuid
from faker import Faker
from datetime import datetime, timedelta
from app import app, db
from models import (ExamCategory, User, Exams, SubCategory, Subscription, Topic, 
                                   UserExamResult, Question)
import bcrypt

fake = Faker()

def seed_database():
    # Exam Categories
    for _ in range(5):
        exam_category = ExamCategory(
            id=uuid.uuid4(),
            name=fake.word(),
            description=fake.text()
        )
        db.session.add(exam_category)

    db.session.commit()

    #Addis Steve as administrator
    password = '123'
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    admin = User(
        id=uuid.uuid4(),
        username='steve',
        email='steve@gmail.com',
        password=hashed_password.decode('utf-8'),
        confirmed_email=True,
        role='admin',
        referral_code=fake.uuid4(),
        created_at=datetime.now()
    )
    db.session.add(admin)
    db.session.commit()

    # Users
    for _ in range(10):
        password = fake.password()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user = User(
            id=uuid.uuid4(),
            username=fake.user_name(),
            email=fake.email(),
            password=hashed_password.decode('utf-8'),
            confirmed_email=fake.boolean(),
            role=fake.word(),
            referral_code=fake.uuid4(),
            created_at=datetime.now()
        )
        db.session.add(user)

    db.session.commit()

    # Subcategories
    exam_categories = ExamCategory.query.all()
    for category in exam_categories:
        for _ in range(3):
            sub_category = SubCategory(
                id=uuid.uuid4(),
                name=fake.word(),
                exam_category_id=category.id
            )
            db.session.add(sub_category)

    db.session.commit()

    # Topics
    subcategories = SubCategory.query.all()
    for subcategory in subcategories:
        for _ in range(2):
            topic = Topic(
                id=uuid.uuid4(),
                name=fake.word(),
                sub_category_id=subcategory.id
            )
            db.session.add(topic)

    db.session.commit()

    # Exams
    users = User.query.all()
    for _ in range(10):
        exam = Exams(
            id=uuid.uuid4(),
            exam_name=fake.word(),
            category=fake.word(),
            subcategory=fake.word(),
            createdBy=fake.name(),
            createdOn=datetime.now(),
            exam_duration=fake.random_int(min=30, max=180),
            examiner_id=fake.random.choice([u.id for u in users])
        )
        db.session.add(exam)

    db.session.commit()

    # Questions
    exams = Exams.query.all()
    topics = Topic.query.all()
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
    for user in users:
        subscription = Subscription(
            id=uuid.uuid4(),
            type=fake.word(),
            amount=fake.random_number(digits=5),
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=365),
            user_id=user.id
        )
        db.session.add(subscription)

    db.session.commit()

    # User Exam Results
    for user in users:
        user_exam_result = UserExamResult(
            id=uuid.uuid4(),
            user_id=user.id,
            exam_id=fake.random.choice([e.id for e in exams]),
            grade=fake.random_int(min=0, max=100)
        )
        db.session.add(user_exam_result)

    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        print("added bruv")
        seed_database()

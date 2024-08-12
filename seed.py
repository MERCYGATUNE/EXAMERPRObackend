import uuid
from faker import Faker
from datetime import datetime
from app import app, db
from models import (Choice, ExamCategory, Exams, Paragraph, Referral, Topic, User, 
                                   Notification, Payment, Profile, Question, 
                                   Resource, Score, SubCategory, Subscription, UserExamResult, UserChoice)

fake = Faker()

def seed_database():
    # Users
    for _ in range(10):
        user = User(
            id=uuid.uuid4(),
            username=fake.user_name(),
            email=fake.email(),
            password=fake.password(),
            confirmed_email=fake.boolean(),
            role=fake.word(),
            referral_code=fake.uuid4(),
            created_at=datetime.now()
        )
        db.session.add(user)

    db.session.commit()

    # Exam Categories
    for _ in range(5):
        exam_category = ExamCategory(
            id=uuid.uuid4(),
            name=fake.word(),
            description=fake.text()
        )
        db.session.add(exam_category)

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
    for _ in range(10):
        exam = Exams(
            id=uuid.uuid4(),
            exam_name=fake.word(),
            category=fake.word(),
            subcategory=fake.word(),
            createdBy=fake.name(),
            createdOn=datetime.now()
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

    # Choice
    questions = Question.query.all()
    for question in questions:
        for _ in range(4):
            choice = Choice(
                id=uuid.uuid4(),
                choice=fake.word(),
                answer_id=question.id,
                created_at=datetime.now()
            )
            db.session.add(choice)

    db.session.commit()

    # Paragraph
    for question in questions:
        paragraph = Paragraph(
            id=uuid.uuid4(),
            paragraph=fake.paragraph(),
            answer_id=question.id,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.session.add(paragraph)

    db.session.commit()

    # Referrals
    for _ in range(10):
        referral = Referral(
            id=uuid.uuid4(),
            referral_code=fake.uuid4(),
            points_earned=fake.random_int(min=0, max=100),
            redeemed=fake.boolean()
        )
        db.session.add(referral)

    db.session.commit()

    # Notifications
    users = User.query.all()
    for user in users:
        notification = Notification(
            id=uuid.uuid4(),
            user_id=user.id,
            subject=fake.sentence(),
            body=fake.text(),
            sender_id=user.id,
            sender_name=user.username,
            created_at=datetime.now()
        )
        db.session.add(notification)

    db.session.commit()


    # Payments
    for user in users:
        payment = Payment(
            id=uuid.uuid4(),
            user_id=user.id,
            subscription_id=None,  # Assuming you set this later
            amount=fake.random_number(digits=5),
            expires_at=fake.future_datetime(),
            payment_type=fake.word(),
            created_at=datetime.now()
        )
        db.session.add(payment)

    db.session.commit()

    # Profiles
    for user in users:
        profile = Profile(
            id=uuid.uuid4(),
            user_id=user.id,
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            photo_url=fake.image_url(),
            title=fake.job(),
            created_at=datetime.now()
        )
        db.session.add(profile)

    db.session.commit()

    # Resources
    for topic in topics:
        resource = Resource(
            id=uuid.uuid4(),
            topic_id=topic.id,
            user_id=fake.random.choice([u.id for u in users]),
            resource_type=fake.word(),
            short_desc=fake.sentence(),
            details=fake.text(),
            created_at=datetime.now()
        )
        db.session.add(resource)

    db.session.commit()

    # Scores
    for user in users:
        score = Score(
            id=uuid.uuid4(),
            user_id=user.id,
            topic_id=fake.random.choice([t.id for t in topics]),
            possible_score=fake.random_int(min=0, max=100),
            user_score=fake.random_int(min=0, max=100),
            completion_rate=fake.random_int(min=0, max=100),
            created_at=datetime.now()
        )
        db.session.add(score)

    db.session.commit()

    # Subscriptions
    for user in users:
        subscription = Subscription(
            id=uuid.uuid4(),
            type=fake.word(),
            amount=fake.random_number(digits=5),
            created_at=datetime.now(),
            expires_at=fake.future_datetime(),
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

    # User Choices
    for question in questions:
        user_choice = UserChoice(
            id=uuid.uuid4(),
            question_id=question.id,
            choice=fake.word(),
            answer_id=question.id
        )
        db.session.add(user_choice)

    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        print("Database seeded successfully!")
        seed_database()

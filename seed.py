from datetime import datetime, timedelta
from app import app, db
from models import User, Subscription, Topic,Questions,Answers,ExamCategory
import bcrypt
from faker import Faker
import random
from uuid import UUID
import uuid

fake = Faker()

# Generate sample data for users
def generate_users(num_users):
    users = []
    for _ in range(num_users):
        email = fake.email()
        password = bcrypt.hashpw(fake.password().encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user = User(
            email=email,
            password=password,
            confirmed_email=random.choice([True, False]),
            role=random.choice(["user", "admin"]),
            referral_code=fake.uuid4(),
            created_at=datetime.utcnow()
        )
        users.append(user)
    return users

# Generate sample data for subscriptions
def generate_subscriptions(users, num_subscriptions):
    subscriptions = []
    for _ in range(num_subscriptions):
        user = random.choice(users)
        subscription = Subscription(
            user_id=user.id,  # Use .id attribute directly
            type=random.choice(["basic", "premium"]),
            amount=round(random.uniform(10.0, 200.0), 2),
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=random.randint(30, 365))
        )
        subscriptions.append(subscription)
    return subscriptions

# Generate sample data for topics
def generate_topics(users, num_topics):
    topics = []
    for _ in range(num_topics):
        topic = Topic(
            name=fake.word(),
            description=fake.text(),
            user_id=random.choice(users).id,  # Use .id attribute directly
            sub_category_id=None  # Adjust as needed
        )
        topics.append(topic)
    return topics

def generate_questions(num_questions, users):
    questions = []
    for _ in range(num_questions):
        topic_id = None
        if random.choice([True, False]):
            topic_id = uuid.uuid4()  # Generate a UUID if needed
        
        question = Questions(
            question=fake.sentence(),
            topic_id=topic_id,
            mode=random.choice(["easy", "medium", "hard"]),
            exam_mode=random.choice(["standard", "timed"]),
            created_at=datetime.utcnow()
        )
        questions.append(question)
    return questions
def generate_answers(questions):
    answers = []
    for question in questions:
        answer = Answers(
            question_id=question.id,
            answer_type="[Text ,choose]",  
            answer="Sample Answer"         
        )
        answers.append(answer)
    return answers
def generate_examcategory(users):
    exam_categories = []
    for _ in range(len(users)):
        user = random.choice(users)
        user_id = user.id if isinstance(user.id, UUID) else UUID(user.id)  # Ensure user_id is a UUID object
        exam_category = ExamCategory(
            name="Sample Category",
            description="Sample Description",
            user_id=user_id
        )
        exam_categories.append(exam_category)
    return exam_categories

# Seeding function
def seed():
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()

        # Clear existing data
        db.session.query(User).delete()
        db.session.query(Subscription).delete()
        db.session.query(Topic).delete()
        db.session.query(Questions).delete()
        db.session.query(Answers).delete()
        db.session.commit()
        # Generate and seed users
        user_instances = generate_users(10)
        for user in user_instances:
            db.session.add(user)
        db.session.commit()

        # Generate and seed subscriptions
        subscriptions = generate_subscriptions(user_instances, 5)
        for sub in subscriptions:
            db.session.add(sub)
        db.session.commit()

        questions = generate_questions(10, user)
        for question in questions:
            db.session.add(question)
        db.session.commit()


        answers = generate_answers(questions)
        for answer in answers:
            db.session.add(answer)
        db.session.commit()

        # Generate and seed topics
        topics = generate_topics(user_instances, 5)
        for topic in topics:
            db.session.add(topic)
        db.session.commit()
          # Generate and seed exam_categories
        exam_categories = generate_examcategory(user_instances)
        for exam_category in exam_categories:
            db.session.add(exam_category)
        db.session.commit()

        print("Database seeded successfully")

if __name__ == '__main__':
    seed()
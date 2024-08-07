

# Routes for User
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])


# Routes for Profile
@app.route('/profiles', methods=['GET'])
def get_profiles():
    profiles = Profile.query.all()
    return jsonify([profile.to_dict() for profile in profiles])

@app.route('/profiles/<uuid:profile_id>', methods=['GET'])
def get_profile(profile_id):
    profile = Profile.query.get(profile_id)
    if profile:
        return jsonify(profile.to_dict())
    else:
        return jsonify({"error": "Profile not found"}), 404


@app.route('/profiles/<uuid:profile_id>', methods=['DELETE'])
def delete_profile(profile_id):
    profile = Profile.query.get(profile_id)
    if profile:
        db.session.delete(profile)
        db.session.commit()
        return jsonify({"message": "Profile deleted"})
    else:
        return jsonify({"error": "Profile not found"}), 404

@app.route('/subcategories', methods=['POST'])
def create_subcategory():
    data = request.get_json()
    new_subcategory = SubCategory(
        name=data['name'],
        description=data.get('description'),
        user_id=data['user_id'],
        exam_category_id=data['exam_category_id']
    )
    db.session.add(new_subcategory)
    db.session.commit()
    return jsonify(new_subcategory.to_dict()), 201

@app.route('/subcategories/<uuid:sub_category_id>', methods=['PUT'])
def update_subcategory(sub_category_id):
    data = request.get_json()
    sub_category = SubCategory.query.get(sub_category_id)
    if sub_category:
        sub_category.name = data.get('name', sub_category.name)
        sub_category.description = data.get('description', sub_category.description)
        db.session.commit()
        return jsonify(sub_category.to_dict())
    else:
        return jsonify({"error": "Subcategory not found"}), 404

@app.route('/subcategories/<uuid:sub_category_id>', methods=['DELETE'])
def delete_subcategory(sub_category_id):
    sub_category = SubCategory.query.get(sub_category_id)
    if sub_category:
        db.session.delete(sub_category)
        db.session.commit()
        return jsonify({"message": "Subcategory deleted"})
    else:
        return jsonify({"error": "Subcategory not found"}), 404




@app.route('/users/<uuid:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify(user.to_dict())
    else:
        return jsonify({"error": "User not found"}), 404

@app.route('/users/<uuid:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    user = User.query.get(user_id)
    if user:
        user.email = data.get('email', user.email)
        user.password = data.get('password', user.password)
        user.confirmed_email = data.get('confirmed_email', user.confirmed_email)
        user.role = data.get('role', user.role)
        user.referral_code = data.get('referral_code', user.referral_code)
        db.session.commit()
        return jsonify(user.to_dict())
    else:
        return jsonify({"error": "User not found"}), 404

@app.route('/users/<uuid:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User deleted"})
    else:
        return jsonify({"error": "User not found"}), 404






@app.route('/examcategories', methods=['GET'])
def get_exam_categories():
    exam_categories = ExamCategory.query.all()
    return jsonify([{
        'id': ec.id,
        'name': ec.name,
        'description': ec.description,
        'user_id': ec.user_id
    } for ec in exam_categories])
    
@app.route('/examcategories/<uuid:exam_category_id>', methods=['GET'])
def get_exam_category(exam_category_id):
    exam_category = ExamCategory.query.get(exam_category_id)
    if exam_category:
        return jsonify({
            'id': exam_category.id,
            'name': exam_category.name,
            'description': exam_category.description,
            'user_id': exam_category.user_id
        })
    else:
        return jsonify({"error": "Exam category not found"}), 404
    
    


@app.route('/subcategories/<uuid:sub_category_id>', methods=['GET'])
def get_subcategory(sub_category_id):
    sub_category = SubCategory.query.get(sub_category_id)
    if sub_category:
        return jsonify({
            'id': sub_category.id,
            'name': sub_category.name,
            'description': sub_category.description,
            'user_id': sub_category.user_id,
            'exam_category_id': sub_category.exam_category_id
        })
    else:
        return jsonify({"error": "Subcategory not found"}), 404


    
@app.route('/topics', methods=['GET'])
def get_topics():
    topics = Topic.query.all()
    return jsonify([{
        'id': topic.id,
        'name': topic.name,
        'description': topic.description,
        'user_id': topic.user_id,
        'sub_category_id': topic.sub_category_id
    } for topic in topics])

@app.route('/topics/<uuid:topic_id>', methods=['GET'])
def get_topic(topic_id):
    topic = Topic.query.get(topic_id)
    if topic:
        return jsonify({
            'id': topic.id,
            'name': topic.name,
            'description': topic.description,
            'user_id': topic.user_id,
            'sub_category_id': topic.sub_category_id
        })
    else:
        return jsonify({"error": "Topic not found"}), 404
    

@app.route('/examcategories', methods=['POST'])
def create_exam_category():
    data = request.get_json()
    
    # Validate incoming data
    required_fields = ['name', 'description', 'user_id']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing {field}"}), 400

    try:
        user_id = uuid.UUID(data['user_id'])  # Ensure user_id is a valid UUID
    except ValueError:
        return jsonify({"error": "Invalid UUID format"}), 400

    new_exam_category = ExamCategory(
        name=data['name'],
        description=data['description'],
        user_id=user_id
    )
    
    db.session.add(new_exam_category)
    try:
        db.session.commit()
        return jsonify({
            'id': str(new_exam_category.id),  # Convert UUID to string for JSON response
            'name': new_exam_category.name,
            'description': new_exam_category.description,
            'user_id': str(new_exam_category.user_id)  # Convert UUID to string for JSON response
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
@app.route('/examcategories/<uuid:exam_category_id>', methods=['PUT'])
def update_exam_category(exam_category_id):
    data = request.get_json()
    exam_category = ExamCategory.query.get(exam_category_id)
    if not exam_category:
        return jsonify({"error": "Exam category not found"}), 404

    exam_category.name = data.get('name', exam_category.name)
    exam_category.description = data.get('description', exam_category.description)
    exam_category.user_id = data.get('user_id', exam_category.user_id)

    try:
        db.session.commit()
        return jsonify({
            'id': exam_category.id,
            'name': exam_category.name,
            'description': exam_category.description,
            'user_id': exam_category.user_id
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}),


@app.route('/examcategories/<uuid:exam_category_id>', methods=['DELETE'])
def delete_exam_category(exam_category_id):
    exam_category = ExamCategory.query.get(exam_category_id)
    if not exam_category:
        return jsonify({"error": "Exam category not found"}), 404

    db.session.delete(exam_category)
    try:
        db.session.commit()
        return jsonify({"message": "Exam category deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
@app.route('/subcategories', methods=['GET'])
def get_subcategories():
    subcategories = SubCategory.query.all()
    return jsonify([{
        'id': sc.id,
        'name': sc.name,
        'description': sc.description,
        'user_id': sc.user_id,
        'exam_category_id': sc.exam_category_id
    } for sc in subcategories])
    
 @app.route('/subcategories', methods=['POST'])
def create_subcategory():
    data = request.get_json()
    
    # Validate incoming data
    required_fields = ['name', 'description', 'user_id', 'exam_category_id']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing {field}"}), 400

    try:
        user_id = UUID(data['user_id'])  # Ensure user_id is a valid UUID
        exam_category_id = UUID(data['exam_category_id'])  # Ensure exam_category_id is a valid UUID
    except ValueError:
        return jsonify({"error": "Invalid UUID format"}), 400

    new_subcategory = SubCategory(
        name=data['name'],
        description=data['description'],
        user_id=user_id,
        exam_category_id=exam_category_id
    )
    
    db.session.add(new_subcategory)
    try:
        db.session.commit()
        return jsonify({
            'id': str(new_subcategory.id),  # Convert UUID to string for JSON response
            'name': new_subcategory.name,
            'description': new_subcategory.description,
            'user_id': str(new_subcategory.user_id),  # Convert UUID to string for JSON response
            'exam_category_id': str(new_subcategory.exam_category_id)  # Convert UUID to string for JSON response
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
@app.route('/subcategories/<uuid:sub_category_id>', methods=['PUT'])
def update_subcategory(sub_category_id):
    data = request.get_json()
    sub_category = SubCategory.query.get(sub_category_id)
    if not sub_category:
        return jsonify({"error": "Subcategory not found"}), 404

    sub_category.name = data.get('name', sub_category.name)
    sub_category.description = data.get('description', sub_category.description)
    sub_category.user_id = data.get('user_id', sub_category.user_id)
    sub_category.exam_category_id = data.get('exam_category_id', sub_category.exam_category_id)

    try:
        db.session.commit()
        return jsonify({
            'id': sub_category.id,
            'name': sub_category.name,
            'description': sub_category.description,
            'user_id': sub_category.user_,
            'exam_category_id': sub_category.exam_category_id
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/subcategories/<uuid:sub_category_id>', methods=['DELETE'])
def delete_subcategory(sub_category_id):
    sub_category = SubCategory.query.get(sub_category_id)
    if not sub_category:
        return jsonify({"error": "Subcategory not found"}), 404

    db.session.delete(sub_category)
    try:
        db.session.commit()
        return jsonify({"message": "Subcategory deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500  
    
    
 @app.route('/questions', methods=['POST'])
def create_question():
    data = request.get_json()
    new_question = Questions(
        question=data['question'],
        topic_id=data['topic_id'],
        mode=data.get('mode'),
        exam_mode=data.get('exam_mode'),
        created_at=datetime.utcnow()
    )
    db.session.add(new_question)
    db.session.commit()
    return jsonify(new_question.to_dict()), 201

@app.route('/questions/<uuid:question_id>', methods=['PUT'])
def update_question(question_id):
    data = request.get_json()
    question = Questions.query.get(question_id)
    if question:
        question.question = data.get('question', question.question)
        question.topic_id = data.get('topic_id', question.topic_id)
        question.mode = data.get('mode', question.mode)
        question.exam_mode = data.get('exam_mode', question.exam_mode)
        db.session.commit()
        return jsonify(question.to_dict())
    else:
        return jsonify({"error": "Question not found"}), 404

@app.route('/questions/<uuid:question_id>', methods=['DELETE'])
def delete_question(question_id):
    question = Questions.query.get(question_id)
    if question:
        db.session.delete(question)
        db.session.commit()
        return jsonify({"message": "Question deleted"})
    else:
        return jsonify({"error": "Question not found"}), 404
    
    

# Routes for UserAnswers
@app.route('/useranswers', methods=['GET'])
def get_user_answers():
    user_answers = UserAnswers.query.all()
    return jsonify([user_answer.to_dict() for user_answer in user_answers])

@app.route('/useranswers/<uuid:user_answer_id>', methods=['GET'])
def get_user_answer(user_answer_id):
    user_answer = UserAnswers.query.get(user_answer_id)
    if user_answer:
        return jsonify(user_answer.to_dict())
    else:
        return jsonify({"error": "User Answer not found"}), 404

@app.route('/useranswers', methods=['POST'])
def create_user_answer():
    data = request.get_json()
    new_user_answer = UserAnswers(
        question_id=data['question_id'],
        user_id=data['user_id'],
        answer_type=data.get('answer_type'),
        answer=data.get('answer'),
        attempts=data.get('attempts', 1)
    )
    db.session.add(new_user_answer)
    db.session.commit()
    return jsonify(new_user_answer.to_dict()), 201

@app.route('/useranswers/<uuid:user_answer_id>', methods=['PUT'])
def update_user_answer(user_answer_id):
    data = request.get_json()
    user_answer = UserAnswers.query.get(user_answer_id)
    if user_answer:
        user_answer.answer_type = data.get('answer_type', user_answer.answer_type)
        user_answer.answer = data.get('answer', user_answer.answer)
        user_answer.attempts = data.get('attempts', user_answer.attempts)
        db.session.commit()
        return jsonify(user_answer.to_dict())
    else:
        return jsonify({"error": "User Answer not found"}), 404

@app.route('/useranswers/<uuid:user_answer_id>', methods=['DELETE'])
def delete_user_answer(user_answer_id):
    user_answer = UserAnswers.query.get(user_answer_id)
    if user_answer:
        db.session.delete(user_answer)
        db.session.commit()
        return jsonify({"message": "User Answer deleted"})
    else:
        return jsonify({"error": "User Answer not found"}), 404
    
 # Notification CRUD Operations
@app.route('/notifications', methods=['POST'])
def create_notification():
    data = request.get_json()
    new_notification = Notification(
        user_id=data['user_id'],
        subject=data.get('subject'),
        body=data.get('body'),
        sender_id=data.get('sender_id'),
        sender_name=data.get('sender_name')
    )
    db.session.add(new_notification)
    db.session.commit()
    return jsonify(to_dict(new_notification)), 201

@app.route('/notifications', methods=['GET'])
def get_notifications():
    notifications = Notification.query.all()
    return jsonify([to_dict(notification) for notification in notifications]), 200

@app.route('/notifications/<uuid:notification_id>', methods=['GET'])
def get_notification(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    return jsonify(to_dict(notification)), 200

@app.route('/notifications/<uuid:notification_id>', methods=['PUT'])
def update_notification(notification_id):
    data = request.get_json()
    notification = Notification.query.get_or_404(notification_id)
    if 'subject' in data:
        notification.subject = data['subject']
    if 'body' in data:
        notification.body = data['body']
    if 'sender_id' in data:
        notification.sender_id = data['sender_id']
    if 'sender_name' in data:
        notification.sender_name = data['sender_name']
    db.session.commit()
    return jsonify(to_dict(notification)), 200

@app.route('/notifications/<uuid:notification_id>', methods=['DELETE'])
def delete_notification(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    db.session.delete(notification)
    db.session.commit()
    return '', 204


# Subscription CRUD Operations
@app.route('/subscriptions', methods=['POST'])
def create_subscription():
    data = request.get_json()
    new_subscription = Subscription(
        type=data['type'],
        amount=data['amount'],
        expires_at=data.get('expires_at'),
        user_id=data['user_id']
    )
    db.session.add(new_subscription)
    db.session.commit()
    return jsonify(to_dict(new_subscription)), 201

@app.route('/subscriptions/<uuid:subscription_id>', methods=['PUT'])
def update_subscription(subscription_id):
    data = request.get_json()
    subscription = Subscription.query.get_or_404(subscription_id)
    if 'type' in data:
        subscription.type = data['type']
    if 'amount' in data:
        subscription.amount = data['amount']
    if 'expires_at' in data:
        subscription.expires_at = data['expires_at']
    if 'user_id' in data:
        subscription.user_id = data['user_id']
    db.session.commit()
    return jsonify(to_dict(subscription)), 200

@app.route('/subscriptions/<uuid:subscription_id>', methods=['DELETE'])
def delete_subscription(subscription_id):
    subscription = Subscription.query.get_or_404(subscription_id)
    db.session.delete(subscription)
    db.session.commit()
    return '', 204

# Payment CRUD Operations
@app.route('/payments', methods=['POST'])
def create_payment():
    data = request.get_json()
    new_payment = Payment(
        user_id=data['user_id'],
        subscription_id=data.get('subscription_id'),
        amount=data['amount'],
        expires_at=data.get('expires_at'),
        payment_type=data.get('payment_type')
    )
    db.session.add(new_payment)
    db.session.commit()
    return jsonify(to_dict(new_payment)), 201

@app.route('/payments', methods=['GET'])
def get_payments():
    payments = Payment.query.all()
    return jsonify([to_dict(payment) for payment in payments]), 200

@app.route('/payments/<uuid:payment_id>', methods=['GET'])
def get_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    return jsonify(to_dict(payment)), 200

@app.route('/payments/<uuid:payment_id>', methods=['PUT'])
def update_payment(payment_id):
    data = request.get_json()
    payment = Payment.query.get_or_404(payment_id)
    if 'user_id' in data:
        payment.user_id = data['user_id']
    if 'subscription_id' in data:
        payment.subscription_id = data['subscription_id']
    if 'amount' in data:
        payment.amount = data['amount']
    if 'expires_at' in data:
        payment.expires_at = data['expires_at']
    if 'payment_type' in data:
        payment.payment_type = data['payment_type']
    db.session.commit()
    return jsonify(to_dict(payment)), 200

@app.route('/payments/<uuid:payment_id>', methods=['DELETE'])
def delete_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    db.session.delete(payment)
    db.session.commit()
    return '', 204

@app.route('/scores/<uuid:score_id>', methods=['PUT'])
def update_score(score_id):
    data = request.get_json()
    score = Score.query.get_or_404(score_id)
    if 'user_id' in data:
        score.user_id = data['user_id']
    if 'topic_id' in data:
        score.topic_id = data['topic_id']
    if 'possible_score' in data:
        score.possible_score = data['possible_score']
    if 'user_score' in data:
        score.user_score = data['user_score']
    if 'completion_rate' in data:
        score.completion_rate = data['completion_rate']
    db.session.commit()
    return jsonify(to_dict(score)), 200

# Score CRUD Operations
@app.route('/scores', methods=['POST'])
def create_score():
    data = request.get_json()
    new_score = Score(
        user_id=data['user_id'],
        topic_id=data.get('topic_id'),
        possible_score=data['possible_score'],
        user_score=data['user_score'],
        completion_rate=data.get('completion_rate')
    )
    db.session.add(new_score)
    db.session.commit()
    return jsonify(to_dict(new_score)), 201

@app.route('/scores', methods=['GET'])
def get_scores():
    scores = Score.query.all()
    return jsonify([to_dict(score) for score in scores]), 200

@app.route('/scores/<uuid:score_id>', methods=['GET'])
def get_score(score_id):
    score = Score.query.get_or_404(score_id)
    return jsonify(to_dict(score)), 200

@app.route('/scores/<uuid:score_id>', methods=['PUT'])
def update_score(score_id):
    data = request.get_json()
    score = Score.query.get_or_404(score_id)
    if 'user_id' in data:
        score.user_id = data['user_id']
    if 'topic_id' in data:
        score.topic_id = data['topic_id']
    if 'possible_score' in data:
        score.possible_score = data['possible_score']
    if 'user_score' in data:
        score.user_score = data['user_score']
    if 'completion_rate' in data:
        score.completion_rate = data['completion_rate']
    db.session.commit()
    return jsonify(to_dict(score)), 200

@app.route('/scores/<uuid:score_id>', methods=['DELETE'])
def delete_score(score_id):
    score = Score.query.get_or_404(score_id)
    db.session.delete(score)
    db.session.commit()
    return '', 204

# Resource CRUD Operations
@app.route('/resources', methods=['POST'])
def create_resource():
    data = request.get_json()
    new_resource = Resource(
        name=data['name'],
        description=data.get('description'),
        type=data.get('type'),
        url=data.get('url')
    )
    db.session.add(new_resource)
    db.session.commit()
    return jsonify(to_dict(new_resource)), 201

@app.route('/resources', methods=['GET'])
def get_resources():
    resources = Resource.query.all()
    return jsonify([to_dict(resource) for resource in resources]), 200

@app.route('/resources/<uuid:resource_id>', methods=['GET'])
def get_resource(resource_id):
    resource = Resource.query.get_or_404(resource_id)
    return jsonify(to_dict(resource)), 200

@app.route('/resources/<uuid:resource_id>', methods=['PUT'])
def update_resource(resource_id):
    data = request.get_json()
    resource = Resource.query.get_or_404(resource_id)
    if 'name' in data:
        resource.name = data['name']
    if 'description' in data:
        resource.description = data['description']
    if 'type' in data:
        resource.type = data['type']
    if 'url' in data:
        resource.url = data['url']
    db.session.commit()
    return jsonify(to_dict(resource)), 200

@app.route('/resources/<uuid:resource_id>', methods=['DELETE'])
def delete_resource(resource_id):
    resource = Resource.query.get_or_404(resource_id)
    db.session.delete(resource)
    db.session.commit()
    return '', 204


# Questions CRUD Operations
@app.route('/questions', methods=['POST'])
def create_question():
    data = request.get_json()
    new_question = Questions(
        text=data['text'],
        topic_id=data.get('topic_id')
    )
    db.session.add(new_question)
    db.session.commit()
    return jsonify(to_dict(new_question)), 201

@app.route('/questions', methods=['GET'])
def get_questions():
    questions = Questions.query.all()
    return jsonify([to_dict(question) for question in questions]), 200

@app.route('/questions/<uuid:question_id>', methods=['GET'])
def get_question(question_id):
    question = Questions.query.get_or_404(question_id)
    return jsonify(to_dict(question)), 200

@app.route('/questions/<uuid:question_id>', methods=['PUT'])
def update_question(question_id):
    data = request.get_json()
    question = Questions.query.get_or_404(question_id)
    if 'text' in data:
        question.text = data['text']
    if 'topic_id' in data:
        question.topic_id = data['topic_id']
    db.session.commit()
    return jsonify(to_dict(question)), 200

@app.route('/questions/<uuid:question_id>', methods=['DELETE'])
def delete_question(question_id):
    question = Questions.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    return '', 204


# UserAnswers CRUD Operations
@app.route('/user_answers', methods=['POST'])
def create_user_answer():
    data = request.get_json()
    new_user_answer = UserAnswers(
        user_id=data['user_id'],
        answer_id=data['answer_id']
    )
    db.session.add(new_user_answer)
    db.session.commit()
    return jsonify(to_dict(new_user_answer)), 201

@app.route('/user_answers', methods=['GET'])
def get_user_answers():
    user_answers = UserAnswers.query.all()
    return jsonify([to_dict(ua) for ua in user_answers]), 200

@app.route('/user_answers/<uuid:user_answer_id>', methods=['GET'])
def get_user_answer(user_answer_id):
    user_answer = UserAnswers.query.get_or_404(user_answer_id)
    return jsonify(to_dict(user_answer)), 200

@app.route('/user_answers/<uuid:user_answer_id>', methods=['PUT'])
def update_user_answer(user_answer_id):
    data = request.get_json()
    user_answer = UserAnswers.query.get_or_404(user_answer_id)
    if 'user_id' in data:
        user_answer.user_id = data['user_id']
    if 'answer_id' in data:
        user_answer.answer_id = data['answer_id']
    db.session.commit()
    return jsonify(to_dict(user_answer)), 200

@app.route('/user_answers/<uuid:user_answer_id>', methods=['DELETE'])
def delete_user_answer(user_answer_id):
    user_answer = UserAnswers.query.get_or_404(user_answer_id)
    db.session.delete(user_answer)
    db.session.commit()
    return '', 204

@app.route('/user_paragraphs', methods=['GET'])
def get_user_paragraphs():
    user_paragraphs = UserParagraph.query.all()
    return jsonify([to_dict(up) for up in user_paragraphs]), 200

@app.route('/user_paragraphs/<uuid:user_paragraph_id>', methods=['GET'])
def get_user_paragraph(user_paragraph_id):
    user_paragraph = UserParagraph.query.get_or_404(user_paragraph_id)
    return jsonify(to_dict(user_paragraph)), 200

@app.route('/user_paragraphs/<uuid:user_paragraph_id>', methods=['PUT'])
def update_user_paragraph(user_paragraph_id):
    data = request.get_json()
    user_paragraph = UserParagraph.query.get_or_404(user_paragraph_id)
    if 'user_id' in data:
        user_paragraph.user_id = data['user_id']
    if 'paragraph_id' in data:
        user_paragraph.paragraph_id = data['paragraph_id']
    if 'is_read' in data:
        user_paragraph.is_read = data['is_read']
    db.session.commit()
    return jsonify(to_dict(user_paragraph)), 200

@app.route('/user_paragraphs/<uuid:user_paragraph_id>', methods=['DELETE'])
def delete_user_paragraph(user_paragraph_id):
    user_paragraph = UserParagraph.query.get_or_404(user_paragraph_id)
    db.session.delete(user_paragraph)
    db.session.commit()
    return '', 204

# UserChoice CRUD Operations
@app.route('/user_choices', methods=['POST'])
def create_user_choice():
    data = request.get_json()
    new_user_choice = UserChoice(
        user_id=data['user_id'],
        choice_id=data['choice_id']
    )
    db.session.add(new_user_choice)
    db.session.commit()
    return jsonify(to_dict(new_user_choice)), 201

# Payment CRUD Operations
@app.route('/payments', methods=['POST'])
def create_payment():
    data = request.get_json()
    new_payment = Payment(
        user_id=data['user_id'],
        subscription_id=data.get('subscription_id'),
        amount=data['amount'],
        expires_at=data.get('expires_at'),
        payment_type=data.get('payment_type')
    )
    db.session.add(new_payment)
    db.session.commit()
    return jsonify(to_dict(new_payment)), 201

@app.route('/payments', methods=['GET'])
def get_payments():
    payments = Payment.query.all()
    return jsonify([to_dict(payment) for payment in payments]), 200

@app.route('/payments/<uuid:payment_id>', methods=['GET'])
def get_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    return jsonify(to_dict(payment)), 200

@app.route('/payments/<uuid:payment_id>', methods=['PUT'])
def update_payment(payment_id):
    data = request.get_json()
    payment = Payment.query.get_or_404(payment_id)
    if 'user_id' in data:
        payment.user_id = data['user_id']
    if 'subscription_id' in data:
        payment.subscription_id = data['subscription_id']
    if 'amount' in data:
        payment.amount = data['amount']
    if 'expires_at' in data:
        payment.expires_at = data['expires_at']
    if 'payment_type' in data:
        payment.payment_type = data['payment_type']
    db.session.commit()
    return jsonify(to_dict(payment)), 200

@app.route('/payments/<uuid:payment_id>', methods=['DELETE'])
def delete_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    db.session.delete(payment)
    db.session.commit()
    return '', 204


# Choice CRUD Operations
@app.route('/choices', methods=['POST'])
def create_choice():
    data = request.get_json()
    new_choice = Choice(
        text=data['text'],
        question_id=data['question_id'],
        is_correct=data.get('is_correct', False)
    )
    db.session.add(new_choice)
    db.session.commit()
    return jsonify(to_dict(new_choice)), 201



@app.route('/choices', methods=['GET'])
def get_choices():
    choices = Choice.query.all()
    return jsonify([to_dict(choice) for choice in choices]), 200


@app.route('/choices/<uuid:choice_id>', methods=['GET'])
def get_choice(choice_id):
    choice = Choice.query.get_or_404(choice_id)
    return jsonify(to_dict(choice)), 200

@app.route('/choices/<uuid:choice_id>', methods=['PUT'])
def update_choice(choice_id):
    data = request.get_json()
    choice = Choice.query.get_or_404(choice_id)
    if 'text' in data:
        choice.text = data['text']
    if 'question_id' in data:
        choice.question_id = data['question_id']
    if 'is_correct' in data:
        choice.is_correct = data['is_correct']
    db.session.commit()
    return jsonify(to_dict(choice)), 200

@app.route('/choices/<uuid:choice_id>', methods=['DELETE'])
def delete_choice(choice_id):
    choice = Choice.query.get_or_404(choice_id)
    db.session.delete(choice)
    db.session.commit()
    return '', 204


# AnswerMetadata CRUD Operations
@app.route('/answer_metadata', methods=['POST'])
def create_answer_metadata():
    data = request.get_json()
    new_answer_metadata = AnswerMetadata(
        question_id=data['question_id'],
        answer_id=data['answer_id'],
        metadata=data.get('metadata')
    )
    db.session.add(new_answer_metadata)
    db.session.commit()
    return jsonify(to_dict(new_answer_metadata)), 201

@app.route('/answer_metadata', methods=['GET'])
def get_answer_metadata():
    answer_metadata = AnswerMetadata.query.all()
    return jsonify([to_dict(am) for am in answer_metadata]), 200

@app.route('/answer_metadata/<uuid:answer_metadata_id>', methods=['GET'])
def get_answer_metadata_by_id(answer_metadata_id):
    answer_metadata = AnswerMetadata.query.get_or_404(answer_metadata_id)
    return jsonify(to_dict(answer_metadata)), 200

@app.route('/answer_metadata/<uuid:answer_metadata_id>', methods=['PUT'])
def update_answer_metadata(answer_metadata_id):
    data = request.get_json()
    answer_metadata = AnswerMetadata.query.get_or_404(answer_metadata_id)
    if 'question_id' in data:
        answer_metadata.question_id = data['question_id']
    if 'answer_id' in data:
        answer_metadata.answer_id = data['answer_id']
    if 'metadata' in data:
        answer_metadata.metadata = data['metadata']
    db.session.commit()
    return jsonify(to_dict(answer_metadata)), 200

@app.route('/answer_metadata/<uuid:answer_metadata_id>', methods=['DELETE'])
def delete_answer_metadata(answer_metadata_id):
    answer_metadata = AnswerMetadata.query.get_or_404(answer_metadata_id)
    db.session.delete(answer_metadata)
    db.session.commit()
    return '', 204

























   
    
    
    
    
    
    
   
    
    
    
    
    
    
 
@app.route('/topics', methods=['POST'])
def create_topic():
    data = request.get_json()
    
    # Validate incoming data
    required_fields = ['name', 'description', 'user_id', 'sub_category_id']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing {field}"}), 400

    try:
        user_id = UUID(data['user_id'])  # Ensure user_id is a valid UUID
        sub_category_id = UUID(data['sub_category_id'])  # Ensure sub_category_id is a valid UUID
    except ValueError:
        return jsonify({"error": "Invalid UUID format"}), 400

    new_topic = Topic(
        name=data['name'],
        description=data['description'],
        user_id=user_id,
        sub_category_id=sub_category_id
    )
    
    db.session.add(new_topic)
    try:
        db.session.commit()
        return jsonify({
            'id': str(new_topic.id),  # Convert UUID to string for JSON response
            'name': new_topic.name,
            'description': new_topic.description,
            'user_id': str(new_topic.user_id),  # Convert UUID to string for JSON response
            'sub_category_id': str(new_topic.sub_category_id)  # Convert UUID to string for JSON response
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500     
    
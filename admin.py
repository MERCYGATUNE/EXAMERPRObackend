
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
    
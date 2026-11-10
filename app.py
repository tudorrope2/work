from flask import Flask, request, jsonify

app = Flask(__name__)

questions_db = []
question_id_counter = 1

# [조회 & 검색 API] 검색어가 있으면 필터링해서 반환
@app.route('/api/questions', methods=['GET'])
def get_questions():
    search_keyword = request.args.get('search', '').strip()
    
    filtered_questions = questions_db
    if search_keyword:
        filtered_questions = [q for q in questions_db if search_keyword in q['content']]
        
    return jsonify(filtered_questions[::-1]), 200

# [작성 API] 카테고리 데이터 함께 저장
@app.route('/api/questions', methods=['POST'])
def create_question():
    global question_id_counter
    data = request.get_json()
    content = data.get('content', '').strip()
    category = data.get('category', '기타') # 프론트에서 보낸 카테고리 받기

    if not content:
        return jsonify({'error': '내용을 입력하세요.'}), 400

    new_question = {
        'id': question_id_counter,
        'category': category,
        'content': content,
        'likes': 0,
        'comments': []
    }
    questions_db.append(new_question)
    question_id_counter += 1

    return jsonify(new_question), 201

# [공감 API]
@app.route('/api/questions/<int:q_id>/like', methods=['POST'])
def like_question(q_id):
    for q in questions_db:
        if q['id'] == q_id:
            q['likes'] += 1
            return jsonify(q), 200
    return jsonify({'error': '질문을 찾을 수 없습니다.'}), 404

# [댓글 API]
@app.route('/api/questions/<int:q_id>/comments', methods=['POST'])
def add_comment(q_id):
    data = request.get_json()
    comment_content = data.get('content', '').strip()
    
    if not comment_content:
        return jsonify({'error': '댓글을 입력하세요.'}), 400

    for q in questions_db:
        if q['id'] == q_id:
            q['comments'].append(comment_content)
            return jsonify(q), 201
            
    return jsonify({'error': '질문을 찾을 수 없습니다.'}), 404

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

questions_db = []
question_id_counter = 1

# [조회 & 검색 & 정렬 API]
@app.route('/api/questions', methods=['GET'])
def get_questions():
    search_keyword = request.args.get('search', '').strip()
    sort_type = request.args.get('sort', 'latest') # 기본값: 최신순
    
    # 1. 검색어 필터링
    filtered_questions = questions_db
    if search_keyword:
        filtered_questions = [q for q in questions_db if search_keyword in q['content']]
        
    # 2. 정렬 처리
    if sort_type == 'likes':
        # 공감순 정렬 (공감이 많고, 최신인 것 우선)
        sorted_questions = sorted(filtered_questions, key=lambda x: (x['likes'], x['id']), reverse=True)
    else:
        # 최신순 정렬 (기본)
        sorted_questions = filtered_questions[::-1]
        
    return jsonify(sorted_questions), 200

# [작성 API] 카테고리 및 현재 시간 저장
@app.route('/api/questions', methods=['POST'])
def create_question():
    global question_id_counter
    data = request.get_json()
    content = data.get('content', '').strip()
    category = data.get('category', '기타')

    if not content:
        return jsonify({'error': '내용을 입력하세요.'}), 400

    # 현재 시간을 'YYYY-MM-DD HH:MM' 형식으로 생성
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M')

    new_question = {
        'id': question_id_counter,
        'category': category,
        'content': content,
        'created_at': current_time,
        'likes': 0,
        'comments': []
    }
    questions_db.append(new_question)
    question_id_counter += 1

    return jsonify(new_question), 201

# [삭제 API]
@app.route('/api/questions/<int:q_id>', methods=['DELETE'])
def delete_question(q_id):
    global questions_db
    initial_len = len(questions_db)
    questions_db = [q for q in questions_db if q['id'] != q_id]
    
    if len(questions_db) < initial_len:
        return jsonify({'message': '삭제되었습니다.'}), 200
    return jsonify({'error': '질문을 찾을 수 없습니다.'}), 404

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
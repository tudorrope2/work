from flask import Flask, request, jsonify

app = Flask(__name__)

# 임시 데이터 저장소
questions_db = []
question_id_counter = 1

# [기능 2] 질문 목록 조회 API
@app.route('/api/questions', methods=['GET'])
def get_questions():
    return jsonify(questions_db[::-1]), 200

# [기능 1] 질문 작성 API
@app.route('/api/questions', methods=['POST'])
def create_question():
    global question_id_counter
    data = request.get_json()
    content = data.get('content', '').strip()

    if not content:
        return jsonify({'error': '내용을 입력하세요.'}), 400

    new_question = {
        'id': question_id_counter,
        'content': content,
        'likes': 0,
        'comments': [] # 댓글 저장용 리스트 추가
    }
    questions_db.append(new_question)
    question_id_counter += 1

    return jsonify(new_question), 201

# [기능 3] 질문 공감 누르기 API
@app.route('/api/questions/<int:q_id>/like', methods=['POST'])
def like_question(q_id):
    for q in questions_db:
        if q['id'] == q_id:
            q['likes'] += 1
            return jsonify(q), 200
    return jsonify({'error': '질문을 찾을 수 없습니다.'}), 404

# [기능 4] 댓글 달기 API (추가됨)
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

# 헬스 체크 API
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, emit
import random

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# 연습할 샘플 문장 리스트
SENTENCES = [
    "Flask and WebSockets make real-time applications incredibly fun and interactive.",
    "Containerization with Docker ensures your environment is consistent everywhere.",
    "Practice typing every day to improve your speed and accuracy significantly.",
    "Cloud deployment on AWS EC2 brings your project to the real world."
]

# 방별 상태 관리 딕셔너리
rooms_state = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join')
def handle_join(data):
    room = data.get('room', 'default')
    username = data.get('username', '익명')
    
    join_room(room)
    
    if room not in rooms_state:
        rooms_state[room] = {
            'sentence': random.choice(SENTENCES),
            'status': 'waiting', # waiting, playing, finished
            'players': {}
        }
    
    rooms_state[room]['players'][request.sid] = {
        'username': username,
        'progress': 0,
        'finished': False
    }
    
    # 방에 있는 모든 사람에게 현재 플레이어 목록 전송
    emit('update_room', rooms_state[room], room=room)

@socketio.on('start_game')
def handle_start(data):
    room = data.get('room')
    if room in rooms_state:
        rooms_state[room]['status'] = 'playing'
        rooms_state[room]['sentence'] = random.choice(SENTENCES)
        for sid in rooms_state[room]['players']:
            rooms_state[room]['players'][sid]['progress'] = 0
            rooms_state[room]['players'][sid]['finished'] = False
            
        emit('game_started', rooms_state[room], room=room)

@socketio.on('update_progress')
def handle_progress(data):
    room = data.get('room')
    progress = data.get('progress', 0)
    
    if room in rooms_state and request.sid in rooms_state[room]['players']:
        rooms_state[room]['players'][request.sid]['progress'] = progress
        
        # 100% 도달 시 승리 처리 체크
        if progress >= 100 and not rooms_state[room]['players'][request.sid]['finished']:
            rooms_state[room]['players'][request.sid]['finished'] = True
            winner_name = rooms_state[room]['players'][request.sid]['username']
            emit('game_over', {'winner': winner_name}, room=room)
            
        emit('update_room', rooms_state[room], room=room)

@socketio.on('disconnect')
def handle_disconnect():
    for room, state in list(rooms_state.items()):
        if request.sid in state['players']:
            del state['players'][request.sid]
            if not state['players']:
                del rooms_state[room] # 방에 사람이 없으면 방 폭파
            else:
                emit('update_room', state, room=room)
            break

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
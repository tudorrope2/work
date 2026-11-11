from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, emit
import random

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# 연습할 샘플 문장 리스트
SENTENCES = [
    "삶은 어쨌든 인간으로 태어난 이상 인간이 바랄 수 있는 것만을 바랄 때 지속 가능한 것이다. 내가 인간으로 살아 있는 것을 잠시 멈추고 인간이 아닌 것으로 있기를 바랄 때 내가 선택할 수 있는 것은 작가가 되는 것이었다. 작가는 인간으로 살아 있기를 멈추고, 인간이 아닌 다른 것이 될 수 있다."
    "나의 상상력은 클로이의 치아 사이의 틈에서 노는 것을 즐겼다. 그녀의 아름다움은 헝클어져 있었기 때문에 창조적 재배치가 가능했다. 클로이의 얼굴은 그 모호함 때문에, 오리와 토끼가 둘 다 들어 있는 것처럼 보이는 비트겐슈타인의 오리-토끼 그림과 비슷했다. 상상력이 오리를 찾으면 그는 오리를 보게 될 것이다. 상상력이 토끼를 찾으면 토끼가 나타날 것이다. 아는 그녀의 영혼으로 그녀의 얼굴에 생기를 불어넣었던 것이었다."
    
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
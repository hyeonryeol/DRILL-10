from pico2d import *   # pico2d의 모든 함수/상수(open_canvas, load_image, SDL_QUIT 등)를 가져옴
import random          # 소년의 시작 위치/프레임을 랜덤으로 정하기 위해 사용


# Game object class here
# ---------------------------------------------------------------
# [LEC11 핵심] 게임 객체(Game Object)
#  - 게임에 등장하는 것들을 "클래스"로 만든다.
#  - 모든 게임 객체는 공통으로 update()와 draw()를 가진다.
#      update() : 상태(위치, 프레임 등)를 바꾸는 함수  -> 게임 로직
#      draw()   : 현재 상태를 화면에 그리는 함수        -> 렌더링
#  - 공통 인터페이스(update/draw)가 있으므로 world 리스트에 다 넣고
#    for 문 하나로 한꺼번에 처리할 수 있다. (다형성)
# ---------------------------------------------------------------

class Grass:
    def __init__(self):                        # 생성자: 객체가 만들어질 때 한 번 호출
        self.image = load_image('grass.png')   # 잔디 이미지 로드 (open_canvas() 이후에만 가능!)
    def draw(self):
        self.image.draw(400, 30)               # 이미지 "중심"을 (400, 30)에 그림 (pico2d 좌표는 왼쪽 아래가 (0,0))
    def update(self): pass                     # 잔디는 움직이지 않지만, world에서 일괄 호출하므로 빈 update가 필요


class Boy:
    def __init__(self):
        self.x, self.y = random.randint(100, 700), 90   # x는 100~700 사이 랜덤, y는 잔디 위 90
        self.frame = random.randint(0, 7)               # 시작 프레임도 랜덤 -> 소년들이 서로 다른 동작으로 달림
        self.image = load_image('run_animation.png')    # 달리기 애니메이션 스프라이트 시트 (100x100 프레임 8장이 가로로 나열)
    def update(self):
        self.frame = (self.frame +1) % 8   # 프레임 0~7 반복 (% 8 로 7 다음에 0으로 돌아감)
        self.x += 5                         # 매 프레임 오른쪽으로 5픽셀 이동
    def draw(self):
        # clip_draw(left, bottom, width, height, x, y)
        #  -> 시트에서 (left, bottom)부터 width x height 만큼 잘라 (x, y)에 그림
        #  -> frame * 100 : 현재 프레임의 왼쪽 x 좌표 (프레임 하나 폭이 100)
        self.image.clip_draw(self.frame * 100, 0, 100, 100, self.x, self.y)

class Zombie:
    def __init__(self):
        self.x, self.y = 100, 170                         # 좀비 시작 위치 (고정)
        self.frame = 0                                    # 첫 프레임부터 시작
        self.image = load_image('zombie_run_animation.png')  # 좀비 시트 (프레임 10장이 가로로 나열)
    def update(self):
        self.frame = (self.frame + 1) % 10   # 프레임 0~9 반복
        self.x += 5                           # 오른쪽으로 5픽셀 이동
    def draw(self):
        frame_width = self.image.w //10   # 이미지 전체 폭 / 10 = 프레임 하나의 폭 (image.w, image.h로 크기 조회)
        frame_height = self.image.h       # 한 줄짜리 시트이므로 프레임 높이 = 이미지 높이
        # clip_draw(left, bottom, w, h, x, y, 그릴_폭, 그릴_높이)
        #  -> 마지막 두 인자로 크기를 조절해서 그림. 여기선 원본의 절반 크기로 축소
        self.image.clip_draw(self.frame * frame_width, 0, frame_width, frame_height, self.x, self.y, frame_width // 2, frame_height //2)

class Ball:
    def __init__(self):
        self.x, self.y = random.randint(200, 700), 70  # 잔디 위에 놓인 작은 공
        self.r = 10                                          # 반지름 (ball21x21 -> 10)
        self.dy = 0                              # 처음엔 멈춰 있음
        self.image = load_image('ball21x21.png')
    
    def update(self):
        self.dy = random.randint(10, 20)     # 위로 띄우기
        if self.y < 570:
            self.y += self.dy
        elif self.y >550:
            self.y -= self.dy
    def draw(self):
        self.image.draw(self.x, self.y)
# ---------------------------------------------------------------
# 게임 루프를 구성하는 함수들
#  reset_world()  : 게임 월드 초기화 (객체 생성)
#  handle_events(): 입력 처리
#  update_world() : 모든 객체 update
#  render_world() : 모든 객체 draw
# ---------------------------------------------------------------

def reset_world():
    global running   # 함수 안에서 전역 변수에 "대입"하려면 global 선언 필수
    global world     # (선언 안 하면 지역 변수가 새로 생겨서 바깥 world가 안 바뀜)
    running = True   # 게임 루프 실행 여부
    world = []       # 모든 게임 객체를 담는 리스트 (게임 월드)

    grass = Grass()          # 잔디 객체 생성
    world.append(grass)      # 월드에 추가
    zomebie = Zombie()       # 좀비 객체 생성
    world.append(zomebie)    # 월드에 추가
    team = [Boy() for i in range(11)]   # 리스트 컴프리헨션으로 소년 11명 생성
    world += team                        # 리스트 합치기 (extend와 같음). append(team)하면 리스트가 통째로 하나의 원소로 들어가니 주의!
    team2 = [Ball() for i in range(20)]
    world += team2      

    # world에 넣은 순서 = 그리는 순서 -> 먼저 넣은 잔디가 가장 뒤(아래)에 그려짐





def update_world():
    for o in world:   # 객체 종류와 상관없이
        o.update()    # 각자의 update()가 호출됨 (다형성)

def render_world():
    clear_canvas()    # 1. 화면 지우기
    for o in world:   # 2. 모든 객체를 world 순서대로 그리기 (백 버퍼에 그림)
        o.draw()
    update_canvas()   # 3. 그린 내용을 화면에 실제로 표시 (더블 버퍼링: 백 버퍼 -> 프론트 버퍼)


def handle_events():
    global running              # running을 False로 바꾸기 위해 global 선언
    events = get_events()       # 쌓여 있는 이벤트(키보드, 마우스, 창 닫기 등)를 리스트로 받아옴
    for event in events:
        if event.type == SDL_QUIT:      # 창의 X 버튼을 눌렀을 때
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:   # ESC 키를 눌렀을 때
            running = False




open_canvas()     # 캔버스(창) 생성. 기본 크기 800 x 600. load_image보다 먼저 호출해야 함

reset_world()     # 게임 월드 초기화 (여기서 객체 생성 -> 이미지 로드)

# 게임 루프 (Game Loop): 입력 -> 갱신 -> 그리기 를 계속 반복
while running:
    handle_events()   # 1. 입력 처리
    update_world()    # 2. 게임 로직 (객체 상태 변경)
    render_world()    # 3. 화면 그리기
    delay(0.05)       # 0.05초 대기 -> 약 20 FPS (너무 빨리 돌지 않게)


close_canvas()    # 캔버스 닫기 (프로그램 종료)



# ===============================================================
# [응용 1] 좀비 여러 명 생성하기
# ===============================================================
# 1) Zombie.__init__에서 위치와 시작 프레임을 랜덤으로 바꾸기
#    (안 바꾸면 전부 (100, 170)에서 같은 프레임으로 시작해서 한 마리처럼 겹쳐 보임)
#
# class Zombie:
#     def __init__(self):
#         self.x, self.y = random.randint(100, 700), 170   # x만 랜덤
#         self.frame = random.randint(0, 9)                # 프레임 0~9 중 랜덤
#         self.image = load_image('zombie_run_animation.png')
#
# 2) reset_world()에서 좀비 한 마리 만들던 부분을 리스트로 바꾸기
#
#     zombies = [Zombie() for i in range(5)]   # 좀비 5마리 생성 (숫자만 바꾸면 됨)
#     world += zombies                          # append가 아니라 += (append하면 리스트째로 들어감)
#
#    또는 for문으로:
#     for i in range(5):
#         world.append(Zombie())
#
# ===============================================================
# [응용 2] 좀비 크기 줄이기
# ===============================================================
# clip_draw의 마지막 두 인자(그릴 폭, 그릴 높이)가 화면에 그려지는 크기.
# 지금은 // 2 (절반). 나누는 숫자를 키우면 더 작아짐.
#
#  원본 프레임 1장 = 430 x 519
#   // 2 -> 215 x 259  (지금)
#   // 3 -> 143 x 173
#   // 4 -> 107 x 129
#
# def draw(self):
#     frame_width = self.image.w // 10
#     frame_height = self.image.h
#     self.image.clip_draw(self.frame * frame_width, 0, frame_width, frame_height,
#                          self.x, self.y, frame_width // 4, frame_height // 4)   # 1/4 크기
#
# ※ 주의: 앞의 4개(frame_width, 0, frame_width, frame_height)는 "시트에서 자르는 영역"이라
#         건드리면 안 됨. 바꾸는 건 마지막 두 개만!
#
# ※ 크기를 줄이면 발이 공중에 뜸 -> y도 같이 낮추기
#    y는 그림의 "중심"이므로  y = 잔디 윗면(약 60) + 그릴_높이 // 2
#     // 2 -> y = 60 + 259 // 2 = 약 190 (지금 170은 발이 잔디에 살짝 묻힌 상태)
#     // 4 -> y = 60 + 129 // 2 = 약 125
#
# [크기를 좀비마다 다르게 하고 싶으면] 배율을 변수로 빼기
# class Zombie:
#     def __init__(self):
#         self.size = random.randint(2, 4)      # 2 ~ 4 중 랜덤 (클수록 작아짐)
#         self.frame_w = 430 // self.size
#         self.frame_h = 519 // self.size
#         self.x, self.y = random.randint(100, 700), 60 + self.frame_h // 2   # 발이 잔디 위에 오게
#         self.frame = random.randint(0, 9)
#         self.image = load_image('zombie_run_animation.png')
#     def draw(self):
#         frame_width = self.image.w // 10
#         frame_height = self.image.h
#         self.image.clip_draw(self.frame * frame_width, 0, frame_width, frame_height,
#                              self.x, self.y, self.frame_w, self.frame_h)
# ---------------- [7] 공 차기 (소년이 공에 닿으면 공이 날아감) ----------------
# 핵심 아이디어
#  1) 공은 속도 dx, dy를 가짐 (가만히 있으면 둘 다 0)
#  2) 매 프레임 "소년과 공이 닿았는지" 검사 -> 닿으면 공에 속도를 줌(= 차기)
#  3) 공은 update에서 dy에 중력을 빼서 포물선으로 날아가고, 잔디에 닿으면 튕김
#
# class Ball:
#     def __init__(self):
#         self.x, self.y = random.randint(200, 700), 60 + 10   # 잔디 위에 놓인 작은 공
#         self.r = 10                                          # 반지름 (ball21x21 -> 10)
#         self.dx, self.dy = 0, 0                              # 처음엔 멈춰 있음
#         self.image = load_image('ball21x21.png')
#     def kick(self):
#         self.dx = random.randint(10, 20)     # 오른쪽으로 (소년이 오른쪽으로 달리니까)
#         self.dy = random.randint(10, 20)     # 위로 띄우기
#     def update(self):
#         self.x += self.dx
#         self.y += self.dy
#         if self.y - self.r > 60 or self.dy > 0:   # 공중에 있으면
#             self.dy -= 1                           # 중력 (매 프레임 아래쪽으로 속도 감소)
#         if self.y - self.r < 60:                   # 잔디에 닿으면
#             self.y = 60 + self.r                   # 잔디 위로 올려놓고
#             self.dy = -self.dy * 0.6               # 튕김 (0.6 = 탄성, 작을수록 덜 튐)
#             self.dx *= 0.8                         # 땅에 닿을 때마다 굴러가는 속도 감소(마찰)
#             if abs(self.dy) < 2: self.dy = 0       # 거의 안 튀면 멈춤
#         if self.x > 800 - self.r or self.x < self.r:   # 화면 양 끝 벽에 튕기기
#             self.dx = -self.dx
#             self.x = clamp(self.r, self.x, 800 - self.r)
#     def draw(self):
#         self.image.draw(self.x, self.y)
#
# 충돌(닿았는지) 검사 - 둘 중 하나 사용
#  (a) 거리로: 소년 중심과 공 중심의 거리가 가까우면
#        def is_touch(boy, ball):
#            return abs(boy.x - ball.x) < 30 and abs(boy.y - ball.y) < 50
#  (b) 사각형으로(정석): 두 사각형이 겹치는지
#        boy 영역 : (x-20, y-50) ~ (x+20, y+50)     ball 영역 : (x-r, y-r) ~ (x+r, y+r)
#        def is_touch(boy, ball):
#            bl, bb, br, bt = boy.x - 20, boy.y - 50, boy.x + 20, boy.y + 50
#            ll, lb, lr, lt = ball.x - ball.r, ball.y - ball.r, ball.x + ball.r, ball.y + ball.r
#            if br < ll or bl > lr: return False   # 좌우로 안 겹침
#            if bt < lb or bb > lt: return False   # 위아래로 안 겹침
#            return True
#        (확인용) draw()에서 draw_rectangle(bl, bb, br, bt) 로 박스를 그려볼 수 있음
#
# reset_world()에서 boys, balls를 따로 리스트로 만들고 global로 기억해 둠:
#     global boys, balls
#     boys = [Boy() for i in range(11)]
#     balls = [Ball() for i in range(5)]
#     world += boys
#     world += balls
#
# update_world()에서 모든 객체 update 후 충돌 검사:
#     def update_world():
#         for o in world:
#             o.update()
#         for boy in boys:
#             for ball in balls:
#                 if is_touch(boy, ball) and ball.dx < 5:   # 이미 날아가는(빠른) 공은 또 안 차게
#                     ball.kick()
#
# [변형] 스페이스바를 눌렀을 때만 차기
#  - handle_events()의 KEYDOWN에서:  elif event.key == SDLK_SPACE: kick_pressed = True  (global 선언!)
#  - update_world()에서:             if kick_pressed and is_touch(boy, ball): ball.kick()
#                                    검사 끝나면 kick_pressed = False
# [변형] 소년이 왼쪽으로 달릴 때는 dx를 음수로:  self.dx = random.randint(10, 20) * boy.dir
#        (kick(self, dir) 처럼 방향을 인자로 받기)
# ===============================================================

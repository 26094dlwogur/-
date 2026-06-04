import math

class Animal:
    TICKS_PER_SECOND = 60

    def __init__(self, name, power, vmax, x=0.0, y=0.0):
        self.name = name
        self.power = power
        self.vmax = vmax  # 팀원들이 아무리 속도를 높여도 이 값을 넘을 수 없음
        
        self.place = (x, y)
        self.vx = 0.0
        self.vy = 0.0
        
        # 초기 조건은 고정으로 받음 (이후 업데이트는 내 알빠 아님!)
        self.is_youth = True
        self.is_starving = False

    @property
    def x(self):
        return self.place[0]

    @property
    def y(self):
        return self.place[1]

    def update_status(self):
        '오버라이딩(조원 담당)'
        pass

    def calculate_velocity(self):
        '오버라이딩(조원 담당)' 
        pass

    def move(self):
        
    
        current_speed = math.hypot(self.vx, self.vy)
        
        if current_speed > self.vmax:
            ratio = self.vmax / current_speed
            self.vx *= ratio
            self.vy *= ratio

        dx_per_tick = self.vx / self.TICKS_PER_SECOND
        dy_per_tick = self.vy / self.TICKS_PER_SECOND
        
        new_x = self.x + dx_per_tick
        new_y = self.y + dy_per_tick
        self.place = (new_x, new_y)

    def update_tick(self):
        self.update_status()      
        self.calculate_velocity() 
        self.move()               

def get_distance(self, partner):
        # 내 좌표(self.x, self.y)와 상대방 좌표(partner.x, partner.y)의 거리 계산
        return math.hypot(self.x - partner.x, self.y - partner.y)

def check_reproduce_condition(self, partner):
        '이것도 오버라이딩'
        pass

def reproduce(self, partner):
        # 조원이 만든 조건 검사 로직을 호출해서 True가 나오면 번식 성공
    if self.check_reproduce_condition(partner):
        print(f"[{self.name}]와(과) [{partner.name}]이(가) 짝짓기에 성공하여 새로운 생명이 태어납니다!")
        return True
            
    else:
        return False
def death(self):
    print(f"[{self.name}] 제압되었습니다.")
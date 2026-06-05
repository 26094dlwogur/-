class Environment:
    def __init__(self):
        """
        맹그로브 숲 생태계를 초기화합니다.
        """
        # 계획서 명시 속성
        self.is_low_tide = False     # 처음 시작은 밀물(False)로 설정 (치어들이 숨어있는 평화로운 상태)
        self.day = 1                 # 현재 날짜 (1일차부터 시작)
        self.organism_list = []      # 생태계에 존재하는 모든 생물(Animal, Plant 등)을 담는 리스트
        
        # 시간(틱) 관리를 위한 내부 변수
        self.current_tick = 0
        self.ticks_per_day = 60 * 60 # 예: 초당 60틱 기준, 60초(3600틱)를 하루로 설정

    def add_organism(self, organism):
        """
        [추가 기능] 생태계에 생물(조원들이 만든 객체)을 추가하는 유틸리티 함수입니다.
        """
        self.organism_list.append(organism)
        print(f"[환경] {organism.name}이(가) 생태계에 추가되었습니다.")

    def change_tide(self):
        """
        [계획서 명시 메서드] 밀물과 썰물을 전환합니다.
        """
        self.is_low_tide = not self.is_low_tide
        
        if self.is_low_tide:
            print(f"\n썰물이 되었습니다! 물이 빠지며 포식자들이 활동을 시작합니다.")
            # 조원들에게 알림: "썰물일 때는 니들 포식자들 속도 올리게 calculate_velocity에 짜놔!"
        else:
            print(f"\n[환경 변화] 밀물이 되었습니다! 물이 차오르며 치어들이 맹그로브 뿌리로 숨습니다.")
            # 조원들에게 알림: "밀물일 때는 니들 치어들 은신처로 이동하게 짜놔!"

    def trigger_timelapse_destruction(self):
        """
        [기획서 반영] 생태계 종료 시점의 타임랩스 환경 파괴 연출
        """
        print("\n=========================================")
        print("[경고] 타임랩스 시작: 환경 파괴가 진행됩니다")
        print("1. 습지가 매립되고 있습니다...")
        print("2. 맹그로브 나무들이 불타고 있습니다...")
        print("3. 콘크리트 건물이 세워집니다...")
        print("생태계 시뮬레이션이 종료되었습니다.")
        print("=========================================")
        # 모든 생물 절멸 처리 등 추가 가능
        self.organism_list.clear()

    def update(self):
        """
        [계획서 명시 메서드] 메인 시뮬레이션 루프. 
        매 틱마다 호출되어 시간, 조수간만, 생물들의 상태를 통제합니다.
        """
        self.current_tick += 1

        # 1. 조수간만의 차 발생 (예: 하루의 절반이 지났을 때 물이 바뀜)
        if self.current_tick % (self.ticks_per_day // 2) == 0:
            self.change_tide()

        # 2. 날짜 변경 처리
        if self.current_tick % self.ticks_per_day == 0:
            self.day += 1
            print(f"\n --- {self.day}일차 아침이 밝았습니다 ---")
            
            # 기획 내용: 특정 날짜가 되면 생태계를 파괴하고 시뮬레이션 종료
            if self.day >= 7: # 예: 7일차가 되면 파괴 엔딩
                self.trigger_timelapse_destruction()
                return False # 메인 루프 종료 신호 반환

        # 3. 생태계 내 모든 생물들에게 "1틱 지났으니 각자 할 일 해!" 라고 지시
        for organism in self.organism_list:
            # 앞서 만든 Animal 클래스의 update_tick()을 일괄 실행
            if hasattr(organism, 'update_tick'):
                organism.update_tick()

        # (선택) 사망한 객체를 리스트에서 청소하는 로직을 여기에 추가할 수 있습니다.
        
        return True # 시뮬레이션 계속 진행
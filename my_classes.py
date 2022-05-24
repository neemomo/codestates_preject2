import numpy as np
import pygame
import pandas as pd


class Simulator:
    def __init__(self, recoder):
        self.recoder = recoder

    def simulate(self, n_preys=10, total_time=30, ff=1, shutdown_immediately=True):
        pygame.init()

        # 화면 크기 설정
        screen_width = 1000
        screen_height = 1000
        screen = pygame.display.set_mode((screen_width, screen_height))

        # 화면 타이틀 설정
        pygame.display.set_caption("neemo's simulator")

        # FPS
        clock = pygame.time.Clock()
        fps = 60

        # 배경 이미지 불러오기
        background = pygame.image.load("./essets/background.jpg")
        # background = pygame.transform.scale(background, (screen_width, screen_height))

        # 캐릭터 이미지 불러오기
        _predator = pygame.image.load("./essets/predator.png")
        _prey = pygame.image.load("./essets/prey.png")

        # predator, prey 개체 만들기
        predator = Circle(screen_width, screen_height, _predator)
        preys = {}
        for i in range(n_preys):
            preys[i] = Circle(screen_width, screen_height, _prey)
        init_preys = preys.copy()

        # 폰트 정의
        game_font = pygame.font.Font('./essets/BMHANNAAir_otf.otf', 50)

        if not shutdown_immediately:
            while True:
                event = pygame.event.poll()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    break

        # 시작 시간
        start_ticks = pygame.time.get_ticks()

        # 이벤트 루프
        running = True
        total_frame = 0
        while running:
            total_frame += ff
            dt = clock.tick(fps)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            screen.blit(background, (0, 0))

            for i in range(ff):
                # 이동
                predator.move(dt)
                for idx in preys:
                    prey = preys[idx]
                    prey.move(dt)

                # 충돌 체크
                collided = []
                for idx in preys:
                    prey = preys[idx]
                    if predator.collide(prey):
                        collided.append(idx)
                for idx in collided:
                    preys.pop(idx)

            # 그리기
            screen.blit(predator.image, (predator.pos_x, predator.pos_y))
            for idx in preys:
                prey = preys[idx]
                screen.blit(prey.image, (prey.pos_x, prey.pos_y))

            # 타이머 및 생존 현황
            elapsed_time = ff * (pygame.time.get_ticks() - start_ticks) / 1000

            timer = game_font.render(
                f'남은 시간 : {int(total_time - elapsed_time)}    생존 : {len(preys)} / {len(init_preys)}', True, (0, 0, 0))
            screen.blit(timer, ((screen_width - timer.get_size()[0]) / 2, 15))

            pygame.display.update()

            if elapsed_time >= total_time or len(preys) == 0:
                print(f'total_frame : {total_frame}', f'survived : {len(preys)}')
                if len(preys) != 0 and total_frame < fps * total_time * 0.95:
                    print('no record for this try')
                    self.simulate(n_preys, total_time, ff)
                    break
                self.recoder.record(predator, init_preys, preys)
                running = False
        # 종료

        # 마우스 왼쪽 클릭 해야 종료
        if not shutdown_immediately:
            while True:
                event = pygame.event.poll()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    break

        pygame.quit()


class Circle:
    def __init__(self, screen_width, screen_height, image,
                 r_min=5, r_max=40, v_x_min=30, v_x_max=300, v_y_min=30, v_y_max=300):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.r = r_min + (r_max - r_min) * np.random.random()
        self.image = pygame.transform.scale(image, (2 * self.r, 2 * self.r))
        self.init_pos_x = (screen_width - self.r) * np.random.random()
        self.init_pos_y = (screen_height - self.r) * np.random.random()
        self.pos_x = self.init_pos_x
        self.pos_y = self.init_pos_y
        self.init_v_x = (v_x_min + (v_x_max - v_x_min) * np.random.random()) * (2 * round(np.random.random()) - 1)
        self.init_v_y = (v_y_min + (v_y_max - v_y_min) * np.random.random()) * (2 * round(np.random.random()) - 1)
        self.v_x = self.init_v_x
        self.v_y = self.init_v_y

    def move(self, dt):
        self.pos_x += self.v_x * dt / 1000
        self.pos_y += self.v_y * dt / 1000

        if self.pos_x <= 0:
            self.pos_x = -self.pos_x
            self.v_x = -self.v_x
        elif self.pos_x >= self.screen_width - 2 * self.r:
            self.pos_x = 2 * self.screen_width - 4 * self.r - self.pos_x
            self.v_x = -self.v_x

        if self.pos_y <= 0:
            self.pos_y = -self.pos_y
            self.v_y = -self.v_y
        elif self.pos_y >= self.screen_height - 2 * self.r:
            self.pos_y = 2 * self.screen_height - 4 * self.r - self.pos_y
            self.v_y = -self.v_y

        image_rect = self.image.get_rect()
        image_rect.left = self.pos_x
        image_rect.top = self.pos_y

    def collide(self, other):
        r_sum = self.r + other.r
        x_delta = abs(self.pos_x + self.r - other.pos_x - other.r)
        y_delta = abs(self.pos_y + self.r - other.pos_y - other.r)
        if x_delta > r_sum:
            return False
        if y_delta > r_sum:
            return False
        return np.power(x_delta, 2) + np.power(y_delta, 2) <= np.power(r_sum, 2)


class Recorder:
    def __init__(self, volume_to_file=10000, file_index=1):
        self.volume_to_file = volume_to_file
        self.data = []
        self.file_index = file_index
        self.total = 0
        self.survived = 0

    def record(self, predator, prey_init, prey_survived):
        indexes_survived = prey_survived.keys()
        for k in prey_init:
            self.add_one(predator, prey_init[k], k in indexes_survived)
            if len(self.data) >= self.volume_to_file:
                self.make_csv()
        print(f'recorded: {len(self.data)}')
        print(f'누적 생존률 : {self.survived / self.total}')

    def add_one(self, predator, prey, survived):
        about_predator = [predator.r, predator.pos_x, predator.pos_y, predator.v_x, predator.v_y]
        about_prey = [prey.r, prey.pos_x, prey.pos_y, prey.v_x, prey.v_y, survived]
        self.data.append(about_predator + about_prey)
        self.total += 1
        if survived:
            self.survived += 1

    def make_csv(self, reset_data=True):
        self.data = np.array(self.data)
        df = pd.DataFrame({
            'predator_radius': self.data[:, 0],
            'predator_pos_x': self.data[:, 1],
            'predator_pos_y': self.data[:, 2],
            'predator_vel_x': self.data[:, 3],
            'predator_vel_y': self.data[:, 4],
            'prey_radius': self.data[:, 5],
            'prey_pos_x': self.data[:, 6],
            'prey_pos_y': self.data[:, 7],
            'prey_vel_x': self.data[:, 8],
            'prey_vel_y': self.data[:, 9],
            'prey_survived': self.data[:, 10]
        })
        df.to_csv(f'./data/data({self.file_index}).csv')
        self.file_index += 1
        if reset_data:
            self.data = []


from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QApplication, QGraphicsScene, QGraphicsView, QGraphicsRectItem, QGraphicsEllipseItem, QStackedWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPen, QColor
import random

class ArkanoidMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Arkanoid")
        self.resize(800, 600)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.stacked_widget = QStackedWidget()
        self.central_layout = QVBoxLayout(self.central_widget)
        self.central_layout.addWidget(self.stacked_widget)

        self.init_menu_screen()

    def init_menu_screen(self):
        menu_widget = QWidget()
        layout = QVBoxLayout(menu_widget)
        layout.setAlignment(Qt.AlignCenter)

        title_label = QLabel("Arkanoid")
        title_label.setFont(QFont("Impact", 32))
        layout.addWidget(title_label)

        play_button = QPushButton("Play Game")
        play_button.setFixedSize(300, 70)
        play_button.clicked.connect(self.show_game_screen)
        layout.addWidget(play_button)

        help_button = QPushButton("Help")
        help_button.setFixedSize(300, 70)
        help_button.clicked.connect(self.show_help_screen)
        layout.addWidget(help_button)

        exit_button = QPushButton("Exit Game")
        exit_button.setFixedSize(300, 70)
        exit_button.clicked.connect(self.close)
        layout.addWidget(exit_button)

        self.stacked_widget.addWidget(menu_widget)

    def show_game_screen(self):
        game_widget = ArkanoidGame()
        self.stacked_widget.addWidget(game_widget)
        self.stacked_widget.setCurrentWidget(game_widget)

    def show_help_screen(self):
        help_text = """
        Арканоид — это классическая аркадная игра, в которой игрок управляет подвижной платформой в 
        нижней части экрана и использует ее, чтобы отбивать мяч и разрушать блоки, расположенные в 
        верхней части экрана.

        Правила игры

        * Цель игры — разрушить все блоки на экране.
        * Управление — игрок управляет платформой с мышки.
        * Мяч — мяч движется по экрану по диагонали, отскакивая от стен, блоков и платформы.
        * Блоки — блоки расположены в верхней части экрана и имеют разные характеристики.
        * Бонусы — некоторые блоки содержат бонусы,например, увеличить размер платформы, уменьшить 
        размер  платформы усиление мяча.
        * Проигрыш — игрок проигрывает, если мяч падает за пределы платформы и у него не остаётся 
        жизней.

        Геймплей

        Игрок использует платформу для того, чтобы отбивать мяч и направлять его в блоки.
        Когда мяч попадает в блок, блок разрушается, а игрок получает очки. 
        Если мяч попадает в бонусный блок, игрок получает соответствующий бонус с вероятностью 10%.
        """

        help_widget = QWidget()
        layout = QVBoxLayout(help_widget)
        layout.setAlignment(Qt.AlignCenter)

        help_label = QLabel(help_text)
        help_label.setFont(QFont("Arial", 12))
        layout.addWidget(help_label)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.show_menu_screen)
        layout.addWidget(close_button)

        self.stacked_widget.addWidget(help_widget)
        self.stacked_widget.setCurrentWidget(help_widget)


    def show_menu_screen(self):
        self.stacked_widget.setCurrentIndex(0)  # Index 0 corresponds to menu screen

    def closeEvent(self, event):
        if self.stacked_widget.currentIndex() != 0:
            self.show_menu_screen()
            event.ignore()
        else:
            event.accept()

class Bonus(QGraphicsRectItem):
    def __init__(self, bonus_type, x, y):
        super().__init__(0, 0, 30, 10)
        self.bonus_type = bonus_type
        self.setPos(x, y)

        if bonus_type == 1:
            self.setBrush(Qt.green)  # Increase platform length
        elif bonus_type == 2:
            self.setBrush(Qt.red)  # Decrease platform length
        elif bonus_type == 3:
            self.setBrush(Qt.blue)  # Ball breaks gray bricks

    def move(self):
        self.setY(self.y() + 2)  # Move downwards

class ArkanoidGame(QGraphicsView, QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(800, 600)

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.platform = QGraphicsRectItem(0, 0, 100, 20)
        self.platform.setPos(200, 400)
        self.scene.addItem(self.platform)
        self.platform.setBrush(QColor("#40E0D0"))

        self.ball = QGraphicsRectItem(0, 0, 12, 12)
        self.ball.setPos(240, 380)
        self.scene.addItem(self.ball)
        self.ball.setBrush(QColor("#DC143C"))

        layout = QVBoxLayout(self)
        self.life = 3
        self.life_indicators = []  # List to hold the life indicator circles
        self.create_life_indicators()

        self.score = 0
        self.score_label = QLabel("Score: " + str(self.score))
        self.score_label.setFont(QFont("Impact", 32))
        self.score_label.setStyleSheet("color: black")
        layout.addWidget(self.score_label, alignment=Qt.AlignTop)

        self.bricks = []
        self.bonuses = []
        self.generate_bricks() # Call generate_bricks function for random layout

        self.game_started = False  # Flag to track game start
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(16)

        self.ball_dx = 2
        self.ball_dy = -2

    def generate_bricks(self):
        # Define brick properties (width, height, spacing)
        brick_width = 75
        brick_height = 20
        brick_spacing_h = 4
        brick_spacing_v = 2

        # Calculate number of rows and columns based on available space
        num_rows = 5
        num_cols = 10

        for row in range(num_rows):
            for col in range(num_cols):
                # Randomly decide to create a brick
                if random.random() < 0.7:
                    brick = QGraphicsRectItem(0, 0, brick_width, brick_height)
                    x_pos = 10 + col * (brick_width + brick_spacing_h)
                    y_pos = 10 + row * (brick_height + brick_spacing_v)
                    brick.setPos(x_pos, y_pos)
                    brick.setBrush(QColor("#CD5C5C"))
                    is_gray = random.random() < 0.1 # Adjust probability (0.2 = 20% chance)
                    is_black = random.random() < 0.1

                    if is_black:
                        brick.setBrush(Qt.black)

                    if is_gray:
                        brick.setBrush(Qt.gray) # Set a different color for indestructible bricks

                    self.scene.addItem(brick)
                    self.bricks.append(brick)

    def create_life_indicators(self):
        x = 700
        y = -100
        radius = 10
        for i in range(self.life):
            life_indicator = QGraphicsEllipseItem(0, 0, 2 * radius, 2 * radius)
            life_indicator.setPos(x + i * (2 * radius + 5), y)
            life_indicator.setBrush(QColor("#FFA07A"))  # Salmon color
            self.scene.addItem(life_indicator)
            self.life_indicators.append(life_indicator)

    def update_life_indicators(self):
        for indicator in self.life_indicators:
            self.scene.removeItem(indicator)
        self.life_indicators.clear()
        self.create_life_indicators()

    def check_lives(self):
        if self.life <= 0:
            # Игрок проиграл
            mainWindow.show_menu_screen()


        if self.life_indicators:
            life_indicator = self.life_indicators.pop()
            self.scene.removeItem(life_indicator)
            self.game_started = False



    def check_restart_conditions(self):
        non_breakable_bricks = all(brick.brush().color() == Qt.black or (brick.brush().color() == Qt.gray and self.ball.brush().color() != Qt.red) for brick in self.bricks)
        if not self.bricks or non_breakable_bricks:
            self.ball.setPos(240, 380)
            self.bricks = []
            self.generate_bricks()
            self.life = 3
            self.game_started = False

    def update(self):
        if not self.game_started:
            return  # Don't update game logic if not started

        self.ball.setPos(self.ball.x() + self.ball_dx, self.ball.y() + self.ball_dy)
        collision_occurred = False  # Флаг для отслеживания столкновений в текущем обновлении
        if self.ball.collidesWithItem(self.platform):
            ball_rect = self.ball.boundingRect()
            platform_rect = self.platform.boundingRect()


            platformleft_collision = self.ball.x() >= self.platform.x() + self.platform.boundingRect().width() - 2
            platformright_collision = self.ball.x() + self.ball.boundingRect().width() <= self.platform.x() + 2
            platformtop_collision = self.ball.y() >= self.platform.y() + self.platform.boundingRect().height() - 2
            platformbottom_collision = self.ball.y() + self.ball.boundingRect().height() <= self.platform.y() + 2

            if platformleft_collision or platformright_collision:
                self.ball_dx = -self.ball_dx
            if platformtop_collision or platformbottom_collision:
                self.ball_dy = -self.ball_dy

        for brick in self.bricks:
            brick_rect = brick.boundingRect()
            ball_rect = self.ball.boundingRect()
            if self.ball.collidesWithItem(brick):
                # Check if the brick is not gray (indestructible)
                if brick.brush().color() == Qt.gray:
                    if self.ball.brush().color() == Qt.red:
                        self.scene.removeItem(brick)
                        self.bricks.remove(brick)
                elif brick.brush().color() != Qt.black:
                    self.scene.removeItem(brick)
                    self.bricks.remove(brick)
                    if brick.brush().color() == Qt.gray:
                        self.score += 30
                    else:
                        self.score += 10
                    self.score_label.setText("Score: " + str(self.score))
                    if random.random() < 0.1:  # 10% chance to drop a bonus
                        bonus_type = random.randint(1, 3)
                        bonus = Bonus(bonus_type, brick.x(), brick.y())
                        self.scene.addItem(bonus)
                        self.bonuses.append(bonus)

                left_collision = self.ball.x() >= brick.x() + brick.boundingRect().width() - 2
                right_collision = self.ball.x() + self.ball.boundingRect().width() <= brick.x() + 2
                top_collision = self.ball.y() >= brick.y() + brick.boundingRect().height() - 2
                bottom_collision = self.ball.y() + self.ball.boundingRect().height() <= brick.y() + 2


                if not collision_occurred:  # Если столкнование с блоком еще не было обработано
                    if left_collision or right_collision:
                        self.ball_dx = -self.ball_dx
                    if top_collision or bottom_collision:
                        self.ball_dy = -self.ball_dy

                collision_occurred = True  # Отмечаем, что произошло столкновение


        for bonus in self.bonuses:
            bonus.move()
            if bonus.collidesWithItem(self.platform):
                self.apply_bonus(bonus.bonus_type)
                self.scene.removeItem(bonus)
                self.bonuses.remove(bonus)
                collision_occurred = True  # Отмечаем, что произошло столкновение
            elif bonus.y() > 430:
                self.scene.removeItem(bonus)
                self.bonuses.remove(bonus)

        if self.ball.x() <= 2 or self.ball.x() >= 790:
            self.ball_dx = -self.ball_dx
        if self.ball.y() <= 20:
            self.ball_dy = -self.ball_dy
        if self.ball.y() >= 420:
            self.life -= 1
            self.ball.setPos(self.platform.pos().x() + 50, self.platform.pos().y() - 20)
            self.ball_dy = -self.ball_dy
            self.check_lives()

        self.check_restart_conditions()

    def mouseReleaseEvent(self, event):  # Left mouse click to start game
        if event.button() == Qt.LeftButton and not self.game_started:
            self.ball.setVisible(True)  # Show the ball
            self.game_started = True

    def apply_bonus(self, bonus_type):
        if bonus_type == 1 and self.platform.rect().width() <= 140:
            self.platform.setRect(self.platform.rect().x(), self.platform.rect().y(), self.platform.rect().width() + 20, self.platform.rect().height())
        elif bonus_type == 2 and self.platform.rect().width() >= 40:
            self.platform.setRect(self.platform.rect().x(), self.platform.rect().y(), self.platform.rect().width() - 20, self.platform.rect().height())
        elif bonus_type == 3:
            self.ball.setBrush(Qt.red)  # Indicate that the ball can break gray bricks

    def mouseMoveEvent(self, event):
        if not self.game_started:
            # Если игра не начата, перемещаем платформу и мяч вместе
            x = event.position().x()
            if 52 <= x <= 750:  # Ограничиваем координату X платформы от 100 до 545
                self.platform.setPos(x - 50, 400)
                self.ball.setPos(x - 10, 380)  # Перемещаем мяч вместе с платформой
        else:
            # Иначе, если игра начата, перемещаем только платформу
            x = event.position().x()
            if 52 <= x <= 750:
                self.platform.setPos(x - 50, 400)


if __name__ == "__main__":
    app = QApplication([])
    mainWindow = ArkanoidMainWindow()
    mainWindow.show()
    app.exec()

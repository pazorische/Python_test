import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QGridLayout, QMessageBox, \
    QTextBrowser
from PyQt5.QtCore import QSize, Qt
import random
from collections import deque


class TileButton(QPushButton):
    def __init__(self, value=0, row=0, col=0, parent=None):
        super().__init__(parent)
        self.setMinimumSize(QSize(80, 80))
        self.setMaximumSize(QSize(80, 80))
        self.value = value
        self.row = row
        self.col = col
        self.update_style()

    def set_value(self, value):
        self.value = value
        self.update_style()

    def destroy(self):
        self.layout.removeWidget()

    def update_style(self):
        color_map = {
            1: "#ADD8E6",  # Легкий голубой
            2: "#FFA07A",  # Светло-коралловый
            3: "#98FB98",  # Бледно-зеленый
            4: "#FFB6C1",  # Розовато-пурпурный
            5: "#FFD700",  # Золотой
            6: "#CD5C5C",  # Индиго
            7: "#20B2AA",  # Темно-циан
            8: "#7FFF00",  # Лаймовый
            9: "#FF4500",  # Оранжево-красный
            10: "#DA70D6",  # Орхидея
            11: "#00FFFF",  # Аквамарин
            12: "#FF1493",  # Глубокий розовый
        }
        self.setStyleSheet(
            f"background-color: {color_map.get(self.value, '#FFF')}; color: black; font: bold 24px; border: 2px solid #888;")
        self.setText(str(self.value))


class RulesWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rules")
        self.setGeometry(100, 100, 900, 900)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.text_browser = QTextBrowser()
        self.layout.addWidget(self.text_browser)

        self.load_rules()

    def load_rules(self):
        rules_html = """
        <h1>Правила игры</h1>
        <p>Пара фишек с одинаковыми числами образуют одну с числом, на единицу большим, чем у соединяющихся. Обязательное скольжение фишки к краю при перемещении отменено, в этой игре Вы можете поставить ее туда куда надо. Хотя, это «куда надо» очень быстро заканчивается, то есть пустых клеток не остается уже на первых паре десятков ходов.</p>
        """
        self.text_browser.setHtml(rules_html)


class TwelveGame(QMainWindow):
    def __init__(self):
        super().__init__()

        self.matrix = matrix = [
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0]
        ]
        self.setWindowTitle("Twelve Game")
        self.setGeometry(100, 100, 400, 400)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.grid_layout = QGridLayout()
        self.layout.addLayout(self.grid_layout)

        self.tiles = [[None] * 5 for _ in range(5)]
        self.init_grid()

        self.moves_left = 11
        self.selected_tile = None

        self.setup_ui()

    def setup_ui(self):
        self.show_rules_button = QPushButton("Показать правила")
        self.show_rules_button.clicked.connect(self.show_rules)
        self.layout.addWidget(self.show_rules_button)

        self.new_game_button = QPushButton("Новая игра")
        self.new_game_button.clicked.connect(self.reset_game)
        self.layout.addWidget(self.new_game_button)

        self.finish_game_button = QPushButton("Закончить игру")
        self.finish_game_button.clicked.connect(self.close)
        self.layout.addWidget(self.finish_game_button)

    def init_grid(self):
        array = []
        while len(array) < 3:
            num = random.randint(0, 24)
            if num not in array:
                array.append(num)

        # Создаем только три заполненных кубика
        for i in range(25):
            if i in array:
                value = random.randint(1, 3)
                row, col = random.randint(0, 4), random.randint(0, 4)
                while self.tiles[row][col] is not None:
                    row, col = random.randint(0, 4), random.randint(0, 4)
                self.matrix[row][col] = 1
                tile_button = TileButton(value, row, col)
                tile_button.clicked.connect(lambda _, r=row, c=col: self.tile_clicked(r, c))
                self.grid_layout.addWidget(tile_button, row, col)
                self.tiles[row][col] = tile_button
            else:
                value = 0
                row, col = random.randint(0, 4), random.randint(0, 4)
                while self.tiles[row][col] is not None:
                    row, col = random.randint(0, 4), random.randint(0, 4)
                tile_button = TileButton(value, row, col)
                tile_button.clicked.connect(lambda _, r=row, c=col: self.tile_clicked(r, c))
                self.grid_layout.addWidget(tile_button, row, col)
                self.tiles[row][col] = tile_button

    def tile_clicked(self, row, col):
        if self.selected_tile:
            if self.selected_tile.row != row or self.selected_tile.col != col:
                selected_row, selected_col = self.selected_tile.row, self.selected_tile.col
                selected_value = self.selected_tile.value
                clicked_value = self.tiles[row][col].value
                passed = self.is_reachable(self.matrix, self.selected_tile.row, self.selected_tile.col, row, col)
                if selected_value == clicked_value and passed == True:
                    if clicked_value != 0:
                        new_value = selected_value + 1
                        self.tiles[row][col].set_value(new_value)
                        self.selected_tile.set_value(0)
                        self.matrix[self.selected_tile.row][self.selected_tile.col] = 0
                        self.selected_tile = None
                        self.moves_left -= 1
                        self.update_status()
                        if new_value == 12:
                            self.game_over()
                        else:
                            # Создаем новый случайный кубик
                            self.create_random_tile()
                else:
                    if clicked_value == 0 and passed == True:
                        self.matrix[self.selected_tile.row][self.selected_tile.col] = 0
                        self.matrix[row][col] = 1
                        self.tiles[row][col].set_value(selected_value)
                        self.selected_tile.set_value(0)
                        self.selected_tile = None
                        self.update_status()
                        self.create_random_tile()
                    else:
                        self.selected_tile = None
                    self.selected_tile = None
            else:
                self.selected_tile = None
        else:
            self.change_border(row, col)
            self.selected_tile = self.tiles[row][col]

    def create_random_tile(self):
        flag = 1
        counter = 0
        while flag == 1:
            counter += 1
            if counter == 25:
                self.game_lose()
            row, col = random.randint(0, 4), random.randint(0, 4)
            if self.tiles[row][col].value == 0:
                self.matrix[row][col] = 1
                self.tiles[row][col].set_value(random.randint(1, 3))
                self.update_status()
                flag = 0

    def is_reachable(self, matrix, startrow, startcol, endrow, endcol):
        def pack(row, column):
            return f"{row}:{column}"

        def unpack(cell):
            return list(map(int, cell.split(':')))

        visited = set()

        def is_valid_neighbour(row, column):
            if row == endrow and column == endcol:
                return True
            if row < 0 or row >= len(matrix):
                return False
            if column < 0 or column >= len(matrix[row]):
                return False
            cell = pack(row, column)
            if cell in visited:
                return False
            return matrix[row][column] == 0

        step = {pack(startrow, startcol): [pack(endrow, endcol)]}

        while step:
            next_step = {}
            for cell, path in step.items():
                row, column = unpack(cell)
                if row == endrow and column == endcol:
                    return True
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    next_row, next_column = row + dr, column + dc
                    if is_valid_neighbour(next_row, next_column):
                        new_cell = pack(next_row, next_column)
                        new_path = path + [new_cell]
                        next_step[new_cell] = new_path
                        visited.add(new_cell)
            step = next_step

        return False

    def reset_game(self):
        # Очищаем сетку от предыдущих кубиков
        for row in range(5):
            for col in range(5):
                if self.tiles[row][col]:
                    self.tiles[row][col].deleteLater()  # Удаляем кнопку из памяти
                    self.tiles[row][col] = None  # Убираем ссылку на кнопку

        # Переинициализируем игру
        self.init_grid()
        self.moves_left = 11
        self.update_status()

    def update_status(self):
        self.statusBar().showMessage(f"Moves left: {self.moves_left}")

    def game_over(self):
        QMessageBox.information(self, "Congratulations!", "You've reached 12! You won!")

    def game_lose(self):
        QMessageBox.information(self, "You lose!", "No more space!")

    def show_rules(self):
        self.rules_window = RulesWindow()
        self.rules_window.show()

    def change_border(self, row, col):
        color_map = {
            1: "#ADD8E6",  # Легкий голубой
            2: "#FFA07A",  # Светло-коралловый
            3: "#98FB98",  # Бледно-зеленый
            4: "#FFB6C1",  # Розовато-пурпурный
            5: "#FFD700",  # Золотой
            6: "#CD5C5C",  # Индиго
            7: "#20B2AA",  # Темно-циан
            8: "#7FFF00",  # Лаймовый
            9: "#FF4500",  # Оранжево-красный
            10: "#DA70D6",  # Орхидея
            11: "#00FFFF",  # Аквамарин
            12: "#FF1493",  # Глубокий розовый
        }
        self.tiles[row][col].setStyleSheet(
            f"background-color: {color_map.get(self.tiles[row][col].value, '#FFF')}; color: black; font: bold 24px; border: 3px solid red;")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TwelveGame()
    window.show()
    sys.exit(app.exec_())

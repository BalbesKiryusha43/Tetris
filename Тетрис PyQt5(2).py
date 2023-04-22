import random
import sys
from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QFont, QPixmap
from PyQt5.QtWidgets import QMainWindow, QFrame, QDesktopWidget, QApplication, QHBoxLayout, QSizePolicy, QWidget, QPushButton, QGridLayout, QMessageBox

class Tetris(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.tboard = Board(self)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        # Создаем центральный виджет и устанавливаем для него grid layout
        self.centralwidget = QWidget(self)
        self.gridLayout = QGridLayout(self.centralwidget)

        # Создаем горизонтальный layout и устанавливаем в него grid layout для кнопок "Пауза" и "Начать игру заново"
        self.horizontalLayout_2 = QHBoxLayout()
        self.gridLayout_1 = QGridLayout(self.centralwidget)

        # Создаем кнопку "Пауза" и устанавливаем ее размеры и шрифт. Также соединяем ее с методом pause класса Board
        self.pausebutton = QPushButton("Пауза", self.centralwidget)
        self.pausebutton.setFont(QFont('Times New Roman', 18))
        self.pausebutton.setStyleSheet("background-color: white; color: black;")
        self.pausebutton.setFixedSize(300, 50)
        self.pausebutton.clicked.connect(self.tboard.pause)
        self.gridLayout_1.addWidget(self.pausebutton)

        # Создаем кнопку "Начать игру заново" и устанавливаем ее размеры и шрифт. Также соединяем ее с методом restart_game класса Board
        self.button1 = QPushButton("Начать игру заново", self.centralwidget)
        self.button1.setFont(QFont('Times New Roman', 18))
        self.button1.setStyleSheet("background-color: white; color: black;")
        self.button1.setFixedSize(300, 50)
        self.gridLayout_1.addWidget(self.button1)
        self.button1.clicked.connect(self.tboard.restart_game)

        # Устанавливаем политику размера и горизонтальный layout с grid layout кнопок в главный grid layout
        self.tboard.setSizePolicy(sizePolicy)
        self.horizontalLayout_2.addWidget(self.tboard)
        self.horizontalLayout_2.addLayout(self.gridLayout_1)
        self.gridLayout.addLayout(self.horizontalLayout_2, 2, 0, 1, 1)

        # Устанавливаем фон центрального виджета и устанавливаем его в качестве главного виджета
        self.centralwidget.setStyleSheet("background-color: lavender;")
        self.centralwidget.setLayout(self.gridLayout)
        self.setCentralWidget(self.centralwidget)

        # Создаем строку статуса и устанавливаем шрифт. Соединяем сигнал msg2Statusbar класса Board со слотом showMessage строки статуса
        self.statusbar = self.statusBar()
        self.statusbar.setFont(QFont('Times New Roman', 18))
        self.tboard.msg2Statusbar[str].connect(self.statusbar.showMessage)

        # Запускаем игру, устанавливаем размеры окна, устанавливаем окно по центру экрана, устанавливаем заголовок окна и отображаем его
        self.tboard.start()
        self.resize(700, 730)
        self.center()
        self.setWindowTitle('Тетрис')
        self.show()

    # Функция для обработки события закрытия окна игры
    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Выход из игры', 'Вы точно хотите покинуть игру?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    # Функция для центрирования окна игры на экране
    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(int((screen.width() - size.width()) / 2),
                  int((screen.height() - size.height()) / 2))

class Board(QFrame):
    msg2Statusbar = pyqtSignal(str)
    BoardWidth = 10 # Клеток в ширину
    BoardHeight = 20 # Клеток в высоту
    Speed = 500 # Начальная скорость падения фигур

    def __init__(self, parent):
        super().__init__(parent)
        self.initBoard()

    def initBoard(self):
        self.timer = QBasicTimer()
        self.isWaitingAfterLine = False
        self.curX = 0
        self.curY = 0
        self.numLinesRemoved = 0
        self.board = []
        self.setFocusPolicy(Qt.StrongFocus)
        self.isStarted = False
        self.isPaused = False
        self.clearBoard()

    # возвращает форму фигуры в указанных координатах доски
    def shapeAt(self, x, y):
        return self.board[(y * Board.BoardWidth) + x]

    # устанавливает форму фигуры в указанных координатах доски
    def setShapeAt(self, x, y, shape):
        self.board[(y * Board.BoardWidth) + x] = shape

    # Возвращает ширину одной клетки доски в пикселях.
    def squareWidth(self):
        return self.contentsRect().width() // Board.BoardWidth

    # Возвращает высоту одной клетки доски в пикселях.
    def squareHeight(self):
        return self.contentsRect().height() // Board.BoardHeight

    # Функция для начала игры
    def start(self):
        if self.isPaused:
            return
        self.isStarted = True
        self.isWaitingAfterLine = False
        self.numLinesRemoved = 0
        self.clearBoard()
        self.msg2Statusbar.emit(str(f'Счёт:{self.numLinesRemoved}'))  # Счётчик
        self.newPiece()
        self.timer.start(Board.Speed, self)

    # Функция для паузы игры
    def pause(self):
        if not self.isStarted:
            return
        self.isPaused = not self.isPaused
        if self.isPaused:
            self.timer.stop()
            self.msg2Statusbar.emit(str(f'Пауза. Счёт:{self.numLinesRemoved}'))
        else:
            self.timer.start(Board.Speed, self)
            self.msg2Statusbar.emit(str(f'Счёт:{self.numLinesRemoved}'))
        self.update()

    # Функция для перезапуска игры
    def restart_game(self):
        self.isStarted = False
        self.numLinesRemoved = 0
        self.msg2Statusbar.emit(str(f'Счёт:{self.numLinesRemoved}'))
        self.initBoard()  # Очистить игровое поле и установить начальные значения
        self.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.contentsRect()
        # Отрисовываем фон
        background = QPixmap("123.png")  # путь к файлу изображения
        painter.drawPixmap(rect, background)
        # Отрисовываем сетку
        boardTop = rect.bottom() - Board.BoardHeight * self.squareHeight()
        for i in range(Board.BoardHeight + 1):
            painter.drawLine(rect.left(), boardTop + i * self.squareHeight(), rect.right(),
                             boardTop + i * self.squareHeight())
        for j in range(Board.BoardWidth + 1):
            painter.drawLine(rect.left() + j * self.squareWidth(), boardTop, rect.left() + j * self.squareWidth(),
                             rect.bottom())
        # Отрисовываем фигуры и текущую фигуру
        for i in range(Board.BoardHeight):
            for j in range(Board.BoardWidth):
                shape = self.shapeAt(j, Board.BoardHeight - i - 1)
                if shape != Tetrominoe.NoShape:
                    self.drawSquare(painter,
                                    rect.left() + j * self.squareWidth(),
                                    boardTop + i * self.squareHeight(), shape)
        if self.curPiece.shape() != Tetrominoe.NoShape:
            for i in range(4):
                x = self.curX + self.curPiece.x(i)
                y = self.curY - self.curPiece.y(i)
                self.drawSquare(painter, rect.left() + x * self.squareWidth(),
                                boardTop + (Board.BoardHeight - y - 1) * self.squareHeight(),
                                self.curPiece.shape())

    # Обработчик событий нажатия клавиш на клавиатуре
    def keyPressEvent(self, event):
        if not self.isStarted or self.curPiece.shape() == Tetrominoe.NoShape:
            super(Board, self).keyPressEvent(event)
            return
        key = event.key()
        if key == Qt.Key_Left:
            self.tryMove(self.curPiece, self.curX - 1, self.curY)
        elif key == Qt.Key_Right:
            self.tryMove(self.curPiece, self.curX + 1, self.curY)
        elif key == Qt.Key_Down:
            self.oneLineDown()
        elif key == Qt.Key_Up:
            self.tryMove(self.curPiece.rotateLeft(), self.curX, self.curY)
        elif key == Qt.Key_Space:
            self.dropDown()
        else:
            super(Board, self).keyPressEvent(event)

    # Функция отвечает за перемещение фигур на игровом поле и увеличение скорости игры при наборе очков.
    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            if self.isWaitingAfterLine:
                self.isWaitingAfterLine = False
                self.newPiece()
            else:
                self.oneLineDown()
            current_speed = Board.Speed - 10 * (
                        self.numLinesRemoved // 1)  # увеличиваем скорость каждый раз на 10 при увеличении счёта на 1
            self.timer.start(current_speed, self)
        else:
            super(Board, self).timerEvent(event)

    # Функция очищает игровое поле и устанавливает все клетки в значение 0
    def clearBoard(self):
        for i in range(Board.BoardHeight * Board.BoardWidth):
            self.board.append(0)
        for i in range(Board.BoardHeight * Board.BoardWidth):
            self.board.append(Tetrominoe.NoShape)
        self.numLinesRemoved = 0

    # Функция ускоряет падение текущей фигуры до конца игрового поля.
    def dropDown(self):
        newY = self.curY
        while newY > 0:
            if not self.tryMove(self.curPiece, self.curX, newY - 1):
                break
            newY -= 1
        self.pieceDropped()

    # Функция смещает текущую фигуру на одну клетку вниз
    def oneLineDown(self):
        if not self.tryMove(self.curPiece, self.curX, self.curY - 1):
            self.pieceDropped()

    # Функция вызывается после того, как фигура упала на дно или на другую фигуру. Она устанавливает фигуру на доску, вызывает функцию removeFullLines и создает новую фигуру.
    def pieceDropped(self):
        for i in range(4):
            x = self.curX + self.curPiece.x(i)
            y = self.curY - self.curPiece.y(i)
            self.setShapeAt(x, y, self.curPiece.shape())
        self.removeFullLines()
        if not self.isWaitingAfterLine:
            self.newPiece()

    # Функция ищет и удаляет полные линии на доске.
    def removeFullLines(self):
        numFullLines = 0
        rowsToRemove = []
        for i in range(Board.BoardHeight):
            n = 0
            for j in range(Board.BoardWidth):
                if not self.shapeAt(j, i) == Tetrominoe.NoShape:
                    n = n + 1
            if n == 10:
                rowsToRemove.append(i)
        rowsToRemove.reverse()
        for m in rowsToRemove:
            for k in range(m, Board.BoardHeight):
                for l in range(Board.BoardWidth):
                    self.setShapeAt(l, k, self.shapeAt(l, k + 1))
        numFullLines = numFullLines + len(rowsToRemove)
        if numFullLines > 0:
            self.numLinesRemoved = self.numLinesRemoved + numFullLines
            self.msg2Statusbar.emit(str(f'Счёт:{self.numLinesRemoved}'))
            self.isWaitingAfterLine = True
            self.curPiece.setShape(Tetrominoe.NoShape)
            self.update()

    # Функция создает новую фигуру
    def newPiece(self):
        self.curPiece = Shape()
        self.curPiece.setRandomShape()
        self.curX = Board.BoardWidth // 2 + 1
        self.curY = Board.BoardHeight - 1 + self.curPiece.minY()
        if not self.tryMove(self.curPiece, self.curX, self.curY):
            self.curPiece.setShape(Tetrominoe.NoShape)
            self.timer.stop()
            self.isStarted = False
            self.msg2Statusbar.emit((str(f'Счёт:{self.numLinesRemoved}''. Игра окончена.')))

    # Функция проверяет возможность перемещения фигуры в новое место на доске
    def tryMove(self, newPiece, newX, newY):
        for i in range(4):
            x = newX + newPiece.x(i)
            y = newY - newPiece.y(i)
            if x < 0 or x >= Board.BoardWidth or y < 0 or y >= Board.BoardHeight:
                return False
            if self.shapeAt(x, y) != Tetrominoe.NoShape:
                return False
        self.curPiece = newPiece
        self.curX = newX
        self.curY = newY
        self.update()
        return True

    # Функция вызывается для рисования одного квадрата игрового поля. Он принимает координаты квадрата и его форму, и заливает квадрат цветом.
    def drawSquare(self, painter, x, y, shape):
        colorTable = [0x000000, 0xCC6666, 0x66CC66, 0x6666CC,
                      0xCCCC66, 0xCC66CC, 0x66CCCC, 0xDAAA00]
        color = QColor(colorTable[shape])
        painter.fillRect(x + 1, y + 1, self.squareWidth() - 2,
                         self.squareHeight() - 2, color)
        painter.setPen(color.lighter())
        painter.drawLine(x, y + self.squareHeight() - 1, x, y)
        painter.drawLine(x, y, x + self.squareWidth() - 1, y)
        painter.setPen(color.darker())
        painter.drawLine(x + 1, y + self.squareHeight() - 1,
                         x + self.squareWidth() - 1, y + self.squareHeight() - 1)
        painter.drawLine(x + self.squareWidth() - 1,
                         y + self.squareHeight() - 1, x + self.squareWidth() - 1, y + 1)

# Перечисление  для форм тетромино, которые могут принимать значения от 0 до 7.
class Tetrominoe(object):
    NoShape = 0
    ZShape = 1
    SShape = 2
    LineShape = 3
    TShape = 4
    SquareShape = 5
    LShape = 6
    MirroredLShape = 7

# Фигуры
class Shape(object):
    coordsTable = (
        ((0, 0), (0, 0), (0, 0), (0, 0)),
        ((0, -1), (0, 0), (-1, 0), (-1, 1)),
        ((0, -1), (0, 0), (1, 0), (1, 1)),
        ((0, -1), (0, 0), (0, 1), (0, 2)),
        ((-1, 0), (0, 0), (1, 0), (0, 1)),
        ((0, 0), (1, 0), (0, 1), (1, 1)),
        ((-1, -1), (0, -1), (0, 0), (0, 1)),
        ((1, -1), (0, -1), (0, 0), (0, 1))
    )

    def __init__(self):
        self.coords = [[0, 0] for i in range(4)]
        self.pieceShape = Tetrominoe.NoShape
        self.setShape(Tetrominoe.NoShape)

    def shape(self):
        return self.pieceShape

    # Функция принимает целочисленный параметр, который задает форму, и устанавливает координаты Тетромино в соответствии с указанной формой.
    def setShape(self, shape):
        table = Shape.coordsTable[shape]
        for i in range(4):
            for j in range(2):
                self.coords[i][j] = table[i][j]
        self.pieceShape = shape

    # Функция задает форму Тетромино в случайном порядке в диапазоне от 1 до 7.
    def setRandomShape(self):
        self.setShape(random.randint(1, 7))

    def x(self, index):
        return self.coords[index][0]

    def y(self, index):
        return self.coords[index][1]

    def setX(self, index, x):
        self.coords[index][0] = x

    def setY(self, index, y):
        self.coords[index][1] = y

    def minX(self):
        m = self.coords[0][0]
        for i in range(4):
            m = min(m, self.coords[i][0])
        return m

    def maxX(self):
        m = self.coords[0][0]
        for i in range(4):
            m = max(m, self.coords[i][0])
        return m

    def minY(self):
        m = self.coords[0][1]
        for i in range(4):
            m = min(m, self.coords[i][1])
        return m

    def maxY(self):
        m = self.coords[0][1]
        for i in range(4):
            m = max(m, self.coords[i][1])
        return m

    # Поворот влево на 90 градусов
    def rotateLeft(self):
        if self.pieceShape == Tetrominoe.SquareShape:
            return self
        result = Shape()
        result.pieceShape = self.pieceShape
        for i in range(4):
            result.setX(i, self.y(i))
            result.setY(i, -self.x(i))
        return result

    # Поворот вправо на 90 градусов
    def rotateRight(self):
        if self.pieceShape == Tetrominoe.SquareShape:
            return self
        result = Shape()
        result.pieceShape = self.pieceShape

        for i in range(4):
            result.setX(i, -self.y(i))
            result.setY(i, self.x(i))
        return result

# Запуск игры
if __name__ == '__main__':
    app = QApplication([])
    tetris = Tetris()
    sys.exit(app.exec_())

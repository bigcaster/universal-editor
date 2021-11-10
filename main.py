import sys
from PIL import Image, ImageEnhance
from audioplayer import AudioPlayer
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QTabWidget, QFileDialog, QLabel, \
    QLineEdit, QPushButton, QSlider, QDialog
from photoEditor import Ui_MainWindow
from textEditor import Ui_Form
from replaceDialog import RD_Ui_Form
from findDialog import Ui_Dialog
from infoDialog import Info_Ui_Dialog


class EmptyInput(Exception):
    pass


class App(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.w, self.h = 700, 500
        self.first_image_opened = None
        self.new_image = False
        self.setGeometry((1920 - self.w) // 2, (1080 - self.h) // 2 - 5, self.w, self.h)
        self.setWindowTitle('Универсальный редактор')
        for i, widget in enumerate(
                [self.lineEdit, self.pushButton, self.pushButton_2, self.pushButton_3, self.pushButton_4,
                 self.pushButton_5]):
            widget.resize(int(0.155 * self.w), 23)
            widget.move(int(0.013 * self.w) + i * (self.w // 100 + int(0.155 * self.w)), 10)
            if i > 0:
                widget.clicked.connect(self.run)
        self.label.move(int(0.025 * self.w), 40)
        self.image = QLabel(self)
        self.tabs = QTabWidget(self)
        self.tabs.move(100, 500)
        self.tab1 = FirstTab(self)
        self.tab2 = SecondTab(self)
        self.tab3 = ThirdTab(self)
        self.tab4 = FourthTab(self)
        self.tab5 = FifthTab(self)
        self.tab6 = SixthTab(self)
        self.tabs.addTab(self.tab6, 'Плеер')
        self.update_tabs()

    def initUI(self, x, y):
        height = y - 245
        self.w, self.h = int(max(600, x)), int(max(500, y))
        self.setGeometry((1920 - self.w) // 2, (1080 - self.h) // 2 - 5, self.w, self.h)
        for i, widget in enumerate(
                [self.lineEdit, self.pushButton, self.pushButton_2, self.pushButton_3, self.pushButton_4,
                 self.pushButton_5]):
            widget.resize(int(0.155 * self.w), 23)
            widget.move(int(0.013 * self.w) + i * (self.w // 100 + int(0.155 * self.w)), 10)
        self.label.move(int(0.025 * self.w), 40)
        self.image.move((self.w - self.image.width()) // 2, (self.h - 245 - height) // 2 + 70)

    def update_tabs(self):
        if self.first_image_opened:
            self.tabs.insertTab(0, self.tab5, "Эффекты")
            self.tabs.insertTab(0, self.tab4, "Цветовая гамма")
            self.tabs.insertTab(0, self.tab3, "Основная регулировка")
            self.tabs.insertTab(0, self.tab2, "Кадрирование")
            self.tabs.insertTab(0, self.tab1, "Обрезка")
            self.first_image_opened = False
        if self.new_image:
            self.tabs.setCurrentIndex(0)
            self.new_image = False
        self.tabs.show()
        self.tabs.resize(self.w + 20, 180)
        self.tabs.move(0, int(self.h - 160))
        self.reset_tabs()

    def reset_tabs(self):
        for tab in [self.tab1, self.tab3, self.tab4]:
            tab.reset()

    def run(self):
        self.label.clear()
        file_name = self.lineEdit.text()
        if self.sender() == self.pushButton:
            try:
                if not file_name:
                    raise EmptyInput
                self.im = Image.open(file_name)
            except EmptyInput:
                self.label.setText('Заполните поле ввода')
            except FileNotFoundError:
                self.label.setText(f'Файл "{file_name}" не найден')
            else:
                self.new_image = True
                self.open_image()
        elif self.sender() == self.pushButton_2:
            file_name = QFileDialog.getOpenFileName(self, 'Выбрать изображение', '')[0]
            try:
                if not file_name:
                    raise EmptyInput
                self.full_res_im = Image.open(file_name)
            except EmptyInput:
                self.label.setText('Выберите изображение')
            except Exception as e:
                self.label.setText(f'Ошибка: "{e}"')
            else:
                self.new_image = True
                self.open_image()
        elif self.sender() == self.pushButton_3:
            try:
                self.full_res_im.save(file_name)
            except AttributeError:
                self.label.setText('Нет открытого изображения')
            except ValueError:
                self.label.setText('Неверное имя или расширение файла')
        elif self.sender() == self.pushButton_4:
            try:
                self.full_res_im = self.orig_im
            except AttributeError:
                self.label.setText('Нет открытого изображения')
            else:
                self.open_image()
                self.reset_tabs()
        elif self.sender() == self.pushButton_5:
            self.textEditor = TextEditor()
            self.textEditor.show()
        self.label.resize(self.label.sizeHint())

    def open_image(self):
        if self.first_image_opened is None:
            self.first_image_opened = True
        width, height = self.full_res_im.size
        if width > 1750 or height > 755:
            width_coeff = width / 1750
            height_coeff = height / 755
            if width_coeff > height_coeff:
                width = min(1750, width)
                height = int(height / width_coeff)
            else:
                height = min(755, height)
                width = int(width / height_coeff)
        self.im = self.full_res_im.resize((width, height), Image.ANTIALIAS)
        self.im.save('pic2.png')
        self.im = Image.open('pic2.png')
        self.pixmap = QPixmap('pic2.png')
        self.image.resize(width, height)
        self.image.setPixmap(self.pixmap)
        self.label.clear()
        if self.new_image:
            self.orig_im = self.full_res_im
        self.initUI(width + 150, height + 245)
        self.update_tabs()

    def crop_image(self):
        x, y = self.tab1.x_line.text(), self.tab1.y_line.text()
        width, height = self.tab1.width_line.text(), self.tab1.height_line.text()
        if not (x.isdigit() and y.isdigit() and width.isdigit() and height.isdigit()):
            self.label.setText('Недопустимое значение')
        else:
            x, y, width, height = int(x), int(y), int(width), int(height)
            if x < 0 or y < 0 or width < 0 or height < 0 or x + width > self.im.width or \
                    height > self.im.height:
                self.label.setText('Недопустимое значение')
            else:
                self.im = self.im.crop((x, y, x + width, y + height))
                self.open_image()
        self.label.resize(self.label.sizeHint())

    def turn_image(self):
        if self.sender() == self.tab2.left_button:
            self.full_res_im = self.full_res_im.transpose(Image.ROTATE_90)
        elif self.sender() == self.tab2.right_button:
            self.full_res_im = self.full_res_im.transpose(Image.ROTATE_270)
        elif self.sender() == self.tab2.vertical_flip_button:
            self.full_res_im = self.full_res_im.transpose(Image.FLIP_LEFT_RIGHT)
        else:
            self.full_res_im = self.full_res_im.transpose(Image.FLIP_TOP_BOTTOM)
        self.open_image()

    def adjust_image(self):
        brightness_enhancer = ImageEnhance.Brightness(self.im.convert('RGB'))
        self.im = brightness_enhancer.enhance(self.tab3.brightness_slider.value() / 100)
        contrast_enhancer = ImageEnhance.Contrast(self.im.convert('RGB'))
        self.im = contrast_enhancer.enhance(self.tab3.contrast_slider.value() / 100)
        color_enhancer = ImageEnhance.Color(self.im.convert('RGB'))
        self.im = color_enhancer.enhance(self.tab3.saturation_slider.value() / 100)
        sharpness_enhancer = ImageEnhance.Sharpness(self.im.convert('RGB'))
        self.im = sharpness_enhancer.enhance(self.tab3.sharpness_slider.value() / 100)
        highlight = self.tab3.highlight_slider.value() - 100
        shadows = self.tab3.shadows_slider.value() - 100
        x, y = self.im.size
        pix = self.im.load()
        for i in range(x):
            for j in range(y):
                r, g, b = pix[i, j]
                summ = r + g + b
                if summ < 255:
                    pix[i, j] = int(r + shadows / 3), int(g + shadows / 3), int(b + shadows / 3)
                elif summ > 510:
                    pix[i, j] = int(r + highlight / 3), int(g + highlight / 3), int(
                        b + highlight / 3)
        self.reset_tabs()
        self.open_image()

    def color_image(self):
        self.im = self.im.convert('RGB')
        x, y = self.im.size
        pix = self.im.load()
        r_coeff = self.tab4.r_slider.value() / 100
        g_coeff = self.tab4.g_slider.value() / 100
        b_coeff = self.tab4.b_slider.value() / 100
        temperature = self.tab4.temperature_slider.value()
        hue = self.tab4.hue_slider.value()
        if temperature > 100:
            r_temperature = g_temperature = temperature - 100
            b_temperature = -r_temperature
        else:
            b_temperature = g_temperature = 100 - temperature
            r_temperature = -b_temperature
        if hue > 100:
            g_hue = hue - 100
            r_hue = b_hue = -g_hue // 2
        else:
            r_hue = b_hue = 100 - hue
            g_hue = -r_hue // 2
        for i in range(x):
            for j in range(y):
                r, g, b = pix[i, j]
                pix[i, j] = int(r * r_coeff + r_temperature + r_hue), int(
                    g * g_coeff + g_temperature + g_hue), int(b * b_coeff + b_temperature + b_hue)
        self.reset_tabs()
        self.open_image()

    def function_image(self):
        self.im = self.im.convert('RGB')
        x, y = self.im.size
        pix = self.im.load()
        if self.sender() == self.tab5.black_white_button:
            for i in range(x):
                for j in range(y):
                    if sum(pix[i, j]) > 382:
                        pix[i, j] = 255, 255, 255
                    else:
                        pix[i, j] = 0, 0, 0
        elif self.sender() == self.tab5.sepia_button:
            for i in range(x):
                for j in range(y):
                    r, g, b = pix[i, j]
                    average = (r + g + b) / 3
                    pix[i, j] = int(average + 40), int(average + 20), int(average)
        else:
            for i in range(x):
                for j in range(y):
                    r, g, b = pix[i, j]
                    pix[i, j] = 255 - r, 255 - g, 255 - b
        self.open_image()


class TextEditor(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.w, self.h = 500, 419
        self.setGeometry((1920 - self.w) // 2, (1080 - self.h) // 2, self.w, self.h)
        self.setWindowTitle('Текстовый редактор')
        self.plainTextEdit.resize(480, 300)
        for i, widget in enumerate([self.pushButton, self.pushButton_2, self.pushButton_3, self.pushButton_4,
                                    self.pushButton_5]):
            if i < 4:
                widget.resize(235, 23)
            else:
                widget.resize(480, 23)
            widget.move(10 + (i % 2) * 245, 320 + (i // 2) * 33)
            widget.clicked.connect(self.run)

    def run(self):
        if self.sender() == self.pushButton:
            text = self.plainTextEdit.toPlainText().lower()
            self.plainTextEdit.setPlainText(text)
        elif self.sender() == self.pushButton_2:
            text = self.plainTextEdit.toPlainText().upper()
            self.plainTextEdit.setPlainText(text)
        elif self.sender() == self.pushButton_3:
            self.replaceDialog = ReplaceDialog(self)
            self.replaceDialog.show()
        elif self.sender() == self.pushButton_4:
            self.findDialog = FindDialog(self)
            self.findDialog.show()
        elif self.sender() == self.pushButton_5:
            self.infoDialog = InfoDialog(self)
            self.infoDialog.show()


class ReplaceDialog(QWidget, RD_Ui_Form):
    def __init__(self, parent=None):
        super().__init__()
        self.setupUi(self)
        self.parent = parent
        self.w, self.h = 250, 126
        self.setGeometry((1920 - self.w) // 2, (1080 - self.h) // 2, self.w, self.h)
        self.setWindowTitle('Заменить')
        self.pushButton.clicked.connect(self.run)

    def run(self):
        self.label_3.setText("")
        if self.lineEdit.text() and self.lineEdit_2.text():
            text = self.parent.plainTextEdit.toPlainText()
            self.parent.plainTextEdit.setPlainText(text.replace(self.lineEdit.text(), self.lineEdit_2.text()))
            self.destroy()
        else:
            self.label_3.setText("Заполните поля ввода")
        self.label_3.resize(self.label_3.sizeHint())


class FindDialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.setupUi(self)
        self.w, self.h = 250, 96
        self.setGeometry((1920 - self.w) // 2, (1080 - self.h) // 2, self.w, self.h)
        self.setWindowTitle('Найти')
        self.pushButton.clicked.connect(self.run)

    def run(self):
        self.label_2.setText("")
        if self.lineEdit.text():
            text = self.parent.plainTextEdit.toPlainText()
            count = text.count(self.lineEdit.text())
            if count:
                self.label_2.setText(f"Найдено: {count}")
            else:
                self.label_2.setText("Не удалось найти")
        else:
            self.label_2.setText("Заполните поле ввода")
        self.label_2.resize(self.label_2.sizeHint())


class InfoDialog(QDialog, Info_Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.setupUi(self)
        self.w, self.h = 300, 150
        self.setGeometry((1920 - self.w) // 2, (1080 - self.h) // 2, self.w, self.h)
        self.setWindowTitle('Инфо')
        text = self.parent.plainTextEdit.toPlainText()
        self.label.setText(f'Количество символов без пробелов: {len(text.replace(" ", ""))}')
        self.label_2.setText(f'Количество символов с пробелами: {len(text)}')
        self.label_3.setText(f'Количество слов в тексте: {len(text.split())}')
        self.label_4.setText(
            f'Количество гласных в тексте: {len(list(filter(lambda x: x in "аеиоуыэюя", text)))}')
        self.label_5.setText(
            f'Количество согласных в тексте: {len(list(filter(lambda x: x in "бвгджзйклмнпрстфхцчшщ", text)))}')
        self.label.resize(self.label.sizeHint())
        self.label_2.resize(self.label_2.sizeHint())
        self.label_3.resize(self.label_3.sizeHint())
        self.label_4.resize(self.label_4.sizeHint())
        self.label_5.resize(self.label_5.sizeHint())
        self.pushButton.clicked.connect(self.run)

    def run(self):
        self.destroy()


class FirstTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.initUi()

    def initUi(self):
        self.x_label = QLabel('X:', self)
        self.y_label = QLabel('Y:', self)
        self.width_label = QLabel('Ширина:', self)
        self.height_label = QLabel('Высота:', self)
        self.x_line = QLineEdit(self)
        self.y_line = QLineEdit(self)
        self.width_line = QLineEdit(self)
        self.height_line = QLineEdit(self)
        self.crop_button = QPushButton('Обрезать', self)
        for i, widget in enumerate(
                [self.x_label, self.y_label, self.width_label, self.height_label, self.x_line,
                 self.y_line, self.width_line, self.height_line, self.crop_button]):
            if i < 4:
                widget.resize(widget.sizeHint())
                widget.move(15 + i % 2 * 202, 10 + i // 2 * 33)
            else:
                widget.resize(138, 23)
                widget.move(15 + int(i != 8) * (54 + i % 2 * 202), 10 + (i // 2 - 2) * 33)
        self.crop_button.clicked.connect(self.parent.crop_image)

    def reset(self):
        for line in [self.x_line, self.y_line, self.width_line, self.height_line]:
            line.clear()


class SecondTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.initUi()

    def initUi(self):
        self.left_button = QPushButton('Против часовой', self)
        self.right_button = QPushButton('По часовой', self)
        self.vertical_flip_button = QPushButton('Отразить по вертикали', self)
        self.horizontal_flip_button = QPushButton('Отразить по горизонтали', self)
        for i, button in enumerate([self.left_button, self.right_button, self.vertical_flip_button,
                                    self.horizontal_flip_button]):
            button.resize(150, 23)
            button.move(15 + i % 2 * 160, 10 + i // 2 * 33)
            button.clicked.connect(self.parent.turn_image)


class ThirdTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.initUi()

    def initUi(self):
        self.brightness_label = QLabel('Яркость:', self)
        self.contrast_label = QLabel('Контраст:', self)
        self.saturation_label = QLabel('Насыщенность:', self)
        self.sharpness_label = QLabel('Четкость:', self)
        self.highlight_label = QLabel('Свет:', self)
        self.shadows_label = QLabel('Тени:', self)
        self.brightness_slider = QSlider(Qt.Horizontal, self)
        self.contrast_slider = QSlider(Qt.Horizontal, self)
        self.saturation_slider = QSlider(Qt.Horizontal, self)
        self.sharpness_slider = QSlider(Qt.Horizontal, self)
        self.highlight_slider = QSlider(Qt.Horizontal, self)
        self.shadows_slider = QSlider(Qt.Horizontal, self)
        for i, widget in enumerate(
                [self.brightness_label, self.contrast_label, self.saturation_label,
                 self.sharpness_label, self.highlight_label, self.shadows_label,
                 self.brightness_slider, self.contrast_slider, self.saturation_slider,
                 self.sharpness_slider, self.highlight_slider, self.shadows_slider]):
            if i < 6:
                widget.resize(widget.sizeHint())
                widget.move(15 + i % 2 * 250, 10 + i // 2 * 32)
            else:
                widget.setMinimum(50)
                widget.setMaximum(150)
                widget.resize(150, 22)
                widget.move(105 + i % 2 * 250, 10 + (i // 2 - 3) * 32)
        self.saturation_slider.setMinimum(0)
        self.saturation_slider.setMaximum(200)
        self.accept_settings = QPushButton('Применить', self)
        self.accept_settings.resize(150, 23)
        self.accept_settings.move(15, 106)
        self.accept_settings.clicked.connect(self.parent.adjust_image)
        self.return_settings = QPushButton('Вернуть', self)
        self.return_settings.resize(150, 23)
        self.return_settings.move(175, 106)
        self.return_settings.clicked.connect(self.reset)

    def reset(self):
        for slider in [self.brightness_slider, self.contrast_slider, self.saturation_slider,
                       self.sharpness_slider, self.highlight_slider, self.shadows_slider]:
            slider.setValue(100)


class FourthTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.initUi()

    def initUi(self):
        self.temperature_label = QLabel('Температура:', self)
        self.hue_label = QLabel('Оттенок:', self)
        self.r_label = QLabel('R:', self)
        self.g_label = QLabel('G:', self)
        self.b_label = QLabel('B:', self)
        self.temperature_slider = QSlider(Qt.Horizontal, self)
        self.hue_slider = QSlider(Qt.Horizontal, self)
        self.r_slider = QSlider(Qt.Horizontal, self)
        self.g_slider = QSlider(Qt.Horizontal, self)
        self.b_slider = QSlider(Qt.Horizontal, self)
        for i, widget in enumerate(
                [self.temperature_label, self.hue_label, self.temperature_slider, self.hue_slider,
                 self.r_label, self.g_label, self.b_label, self.r_slider, self.g_slider,
                 self.b_slider]):
            if i < 2:
                widget.resize(widget.sizeHint())
                widget.move(15 + i * 240, 10)
            elif i < 4:
                widget.resize(150, 22)
                widget.move(95 + (i - 2) * 240, 10)
                widget.setMinimum(50)
                widget.setMaximum(150)
            elif i < 7:
                widget.resize(widget.sizeHint())
                widget.move(15 + (i - 4) * 181, 42)
            else:
                widget.resize(150, 22)
                widget.move(36 + (i - 7) * 181, 42)
                widget.setMinimum(50)
                widget.setMaximum(150)
        self.accept_settings = QPushButton('Принять', self)
        self.accept_settings.resize(150, 23)
        self.accept_settings.move(15, 74)
        self.accept_settings.clicked.connect(self.parent.color_image)
        self.return_settings = QPushButton('Вернуть', self)
        self.return_settings.resize(150, 23)
        self.return_settings.move(175, 74)
        self.return_settings.clicked.connect(self.reset)

    def reset(self):
        for slider in [self.temperature_slider, self.hue_slider, self.r_slider, self.g_slider,
                       self.b_slider]:
            slider.setValue(100)


class FifthTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.initUi()

    def initUi(self):
        self.black_white_button = QPushButton('ЧБ', self)
        self.sepia_button = QPushButton('Сепия', self)
        self.negative_button = QPushButton('Негатив', self)
        for i, button in enumerate(
                [self.black_white_button, self.sepia_button, self.negative_button]):
            button.resize(150, 23)
            button.move(15 + i * 160, 10)
            button.clicked.connect(self.parent.function_image)


class SixthTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.initUi()

    def initUi(self):
        self.way_line = QLineEdit(self)
        self.open_button = QPushButton('Открыть', self)
        self.choose_button = QPushButton('Выбрать', self)
        self.play_button = QPushButton('Играть', self)
        for i, button in enumerate(
                [self.way_line, self.open_button, self.choose_button, self.play_button]):
            button.resize(110, 23)
            button.move(15 + i * 115, 10)
            if i > 0:
                button.clicked.connect(self.run)
        self.play_button.move(15, 43)
        self.volume_label = QLabel('Громкость:', self)
        self.volume_label.move(135, 47)
        self.volume_slider = QSlider(Qt.Horizontal, self)
        self.volume_slider.resize(150, 22)
        self.volume_slider.move(202, 43)
        self.volume_slider.setValue(100)
        self.volume_slider.valueChanged.connect(self.run)
        self.is_playing = None

    def run(self):
        self.parent.label.clear()
        if self.sender() == self.open_button:
            file_name = self.way_line.text()
            if not file_name:
                self.parent.label.setText('Заполните поле ввода')
            else:
                try:
                    self.player = AudioPlayer(file_name)
                    self.player.play(loop=True)
                except FileNotFoundError:
                    self.parent.label.setText(f'Файл "{file_name}" не найден')
                except Exception as e:
                    self.parent.label.setText(f'Ошибка ({e})')
                else:
                    self.player.pause()
                    self.play_button.setText('Играть')
                    self.volume_slider.setValue(100)
                self.is_playing = False
        elif self.sender() == self.choose_button:
            file_name = QFileDialog.getOpenFileName(self, 'Выбрать изображение', '')[0]
            if not file_name:
                self.parent.label.setText('Выберите файл')
            try:
                self.player = AudioPlayer(file_name)
                self.player.play(loop=True)
            except Exception as e:
                self.parent.label.setText(f'Ошибка ({e})')
            else:
                self.player.pause()
                self.play_button.setText('Играть')
                self.volume_slider.setValue(100)
                self.is_playing = False
        elif self.sender() == self.play_button:
            if self.is_playing is None:
                self.parent.label.setText('Выберите аудиофайл')
            elif self.is_playing:
                self.player.pause()
                self.play_button.setText('Играть')
                self.is_playing = False
            else:
                self.player.resume()
                self.play_button.setText('Пауза')
                self.is_playing = True
        elif self.sender() == self.volume_slider:
            if self.is_playing is not None:
                self.player._do_setvolume(self.volume_slider.value())
        self.parent.label.resize(self.parent.label.sizeHint())


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())

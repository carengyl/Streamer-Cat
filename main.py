import os
import sys
from random import randint

import pygame as pg
import pyaudio as pa
import numpy as np

import win32api
import win32con
import win32gui

# Параметры приложения.
WINDOW_WIDTH = 400  # Ширина окна.
WINDOW_HEIGHT = 500  # Высота окна.
MIC_SENSITIVITY = 100  # Порог срабатывания рта.
SHAKE_SENSITIVITY = 1000  # Порог срабатывания тряски. Причина тряски?
SHAKE_INTENSE = 20  # Интенсивность тряски.

"""





-------------------- НЕ ЛЕЗЬ, БЛЯТЬ - ОНО ТЕБЯ СОЖРЕТ----------------------







"""

# Инициализация PyGame.
pg.init()

# Инициализация PyAudio.
audio = pa.PyAudio()

# Перечисляем все доступные устройства ввода
print("Доступные устройства ввода:")
for i in range(audio.get_device_count()):
    dev = audio.get_device_info_by_index(i)
    if dev['maxInputChannels'] > 0:
        print(f"{i}: {dev['name']}".encode('cp1251').decode('utf-8', 'ignore'))

# Выбор устройства по его индексу
device_index = int(input("Введите индекс устройства, которое хотите использовать: "))

# Проверяем, поддерживает ли устройство нужный RATE
device_info = audio.get_device_info_by_index(device_index)
supported_rate = int(device_info['defaultSampleRate'])
print(f"Поддерживаемая частота для этого устройства: {supported_rate}")

# Параметры PyAudio
FORMAT = pa.paInt16
CHANNELS = 1
RATE = supported_rate  # Используем поддерживаемую частоту
CHUNK = 1024

# Открытие выбранного устройства для захвата звука
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    input_device_index=device_index,
                    frames_per_buffer=CHUNK)


def get_microphone_level():
    data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
    peak = np.abs(data).mean()
    return peak


# Установка прозрачного фона и создание окна без рамки
window_screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pg.NOFRAME)
hwnd = pg.display.get_wm_info()["window"]
win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                       win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
                       | win32con.WS_EX_LAYERED
                       | win32con.WS_EX_TRANSPARENT)
win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0, 0, 0), 0, win32con.LWA_COLORKEY)

# Загрузка изображений с альфа-каналом и масштабирование
cat_mouth_closed = pg.image.load(os.path.join("resource", "popcat.png")).convert_alpha()
cat_mouth_open = pg.image.load(os.path.join("resource", "popcat-wow.png")).convert_alpha()

# Масштабируем изображения
cat_mouth_closed = pg.transform.scale(cat_mouth_closed, (WINDOW_WIDTH, WINDOW_HEIGHT))
cat_mouth_open = pg.transform.scale(cat_mouth_open, (WINDOW_WIDTH, WINDOW_HEIGHT))

window_screen.fill((0, 0, 0))  # Устанавливаем фоновый цвет, который будет прозрачным
window_screen.blit(cat_mouth_open, (0, 0))
pg.display.update()

running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    # Очищаем экран перед отрисовкой нового кадра
    window_screen.fill((0, 0, 0))  # Используем цвет, который установлен как прозрачный

    # Получаем уровень звука с микрофона
    mic_level = get_microphone_level()

    # Отображаем уровень микрофона в консоли
    sys.stdout.write(f'\rMic Level: {mic_level:.2f}')  # Выводим строку в консоль с возвратом каретки
    sys.stdout.flush()  # Обновляем вывод

    # Если звук выше порога, то открываем рот кота
    if mic_level > MIC_SENSITIVITY:
        shake_offset_x = 0
        shake_offset_y = 0

        if mic_level > SHAKE_SENSITIVITY:
            if mic_level > SHAKE_SENSITIVITY:
                # Нормализуем уровень звука относительно порога тряски
                normalized_mic_level = (mic_level - SHAKE_SENSITIVITY) / (
                            mic_level - SHAKE_SENSITIVITY)
                # Увеличиваем интенсивность тряски в зависимости от уровня звука
                dynamic_shake_intense = int(SHAKE_INTENSE * normalized_mic_level)

                shake_offset_x = randint(-dynamic_shake_intense, dynamic_shake_intense)  # Смещение по оси X
                shake_offset_y = randint(-dynamic_shake_intense, dynamic_shake_intense)  # Смещение по оси Y

            window_screen.blit(cat_mouth_open, (shake_offset_x, shake_offset_y))

        window_screen.blit(cat_mouth_open, (shake_offset_x, shake_offset_y))

    else:
        window_screen.blit(cat_mouth_closed, (0, 0))

    pg.display.update()

# Завершаем работу
stream.stop_stream()
stream.close()
audio.terminate()
pg.quit()

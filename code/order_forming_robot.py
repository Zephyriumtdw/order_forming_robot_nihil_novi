 #!/usr/bin/python3
import RPi.GPIO as GPIO
import time
import cv2
import numpy as np
import pyzbar.pyzbar as qr
from luma.core.interface.serial import i2c, spi, pcf8574
from luma.core.interface.parallel import bitbang_6800
from luma.core.render import canvas
from luma.oled.device import ssd1306
from PIL import ImageFont


serial = i2c(port=1, address = 0x3c)
device = ssd1306(serial)
font2 = ImageFont.truetype("/home/zephyr/Desktop/arial.ttf",35)
def draw_text(input_text): # Функция отрисовки текста на дисплее
    with canvas(device) as draw:
        draw.text((0, 10), f"{input_text}", font=font2, fill="white")

in1ret = 19
in2ret = 13
in3ret = 6
in4ret = 5

in1grab = 7
in2grab = 8
in3grab = 25
in4grab = 11

dir_pin_y = 23
step_pin_y = 22

dir_pin_x = 17
step_pin_x = 27

# Время между шагами
step_time = 0.002

grabber_step_count = 1500 # Кол-во шагов для захвата
retract_step_count = 5000 # Кол-во шагов для механизма выдвижения захвата

step_sequence = [[1,0,0,1],
                 [1,0,0,0],
                 [1,1,0,0],
                 [0,1,0,0],
                 [0,1,1,0],
                 [0,0,1,0],
                 [0,0,1,1],
                 [0,0,0,1]]

GPIO.setmode( GPIO.BCM )
GPIO.setup( in1ret, GPIO.OUT )
GPIO.setup( in2ret, GPIO.OUT )
GPIO.setup( in3ret, GPIO.OUT )
GPIO.setup( in4ret, GPIO.OUT )

GPIO.setup( in1grab, GPIO.OUT )
GPIO.setup( in2grab, GPIO.OUT )
GPIO.setup( in3grab, GPIO.OUT )
GPIO.setup( in4grab, GPIO.OUT )

GPIO.setup(step_pin_y, GPIO.OUT)
GPIO.setup(dir_pin_y, GPIO.OUT)

GPIO.setup(step_pin_x, GPIO.OUT)
GPIO.setup(dir_pin_x, GPIO.OUT)

GPIO.output( in1ret, GPIO.LOW )
GPIO.output( in2ret, GPIO.LOW )
GPIO.output( in3ret, GPIO.LOW )
GPIO.output( in4ret, GPIO.LOW )

GPIO.output( in1grab, GPIO.LOW )
GPIO.output( in2grab, GPIO.LOW )
GPIO.output( in3grab, GPIO.LOW )
GPIO.output( in4grab, GPIO.LOW )

GPIO.output(step_pin_y, GPIO.LOW)
GPIO.output(dir_pin_y, GPIO.LOW)

GPIO.output(step_pin_x, GPIO.LOW)
GPIO.output(dir_pin_x, GPIO.LOW)

grabber_pins = [in1grab,in2grab,in3grab,in4grab]
retract_pins = [in1ret,in2ret,in3ret,in4ret]
motor_step_counter = 0

def cleanup():
    GPIO.output( in1ret, GPIO.LOW )
    GPIO.output( in2ret, GPIO.LOW )
    GPIO.output( in3ret, GPIO.LOW )
    GPIO.output( in4ret, GPIO.LOW )
    
    GPIO.output( in1grab, GPIO.LOW )
    GPIO.output( in2grab, GPIO.LOW )
    GPIO.output( in3grab, GPIO.LOW )
    GPIO.output( in4grab, GPIO.LOW )

    GPIO.output(step_pin_y, GPIO.LOW)
    GPIO.output(dir_pin_y, GPIO.LOW)

    GPIO.output(step_pin_x, GPIO.LOW)
    GPIO.output(dir_pin_x, GPIO.LOW)

    GPIO.cleanup()

def release():
    i = 0
    motor_step_counter = 0
    for i in range(grabber_step_count):
        for pin in range(0, len(grabber_pins)):
            GPIO.output( grabber_pins[pin], step_sequence[motor_step_counter][pin] )
        motor_step_counter = (motor_step_counter + 1) % 8
        time.sleep( step_time )
    motor_step_counter = 0

def grab():
    i = 0
    motor_step_counter = 0
    for i in range(grabber_step_count):
        for pin in range(0, len(grabber_pins)):
            GPIO.output( grabber_pins[pin], step_sequence[motor_step_counter][pin] )
        motor_step_counter = (motor_step_counter - 1) % 8
        time.sleep( step_time )
    motor_step_counter = 0

def push():
    i = 0
    motor_step_counter = 0
    for i in range(retract_step_count):
        for pin in range(0, len(retract_pins)):
            GPIO.output( retract_pins[pin], step_sequence[motor_step_counter][pin] )
        motor_step_counter = (motor_step_counter + 1) % 8
        time.sleep( step_time )

def pull():
    i = 0
    motor_step_counter = 0
    for i in range(retract_step_count):
        for pin in range(0, len(retract_pins)):
            GPIO.output( retract_pins[pin], step_sequence[motor_step_counter][pin] )
        motor_step_counter = (motor_step_counter - 1) % 8
        time.sleep( step_time )


def move_y_step_up(): # Функции для совершения одного шага двигателей Nema 17 для осей X и Y
    GPIO.output(dir_pin_y, GPIO.HIGH)
    GPIO.output(step_pin_y, GPIO.HIGH)
    time.sleep( step_time )
    GPIO.output(step_pin_y, GPIO.LOW )

def move_y_step_down():
    GPIO.output(dir_pin_y, GPIO.LOW)
    GPIO.output(step_pin_y, GPIO.HIGH)
    time.sleep( step_time )
    GPIO.output(step_pin_y, GPIO.LOW )

def move_x_step_right():
    GPIO.output(dir_pin_x, GPIO.LOW)
    GPIO.output(step_pin_x, GPIO.HIGH)
    time.sleep( step_time )
    GPIO.output(step_pin_x, GPIO.LOW )

def move_x_step_left():
    GPIO.output(dir_pin_x, GPIO.HIGH)
    GPIO.output(step_pin_x, GPIO.HIGH)
    time.sleep( step_time )
    GPIO.output(step_pin_x, GPIO.LOW )

def move_one_cell_up(count=1): # Функции перемещения на n ячеек. По умолчанию одна
    i = 0
    while True:
        move_y_step_up()
        i += 1
        if i > 1024 * count:
            break

def move_one_cell_down(count=1):
    i = 0
    while True:
        move_y_step_down()
        i += 1
        if i > 1024 * count:
            break

def move_one_cell_right(count=1):
    i = 0
    while True:
        move_x_step_right()
        i += 1
        if i > 1024 * count:
            break

def move_one_cell_left(count=1):
    i = 0
    while True:
        move_x_step_right()
        i += 1
        if i > 1024 * count:
            break

cargo_locations = dict()
cargo_types = {'Винты': 'screw', 'Гайки': 'nut', 'Шайбы': 'shim', 'Шпильки': 'pin', 'Подшипники': 'bearing', 'Линейные направляющие': 'linear', 'Валы': 'shaft', 'Двигатели': 'motor', 'Датчики': 'sensor'}

def scan(): # Программа последовательного сканирования всех ячеек.
    global cargo_locations
    img = cv2.VideoCapture(0)
    def get_data():
        ret, frame = img.read()
        frame = cv2.flip(frame, flipCode=-1)
        qr_decode = frame.decode("utf-8")
        for qr in qr_decode:
            qrdata = qr.data[2:-1]
        print(qrdata)
        draw_text(qrdata)
        return qrdata
    cargo_locations[f'{qrdata}'] = 'C1'
    qrcode = get_data()
    print(draw_text(qrcode))
    move_one_cell_right()
    qrdata = get_data()
    cargo_locations[f'{qrdata}'] = 'C2'
    move_one_cell_right()
    qrdata = get_data()
    cargo_locations[f'{qrdata}'] = 'C3'
    move_one_cell_up()
    qrdata = get_data()
    cargo_locations[f'{qrdata}'] = 'B3'
    move_one_cell_left()
    qrdata = get_data()
    cargo_locations[f'{qrdata}'] = 'B2'
    move_one_cell_left()
    qrdata = get_data()
    cargo_locations[f'{qrdata}'] = 'B1'
    move_one_cell_up()
    qrdata = get_data()
    cargo_locations[f'{qrdata}'] = 'A1'
    move_one_cell_right()
    qrdata = get_data()
    cargo_locations[f'{qrdata}'] = 'A2'
    move_one_cell_right()
    qrdata = get_data()
    cargo_locations[f'{qrdata}'] = 'A3'
    move_one_cell_left(2)
    move_one_cell_down(2)

#Функции для захвата грузов в соответствии с ячейкой. Карта ячеек
#  A1 | A2 | A3
#  ---|----|---
#  B1 | B2 | B3
#  ---|----|---
#  C1 | C2 | C3
def get_a1():
    move_one_cell_up(2)
    push()
    grab()
    pull()
    move_one_cell_right(3)
    push()
    release()
    pull()
    move_one_cell_left(3)
    move_one_cell_down(2)

def get_a2():
    move_one_cell_up(2)
    move_one_cell_right()
    push()
    grab()
    pull()
    move_one_cell_right(2)
    push()
    release()
    pull()
    move_one_cell_left(3)
    move_one_cell_down(2)

def get_a3():
    move_one_cell_up(2)
    move_one_cell_right(2)
    push()
    grab()
    pull()
    move_one_cell_right()
    push()
    release()
    pull()
    move_one_cell_left(3)
    move_one_cell_down(2)

def get_b1():
    move_one_cell_up()
    push()
    grab()
    pull()
    move_one_cell_right(3)
    move_one_cell_up()
    push()
    release()
    pull()
    move_one_cell_left(3)
    move_one_cell_down(2)

def get_b2():
    move_one_cell_up()
    move_one_cell_right()
    push()
    grab()
    pull()
    move_one_cell_right(2)
    move_one_cell_up()
    push()
    release()
    pull()
    move_one_cell_left(3)
    move_one_cell_down(2)

def get_b3():
    move_one_cell_up()
    move_one_cell_right(2)
    push()
    grab()
    pull()
    move_one_cell_right()
    move_one_cell_up()
    push()
    release()
    pull()
    move_one_cell_left(3)
    move_one_cell_down(2)

def get_c1():
    push()
    grab()
    pull()
    move_one_cell_right(3)
    move_one_cell_up(2)
    push()
    release()
    pull()
    move_one_cell_left(3)
    move_one_cell_down(2)

def get_c2():
    move_one_cell_right()
    push()
    grab()
    pull()
    move_one_cell_right(2)
    move_one_cell_up(2)
    push()
    release()
    pull()
    move_one_cell_left(3)
    move_one_cell_down(2)

def get_c3():
    move_one_cell_right()
    push()
    grab()
    pull()
    move_one_cell_right()
    move_one_cell_up(2)
    push()
    release()
    pull()
    move_one_cell_left(3)
    move_one_cell_down(2)

def capture(location):
    if location == 'A1':
        get_a1()
    if location == 'A2':
        get_a2()
    if location == 'A3':
        get_a3()
    if location == 'B1':
        get_b1()
    if location == 'B2':
        get_b2()
    if location == 'B3':
        get_b3()
    if location == 'C1':
        get_c1()
    if location == 'C2':
        get_c2()
    if location == 'C3':
        get_c3()

def get_items(input_str):
    items = input_str.split(",")
    for i in range(len(items)):
        item = cargo_types[f'{items[i]}']
        capture(cargo_locations[f'item'])

commands = {
  'Scan': scan,
  'Form_Order': get_items,
}
def process(line):
  cmd, *args = line.split()
  return commands[cmd](*args)

print('Программа управления сборщиком заказов.\n '
           'Чтобы начать, воспользуйтесь командой "Scan" для обновления данных о местоположении грузов.\n'
           'Команда формирования заказов - "Form_Order [Типы деталей]". Доступные виды деталей: Винты, Гайки, Шайбы, Шпильки, Подшипники, Линейные направляющие, Валы, Двигатели, Датчики.\n'
      'Перечисление в аргументах через запятую, без пробелов.\n'
      'Команда остановки - "Exit"')

while True:
    line = input()
    if line == "Exit":
        break
    elif line != 'Scan' and line[:10] != "Form_Order":
        print("Такой команды не существует.")
    else:
        process(line)

cleanup()
exit( 0 )

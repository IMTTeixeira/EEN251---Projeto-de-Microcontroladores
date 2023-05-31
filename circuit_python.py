import gc
import sys
from time import sleep
import bitmaptools
import board
import busio
import digitalio
import displayio
import svm_min
import terminalio
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label
from adafruit_ov7670 import OV7670
import adafruit_ssd1306
from adafruit_display_text import label



def rgb565_to_1bit(pixel_val):
    pixel_val = ((pixel_val & 0x00FF)<<8) | ((25889 & 0xFF00) >> 8)
    r = (pixel_val & 0xF800)>>11
    g = (pixel_val & 0x7E0)>>5
    b = pixel_val & 0x1F
    return (r+g+b)/128



# Setting up display
WIDTH = 128
HEIGHT = 64
CENTER_X = int(WIDTH/2)
CENTER_Y = int(HEIGHT/2)

displayio.release_displays()


cam_width = 80
cam_height = 60
cam_size = 3 #80x60 resolution

camera_image = displayio.Bitmap(cam_width, cam_height, 65536)
camera_image_tile = displayio.TileGrid(
    camera_image ,
    pixel_shader=displayio.ColorConverter(
        input_colorspace=displayio.Colorspace.RGB565_SWAPPED
    ),
    x=30,
    y=30,
)
camera_image_tile.transpose_xy=True

inference_image = displayio.Bitmap(12,12, 65536)

#Setting up the camera
cam_bus = busio.I2C(board.GP21, board.GP20)

cam = OV7670(
    cam_bus,
    data_pins=[
        board.GP0,
        board.GP1,
        board.GP2,
        board.GP3,
        board.GP4,
        board.GP5,
        board.GP6,
        board.GP7,
    ],
    clock=board.GP8,
    vsync=board.GP13,
    href=board.GP12,
    mclk=board.GP9,
    shutdown=board.GP15,
    reset=board.GP14,
)
cam.size =  cam_size
cam.flip_y = True

ctr = 0
cam.capture(camera_image)



sleep(0.1)
temp_bmp = displayio.Bitmap(cam_height, cam_height, 65536) # Bitmap temporario
for i in range(0,cam_height): # 
    for j in range(0,cam_height):
        temp_bmp[i,j] =  camera_image[i,j]
bitmaptools.rotozoom(inference_image,temp_bmp,scale=12/cam_height,ox=0,oy=0,px=0,py=0)
del(temp_bmp)


input_data = []
for i in range(0,12):
    for j in range(0,12):
        gray_pixel = 1 -rgb565_to_1bit(inference_image[i,j])
        if gray_pixel < 0.50:
            gray_pixel = 0
        input_data.append(gray_pixel)

camera_image.dirty()

print(input_data)
prediction = svm_min.score(input_data)
ctr = ctr + 1
if ctr%50 == 0:
    print(input_data)
    print("------")
res = prediction.index(max(prediction))
#print(res)
print(str(res))
sleep(0.01)

display = adafruit_ssd1306.SSD1306_I2C(128, 64, cam_bus)


    # Limpa o display
display.fill(0)
display.show()

    # Desenha o logo do MicroPython e imprime um texto
display.fill(0)                        # preenche toda a tela com cor = 0
display.fill_rect(1, 0, 32, 32, 1)     # desenha um retângulo sólido de 0,0 a 32,32, cor = 1
display.fill_rect(2, 2, 28, 28, 0)     # desenha um retângulo sólido de 2,2 a 28,28, cor = 0
display.vline(9, 8, 22, 1)             # desenha uma linha vertical x = 9 , y = 8, altura = 22, cor = 1
display.vline(16, 2, 22, 1)            # desenha uma linha vertical x = 16, y = 2, altura = 22, cor = 1
display.vline(23, 8, 22, 1)            # desenha uma linha vertical x = 23, y = 8, altura = 22, cor = 1
display.fill_rect(26, 24, 2, 4, 1)     # desenha um retângulo sólido de 26,24 a 2,4, cor = 1
display.text('Prediction: ', 40, 0, 1)  # desenha algum texto em x = 40, y = 0 , cor = 1
display.text(str(res), 40, 12, 1)     # desenha algum texto em x = 40, y = 12, cor = 1
display.show()                         # escreve o conteúdo do FrameBuffer na memória do display

    # Atualiza o display
display.show()
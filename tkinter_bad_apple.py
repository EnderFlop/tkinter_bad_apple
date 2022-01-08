import tkinter as tk
import cv2
import fpstimer
import time
from PIL import Image, ImageOps
from tkinter import ttk

#constants
#RATIOS 1920:1080, 128:72 96:54, 64:36, 48:27, 9:16
WIDTH = 96
HEIGHT = 54
#Native FPS is 30. Lags when running at high resolutions. Can run at higher resolutions but lower FPS, speed up in post.
FRAMES_PER_SECOND = 1
# 48:27 @ 30 runs semi-smoothly
# 96:54 @ 1 for recording, speed up x30 in post. ONLY IF LONGEST DELAY < 1 SECOND
# run at 30 fps to run at maximum speed every single frame, then see how long the longest delay is and adjust.

#Set up "display" in Tkinter
def setup_display():
  frame_dict = {} #frame dict is set up like (x,y) = style
  root = tk.Tk()
  root.title("Bad Apple in Tkinter")
  color = ttk.Style()
  color.configure("Black.TFrame", background="black")
  color.configure("White.TFrame", background="white")
  for x in range(WIDTH):
    for y in range(HEIGHT):
      frame = ttk.Frame(root, style="White.TFrame", width=10, height=10)
      if (x + y) % 2 == 0:
        frame.configure(style="Black.TFrame")
      frame.grid(column=x, row=y)
      frame_dict[(x,y)] = frame.cget("style")
    print(f"finish column {x} of {WIDTH}")
  print("DISPLAY SETUP FINISHED")
  return root, frame_dict

#helper functions
def grayscale(image):
  return ImageOps.grayscale(image)

def resize_image(image):
  return image.resize((WIDTH, HEIGHT), Image.NEAREST) #NEAREST to interpolate into solid pixels

#Open video and scrape frames (heavily inspired by CalvinLoke's Bad Apple in Python)
def create_images(number_of_frames = 6572):
  image_list = []
  video = cv2.VideoCapture("./bad_apple.mp4")
  frame_count = 0
  while True:
    ret, image_frame = video.read()
    if ret == False or frame_count > number_of_frames: #when we reach the end of the video
      break
    image = Image.fromarray(image_frame)
    image = resize_image(image)
    image = grayscale(image)
    image_list.append(image)
    frame_count += 1
    if frame_count % 100 == 0:
      print(f"finish frame {frame_count} out of {number_of_frames}")
  print("IMAGE CREATION FINISHED")
  video.release()
  return image_list

#run through the frames
def driver(images, root, frame_dict, start_button):
  start_button.grid_remove()
  frame_count = 0
  timer = fpstimer.FPSTimer(FRAMES_PER_SECOND)
  longest_frame = 0
  for image in images:
    image_start_time = time.time()
    for x in range(WIDTH):
      for y in range(HEIGHT):
        pixel = image.getpixel((x, y))
        #0 for black, 255 for white
        style = frame_dict[(x,y)]
        if pixel < 128:
          if style == "Black.TFrame": #if the pixel is already black, ignore it
            continue
          root.grid_slaves(column=x, row=y)[0].configure(style="Black.TFrame")
          frame_dict[(x,y)] = "Black.TFrame"
        elif pixel >= 128:
          if style == "White.TFrame": #if the pixel is already white, ignore it
            continue
          root.grid_slaves(column=x, row=y)[0].configure(style="White.TFrame")
          frame_dict[(x,y)] = "White.TFrame"
        else:
          print(f"pixel value = {pixel}")
    root.update()
    image_end_time = time.time()
    difference = image_end_time - image_start_time
    if difference > longest_frame and frame_count != 0: #frame 1 takes a crazy amount of startup time. ignore
      longest_frame = round(difference, 5)
    if difference > (1/FRAMES_PER_SECOND): #if the time takes more than 1/framerate
      print(f"lagging! {round(difference, 5)}. Should be {round(1/FRAMES_PER_SECOND, 5)}")
      print(f"longest_frame {longest_frame}")
    timer.sleep()
    frame_count += 1
    if frame_count % 100 == 0:
      print(f"finish frame {frame_count}")
  print(f"done! longest frame {longest_frame}")

def start():
  root, frame_dict = setup_display()
  images = create_images()
  start_button = tk.Button(root, text="Start", command=lambda: driver(images, root, frame_dict, start_button))
  start_button.grid(column=0, row=HEIGHT + 1, columnspan=WIDTH)
  root.mainloop()

if __name__ == "__main__":
  start()
  #alex made this!

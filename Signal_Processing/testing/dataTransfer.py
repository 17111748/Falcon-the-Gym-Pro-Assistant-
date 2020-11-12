from PIL import Image
import os
import serial

def writeFile(path, result):
    with open(path, "wt") as f:
        f.write(result)

# Initializing the list of images
sample_image_dir = "Nov" 
workoutPhotos = {
    "l": [os.path.join("lungeForward", "Backward.png"), os.path.join("lungeForward", "Forward.png"), os.path.join("lungeForward", "Perfect.png")],
    "u": [os.path.join("pushUp", "HandForward.png"), os.path.join("pushUp", "High.png"), os.path.join("pushUp", "Perfect.png"), os.path.join("pushUp", "Perfect2.png")],
    "c": [os.path.join("legRaise", "kneeBent.png"), os.path.join("legRaise", "Over.png"), os.path.join("legRaise", "Perfect.png"), os.path.join("legRaise", "Under.png")]
}

resized_col = 160
resized_row = 120

# # Initializing the serial connection
# ser = serial.Serial(port = "COM3",
#     baudrate=921600, 
#     bytesize=serial.EIGHTBITS,
#     stopbits=serial.STOPBITS_ONE)

# Iterating through all of the images
for workout in workoutPhotos:
    for exercise in range(len(workoutPhotos[workout])):
        original_image = Image.open(os.path.join(sample_image_dir, workoutPhotos[workout][exercise]))
        original_image_pixels = original_image.load()

        new_image = original_image.resize((resized_col, resized_row))
        converted_image = new_image.convert('HSV')

        # Generating the golden solution
        res = ""
        for tup in converted_image.getdata():
            for val in tup:
                res += str(val) + " "

        writeFile(workout + "_" + str(exercise) + "_" + "orig_bytes.txt", res)

        # # Seeing what the FPGA says
        # byte_arr = converted_image.tobytes()
        # ser.write(byte_arr)
        
        # total = b''
        # data_received = b''
        # while ("\n" not in data_received.decode("utf-8")):
        #     data_received = d.ser.read(d.ser.in_waiting)
        #     total += data_received
        #     # if(len(data_received) != 0):
        #     #     print(data_received.decode("utf-8"))
        # result = total.decode("utf-8")

        # # Generating the produced result
        # writeFile(workout + "_" + str(exercise) + "_" + "found_bytes.txt", result[:-2])
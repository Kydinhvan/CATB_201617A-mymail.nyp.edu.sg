from pathlib import Path
from peekingduck.pipeline.nodes.draw import bbox
from peekingduck.pipeline.nodes.input import visual
from peekingduck.pipeline.nodes.model import yolo
from peekingduck.pipeline.nodes.output import media_writer, screen
import cv2
import pandas as pd
from datetime import datetime

today_date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

# input image
filename = "qwe.jpg"

# A dictionary to store the calorie information of each food item
calorie_info = {'orange': 8, 'broccoli': 12, 'carrot': 10, 'apple': 15}

#pipeline setting 
yolo_node = yolo.Node(detect=[ "apple", "orange","broccoli", "carrot"], iou_threshold =0.1)
bbox_node = bbox.Node(show_labels=True)
screen_node = screen.Node()
media_writer_node = media_writer.Node(output_dir=str(Path.cwd()))
visual_input_node = visual.Node(source=str(Path.cwd()/ filename ))

#run
input = visual_input_node.run({})["img"]
yolo_outputs = yolo_node.run({"img": input})
bbox_input = {
        "img": input,
        "bboxes": yolo_outputs["bboxes"],
        "bbox_labels": yolo_outputs["bbox_labels"],
    }
draw_box = bbox_node.run(bbox_input)


width = int(input.shape[1] * 100 / 100)
height = int(input.shape[0] * 100 / 100)
dim = (width, height)

#assign boxes to their respective label
box_dict ={}
for i in range (len(yolo_outputs["bboxes"])):
    x = str(i)
    box_dict[yolo_outputs["bbox_labels"][i]+ x ] = yolo_outputs["bboxes"][i]
# print(box_dict,len(yolo_outputs["bboxes"]))

# Get coordinate of boxes and calculate optimal 
x1=0
y1=1
x2=2
y2=3
coordinate_dict={}
boxdictcheck = []
for r in range (len(yolo_outputs["bboxes"])):
    x01=box_dict[yolo_outputs["bbox_labels"][r] + str(r)][x1]
    x02=box_dict[yolo_outputs["bbox_labels"][r] + str(r)][x2]
    y01=box_dict[yolo_outputs["bbox_labels"][r] + str(r)][y1]
    y02=box_dict[yolo_outputs["bbox_labels"][r] + str(r)][y2]
    x01_abs = int(x01*width)
    y01_abs = int(y01*height)
    x02_abs = int(x02*width)
    y02_abs = int(y02*height)
    # print(x01_abs, y01_abs,x02_abs,y02_abs)

    if x01_abs > x02_abs:
        checkdimensionx = x01_abs - x02_abs
        smallerx=x02_abs
    else:
        checkdimensionx = x02_abs - x01_abs
        smallerx=x01_abs

    if y01_abs > y02_abs:
        checkdimensiony = y01_abs - y02_abs
        smallery=y02_abs
    else:
        checkdimensiony = y02_abs - y01_abs
        smallery=y01_abs

    if  checkdimensiony - checkdimensiony*20/100 <= checkdimensionx <= checkdimensiony + checkdimensiony*20/100:
        center = True
        # print("this dimension is a square")
    else:
        # print("this dimension is a rectangle")
        center = False

    if center == False:
        if checkdimensionx < checkdimensiony:
            pokex=int(checkdimensionx/2 + smallerx)
            pokey=int(checkdimensiony*80/100 + smallery)
        else:
            pokex=int(checkdimensionx*80/100 + smallerx)
            pokey=int(checkdimensiony/2 + smallery)
    else:
        pokex = int(checkdimensionx/2 + smallerx)
        pokey = int(checkdimensiony/2 + smallery)

    # cv2.circle(input,(x01_abs,y01_abs), 10, (0,0,255), -1) 
    # cv2.circle(input,(x02_abs,y02_abs), 10, (0,0,255), -1) 
    cv2.circle(input,(pokex,pokey), 10, (0,0,255), -1) 

label = {}
for i in range(len(yolo_outputs["bboxes"])):
    items = [yolo_outputs["bbox_labels"][i]]
    for item in items:
        if item in label:
            label[item] += 1
        else:
            label[item] = 1

#input monitoring data 
resultList = list(label.items())
list_of_lists = []
finallist = []
for tup in resultList:
    list_of_lists.append(list(tup))

for lst in list_of_lists:
    lst.insert(0,today_date)
    finallist.append(lst)
print(finallist)



# Calculate the total number of calories
total_calories = 0
for food in finallist:
    food_name = food[1]
    food_amount = food[2]
    total_calories += calorie_info[food_name] * food_amount

# Print the result
print("Total calories:", total_calories, "calories")

df = pd.read_excel('monitoring.xlsx')
new_data = pd.DataFrame(data=finallist, columns=['Date and Time', 'Food Eaten', 'quantity(pieces)'])
df = pd.concat([df, new_data], ignore_index=True)

writer = pd.ExcelWriter('monitoring.xlsx', engine='xlsxwriter')
df.to_excel(writer, index = False)
writer.save()

width = int(input.shape[1] * 70 / 100)
height = int(input.shape[0] * 70 / 100)
dim = (width, height)
resized = cv2.resize(input, dim, interpolation = cv2.INTER_AREA)
cv2.imshow('',resized)
k = cv2.waitKey(0)
 
import os
import cv2
from pathlib2 import Path, PureWindowsPath
import face_recognition
import face_recognition_models
from PIL import Image
from datetime import datetime
import functools

# from .utils import plot_image




# face_locations = face_recognition.face_locations(image,number_of_times_to_upsample=1,model="hog")




# print(face_locations)

def face_detection(image, number_of_times_to_upsample=1, model="hog"):
    # image = cv2.cvtColor(cv2.imread("./group_photo.jpg"),cv2.COLOR_BGR2RGB)
    image = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(image, number_of_times_to_upsample=number_of_times_to_upsample, model=model)
    face_encodings = face_recognition.face_encodings(image, face_locations, num_jitters=3, model="large")
    # top, right, bottom, left
    face_locations = [ [left,top,right,bottom] for [top, right, bottom, left] in face_locations ]
    face_images = [image[y1:y2, x1:x2]  for x1,y1,x2,y2 in face_locations ]
    # face_encodings = [i.reshape(1,-1) for i in face_encodings]
    return face_locations, face_images, face_encodings


def detect_face_from_image(image, number_of_times_to_upsample=1, expand=False, x_ratio=0.1, y_ratio=0.1, model="hog", save_dir="./", prefix=""):

    # image = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(image,number_of_times_to_upsample=number_of_times_to_upsample,model=model)
    face_locations = [ [left,top,right,bottom] for [top, right, bottom, left] in face_locations ]
    if expand:
        face_locations = box_expand(image, face_locations, x_ratio, y_ratio)
    face_images = [image[y1:y2, x1:x2]  for x1,y1,x2,y2 in face_locations ]

    for face_image in face_images:
        filename = os.path.join(save_dir, f"{now()}.jpg") if prefix==""  else os.path.join(save_dir, f"{prefix}_{now()}.jpg") 
        cv2.imwrite(filename,face_image)

def box_expand(image, boxes, x_ratio=0.1, y_ratio=0.1):
    return [one_box_expand(image, box, x_ratio, y_ratio) for box in boxes]

def one_box_expand(image, box, x_ratio=0.1, y_ratio=0.1):
    '''
        将图片上的boundingbox沿着x和y方向按照一定比例进行扩展。
        image: 输入图像。
        box: boundingbox [x1,y1,x2,y2]
        x_ratio: box左右两侧扩展的比例，基数为box的宽度。
        y_ratio: box上下两侧扩展的比例，基数为box的高度。

    '''
    h,w = image.shape[:2]
    x1,y1,x2,y2 = box
    b_w, b_h = x2 - x1, y2 - y1
    new_x1 = max(0, x1-round(b_w*x_ratio))
    new_x2 = min(w, x2+round(b_w*x_ratio))
    new_y1 = max(0, y1-round(b_h*y_ratio))
    new_y2 = min(h, y2+round(b_h*y_ratio))
    return [new_x1,new_y1, new_x2, new_y2]

def detect_face_from_dir(image_dir, number_of_times_to_upsample=1,expand=True, x_ratio=0.1, y_ratio=0.1, model="hog", save_dir="./", prefix=""):
    detect_face = functools.partial(detect_face_from_image,  number_of_times_to_upsample=number_of_times_to_upsample,\
                                                              expand=expand,\
                                                              x_ratio=x_ratio,\
                                                              y_ratio=y_ratio,\
                                                              model=model, \
                                                              save_dir=save_dir, \
                                                              prefix=prefix)
    for image_path in Path(image_dir).rglob("*.[j,p]*"):
        image = cv2.imread(str(image_path))
        detect_face(image)

def face_recog_svm(image, face_model, face_encodings):
    return [ face_model.predict(f_encoding).tolist()[0]  for f_encoding in face_encodings]

def now():
    return datetime.now().strftime('%Y%m%d-%H%M%S.%f')[:-3]























# # initialize the list of known encodings and known names
# knownEncodings = []
# knownNames = []

# # loop over the image paths
# for (i, imagePath) in enumerate(imagePaths):
# 	# extract the person name from the image path
# 	print("[INFO] processing image {}/{}".format(i + 1,
# 		len(imagePaths)))
# 	name = imagePath.split(os.path.sep)[-2]
# 	# load the input image and convert it from BGR (OpenCV ordering)
# 	# to dlib ordering (RGB)
# 	image = cv2.imread(imagePath)
# 	rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

#     # detect the (x, y)-coordinates of the bounding boxes
# 	# corresponding to each face in the input image
# 	boxes = face_recognition.face_locations(rgb,
# 		model=args["detection_method"])
# 	# compute the facial embedding for the face
# 	encodings = face_recognition.face_encodings(rgb, boxes)
# 	# loop over the encodings
# 	for encoding in encodings:
# 		# add each encoding + name to our set of known names and
# 		# encodings
# 		knownEncodings.append(encoding)
# 		knownNames.append(name)



#         # dump the facial encodings + names to disk
# print("[INFO] serializing encodings...")
# data = {"encodings": knownEncodings, "names": knownNames}
# f = open(args["encodings"], "wb")
# f.write(pickle.dumps(data))
# f.close()





# # load the known faces and embeddings
# print("[INFO] loading encodings...")
# data = pickle.loads(open(args["encodings"], "rb").read())
# # load the input image and convert it from BGR to RGB
# image = cv2.imread(args["image"])
# rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
# # detect the (x, y)-coordinates of the bounding boxes corresponding
# # to each face in the input image, then compute the facial embeddings
# # for each face
# print("[INFO] recognizing faces...")
# boxes = face_recognition.face_locations(rgb,
# 	model=args["detection_method"])
# encodings = face_recognition.face_encodings(rgb, boxes)
# # initialize the list of names for each face detected
# names = []



# # loop over the facial embeddings
# for encoding in encodings:
# 	# attempt to match each face in the input image to our known
# 	# encodings
# 	matches = face_recognition.compare_faces(data["encodings"],
# 		encoding)
# 	name = "Unknown"

#     # check to see if we have found a match
# 	if True in matches:
# 		# find the indexes of all matched faces then initialize a
# 		# dictionary to count the total number of times each face
# 		# was matched
# 		matchedIdxs = [i for (i, b) in enumerate(matches) if b]
# 		counts = {}
# 		# loop over the matched indexes and maintain a count for
# 		# each recognized face face
# 		for i in matchedIdxs:
# 			name = data["names"][i]
# 			counts[name] = counts.get(name, 0) + 1
# 		# determine the recognized face with the largest number of
# 		# votes (note: in the event of an unlikely tie Python will
# 		# select first entry in the dictionary)
# 		name = max(counts, key=counts.get)
	
# 	# update the list of names
# 	names.append(name)
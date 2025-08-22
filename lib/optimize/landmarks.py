import os
import numpy as np
import json

input_data_path = 'input_data'
landmark_filename = 'landmarks Txt.txt'

landmark_filepath = os.path.join(input_data_path, landmark_filename)

with open(landmark_filepath) as f:
    lines = f.readlines()

landmarks = {}

for line in lines:
    toothId = 0
    if line[0:2].isdigit() :
        toothId = line[0:2]
    elif line[0:2] == 'ap':
        toothId = line[5:7]
    
    details = line.split()

    if toothId != 0 and details[-1][-1] == 'm':
        if toothId not in landmarks.keys():
            landmarks[toothId] = {}

        coordinate_code = details[1] + " " + details[2]
        coordinates = details[-3:]

        coordinates[0] = float(coordinates[0][0:-2])
        coordinates[1] = float(coordinates[1][0:-2])
        coordinates[2] = float(coordinates[2][0:-2])

        landmarks[toothId][coordinate_code] = coordinates
        
        # print(coordinate_code, toothId)

for tooth in landmarks:

    listAxis = [(landmarks[tooth]['Mesial Point'][0] - landmarks[tooth]['Distal point'][0]), (landmarks[tooth]['Mesial Point'][1] - landmarks[tooth]['Distal point'][1]),(landmarks[tooth]['Mesial Point'][2] - landmarks[tooth]['Distal point'][2])]
    arrayAxis = np.array(listAxis)
    norm = np.linalg.norm(arrayAxis)
    listNormAxis = (arrayAxis/norm).tolist()
    landmarks[tooth]['mdAxis'] = listNormAxis


    landmarks[tooth]["mdCenter"] = [(landmarks[tooth]['Mesial Point'][0] + landmarks[tooth]['Distal point'][0])/2, (landmarks[tooth]['Mesial Point'][1] + landmarks[tooth]['Distal point'][1])/2,(landmarks[tooth]['Mesial Point'][2] + landmarks[tooth]['Distal point'][2])/2]


    listAxis = [(landmarks[tooth]['Apical Rotation'][0] - landmarks[tooth]['mdCenter'][0]), (landmarks[tooth]['Apical Rotation'][1] - landmarks[tooth]['mdCenter'][1]),(landmarks[tooth]['Apical Rotation'][2] - landmarks[tooth]['mdCenter'][2])]
    arrayAxis = np.array(listAxis)
    norm = np.linalg.norm(arrayAxis)
    listNormAxis = (arrayAxis/norm).tolist()
    landmarks[tooth]['toothAxis'] = listNormAxis


    landmarks[tooth]['verticalToothAxis'] = [0, 1, 0]  if int(tooth) > 30 else [0, -1, 0]


    listAxis = np.cross(landmarks[tooth]['verticalToothAxis'], landmarks[tooth]['mdAxis']).tolist() if int(tooth)> 20 and int(tooth) < 30 or int(tooth) > 40 else np.cross(landmarks[tooth]['mdAxis'], landmarks[tooth]['verticalToothAxis']).tolist()
    arrayAxis = np.array(listAxis)
    norm = np.linalg.norm(arrayAxis)
    listNormAxis = (arrayAxis/norm).tolist()
    landmarks[tooth]['vestibularAxis'] = listNormAxis
    
    
    
    landmarks[tooth]['attachPoint'] = [landmarks[tooth]['Vestibular Gingival'][0],landmarks[tooth]["mdCenter"][1], landmarks[tooth]['Vestibular Gingival'][2]] 

    listAxis = np.cross(landmarks[tooth]['toothAxis'], landmarks[tooth]['mdAxis']).tolist() if  int(tooth)> 20 and int(tooth) < 30 or int(tooth) > 40 else np.cross(landmarks[tooth]['mdAxis'],landmarks[tooth]['toothAxis']).tolist() #int(tooth)> 20 and int(tooth) < 40
    arrayAxis = np.array(listAxis)
    norm = np.linalg.norm(arrayAxis)
    listNormAxis = (arrayAxis/norm).tolist()
    landmarks[tooth]['mdToothPerpendicular'] = listNormAxis



    # print(tooth)
    print(landmarks[tooth].keys())
    # print('----------', landmarks[tooth]['Mesial Point'][0] , landmarks[tooth]['Distal point'][0],
    # landmarks[tooth]['mdAxis'])

with open (os.path.join('optimized_data', 'landmarks.json'),'w') as f:
    json.dump(landmarks,f)
    
        

    


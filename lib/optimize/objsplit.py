#!/usr/bin/python3
# -*- coding: utf-8 -*-


"""
objsplit.py

Ce script Python est utilisé pour générer des données optimisées à partir de fichiers .obj non compressés. 
Il effectue les opérations suivantes :
- Séparer les objets dans les fichiers .obj
- Optimiser les objets séparés
- Générer des données liées aux dents, aux IPR, aux mouvements, aux repères, etc.
- Sauvegarder toutes les données générées dans un fichier JSON

Functions:
- suppress_stdout: context manager pour supprimer temporairement la sortie standard
- compute_rotation: Calcule la rotation à partir d'une matrice de transformation
- parse_obj_file: Parse un fichier OBJ et retourne un dictionnaire contenant les maillages et leurs sommets
- calculate_centroid: Calcule le centroïde d'un ensemble de sommets
- calculate_covariance_matrix: Calcule la matrice de covariance à partir d'un ensemble de sommets et de leur centroïde
- calculate_principal_axes: Calcule les axes principaux à partir d'une matrice de covariance
- calculate_rotations_from_axes: Calcule les rotations à partir des axes principaux
- is_valid_object_name: Vérifie si le nom d'un objet est valide
- calculate_extent: Calcule l'étendue (dimensions) d'un ensemble de sommets
- calculate_max_length: Calcule la longueur maximale d'une étendue
- create_bounding_box: Crée une boîte englobante à partir du centroïde et de la longueur maximale
- calculate_rotation_from_bounding_box: Calcule la rotation à partir d'une boîte englobante et de son centroïde
- calculate_face_normal: Calcule la normale d'une face à partir de ses sommets
- calculate_rotation_from_normals: Calcule la rotation à partir d'un ensemble de normales
- extract_position_and_rotation: Extrait la position et la rotation d'un fichier OBJ
- create_position_rotation_dict: Crée un dictionnaire contenant la position et la rotation pour chaque étape
- main: Fonction principale qui effectue la séparation et l'optimisation des fichiers
- optimizing_file: Optimise un fichier en réduisant le nombre de sommets et faces
- find_step_structure: Génère la structure des étapes à partir d'un fichier JSON.
- generateIPRdata: Génère les données d'IPR à partir d'un fichier CSV et d'un fichier JSON.
- generateTotalMoveData: Génère les données de mouvement total à partir d'un fichier CSV et d'un fichier JSON.
- generateToothData: Génère les données dentaires à partir d'un fichier JSON et d'un nom de dossier.
- updateJsonIpr: Met à jour les données d'IPR dans un fichier JSON.
- didToothMove: Vérifie si une dent a bougé entre deux étapes.
- generateMovData: Génère les données de mouvement à partir d'un fichier JSON et d'un répertoire de fichiers non compressés.

- generateArcanumMoveData(jsonData, totalSteps) :
  Cette fonction génère les données de mouvement pour chaque étape en fonction des données JSON fournies.
  Elle ajoute un nouvel attribut "movDataByArcanum" dans le JSON pour chaque étape, qui contient des informations sur les mouvements des arcades dentaires supérieures et inférieures.

- generateOptimizedData(uncom_files_dir, splitted_files_dir, optimized_files_dir, ipr_data_filename, landmark_data_filename, output_json_filename, landmarkxls_data_filename, pathMovementTable, output_history_filename) :
  Cette fonction est la fonction principale du script. Elle prend en entrée les chemins des différents fichiers et répertoires nécessaires pour les opérations.
  Elle réalise les opérations de séparation, d'optimisation et de génération des données, puis sauvegarde toutes les données générées dans un fichier JSON.


"""

import re
import os.path as p
import sys
from pprint import pprint
from contextlib import contextmanager
import os
import pymeshlab as ml
import shutil
import json
import csv, codecs, pywavefront, math
import numpy as np
# import meshlib.mrmeshpy as mr
# import trimesh
import pywavefront
from random import random
from datetime import datetime, timezone, timedelta
import re
import pandas as pd
import subprocess
import lib.optimize.bolton_analysis as ba
from decouple import config
from lib.loguru import logger
from .upload import aws
import time
from threading import Thread

# BLENDER_PATH = config('BLENDER_PATH', default='blender')
BLENDER_PATH = os.getenv('BLENDER_PATH', 'blender')

@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout

def compute_rotation(matrix, in_degrees=False):
    """
    Calcule la rotation à partir d'une matrice de transformation.
    :param matrix: matrice de transformation 4x4
    :param in_degrees: si True, retourne les angles de rotation en degrés, sinon en radians (par défaut)
    :return: liste contenant les angles de rotation [rx, ry, rz]
    """
    r = np.zeros(3)

    if matrix[2, 0] != 1 and matrix[2, 0] != -1:
        r[1] = -math.asin(matrix[2, 0])
        r[0] = math.atan2(matrix[2, 1] / math.cos(r[1]), matrix[2, 2] / math.cos(r[1]))
        r[2] = math.atan2(matrix[1, 0] / math.cos(r[1]), matrix[0, 0] / math.cos(r[1]))
    else:
        r[2] = 0
        if matrix[2, 0] == -1:
            r[1] = math.pi / 2
            r[0] = math.atan2(matrix[0, 1], matrix[0, 2])
        else:
            r[1] = -math.pi / 2
            r[0] = math.atan2(-matrix[0, 1], -matrix[0, 2])

    if in_degrees:
        return np.degrees(r)  # Convertir en degrés si in_degrees est True
    else:
        return r  # Retourner en radians par défaut

def parse_obj_file(obj_file_path):
    meshes = {}
    current_mesh_name = None
    vertices = []
    
    with open(obj_file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('g '):  # Nouveau groupe (mesh)
                current_mesh_name = line[2:].strip()
                meshes[current_mesh_name] = []
            elif line.startswith('v '):  # Vertex
                vertex = np.array(list(map(float, line[2:].split())))
                vertices.append(vertex)
            elif line.startswith('f '):  # Face
                if current_mesh_name is not None:
                    face_indices = list(map(int, re.findall(r'\d+', line)))
                    face_vertices = [vertices[i - 1] for i in face_indices]
                    meshes[current_mesh_name].append(face_vertices)
    return meshes

def calculate_centroid(vertices):
    return np.mean(vertices, axis=0)

def calculate_covariance_matrix(vertices, centroid):
    centered_vertices = vertices - centroid
    return np.cov(centered_vertices.T)

def calculate_principal_axes(covariance_matrix):
    eigenvalues, eigenvectors = np.linalg.eig(covariance_matrix)
    return eigenvectors

def calculate_rotations_from_axes(principal_axes):
    # (Utilisez la fonction compute_rotation que vous avez déjà définie)
    return compute_rotation(principal_axes)

def is_valid_object_name(name):
    pattern = r'^\d+:\s.*'
    return re.match(pattern, name) is not None

def calculate_extent(vertices):
    min_coords = np.min(vertices, axis=0)
    max_coords = np.max(vertices, axis=0)
    extent = max_coords - min_coords
    return extent

def calculate_max_length(extent):
    return np.max(extent)

def create_bounding_box(centroid, max_length):
    half_length = max_length / 2
    min_coords = centroid - half_length
    max_coords = centroid + half_length
    return min_coords, max_coords

def calculate_rotation_from_bounding_box(vertices, centroid):
    covariance_matrix = calculate_covariance_matrix(vertices, centroid)
    principal_axes = calculate_principal_axes(covariance_matrix)
    rotation_matrix = principal_axes
    return compute_rotation(rotation_matrix)

def calculate_face_normal(vertices):
    v0, v1, v2 = vertices
    edge1 = v1 - v0
    edge2 = v2 - v0
    normal = np.cross(edge1, edge2)
    return normal / np.linalg.norm(normal)

def calculate_rotation_from_normals(normals):
    normal_matrix = np.vstack(normals)
    covariance_matrix = np.cov(normal_matrix.T)
    eigenvalues, eigenvectors = np.linalg.eig(covariance_matrix)
    rotation_matrix = eigenvectors
    return compute_rotation(rotation_matrix)

def extract_position_and_rotation(obj_file_path):
    meshes = parse_obj_file(obj_file_path)
    positions_and_rotations = {}

    for name, faces in meshes.items():
        if is_valid_object_name(name):
            vertices = np.vstack([v for face in faces for v in face])
            centroid = calculate_centroid(vertices)
            extent = calculate_extent(vertices)
            max_length = calculate_max_length(extent)
            min_coords, max_coords = create_bounding_box(centroid, max_length)
            
            # Construire une boîte englobante approximative à partir des coordonnées min et max
            bounding_box_vertices = np.array([
                [min_coords[0], min_coords[1], min_coords[2]],
                [min_coords[0], min_coords[1], max_coords[2]],
                [min_coords[0], max_coords[1], min_coords[2]],
                [min_coords[0], max_coords[1], max_coords[2]],
                [max_coords[0], min_coords[1], min_coords[2]],
                [max_coords[0], min_coords[1], max_coords[2]],
                [max_coords[0], max_coords[1], min_coords[2]],
                [max_coords[0], max_coords[1], max_coords[2]],
            ])

            rotations = calculate_rotation_from_bounding_box(bounding_box_vertices, centroid)
            positions_and_rotations[name] = {"position": centroid.tolist(), "rotation": rotations.tolist()}

    return positions_and_rotations


def create_position_rotation_dict(file_paths):
    position_rotation_dict = {}

    for path in file_paths:
        # Extraire le numéro à partir du nom du fichier
        file_name = os.path.basename(path)
        step_number = int(re.findall(r'Step(\d+)', file_name)[0])
        
        # Extraire les positions et rotations
        position_rotation_info = extract_position_and_rotation(path)

        # Ajouter ou mettre à jour les informations dans le dictionnaire
        if step_number in position_rotation_dict:
            position_rotation_dict[step_number].update(position_rotation_info)
        else:
            position_rotation_dict[step_number] = position_rotation_info

    return position_rotation_dict


def main(file_in, spt_out, writing=True):
    splitted_file_names = []

    v_pat = re.compile(r"^v\s[\s\S]*")  # vertex
    vn_pat = re.compile(r"^vn\s[\s\S]*")  # vertex normal
    f_pat = re.compile(r"^f\s[\s\S]*")  # face
    o_pat = re.compile(r"^o\s[\s\S]*")  # named object
    ml_pat = re.compile(r"^mtllib[\s\S]*")  # .mtl file
    mu_pat = re.compile(r"^usemtl[\s\S]*")  # material to use
    s_pat = re.compile(r"^s\s[\s\S]*")  # shading
    vertices = ['None']  # because OBJ has 1-based indexing
    v_normals = ['None']  # because OBJ has 1-based indexing
    objects = {}
    faces = []
    mtllib = None
    usemtl = None
    shade = None
    o_id = None

    # with open(file_in, 'r') as f_in:
    #     lines = f_in.readlines()

    encodings_to_try = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
    lines = None

    for encoding in encodings_to_try:
        try:
            with open(file_in, 'r', encoding=encoding) as f_in:
                lines = f_in.readlines()
            print(f"Fichier lu avec succès avec l'encodage {encoding}")
            break
        except UnicodeDecodeError:
            print(f"Échec de lecture avec l'encodage {encoding}")

    for line in lines:
        v = v_pat.match(line)
        o = o_pat.match(line)
        f = f_pat.match(line)
        vn = vn_pat.match(line)
        ml = ml_pat.match(line)
        mu = mu_pat.match(line)
        s = s_pat.match(line)

        if v:
            vertices.append(v.group())
        elif vn:
            v_normals.append(vn.group())
        elif o:
          if o_id:
              new_o_id = o_id
              suffix = 0
              while new_o_id in objects:
                  suffix += 1
                  new_o_id = f"{o_id.strip()}_{suffix}\n"
              objects[new_o_id] = {'faces': faces,
                                  'usemtl': usemtl,
                                  's': shade}
              o_id = o.group()
              faces = []
          else:
              o_id = o.group()

        elif f:
            faces.append(f.group())
        elif mu:
            usemtl = mu.group()
        elif s:
            shade = s.group()
        elif ml:
            mtllib = ml.group()
        else:
            # ignore vertex texture coordinates, polygon groups, parameter space vertices
            pass
        
    if o_id:
        new_o_id = o_id
        suffix = 0
        while new_o_id in objects:
            suffix += 1
            new_o_id = f"{o_id.strip()}_{suffix}\n"
        # print("new_o_id : ", new_o_id)

        objects[new_o_id] = {'faces': faces,
                            'usemtl': usemtl,
                            's': shade}
    else:
        sys.exit("Cannot split an OBJ without named objects in it!")


    # vertex indices of a face
    fv_pat = re.compile(r"(?<= )\b[0-9]+\b", re.MULTILINE)
    # vertex normal indices of a face
    fn_pat = re.compile(r"(?<=\/)\b[0-9]+\b(?=\s)", re.MULTILINE)
    for o_id in objects.keys():
        faces = ''.join(objects[o_id]['faces'])
        f_vertices = {int(v) for v in fv_pat.findall(faces)}
        f_vnormals = {int(vn) for vn in fn_pat.findall(faces)}
        # vertex mapping to a sequence starting with 1
        v_map = {str(v): str(e) for e, v in enumerate(f_vertices, start=1)}
        vn_map = {str(vn): str(e) for e, vn in enumerate(f_vnormals, start=1)}
        faces_mapped = re.sub(fv_pat, lambda x: v_map[x.group()], faces)
        faces_mapped = re.sub(
            fn_pat, lambda x: vn_map[x.group()], faces_mapped)

        objects[o_id]['vertices'] = f_vertices
        objects[o_id]['vnormals'] = f_vnormals
        # old vertex indices are not needed anymore
        objects[o_id]['faces'] = faces_mapped

    oid_pat = re.compile(r"(?<=o\s).+")
    # with suppress_stdout():
    for o_id in objects.keys():
        fname = oid_pat.search(o_id).group()

        ind = 0

        nameFile = fname.replace(' ', '').replace('/', '.').replace('\\', '').split('(')[0].split(':')[0]  + ".obj"

        file_out = p.join(spt_out, nameFile)

        
        if(p.isfile(file_out)):

          if(writing == False and nameFile not in splitted_file_names):
            splitted_file_names.append(nameFile)

          while(p.isfile(file_out)):
            nameFile = fname.replace(' ', '').replace('/', '.').split('(')[0].split(':')[0] + "_" + str(ind) + ".obj"
            file_out = p.join(spt_out, nameFile)
            ind += 1
            if(writing == False and p.isfile(file_out) and nameFile not in splitted_file_names):
              splitted_file_names.append(nameFile)

        if(writing and nameFile not in splitted_file_names):
          splitted_file_names.append(nameFile)

          with open(file_out, 'w', newline=None) as f_out:

              if mtllib:
                  f_out.write(mtllib)

              f_out.write(o_id)

              for vertex in objects[o_id]['vertices']:
                  f_out.write(vertices[int(vertex)])

              for normal in objects[o_id]['vnormals']:
                  f_out.write(v_normals[int(normal)])

              if objects[o_id]['usemtl']:
                  f_out.write(objects[o_id]['usemtl'])

              if objects[o_id]['s']:
                  f_out.write(objects[o_id]['s'])

              f_out.write(objects[o_id]['faces'])
  

    return(splitted_file_names)


def translate_mesh(mesh, translation):
    mesh.vertices += translation


def get_csv_file_paths(directory_path):
    """
    Scans a directory and returns a list of absolute file paths of CSV files 
    matching the pattern 'StepXX_*.csv' where XX is a digit.

    Args:
        directory_path(str): The path of the directory to scan.

    Returns:
        file_paths(list): A list of absolute paths of the matched CSV files.
    """
    file_paths = []
    for file_name in os.listdir(directory_path):
        if re.match(r'^Step(\d+)_.*\.csv$', file_name):
            file_path = os.path.join(directory_path, file_name)
            file_paths.append(file_path)
        elif re.match(r'^Step (\d+) - Info\.csv$', file_name):
            file_path = os.path.join(directory_path, file_name)
            file_paths.append(file_path)
    return file_paths


def copy_other_objects(step, obj_folder_path, destination_folder):
    """
    Copies all .obj files for the given step that are neither pontic teeth nor "Mandible.obj" nor "Maxilla.obj".

    Args:
        step (str): The step to process.
        obj_folder_path (str): The path to the folder containing the OBJ files.
        destination_folder (str): The path to the destination folder where the files will be copied.
        pontic_teeth (dict): Dictionary of pontic teeth for each step.
    """
    obj_folder_for_step = os.path.join(obj_folder_path, step)
    if not os.path.isdir(obj_folder_for_step):
        print(f"Missing OBJ folder for step: {step}")
        return

    obj_files_for_step = [f for f in os.listdir(obj_folder_for_step) if f.endswith('.obj')]
    
    # Extract pontic teeth for this step and add file extension ".obj"
    # pontic_teeth_for_step = [f"{tooth}.obj" for tooth in pontic_teeth.get(step, [])]
    pontic_teeth_for_step = []
    
    # Exclude pontic teeth, Mandible.obj and Maxilla.obj
    obj_files_to_copy = [f for f in obj_files_for_step if f not in pontic_teeth_for_step and f not in ["Mandible.obj", "Maxilla.obj"]]
    
    # Copy the files to the destination folder
    for obj_file in obj_files_to_copy:
        destination_folder_for_objects = os.path.join(destination_folder, "objects")
        os.makedirs(destination_folder_for_objects, exist_ok=True)  # Create the destination sub-folder for this step if it does not exist yet
        shutil.copy2(os.path.join(obj_folder_for_step, obj_file), destination_folder_for_objects)


# def find_and_copy_pontics(csv_file_paths, obj_folder_path, destination_folder):
#     """
#     Finds pontic objects by comparing data from CSV files and OBJ files and copy them to a destination folder.

#     Args:
#         csv_file_paths(list): A list of absolute paths of the CSV files to process.
#         obj_folder_path(str): The path to the folder containing the OBJ files.
#         destination_folder(str): The path to the destination folder where the pontic files will be copied.

#     Returns:
#         dict_pontics(dict): A dictionary containing the pontic objects for each step.
#     """

#     pattern_tooth = re.compile(r'^Tooth \d{2}$')  # Matches "Tooth XX"
#     pattern_tooth_obj = re.compile(r'^Tooth\d{2}$')  # Matches "Tooth XX"
#     dict_pontics = {}
    
#     # Group CSV file paths by step
#     csv_files_by_step = {}
#     for csv_file_path in get_csv_file_paths(csv_file_paths):
#         file_name = os.path.basename(csv_file_path)
#         step = re.match(r'^Step(\d+)_.*\.csv$', file_name)
#         if step is not None:
#             step = step.group(1)
#         else:
#             print(f"Invalid file name format: {file_name}")
#             continue

#         if step not in csv_files_by_step:
#             csv_files_by_step[step] = []

#         csv_files_by_step[step].append(csv_file_path)

#     # Process each step
#     for step, csv_file_paths_for_step in csv_files_by_step.items():
#         # Get all the tooth names in the CSV files for this step
#         csv_teeth = set()
#         for csv_file_path in csv_file_paths_for_step:
#             df = pd.read_csv(csv_file_path, sep='\t')  # You might need to adjust the separator
#             csv_teeth.update({row['name'].replace(' ', '') for index, row in df.iterrows() if pattern_tooth.match(row['name'])})

#         # print(f"Step {step} - Teeth in CSV files: {csv_teeth}")
        
#         # Check the OBJ files for this step
#         obj_folder_for_step = os.path.join(obj_folder_path, step)
#         if not os.path.isdir(obj_folder_for_step):
#             print(f"Missing OBJ folder for step: {step}")
#             continue
        
#         obj_files_for_step = [f for f in os.listdir(obj_folder_for_step) if f.endswith('.obj')]
#         obj_teeth = {os.path.splitext(f)[0] for f in obj_files_for_step if pattern_tooth_obj.match(f.split('.')[0])}  # Get the tooth names from the file names

#         # print(f"Step {step} - Teeth in OBJ files: {obj_teeth}")
        
#         # Find the pontic teeth for this step (teeth that are in the OBJ files but not in the CSV file)
#         pontic_teeth = obj_teeth - csv_teeth
        
#         # Copy the pontic files to the destination folder
#         # for pontic_tooth in pontic_teeth:
#         #     pontic_file = f"{pontic_tooth}.obj"
#         #     new_pontic_file = f"{pontic_tooth}_{step}.obj"  # Append the step to the file name
#         #     destination_folder_for_pontics = os.path.join(destination_folder, "pontics")
#         #     os.makedirs(destination_folder_for_pontics, exist_ok=True)  # Create the destination sub-folder for this step if it does not exist yet
#         #     shutil.copy2(os.path.join(obj_folder_for_step, pontic_file), os.path.join(destination_folder_for_pontics, new_pontic_file))

            
#         dict_pontics[step] = list(pontic_teeth)

#     return dict_pontics





def process_csv_matrix(file_paths):
    """
    Processes a list of CSV files, each containing transformation data for objects.
    Extracts transformation matrices for objects whose names match the pattern 'XX:*' or 'Tooth XX'
    where XX is a digit. Stores each transformation matrix in a nested dictionary
    keyed by step number and attachment number or "ToothXX". If multiple attachments with the same 
    number exist, appends an underscore and an index to the attachment number.

    Args:
        file_paths(list): A list of absolute paths of the CSV files to process.

    Returns:
        transformation_attachments(dict), transformation_tooth(dict): A nested dictionary containing transformation
        matrices for each object, keyed by step number and attachment number or "ToothXX".
    """
    # Check the name format
    pattern_attachment = re.compile(r'^\d+:.*$')  # Matches "XX:" at the start of the string
    pattern_tooth = re.compile(r'^Tooth \d{2}( \(Copy\))?$')  # Matches "Tooth XX" or "Tooth XX (Copy)"
    transformation_attachments = {}
    transformation_tooth = {}

    for file_path in file_paths:
        # Extract the step number from the file name
        file_name = os.path.basename(file_path)
        step = re.match(r'^Step(\d+)_.*\.csv$', file_name)
        if step is not None:
            step = step.group(1)
        else:
            print(f"Invalid file name format: {file_name}")
            continue

        # Read the csv file
        df = pd.read_csv(file_path, sep='\t')  # You might need to adjust the separator

        if step not in transformation_attachments:
            transformation_attachments[step] = {}
            transformation_tooth[step] = {}

        for index, row in df.iterrows():
            if pattern_attachment.match(row['name']):
                # Extract the attachment number and position and rotation matrix
                identifier = re.match(r'^(\d+):.*$', row['name']).group(1)
                dict_to_fill = transformation_attachments

            elif pattern_tooth.match(row['name']):
                # Extract the tooth number and position and rotation matrix
                identifier = row['name'].replace(' ', '')
                dict_to_fill = transformation_tooth

            else:
                continue

            position = np.array([row['oX'], row['oY'], row['oZ']])
            rotation = np.array([[row['xX'], row['yX'], row['zX']],
                                 [row['xY'], row['yY'], row['zY']],
                                 [row['xZ'], row['yZ'], row['zZ']]])

            # Create a 4x4 transformation matrix
            transformation_matrix = np.eye(4)
            transformation_matrix[0:3, 0:3] = rotation
            transformation_matrix[0:3, 3] = position

            # Convert the transformation matrix to a nested list
            transformation_matrix = transformation_matrix.tolist()

            # Check if identifier already exists, if so, append an index
            if identifier in dict_to_fill[step]:
                i = 0
                while f"{identifier}_{i}" in dict_to_fill[step]:
                    i += 1
                identifier = f"{identifier}_{i}"

            dict_to_fill[step][identifier] = transformation_matrix

    # Return the transformation attachments and transformation tooth
    return transformation_attachments, transformation_tooth


def optimizing_file(file_in_dir,file_out_name, divide_by=0.1):
  ms = ml.MeshSet()
  ms.load_new_mesh(file_in_dir) #'out_dir/Mandible.obj'
  m = ms.current_mesh()
  # print('input mesh has', m.vertex_number(), 'vertex and', m.face_number(), 'faces')

  #Target number of vertex
  TARGET=m.vertex_number()*divide_by

  #Simplify the mesh. Only first simplification will be agressive
  while (ms.current_mesh().vertex_number() > TARGET):
      ms.apply_filter('meshing_decimation_quadric_edge_collapse', preservenormal=True)#, targetfacenum=numFaces, preservenormal=True)
      
  m = ms.current_mesh()
  # print('output mesh has', m.vertex_number(), 'vertex and', m.face_number(), 'faces')
  ms.save_current_mesh(file_out_name) #".obj file")


def find_teeth_structure(list_all,output_json): 
  output_json['upper'] = []
  output_json['lower'] = []
  output_json['attach'] = []
  output_json['quadrant'] = [0,0,0,0]
  output_json['stages'] = []
  output_json['fake'] = []

  for item in list_all:
    name = item.split('.')[0]
    name = name.split('_')[0]
    if len(name) < 3:
      output_json['attach'].append(item)
    elif 'Tooth' in item:
      tooth_number = item.split('.')[0][5:]
      if tooth_number[0] == '1':
        output_json['upper'].append(item)
        output_json['quadrant'][0] += 1
      elif tooth_number[0] == '2':
        output_json['upper'].append(item)
        output_json['quadrant'][1] += 1
      elif tooth_number[0] == '3':
        output_json['lower'].append(item)
        output_json['quadrant'][2] += 1
      elif tooth_number[0] == '4':
        output_json['lower'].append(item)
        output_json['quadrant'][3] += 1

def find_step_structure(output_json):
  step_i = output_json['steps']
  for i in range(step_i):
    step_dict = {}
    step_dict['step'] = i+1
    step_dict['path'] = '/' + str(i) + '/'
    step_dict['maxilla'] = 'Maxilla.obj'
    step_dict['mandible'] = 'Mandible.obj'
    # The following needs to be calculated
    step_dict['maxillaMatrix'] = {}
    step_dict['mandibleMatrix'] = {}
    step_dict['upperMatrices'] = []
    step_dict['lowerMatrices'] = []
    step_dict['upperIPR'] = []
    step_dict['lowerIPR'] = []

    output_json['stages'].append(step_dict)


def find_highest_files_landmarks(directory):
    regex = re.compile(r'Step (\d+) - Landmarks')
    highest_step = -1
    files_to_process = ""

    for filename in os.listdir(directory):
        match = regex.match(filename)
        if match:
            step = int(match.group(1))
            if step > highest_step:
                highest_step = step
                files_to_process = os.path.join(directory, filename)
    
    return files_to_process


def find_highest_step_files_Spacing(directory):
    # Expression régulière pour identifier les fichiers et extraire le numéro de step
    regex = re.compile(r'Step (\d+) - Protocol Distances (U|L)\.csv')
    highest_step = -1
    files_to_process = {'U': None, 'L': None}

    for filename in os.listdir(directory):
        match = regex.match(filename)
        if match:
            step, part = int(match.group(1)), match.group(2)
            if step > highest_step:
                highest_step = step
                files_to_process = {'U': None, 'L': None}  # Réinitialise pour le plus haut step trouvé
            if step == highest_step:
                if part == 'U':
                    files_to_process['U'] = os.path.join(directory, filename)
                elif part == 'L':
                    files_to_process['L'] = os.path.join(directory, filename)
    
    return files_to_process['U'], files_to_process['L']


def find_highest_step_files_IPR(directory):
    # Expression régulière pour identifier les fichiers et extraire le numéro de step
    regex = re.compile(r'Step (\d+) - Protocol Stripping (U|L)\.csv')
    highest_step = -1
    files_to_process = {'U': None, 'L': None}

    for filename in os.listdir(directory):
        match = regex.match(filename)
        if match:
            step, part = int(match.group(1)), match.group(2)
            if step > highest_step:
                highest_step = step
                files_to_process = {'U': None, 'L': None}  # Réinitialise pour le plus haut step trouvé
            if step == highest_step:
                if part == 'U':
                    files_to_process['U'] = os.path.join(directory, filename)
                elif part == 'L':
                    files_to_process['L'] = os.path.join(directory, filename)
    
    return files_to_process['U'], files_to_process['L']


def generateIPRdata(pathIPR, jsonData, pathUpper=None, pathLower=None):
    # Initialisation des structures de données
    iprDataNew = {}
    for i in range(jsonData['steps']):
        iprDataNew[i+1] = {'upper': [], 'lower': []}
    
    # Traitement du fichier IPR.csv si existant
    if os.path.exists(pathIPR):
        with codecs.open(pathIPR, 'rU', 'utf-16') as file:
            iprReader = csv.reader(file)
            iprData = process_ipr_file(iprReader)
    
    # Sinon, traitement des fichiers Step XX - Protocol Stripping U/L.csv
    else:
        print("Two files IPR generation")
        if pathUpper and os.path.exists(pathUpper):
            print("Upper files IPR generation")
            with codecs.open(pathUpper, 'rU', 'utf-16') as file:
                iprReader = csv.reader(file)
                iprData = process_ipr_file(iprReader, gumName='Maxilla')
        
        if pathLower and os.path.exists(pathLower):
            print("Lower files IPR generation")
            with codecs.open(pathLower, 'rU', 'utf-16') as file:
                iprReader = csv.reader(file)
                iprDataTemp = process_ipr_file(iprReader, gumName='Mandible')
                if 'Maxilla' in iprData:
                    iprData['Mandible'] = iprDataTemp['Mandible']
                else:
                    iprData = iprDataTemp
    
    # Conversion des données IPR traitées en structure finale
    for gumName, details in iprData.items():
        loc = 'upper' if gumName == 'Maxilla' else 'lower'
        for step, iprs in details['validIprs'].items():
            iprDataNew[step+1][loc].extend(iprs)

   
    
    return iprDataNew


def process_ipr_file(iprReader, gumName=None):
    iprData = {'Maxilla': {'Tooth': [], 'validIprs': {}}, 'Mandible': {'Tooth': [], 'validIprs': {}}}
    currentGumName = gumName
    for row in iprReader:
        # Conversion et nettoyage de la ligne
        splittedRow = row[0].split('\t')
        splittedRow = [item.replace('"', '').replace('Before ', '') for item in splittedRow]
        splittedRow = ['0' if item == '' else item for item in splittedRow]

        # Détermination de la mâchoire concernée si gumName n'est pas spécifié
        if gumName is None:
            if 'Maxilla' in splittedRow[0] or 'Mandible' in splittedRow[0]:
                gumName = 'Maxilla' if 'Maxilla' in splittedRow[0] else 'Mandible'
        else:
            # Si gumName est spécifié, cela signifie que nous traitons les fichiers séparés
            # et donc toutes les lignes appartiennent à la même mâchoire
            if 'mm' in splittedRow[0]:
                iprData[gumName]['Tooth'] = splittedRow[1:]
            elif 'Step' in splittedRow[0]:
                stepNum = int(splittedRow[0].split(' ')[1])
                iprs = [float(ipr) for ipr in splittedRow[1:]]
                iprData[gumName]['validIprs'].setdefault(stepNum, [])
                # for j, ipr in enumerate(iprs):
                #     if ipr != 0:
                #         tooth = iprData[gumName]['Tooth'][j]
                #         toothId, toothSide = int(tooth[:2]), tooth[-1]
                #         iprData[gumName]['validIprs'][stepNum].append([toothId, toothSide, ipr])
                for j, ipr in enumerate(iprs):
                  if ipr != 0:
                      tooth = iprData[currentGumName]['Tooth'][j]
                      toothId, toothSide = int(tooth[:2]), tooth[-1]

                      if j > 0:
                          if iprs[j-1] == 0:
                              toothLeft = iprData[currentGumName]['Tooth'][j-1]
                              toothIdLeft, toothSideLeft = int(toothLeft[:2]), toothLeft[-1]

                              if toothId == 21 or toothId == 31:
                                if toothId != toothIdLeft and toothSide == 'm' and toothSideLeft == 'm':                              
                                    iprData[currentGumName]['validIprs'][stepNum].append([toothIdLeft, toothSideLeft, 0])
                              elif toothIdLeft > 20: 
                                if toothId != toothIdLeft and toothSideLeft == 'd':
                                  iprData[currentGumName]['validIprs'][stepNum].append([toothIdLeft, toothSideLeft, 0])
                              else:
                                if toothId != toothIdLeft and toothSide == 'd':
                                    iprData[currentGumName]['validIprs'][stepNum].append([toothIdLeft, toothSideLeft, 0])
                      
                      iprData[currentGumName]['validIprs'][stepNum].append([toothId, toothSide, ipr])

                      if j < len(iprs) - 1:
                          if iprs[j+1] == 0:
                              toothRight = iprData[currentGumName]['Tooth'][j+1]
                              toothIdRight, toothSideRight = int(toothRight[:2]), toothRight[-1]
                              
                              if toothId == 11 or toothId == 41:
                                  if toothId != toothIdRight and toothSide =='m' and toothSideRight =='m':                              
                                    iprData[currentGumName]['validIprs'][stepNum].append([toothIdRight, toothSideRight, 0])
                              elif toothIdRight > 20: 
                                if toothId != toothIdRight and toothSide == 'd':
                                    if  iprs[j+2] == 0:
                                      if iprData[currentGumName]['Tooth'][j+2]:
                                        toothnext = iprData[currentGumName]['Tooth'][j+2]
                                        if int(toothRight[:2]) == toothIdRight and toothnext[-1] == 'm':
                                          continue
                                        else:
                                          iprData[currentGumName]['validIprs'][stepNum].append([toothIdRight, toothSideRight, 0])
                                    else:
                                      iprData[currentGumName]['validIprs'][stepNum].append([toothIdRight, toothSideRight, 0])
                              else:
                                if toothId != toothIdRight and toothSide == 'm':
                                  if  iprs[j+2] == 0:
                                    if iprData[currentGumName]['Tooth'][j+2]:
                                      toothnext = iprData[currentGumName]['Tooth'][j+2]
                                      if int(toothRight[:2]) == toothIdRight and toothnext[-1] == 'm':
                                        continue
                                      else:
                                        iprData[currentGumName]['validIprs'][stepNum].append([toothIdRight, toothSideRight, 0])
                                  else:
                                    iprData[currentGumName]['validIprs'][stepNum].append([toothIdRight, toothSideRight, 0])
                               
    

    return iprData


def process_spacing_file_separate(spacingReader, gumName):
    spacingData = {'Maxilla': {'Tooth': [], 'validSpacings': {}}, 'Mandible': {'Tooth': [], 'validspacings': {}}}
    currentGumName = gumName
    for row in spacingReader:
        splittedRow = row[0].split('\t')
        splittedRow = [item.replace('"', '').replace('Before ', '') for item in splittedRow]
        splittedRow = ['0' if item == '' else item for item in splittedRow]

        if 'mm' in splittedRow[0]:
            spacingData[currentGumName]['Tooth'] = splittedRow[1:]
        elif 'Step' in splittedRow[0]:
            stepNum = int(splittedRow[0].split(' ')[1])
            spacings = [float(spacing) for spacing in splittedRow[1:]]
            spacingData[currentGumName]['validSpacings'].setdefault(stepNum, [])
            for j, spacing in enumerate(spacings):
                if spacing != 0:
                    tooth = spacingData[currentGumName]['Tooth'][j]
                    toothId, toothSide = int(tooth[:2]), tooth[-1]
                    spacingData[currentGumName]['validSpacings'][stepNum].append([toothId, toothSide, spacing])

    return spacingData


def process_ipr_file_separate(iprReader, gumName):
    iprData = {'Maxilla': {'Tooth': [], 'validIprs': {}}, 'Mandible': {'Tooth': [], 'validIprs': {}}}
    currentGumName = gumName
    for row in iprReader:
        splittedRow = row[0].split('\t')
        splittedRow = [item.replace('"', '').replace('Before ', '') for item in splittedRow]
        splittedRow = ['0' if item == '' else item for item in splittedRow]

        if 'mm' in splittedRow[0]:
            iprData[currentGumName]['Tooth'] = splittedRow[1:]
        elif 'Step' in splittedRow[0]:
            stepNum = int(splittedRow[0].split(' ')[1])
            iprs = [float(ipr) for ipr in splittedRow[1:]]
            iprData[currentGumName]['validIprs'].setdefault(stepNum, [])
            # for j, ipr in enumerate(iprs):
            #     if ipr != 0:
            #         tooth = iprData[currentGumName]['Tooth'][j]
            #         toothId, toothSide = int(tooth[:2]), tooth[-1]
            #         iprData[currentGumName]['validIprs'][stepNum].append([toothId, toothSide, ipr])
            for j, ipr in enumerate(iprs):
              if ipr != 0:
                  tooth = iprData[currentGumName]['Tooth'][j]
                  toothId, toothSide = int(tooth[:2]), tooth[-1]

                  if j > 0:
                      if iprs[j-1] == 0:
                          toothLeft = iprData[currentGumName]['Tooth'][j-1]
                          toothIdLeft, toothSideLeft = int(toothLeft[:2]), toothLeft[-1]

                          if toothId == 21 or toothId == 31:
                            if toothId != toothIdLeft and toothSide == 'm' and toothSideLeft == 'm':                              
                                iprData[currentGumName]['validIprs'][stepNum].append([toothIdLeft, toothSideLeft, 0])
                          elif toothIdLeft > 20 and toothIdLeft < 29 or toothIdLeft > 30 and toothIdLeft < 39: 
                            if toothId != toothIdLeft and toothSideLeft == 'd':
                              iprData[currentGumName]['validIprs'][stepNum].append([toothIdLeft, toothSideLeft, 0])
                          else:
                             if toothId != toothIdLeft and toothSide == 'd':
                                iprData[currentGumName]['validIprs'][stepNum].append([toothIdLeft, toothSideLeft, 0])
                  
                  iprData[currentGumName]['validIprs'][stepNum].append([toothId, toothSide, ipr])

                  if j < len(iprs) - 1:
                      if iprs[j+1] == 0:
                          toothRight = iprData[currentGumName]['Tooth'][j+1]
                          toothIdRight, toothSideRight = int(toothRight[:2]), toothRight[-1]
                          
                          if toothId == 11 or toothId == 41:
                              if toothId != toothIdRight and toothSide =='m' and toothSideRight =='m':                              
                                iprData[currentGumName]['validIprs'][stepNum].append([toothIdRight, toothSideRight, 0])
                          elif toothIdRight > 20 and toothIdRight < 29 or toothIdRight > 30 and toothIdRight < 39: 
                            if toothId != toothIdRight and toothSide == 'd':
                                if  iprs[j+2] == 0 and iprs[j-1] == 0:
                                  if iprData[currentGumName]['Tooth'][j+2]:
                                    toothnext = iprData[currentGumName]['Tooth'][j+2]
                                    if int(toothnext[:2]) == toothIdRight and toothnext[-1] == 'd':
                                      continue
                                    else:
                                      iprData[currentGumName]['validIprs'][stepNum].append([toothIdRight, toothSideRight, 0])
                                  else:
                                    iprData[currentGumName]['validIprs'][stepNum].append([toothIdRight, toothSideRight, 0])
                                else:
                                  iprData[currentGumName]['validIprs'][stepNum].append([toothIdRight, toothSideRight, 0])
                          else:
                            if toothId != toothIdRight and toothSideRight == 'd':
                              if  iprs[j+2] == 0 and iprs[j-1] == 0:
                                if iprData[currentGumName]['Tooth'][j+2]:
                                  toothnext = iprData[currentGumName]['Tooth'][j+2]
                                  if int(toothnext[:2]) == toothIdRight and toothnext[-1] == 'm':
                                    continue
                                  else:
                                    iprData[currentGumName]['validIprs'][stepNum].append([toothIdRight, toothSideRight, 0])
                                else:
                                  iprData[currentGumName]['validIprs'][stepNum].append([toothIdRight, toothSideRight, 0])
                              else:
                                iprData[currentGumName]['validIprs'][stepNum].append([toothIdRight, toothSideRight, 0])
                               
    

    return iprData

def generateIPRdataSeparate(pathUpper, pathLower, jsonData):
    print("Début de la génération des données IPR séparées...")
    iprDataNew = {i+1: {'upper': [], 'lower': []} for i in range(jsonData['steps'])}


    print(f"pathUpper, pathLower : {pathUpper}, {pathLower}")

    # Traitement du fichier pour la mâchoire supérieure
    if pathUpper and os.path.exists(pathUpper):
        print(f"Traitement du fichier supérieur : {pathUpper}")
        try:
            with codecs.open(pathUpper, 'rU', 'utf-16') as file:
                iprReader = csv.reader(file)
                iprDataUpper = process_ipr_file_separate(iprReader, 'Maxilla')
                print("Données supérieures traitées avec succès.")
        except Exception as e:
            print(f"Erreur lors du traitement du fichier supérieur : {e}")
    else:
        print("Fichier supérieur introuvable ou chemin non fourni.")
        iprDataUpper = {'Maxilla': {'validIprs': {}}}  # Assurez-vous que la structure est correcte même en cas d'erreur

    # Traitement du fichier pour la mâchoire inférieure
    if pathLower and os.path.exists(pathLower):
        print(f"Traitement du fichier inférieur : {pathLower}")
        try:
            with codecs.open(pathLower, 'rU', 'utf-16') as file:
                iprReader = csv.reader(file)
                iprDataLower = process_ipr_file_separate(iprReader, 'Mandible')
                print("Données inférieures traitées avec succès.")
        except Exception as e:
            print(f"Erreur lors du traitement du fichier inférieur : {e}")
    else:
        print("Fichier inférieur introuvable ou chemin non fourni.")
        iprDataLower = {'Mandible': {'validIprs': {}}}  # Assurez-vous que la structure est correcte même en cas d'erreur

    

    # Fusion des données des mâchoires supérieure et inférieure
    print("Fusion des données des mâchoires supérieure et inférieure...")
    try:
        for step in range(1, jsonData['steps'] + 1):
            if step in iprDataUpper['Maxilla']['validIprs']:
                iprDataNew[step]['upper'].extend(iprDataUpper['Maxilla']['validIprs'][step])
            if step in iprDataLower['Mandible']['validIprs']:
                iprDataNew[step]['lower'].extend(iprDataLower['Mandible']['validIprs'][step])
        print("Fusion terminée avec succès.")
    except Exception as e:
        print(f"Erreur lors de la fusion des données : {e}")
  


    return iprDataNew


def extract_tooth_distances(pathUpper, pathLower):
    results = []
    paths = [pathUpper, pathLower]

    # Trouver les indices des lignes intéressantes
    teeth_index = 1  # Généralement la seconde ligne contient les noms de dents
    distances_index = 4  # La cinquième ligne contient les distances

    for path in paths:
        print(f"Traitement du fichier: {path}")
        # try:
        with open(path, 'r', encoding='utf-16') as file:
          reader = csv.reader(file, delimiter='\t')

          list_of_lists = []

          for row in reader:
              list_of_lists.append(row)

          # Obtenir les lignes de dents et de distances
          teeth = list_of_lists[teeth_index]
          distances = list_of_lists[distances_index]

          # Associer chaque paire de dents avec sa distance correspondante
          for tooth_text, distance in zip(teeth, distances):
            
              # Vérifier le format de tooth_text
              if re.match(r'^\d+ - \d+$', tooth_text) and distance:
                  # try:
                  tooth1, tooth2 = map(int, tooth_text.split(' - '))
                  distance = float(distance)  # Convertir distance en float
                  results.append({
                      'Tooth1': tooth1,
                      'Tooth2': tooth2,
                      'Distance': distance
                  })
                  # except ValueError as ve:
                  #     print(f"Erreur de conversion pour {tooth_text} ou {distance}: {ve}")

        # except Exception as e:
        #     print(f"Erreur lors du traitement du fichier {path}: {e}")

    return results


def generateTotalMoveData(pathMovementTable, jsonData):

  movementTable = {}
  if(os.path.exists(pathMovementTable)):
    movementReader = csv.reader(codecs.open(pathMovementTable,'rU','utf-16'))
  else:
    print(("The movement Table ", pathMovementTable, " cannot be found. Skipping generateTotalMoveData"))
    logger.error(f"The movement Table {pathMovementTable}, cannot be found. Skipping generateTotalMoveData")
    return jsonData

  rows = []
  for row in movementReader:
    splittedRow = row[0].split('\t')
    for i in range(len(splittedRow)):
      splittedRow[i] = splittedRow[i].replace('"','') 
      
    rows.append(splittedRow)

  ind_row = 1
  #Loop to explore the rows
  for row in rows :
    # If we find a row of tooth, we add the properties of each tooth
    if(row[0] == 'Tooth'):
      # For each tooth
      ind_tooth = 1
      for tooth in row[1:]:
        #If it's tooth number we add it
        if(len(tooth) == 2):
          movementTable[tooth] = []
          # For each property
          for toothProperty in rows[ind_row:] :
            #If the property doesn't have the Tooth value
            if(toothProperty[0] != "Tooth" and toothProperty[0] != 'Mandible' and toothProperty[0] != 'Maxilla'):
              splittedProperty = toothProperty[0].split(' ')
              type = ""
              for item in splittedProperty[:-1]:
                # if(item != '+/-'):
                if(type == "") :
                  type += item
                else:
                  type += " " + item
                
              unity = splittedProperty[-1][1:-1]
              value = toothProperty[ind_tooth]
              if(value == ''): value = 0
              else: value = float(value)

              movementTable[tooth].append({"type": type, "unity": unity, "value": value})
            # Else we break the loop, because we found a new tooth row
            else:
              break
        ind_tooth += 1
    ind_row += 1
  jsonData['movementTable'] = movementTable
  return jsonData


def generateToothData(jsonData, folderName):
  locs = ['upper','lower']
  loc = locs[0]
  toothData = {}

  print("jsonData['steps']", jsonData['steps'])
  print("folderName", folderName)

  for i in range(jsonData['steps']):
    print("Tooth Data Step : ", i)

    toothData[i+1] = {} #generating for each step
    for loc in locs:
      xcall, ycall, zcall, toothNumers = [], [] , [], []

      # print(jsonData[loc])

      for tooth in jsonData[loc]: #generating for each tooth
        toothUrl = os.path.join(folderName,str(i),tooth)

        # print("toothUrl", toothUrl)

        scene = pywavefront.Wavefront(toothUrl,create_materials=True)
        x,y,z = [], [], []
        for j in range(len(scene.vertices)):
          x.append(scene.vertices[i][0])
          y.append(scene.vertices[i][1])
          z.append(scene.vertices[i][2])
        
        toothNum = tooth.split('.')[0]
        toothNum = int(toothNum.split('_')[0][-2:])
        toothNumers.append(toothNum)
        toothData[i+1][toothNum] = {}
        toothData[i+1][toothNum]['xmax'] = max(x)
        toothData[i+1][toothNum]['xmin'] = min(x)
        toothData[i+1][toothNum]['ymax'] = max(y)
        toothData[i+1][toothNum]['ymin'] = min(y)
        toothData[i+1][toothNum]['zmax'] = max(z)
        toothData[i+1][toothNum]['zmin'] = min(z)
        
        toothData[i+1][toothNum]['xc'] = 0.5*(toothData[i+1][toothNum]['xmax']+toothData[i+1][toothNum]['xmin'])
        toothData[i+1][toothNum]['yc'] = 0.5*(toothData[i+1][toothNum]['ymax']+toothData[i+1][toothNum]['ymin'])
        toothData[i+1][toothNum]['zc'] = 0.5*(toothData[i+1][toothNum]['zmax']+toothData[i+1][toothNum]['zmin'])

        toothData[i+1][toothNum]['isLower'] = False if loc == 'upper' else True
        toothData[i+1][toothNum]['isLeft'] = True if toothNum<20 or toothNum>40 else False

        # print("toothData[", (i+1), "][", toothNum, "]", toothData[i+1][toothNum])

        xcall.append(toothData[i+1][toothNum]['xc']) #
        ycall.append(toothData[i+1][toothNum]['yc'])
        zcall.append(toothData[i+1][toothNum]['zc'])
      
      toothData[i+1][loc+'Center'] =  [0.5*(max(xcall)+min(xcall)),0.5*(max(ycall)+min(ycall)),0.5*(max(zcall)+min(zcall))]
      toothData[i+1][loc+'Num'] = toothNumers


  for step in toothData:
    for loc in locs:
      avgCenter = toothData[step][loc+'Center']
      for i in range(len(toothData[step][loc+'Num'])-1):
        toothNum, toothNumNext =toothData[step][loc+'Num'][i],toothData[step][loc+'Num'][i+1]
        tooth, toothNext = toothData[step][toothNum], toothData[step][toothNumNext]
        toothCenter = [0.5*(tooth['xc']+toothNext['xc']),avgCenter[1],0.5*(tooth['zc']+toothNext['zc'])]
        if toothData[step][toothNum]['isLeft'] == toothData[step][toothNumNext]['isLeft']: 
          #Most of the teeth will be in this case, except two cases in upper and lower center
          #first item for pair is for tooth Num
          if toothNum > toothNumNext : 
            pair = ['m','d']
          else:
            pair = ['d','m']
        else:
          pair = ['m','m']
        
        
        toothData[step][toothNum][pair[0]] = {}
        toothData[step][toothNum][pair[0]]['pos'] = toothCenter
        toothData[step][toothNum][pair[0]]['rotSelf'] = [0.75,0,0] if toothData[step][toothNum]['isLower'] else [-0.75,0,0]
        toothData[step][toothNumNext][pair[1]] = {}
        toothData[step][toothNumNext][pair[1]]['pos'] = toothCenter
        toothData[step][toothNumNext][pair[1]]['rotSelf'] = [0.75,0,0] if toothData[step][toothNumNext]['isLower'] else [-0.75,0,0]

        if toothCenter[2] >0:
          yRot = math.atan(abs(toothCenter[0] / toothCenter[2]))
        else: 
          yRot = math.pi/2
        if toothCenter[0] < 0:
          yRot *= -1
        toothData[step][toothNum][pair[0]]['rotParent'] = [0,yRot,0]
        toothData[step][toothNumNext][pair[1]]['rotParent'] = [0,yRot,0]
  return toothData



def updateJsonIpr(jsonData,iprData,toothData):
  locs = ['upper','lower']
  # print(toothData)
  # try:
  for steps in jsonData['stages']:
    
    step = steps['step']
    for loc in locs:
      for iprItems in iprData[step][loc]:
        iprValue = iprItems[2]
        iprSubscript = str(iprItems[0]) + iprItems[1]
        
        if iprItems[0] not in toothData[step]:
                continue 
        
        pos = toothData[step][iprItems[0]][iprItems[1]]['pos']

        rotParent = toothData[step][iprItems[0]][iprItems[1]]['rotParent']

        rotSelf = toothData[step][iprItems[0]][iprItems[1]]['rotSelf']

        oneIPRItem = [iprValue,pos,rotParent,rotSelf,iprSubscript]
        steps[loc+'IPR'].append(oneIPRItem)

  # except Exception as e:
  #    pprint(e)
  
  return jsonData



def didToothMove(toothDataStep1, toothDataStep2): #data 1 and data 2 are lists
  movementOccured = 0
  for i in range(len(toothDataStep1)):
    if float(toothDataStep1[i]) != float(toothDataStep2[i]):
      movementOccured += 1
  
  return True if movementOccured > 0 else False


def find_highest_totalmovement_files(directory):
    regex = re.compile(r'Step (\d+) - Protocol Movement Total (U|L)')
    highest_step = -1
    files_to_process = {'U': None, 'L': None}

    for filename in os.listdir(directory):
        match = regex.match(filename)
        if match:
            step, part = int(match.group(1)), match.group(2)
            if step > highest_step:
                highest_step = step
                files_to_process = {'U': None, 'L': None}
            if step == highest_step:
                files_to_process[part] = os.path.join(directory, filename)
    
    return files_to_process['U'], files_to_process['L']


def find_highest_movement_files(directory):
    regex = re.compile(r'Step (\d+) - Protocol Movement Step (U|L)')
    highest_step = -1
    files_to_process = {'U': None, 'L': None}

    for filename in os.listdir(directory):
        match = regex.match(filename)
        if match:
            step, part = int(match.group(1)), match.group(2)
            if step > highest_step:
                highest_step = step
                files_to_process = {'U': None, 'L': None}
            if step == highest_step:
                files_to_process[part] = os.path.join(directory, filename)
    
    return files_to_process['U'], files_to_process['L']


def extractMoveDataFromJsonInfoFile(jsonData, uncom_files_dir):
    print("Début de extractMoveDataFromJsonInfoFile")
    
    movData = {}
    totalSteps = jsonData.get('steps', 0)
    print(f"Total steps: {totalSteps}")
    
    try:
        listOfFiles = os.listdir(uncom_files_dir)
        print(f"Liste des fichiers dans {uncom_files_dir}: {listOfFiles}")
    except Exception as e:
        print(f"Erreur lors de la lecture du répertoire {uncom_files_dir}: {e}")
        return None  # Retourner None explicitement en cas d'erreur
    
    listOfJSON = [f for f in listOfFiles if f.endswith('.json')]
    print(f"Fichiers JSON détectés: {listOfJSON}")
    
    attachmentData = {}
    transformation_attachments = {}
    transformation_tooth = {}
    objects_data = {}
    
    for step in range(totalSteps):
        print(f"--- Traitement de l'étape {step} ---")
        pattern = re.compile(f'^Step {step} - Info\\.json$')
        fileNames = list(filter(lambda f: pattern.match(f), listOfJSON))
        # print(f"Fichiers correspondant pour l'étape {step}: {fileNames}")
        
        transformation_tooth[step] = {}
        transformation_attachments[step] = {}
        
        if not fileNames:
            print(f"Erreur à l'étape {step}: fichier JSON introuvable")
            continue
        
        for fileName in fileNames:
            pathMov = os.path.join(uncom_files_dir, fileName)
            # print(f"Traitement du fichier: {pathMov}")
            
            try:
                with open(pathMov, 'r') as jsonfile:
                    data = json.load(jsonfile)
                    # print(f"Données chargées depuis {fileName}: {data.keys()}")
                    
                    for obj in data.get("Objects", []):
                        # print(f"Traitement de l'objet: {obj.get('Name')}")
                        if "Tooth" in obj.get("Name", ""):
                            identifier = obj["Name"].replace(' ', '')
                            dict_to_fill = transformation_tooth
                            # print(f"Identificateur de la dent: {identifier}")
                        elif re.match(r'^\d+:', obj.get("Name", "")):
                            match = re.match(r'^(\d+):.*$', obj["Name"])
                            identifier = match.group(1) if match else "Unknown"
                            dict_to_fill = transformation_attachments
                            # print(f"Identificateur de l'attachement: {identifier}")
                        else:
                            identifier = obj["Name"].replace(' ', '').replace('/', '.')
                            dict_to_fill = transformation_attachments
                            # print(f"Autre identificateur: {identifier}")
                            # Optionnel: continue pour ignorer les objets non pertinents
                            # continue
                        
                        transform = obj.get("Transform", [])
                        if len(transform) < 12:
                            print(f"Transform incomplète pour l'objet {obj.get('Name')}: {transform}")
                            continue  # Ignorer cet objet
                        
                        position = np.array([transform[3], transform[7], transform[11]])  # éléments de position
                        rotation = np.array([
                            transform[0:3], 
                            transform[4:7], 
                            transform[8:11]
                        ])  # matrice de rotation 3x3
                        
                        transformation_matrix = np.eye(4)
                        transformation_matrix[0:3, 0:3] = rotation
                        transformation_matrix[0:3, 3] = position
                        transformation_matrix = transformation_matrix.tolist()
                        
                        # print(f"Matrice de transformation pour {identifier}: {transformation_matrix}")
                        
                        # Gestion des identifiants uniques
                        if identifier in dict_to_fill[step]:
                            i = 0
                            while f"{identifier}_{i}" in dict_to_fill[step]:
                                i += 1
                            identifier = f"{identifier}_{i}"
                            # print(f"Identificateur modifié pour unicité: {identifier}")
                        
                        dict_to_fill[step][identifier] = transformation_matrix
                        
                        # Gestion des données de mouvement
                        if "Tooth" in obj.get("Name", ""):
                            toothNum = int(re.search(r'\d+', obj["Name"]).group())
                            if toothNum not in movData:
                                movData[toothNum] = {}
                            movData[toothNum][step] = transform
                            # print(f"Dent {toothNum} mise à jour pour l'étape {step}")
                        elif re.match(r'^\d+:', obj.get("Name", "")):
                            toothNum = int(re.match(r'^(\d+):', obj["Name"]).group(1))
                            if toothNum not in attachmentData:
                                attachmentData[toothNum] = {}
                            if step not in attachmentData[toothNum]:
                                attachmentData[toothNum][step] = []
                            attachmentData[toothNum][step].append({"type": obj.get("Descr", "Unknown")})
                            # print(f"Attachement ajouté pour la dent {toothNum} à l'étape {step}")
                    
                    objects_data[step] = data.get("Objects", [])
                    print(f"Données des objets enregistrées pour l'étape {step}")
            
            except Exception as e:
                print(f"Échec du traitement de {pathMov}: {e}")
    
    # Traitement des attachements
    newAttchmentData = {}
    for tooth in attachmentData:
        newAttchmentData[tooth] = {}
        for step in attachmentData[tooth]:
            if step == 0:
                newAttchmentData[tooth][step] = {"new": attachmentData[tooth][step], "lost": []}
                # print(f"Dent {tooth}, étape {step}: initialisation des attachements nouveaux")
            else:
                newAttchmentData[tooth][step] = {"new": [], "lost": []}
                for attchment1 in attachmentData[tooth][step]:
                    if attchment1 not in attachmentData[tooth].get(step - 1, []):
                        newAttchmentData[tooth][step]["new"].append(attchment1)
                        # print(f"Attachement nouveau détecté pour la dent {tooth} à l'étape {step}: {attchment1}")
                for attchment1 in attachmentData[tooth].get(step - 1, []):
                    if attchment1 not in attachmentData[tooth][step]:
                        newAttchmentData[tooth][step]["lost"].append(attchment1)
                        # print(f"Attachement perdu détecté pour la dent {tooth} à l'étape {step}: {attchment1}")
    
    # Calcul des mouvements
    movDataSteps = {}
    for toothNum in movData:
        movDataSteps[toothNum] = {}
        for i in range(totalSteps - 1):
            toothDataStep1 = movData[toothNum].get(i)
            toothDataStep2 = movData[toothNum].get(i + 1)
            if toothDataStep1 is None or toothDataStep2 is None:
                # print(f"Données de mouvement manquantes pour la dent {toothNum} entre les étapes {i} et {i + 1}")
                continue
            movDataSteps[toothNum][i] = didToothMove(toothDataStep1, toothDataStep2)
            # print(f"Mouvement calculé pour la dent {toothNum} entre les étapes {i} et {i + 1}: {movDataSteps[toothNum][i]}")
    
    # Export des données de mouvement
    movDataExport = {}
    for toothNum in movDataSteps:
        movList = movDataSteps[toothNum]
        movDataExport[toothNum] = []
        prev = -1
        perI = 0
        for j in range(totalSteps - 1):
            if movList.get(j) != prev:
                if j != 0 and movDataExport[toothNum]:
                    movDataExport[toothNum][-1]['percent'] = perI / (totalSteps - 1) * 100
                    # print(f"Pourcentage mis à jour pour la dent {toothNum}, segment précédent: {movDataExport[toothNum][-1]}")
                prev = movList.get(j)
                perI = 1
                movDataExport[toothNum].append({'active': movList.get(j), 'percent': 1 / (totalSteps - 1) * 100})
                # print(f"Nouvelle entrée ajoutée pour la dent {toothNum}: {movDataExport[toothNum][-1]}")
            else:
                perI += 1
                if j + 2 == totalSteps:
                    movDataExport[toothNum][-1]['percent'] = perI / (totalSteps - 1) * 100
                    # print(f"Pourcentage final mis à jour pour la dent {toothNum}, segment actuel: {movDataExport[toothNum][-1]}")
    
    # Mise à jour de jsonData
    jsonData["transformationTooth"] = transformation_tooth
    jsonData["transformationAttachment"] = transformation_attachments
    jsonData['movData'] = movDataExport
    jsonData['attachmentData'] = newAttchmentData
    jsonData['objectsData'] = objects_data
    
    print("Fin de extractMoveDataFromJsonInfoFile, retour de jsonData")
    return jsonData



def generateMovDataForSeparatedFiles(jsonData, uncom_files_dir):
    movData = {}
    totalSteps = jsonData['steps']

    listOfFiles = os.listdir(uncom_files_dir)
    listOfCSV = [f for f in listOfFiles if f.endswith('.csv')]
    
    attachmentData = {}

    pattern_attachment = re.compile(r'^\d+:.*$')  # Matches "XX:" at the start of the string
    pattern_tooth = re.compile(r'^Tooth \d{2}( \(Copy\))?$')  # Matches "Tooth XX" or "Tooth XX (Copy)"
    transformation_attachments = {}
    transformation_tooth = {}

    for step in range(0, totalSteps):  # Commencez à 1 si vos étapes commencent à 1
        pattern = re.compile(f'^Step {step} - Info\\.csv$')
        fileNames = list(filter(lambda f: pattern.match(f), listOfCSV))

        transformation_tooth[step] = {}
        transformation_attachments[step] = {}

        if not fileNames:
            print(f"Error on Step {step} to load CSV file")
            continue

        for fileName in fileNames:
            pathMov = os.path.join(uncom_files_dir, fileName)
            print(f"Processing {pathMov}")

            try:
                with codecs.open(pathMov, 'r', 'utf-16') as csvfile:
                    moveReader = csv.DictReader(csvfile, delimiter='\t')
                    for row in moveReader:
                        toothIdMatch = re.search(r'Tooth (\d+)', row['name'])
                        attachmentMatch = re.search(r'(\d+):', row['name'])

                        if pattern_attachment.match(row['name']):
                            # Extract the attachment number and position and rotation matrix
                            identifier = re.match(r'^(\d+):.*$', row['name']).group(1)
                            dict_to_fill = transformation_attachments

                        elif pattern_tooth.match(row['name']):
                            # Extract the tooth number and position and rotation matrix
                            identifier = row['name'].replace(' ', '')
                            dict_to_fill = transformation_tooth

                        else:
                            identifier = row["name"].replace(' ', '').replace('/', '.')
                            dict_to_fill = transformation_attachments
                            # continue

                        position = np.array([row['oX'], row['oY'], row['oZ']])
                        rotation = np.array([[row['xX'], row['yX'], row['zX']],
                                            [row['xY'], row['yY'], row['zY']],
                                            [row['xZ'], row['yZ'], row['zZ']]])

                        # Create a 4x4 transformation matrix
                        transformation_matrix = np.eye(4)
                        transformation_matrix[0:3, 0:3] = rotation
                        transformation_matrix[0:3, 3] = position

                        # Convert the transformation matrix to a nested list
                        transformation_matrix = transformation_matrix.tolist()

                        # Check if identifier already exists, if so, append an index
                        if identifier in dict_to_fill[step]:
                            i = 0
                            while f"{identifier}_{i}" in dict_to_fill[step]:
                                i += 1
                            identifier = f"{identifier}_{i}"

                        dict_to_fill[step][identifier] = transformation_matrix

                        if toothIdMatch:
                            toothNum = int(toothIdMatch.group(1))
                            if toothNum not in movData:
                                movData[toothNum] = {}
                            movData[toothNum][step] = [float(row['oX']), float(row['oY']), float(row['oZ']), float(row['xX']), float(row['xY']), float(row['xZ']), float(row['yX']), float(row['yY']), float(row['yZ']), float(row['zX']), float(row['zY']), float(row['zZ'])]
                        elif attachmentMatch:
                            toothNum = int(attachmentMatch.group(1))
                            if toothNum not in attachmentData:
                                attachmentData[toothNum] = {}
                            if step not in attachmentData[toothNum]:
                                attachmentData[toothNum][step] = []
                            attachmentData[toothNum][step].append({"type": row['type']})

            except Exception as e:
                print(f"Failed to process {pathMov}: {e}")

    newAttchmentData = {}

    for tooth in attachmentData:
      newAttchmentData[tooth] = {}
      for step in attachmentData[tooth]:
          if(step == 0):
            newAttchmentData[tooth][step] = {"new": attachmentData[tooth][step], "lost": []}

          # elif(attchmentData[tooth][step] == attchmentData[tooth][step-1]):
          #    print("no difference for step ", step, " | tooth : ", tooth)
          else:
            newAttchmentData[tooth][step] = {"new": [], "lost": []}

            # Looking for new attachment
            for attchment1 in attachmentData[tooth][step]:
              isNew = True
              for attchment2 in attachmentData[tooth][step-1]:
                if(attchment1 == attchment2):
                  isNew = False
              if(isNew):
                newAttchmentData[tooth][step]["new"].append(attchment1)
            
            # Looking for lost attachment
            for attchment1 in attachmentData[tooth][step-1]:
              isLost = True
              for attchment2 in attachmentData[tooth][step]:
                if(attchment1 == attchment2):
                  isLost = False
              if(isLost):
                newAttchmentData[tooth][step]["lost"].append(attchment1)

    movDataSteps = {}

    # print("movData : ", movData)

    for toothNum in movData:
      movDataSteps[toothNum] = {}
      for i in range(totalSteps - 1):
        toothDataStep1 = movData[toothNum][i]
        toothDataStep2 = movData[toothNum][i + 1]
        
        movDataSteps[toothNum][i] = didToothMove(toothDataStep1, toothDataStep2)


    movDataExport = {}
    for toothNum in movDataSteps:
      movList = movDataSteps[toothNum]
      movDataExport[toothNum] = []
      prev = -1
      perI = 0
      for j in range(totalSteps-1):
        if movList[j] != prev:
          if j != 0:
            movDataExport[toothNum][-1]['percent'] = perI/(totalSteps-1)*100
          prev = movList[j]
          perI = 1
          movDataExport[toothNum].append({'active': movList[j], 'percent': 1/(totalSteps-1)*100})

        else:
          perI += 1
          if j+2  == totalSteps:
            movDataExport[toothNum][-1]['percent'] = perI/(totalSteps-1)*100

    jsonData["transformationTooth"] = transformation_tooth
    jsonData["transformationAttachment"] = transformation_attachments
    jsonData['movData'] = movDataExport
    jsonData['attachmentData'] = newAttchmentData
    return jsonData


def generateMovData(jsonData, uncom_files_dir):
  movData = {}
  totalSteps = jsonData['steps']

  listOfFiles = os.listdir(uncom_files_dir)
  listOfCSV = []

  attchmentData = {}

  for nameFile in listOfFiles:
    if (nameFile[len(nameFile)-4:] == '.csv'):
      listOfCSV.append(nameFile)
  
  for i in range(totalSteps):
    fileNameStep = 'Step'+str(i)+'_'
    fileNames = []
    for csvFile in listOfCSV:
      if(csvFile[:len(fileNameStep)] == fileNameStep):
        fileNames.append(csvFile)

    if(fileNames == []): print("Error on Step ", i, " to load CSV file")
    # fileName = 'Step'+str(i)+'_OnyxCeph3_Export_.obj Info.csv'

    for fileName in fileNames:
      pathMov = os.path.join(uncom_files_dir, fileName)

      print(f"Processing {pathMov}")

      moveReader = csv.reader(codecs.open(pathMov,'rU'))
      for rows in moveReader:
        splittedRow = rows[0].split('\t')

        if 'Tooth' in splittedRow[0]:
          toothNumMatches = re.findall(r'\d+', splittedRow[0])
          if toothNumMatches:
              toothNum = int(toothNumMatches[0])
              if toothNum not in movData.keys():
                  movData[toothNum] = {} #
              movData[toothNum][i] = splittedRow[2:]
        else :
           if(splittedRow[0][:2].isnumeric() ):
              dataTAQ = splittedRow[0].split(': ')
              typeTAQ = dataTAQ[1]
              toothNum = int(dataTAQ[0])

              if toothNum not in attchmentData.keys():
                attchmentData[toothNum] = {} #
              if i not in attchmentData[toothNum].keys():
                attchmentData[toothNum][i] = [] #
              
              attchmentData[toothNum][i].append({"type" : dataTAQ[1]})
  newAttchmentData = {}

  for tooth in attchmentData:
     newAttchmentData[tooth] = {}
     for step in attchmentData[tooth]:
        if(step == 0):
          newAttchmentData[tooth][step] = {"new": attchmentData[tooth][step], "lost": []}

        # elif(attchmentData[tooth][step] == attchmentData[tooth][step-1]):
        #    print("no difference for step ", step, " | tooth : ", tooth)
        else:
          newAttchmentData[tooth][step] = {"new": [], "lost": []}

          # Looking for new attachment
          for attchment1 in attchmentData[tooth][step]:
            isNew = True
            for attchment2 in attchmentData[tooth][step-1]:
              if(attchment1 == attchment2):
                isNew = False
            if(isNew):
               newAttchmentData[tooth][step]["new"].append(attchment1)
          
          # Looking for lost attachment
          for attchment1 in attchmentData[tooth][step-1]:
            isLost = True
            for attchment2 in attchmentData[tooth][step]:
              if(attchment1 == attchment2):
                isLost = False
            if(isLost):
               newAttchmentData[tooth][step]["lost"].append(attchment1)

  movDataSteps = {}

  for toothNum in movData:
    movDataSteps[toothNum] = {}
    for i in range(totalSteps - 1):
      toothDataStep1 = movData[toothNum][i]
      toothDataStep2 = movData[toothNum][i + 1]
      movDataSteps[toothNum][i] = didToothMove(toothDataStep1, toothDataStep2)


  movDataExport = {}
  for toothNum in movDataSteps:
    movList = movDataSteps[toothNum]
    movDataExport[toothNum] = []
    prev = -1
    perI = 0
    for j in range(totalSteps-1):
      if movList[j] != prev:
        if j != 0:
          movDataExport[toothNum][-1]['percent'] = perI/(totalSteps-1)*100
        prev = movList[j]
        perI = 1
        movDataExport[toothNum].append({'active': movList[j], 'percent': 1/(totalSteps-1)*100})

      else:
        perI += 1
        if j+2  == totalSteps:
          movDataExport[toothNum][-1]['percent'] = perI/(totalSteps-1)*100

  jsonData['movData'] = movDataExport
  jsonData['attachmentData'] = newAttchmentData
  return jsonData


def generateLandmarkData(input_data_path, landmark_filename, jsonData):

  landmark_filepath = os.path.join(input_data_path, landmark_filename)

  if(os.path.exists(landmark_filepath)):

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
  
    new_landmarks = landmarks.copy()
    for tooth in landmarks:
      if(landmarks[tooth] == {}): 
        new_landmarks.pop(tooth)
    
    landmarks = new_landmarks

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

    
    jsonData['landmarks'] = landmarks
    return jsonData
  
  
def generateTotalMoveDataFromSeparatedFiles(uncom_files_dir, jsonData):
    print("Start total movement table calcul from separated files ...")
    pathMovementU, pathMovementL = find_highest_totalmovement_files(uncom_files_dir)

    if pathMovementU and pathMovementL:
        print("Files found:", pathMovementU, pathMovementL)
    else:
        print("Warning: Movement total files not found!")
        return jsonData

    movementTable = {}

    def process_movement_file(path, movementTable, positionString):
        if(os.path.exists(path)):
          movementReader = csv.reader(codecs.open(path,'rU','utf-16'))
        else:
          print(("The movement Table ", path, " cannot be found. Skipping generateTotalMoveData"))
          logger.error(f"The movement Table {path}, cannot be found. Skipping generateTotalMoveData")
          return {}

        rows = []
        for row in movementReader:
          splittedRow = row[0].split('\t')
          for i in range(len(splittedRow)):
            splittedRow[i] = splittedRow[i].replace('"','') 
            
          rows.append(splittedRow)

        ind_row = 1
        #Loop to explore the rows
        for row in rows :
          # If we find a row of tooth, we add the properties of each tooth
          if(row[0] == 'Tooth'):
            # For each tooth
            ind_tooth = 1
            for tooth in row[1:]:
              #If it's tooth number we add it
              if(len(tooth) == 2):
                movementTable[tooth] = []
                # For each property
                for toothProperty in rows[ind_row:] :
                  #If the property doesn't have the Tooth value
                  if(toothProperty[0] != "Tooth" and toothProperty[0] != 'Mandible' and toothProperty[0] != 'Maxilla'):
                    splittedProperty = toothProperty[0].split(' ')
                    type = ""
                    for item in splittedProperty[:-1]:
                      # if(item != '+/-'):
                      if(type == "") :
                        type += item
                      else:
                        type += " " + item
                      
                    unity = splittedProperty[-1][1:-1]
                    value = toothProperty[ind_tooth]
                    if(value == ''): value = 0
                    else: value = float(value)

                    movementTable[tooth].append({"type": type, "unity": unity, "value": value})
                  # Else we break the loop, because we found a new tooth row
                  else:
                    break
              ind_tooth += 1
          ind_row += 1

    process_movement_file(pathMovementU, movementTable, 'U')
    process_movement_file(pathMovementL, movementTable, 'L')

    jsonData['movementTable'] = movementTable
    return jsonData


def generateLandmarkDataFromCSV(landmark_filename, jsonData):
    
    if os.path.exists(landmark_filename):
        
        print("Start analysing landmark : ", landmark_filename)
        df = pd.read_csv(landmark_filename, delimiter='\t', encoding='utf-16')
        
        landmarks = {}
        
        # Mapping des suffixes aux points correspondants
        suffix_to_point = {
            "d": "Distal point",
            "m": "Mesial Point",
            "vMG": "Vestibular Gingival",
            "C": "Cusp",
            "b": "Buccal Cusp",
            "I": "Incisal Edge",
            "mb": "Mesial Buccal Cusp",
            "db": "Distal Buccal Cusp",
            "mP": "Mesial Point",
            "apRot": "Apical Rotation"
        }

        pattern = re.compile(r"(?P<suffix>[a-zA-Z]+)(?P<toothId>\d+)|(?P<toothId2>\d+)(?P<suffix2>[a-zA-Z]+)")
        
        for _, row in df.iterrows():
            match = pattern.search(row['Landmarks'])
            if match:
                groups = match.groupdict()
                suffix = groups['suffix'] if groups['suffix'] else groups['suffix2']
                toothId = groups['toothId'] if groups['toothId'] else groups['toothId2']
                pointType = suffix_to_point.get(suffix, None)
                
                if pointType:
                    if toothId not in landmarks:
                        landmarks[toothId] = {}
                    
                    coordinates = [float(row['X-Pos']), float(row['Y-Pos']), float(row['Z-Pos'])]
                    landmarks[toothId][pointType] = coordinates

        # Effectue les calculs nécessaires pour chaque dent
        for tooth in landmarks:

          points = landmarks[tooth]

          if "Mesial Point" in points and "Distal point" in points:
              mdAxis = np.array(points["Mesial Point"]) - np.array(points["Distal point"])
              mdAxis_norm = mdAxis / np.linalg.norm(mdAxis)
              landmarks[tooth]['mdAxis'] = mdAxis_norm.tolist()
              
              mdCenter = (np.array(points["Mesial Point"]) + np.array(points["Distal point"])) / 2
              landmarks[tooth]['mdCenter'] = mdCenter.tolist()
              
          if "Apical Rotation" in points:
              
              toothAxis = np.array(points["Apical Rotation"]) - mdCenter
              toothAxis_norm = toothAxis / np.linalg.norm(toothAxis)
              landmarks[tooth]['toothAxis'] = toothAxis_norm.tolist()
              
              
              verticalToothAxis = np.array([0, 1, 0]) if int(tooth) > 30 else np.array([0, -1, 0])
              landmarks[tooth]['verticalToothAxis'] = verticalToothAxis.tolist()
              
              vestibularAxis = np.cross(verticalToothAxis, mdAxis_norm) if int(tooth) > 20 and int(tooth) < 30 or int(tooth) > 40 else np.cross(mdAxis_norm, verticalToothAxis)
              vestibularAxis_norm = vestibularAxis / np.linalg.norm(vestibularAxis)
              landmarks[tooth]['vestibularAxis'] = vestibularAxis_norm.tolist()
              
              if "Vestibular Gingival" in points:
                  attachPoint = [points["Vestibular Gingival"][0], mdCenter[1], points["Vestibular Gingival"][2]]
                  landmarks[tooth]['attachPoint'] = attachPoint
              
              mdToothPerpendicular = np.cross(toothAxis_norm, mdAxis_norm) if int(tooth) > 20 and int(tooth) < 30 or int(tooth) > 40 else np.cross(mdAxis_norm, toothAxis_norm)
              mdToothPerpendicular_norm = mdToothPerpendicular / np.linalg.norm(mdToothPerpendicular)
              landmarks[tooth]['mdToothPerpendicular'] = mdToothPerpendicular_norm.tolist()
          
        jsonData['landmarks'] = landmarks
        return jsonData
    else:
        print("Le fichier spécifié n'existe pas")
        return jsonData

                   

def generateArcanumMoveData(jsonData, totalSteps):
  movData = jsonData["movData"]
  jsonData["movDataByArcanum"] = {}

  for step in range(totalSteps):
    percent = step / totalSteps
    jsonData["movDataByArcanum"][step] = {"Lower": False, "Upper": False}

    
    for tooth in movData:

      activityInd = 0
      for activity in movData[tooth]:
        result = False
        if(activityInd == 0):
          if(percent <= activity["percent"]):
            if(activity["active"]): result = True
        else:
          sum = 0
          for x in movData[tooth][:activityInd]:
              sum += x["active"]
          if(percent <= sum + activity["percent"] and percent >= sum):
            if(activity["active"]): result = True

        activityInd += 1

      # Lower analyse by step
      if(str(tooth)[0] == '3' or str(tooth)[0] == '4'):
        if(result): jsonData["movDataByArcanum"][step]["Lower"] = result
      if(str(tooth)[0] == '1' or str(tooth)[0] == '2'):
        if(result): jsonData["movDataByArcanum"][step]["Upper"] = result
  
  return jsonData


def calculate_aligners(movData, total_steps):
    upper_aligners = set()
    lower_aligners = set()

    for tooth, movement_list in movData.items():
        current_step = 0
        for movement in movement_list:
            if movement["active"]:
                steps_active = int(movement["percent"] / 100 * total_steps)
                for step in range(current_step, current_step + steps_active):
                    if tooth.startswith(('1', '2')):
                        upper_aligners.add(step)
                    else:
                        lower_aligners.add(step)
            current_step += steps_active

    return len(upper_aligners), len(lower_aligners)


def calculate_aligners_by_arcanum(movDataByArcanum):
    upper_aligners = 0
    lower_aligners = 0

    for step, movement in movDataByArcanum.items():
        if movement["Upper"]:
            upper_aligners += 1
        if movement["Lower"]:
            lower_aligners += 1

    return upper_aligners, lower_aligners


def generateAFcheck(jsonData):
  jsonAfCheck = {}
  jsonAfCheck["aligners"] = []
  jsonAfCheck["attachments"] = []
  paris_tz = timezone(timedelta(hours=2))

  # upper_aligners = 0
  # lower_aligners = 0

  alignersInd = 0


  for stage in jsonData["stages"]:
    try:
      maxIprIndUpper = len(stage["upperIPR"])
      maxIprIndLower = len(stage["lowerIPR"])

      

      if(maxIprIndUpper == 0 and maxIprIndLower == 0): continue

      jsonAfCheck["aligners"].append({})
      # jsonAfCheck["aligners"][alignersInd] = {}

      jsonAfCheck["aligners"][alignersInd]["upper_aligners"], jsonAfCheck["aligners"][alignersInd]["lower_aligners"] = calculate_aligners_by_arcanum(jsonData["movDataByArcanum"])

      # idAligner = round(random() * 1000)
      jsonAfCheck["aligners"][alignersInd]["sub_index"] = alignersInd
      # jsonAfCheck["aligners"][alignersInd]["id"] = idAligner
      # jsonAfCheck["aligners"][alignersInd]["upper_aligners"] = 0
      # jsonAfCheck["aligners"][alignersInd]["lower_aligners"] = 0
      jsonAfCheck["aligners"][alignersInd]["aligner_iprs"] = []

      


      iprInd = 0
      afCheckAlignerInd = 0
      maxIprInd = len(stage["upperIPR"])

      while(iprInd < maxIprInd):


        jsonAfCheck["aligners"][alignersInd]["aligner_iprs"].append({})

        jsonAfCheck["aligners"][alignersInd]["aligner_iprs"][afCheckAlignerInd]["sub_aligner_index"] = stage["step"] 
        # jsonAfCheck["aligners"][alignersInd]["aligner_iprs"][afCheckAlignerInd]["aligner_id"] = idAligner
        # jsonAfCheck["aligners"][alignersInd]["aligner_iprs"][afCheckAlignerInd]["id"] = round(random() * 10000)
        jsonAfCheck["aligners"][alignersInd]["aligner_iprs"][afCheckAlignerInd]["type"] = "HIGHER"

        if((stage["upperIPR"][iprInd][-1][-1] == 'm' and stage["upperIPR"][iprInd][-1][0] == '2') or (stage["upperIPR"][iprInd][-1][-1] == 'd' and stage["upperIPR"][iprInd][-1][0] == '1')):
          jsonAfCheck["aligners"][alignersInd]["aligner_iprs"][afCheckAlignerInd]["first_number"] = stage["upperIPR"][iprInd+1][-1][0:-1]
          jsonAfCheck["aligners"][alignersInd]["aligner_iprs"][afCheckAlignerInd]["second_number"] = stage["upperIPR"][iprInd][-1][0:-1]
        else:
          jsonAfCheck["aligners"][alignersInd]["aligner_iprs"][afCheckAlignerInd]["first_number"] = stage["upperIPR"][iprInd][-1][0:-1]
          jsonAfCheck["aligners"][alignersInd]["aligner_iprs"][afCheckAlignerInd]["second_number"] = stage["upperIPR"][iprInd+1][-1][0:-1]
          

        if iprInd + 1 < len(stage["upperIPR"]):
            jsonAfCheck["aligners"][alignersInd]["aligner_iprs"][afCheckAlignerInd]["distance"] = stage["upperIPR"][iprInd][0] + stage["upperIPR"][iprInd + 1][0]
        else:
            jsonAfCheck["aligners"][alignersInd]["aligner_iprs"][afCheckAlignerInd]["distance"] = stage["upperIPR"][iprInd][0] * 2

        # jsonAfCheck["aligners"][alignersInd]["aligner_iprs"][afCheckAlignerInd]["distance"] = stage["upperIPR"][iprInd][0] +stage["upperIPR"][iprInd+1][0]
        now = datetime.now(paris_tz)
        jsonAfCheck["aligners"][alignersInd]["aligner_iprs"][afCheckAlignerInd]["updated_at"] = now.isoformat()
        jsonAfCheck["aligners"][alignersInd]["aligner_iprs"][afCheckAlignerInd]["created_at"] = now.isoformat()

        # jsonAfCheck["aligners"][alignersInd]["upper_aligners"] += 1
        afCheckAlignerInd += 1
        iprInd += 2
      
      iprInd = 0
      maxIprInd = len(stage["lowerIPR"])

      while(iprInd < maxIprInd):


        jsonAfCheck["aligners"][alignersInd]["aligner_iprs"].append({})

        jsonAfCheck["aligners"][alignersInd]["aligner_iprs"][afCheckAlignerInd]["sub_aligner_index"] = stage["step"] 
        # jsonAfCheck["aligners"][alignersInd]["aligner_iprs"][afCheckAlignerInd]["aligner_id"] = idAligner
        # jsonAfCheck["aligners"][alignersInd]["aligner_iprs"][afCheckAlignerInd]["id"] = round(random() * 10000)
        jsonAfCheck["aligners"][alignersInd]["aligner_iprs"][afCheckAlignerInd]["type"] = "LOWER"

        if((stage["lowerIPR"][iprInd][-1][-1] == 'm' and stage["lowerIPR"][iprInd][-1][0] == '3') or (stage["lowerIPR"][iprInd][-1][-1] == 'd' and stage["lowerIPR"][iprInd][-1][0] == '4')):
          jsonAfCheck["aligners"][alignersInd]["aligner_iprs"][afCheckAlignerInd]["second_number"] = stage["lowerIPR"][iprInd][-1][0:-1]
          jsonAfCheck["aligners"][alignersInd]["aligner_iprs"][afCheckAlignerInd]["first_number"] = stage["lowerIPR"][iprInd+1][-1][0:-1]
        else:
          jsonAfCheck["aligners"][alignersInd]["aligner_iprs"][afCheckAlignerInd]["second_number"] = stage["lowerIPR"][iprInd+1][-1][0:-1]
          jsonAfCheck["aligners"][alignersInd]["aligner_iprs"][afCheckAlignerInd]["first_number"] = stage["lowerIPR"][iprInd][-1][0:-1]

          
        if iprInd + 1 < len(stage["lowerIPR"]):
          jsonAfCheck["aligners"][alignersInd]["aligner_iprs"][afCheckAlignerInd]["distance"] = stage["lowerIPR"][iprInd][0] + stage["lowerIPR"][iprInd+1][0]
        else:
          jsonAfCheck["aligners"][alignersInd]["aligner_iprs"][afCheckAlignerInd]["distance"] = stage["lowerIPR"][iprInd][0] * 2

        # jsonAfCheck["aligners"][alignersInd]["aligner_iprs"][afCheckAlignerInd]["distance"] = stage["lowerIPR"][iprInd][0] * 2
           
        now = datetime.now(paris_tz)
        jsonAfCheck["aligners"][alignersInd]["aligner_iprs"][afCheckAlignerInd]["updated_at"] = now.isoformat()
        jsonAfCheck["aligners"][alignersInd]["aligner_iprs"][afCheckAlignerInd]["created_at"] = now.isoformat()

        # jsonAfCheck["aligners"][alignersInd]["lower_aligners"] += 1
        afCheckAlignerInd += 1
        iprInd += 2

      alignersInd += 1   
    except:
      pass



  # Attachment part
  attachIndex = 0
  jsonAfCheck["attachments"].append({})
  jsonAfCheck["attachments"][attachIndex]["attachments"] = ""
  jsonAfCheck["attachments"][attachIndex]["id"] = round(random() * 1000)
  for attachmentString in jsonData["attach"]:
    if(len(attachmentString.split('_')) < 2):
        jsonAfCheck["attachments"][attachIndex]["attachments"] += attachmentString.split('.')[0] + ','
  now = datetime.now(paris_tz)
  jsonAfCheck["attachments"][attachIndex]["attachments"] = jsonAfCheck["attachments"][attachIndex]["attachments"][0:-1]
  jsonAfCheck["attachments"][attachIndex]["updated_at"] = now.isoformat()
  jsonAfCheck["attachments"][attachIndex]["created_at"] = now.isoformat()
  return jsonAfCheck
        
import os
import re
import traceback
import concurrent.futures

def parallel_process_files(
    uncompressed_files, 
    uncom_files_dir, 
    splitted_files_dir, 
    optimized_files_dir,
    file_pattern,         # ex: re.compile(...)
    generate_obj, 
    callback_status_func, # ou None
    a_3d_o,               # pour callback
    main,                 # votre fonction de splitting
    isNewStructure=False, 
    step_i=0, 
    spt_out_prev=None,
    save_file_in=None,
    debug=False
):
    """
    Version parallélisée du traitement des fichiers .obj.
    Retourne la liste 'list_of_obj' à la fin.
    """
    if save_file_in is None:
        save_file_in = []

    # On stockera ici tous les 'obj' qu'on veut retourner
    list_of_obj = []

    # Petit wrapper pour conserver l'état local (step_i, spt_out_prev), etc.
    # et surtout faire le traitement d'un seul fichier.
    def process_single_file(files):
        nonlocal isNewStructure, step_i, spt_out_prev

        results_local = {
            'list_of_obj': [],
            'step_i': step_i,
            'spt_out_prev': spt_out_prev,
            'save_file_in': []
        }

        try:
            # ----- LOGIQUE DE TRAITEMENT -----
            if not files.endswith('.obj'):
                # On ignore les non .obj
                return results_local

            # Test du pattern
            match = file_pattern.match(files)
            if match:
                # Cas "nouvelle structure" => step_number, jaw_side
                step_number, jaw_side = match.groups()

                if isNewStructure and debug:
                    print("Using new structure generation")

                isNewStructure = True

                if debug:
                    print(f"Traitement de : Step {step_number} - Obj3D {jaw_side}")

                file_in = os.path.join(uncom_files_dir, files)
                
                # Création du dossier pour les fichiers séparés
                spt_out = os.path.join(splitted_files_dir, step_number)
                # if not os.path.exists(spt_out):
                #     os.makedirs(spt_out)
                os.makedirs(spt_out, exist_ok=True)
                
                # Sauvegarde du step 0 ?
                if step_number == "0":
                    results_local['save_file_in'].append(file_in)
                    save_spt_out = spt_out  # On l'assigne localement

                if debug:
                    print(f"[Parallèle] Splitting + optimisation pour step={step_number}, jaw={jaw_side}")
                
                # Création du dossier pour les fichiers optimisés
                opt_out = os.path.join(optimized_files_dir, step_number)
                # if not os.path.exists(opt_out):
                #     os.makedirs(opt_out)
                os.makedirs(opt_out, exist_ok=True)

                # Appel de la fonction de splitting
                splitted_files = main(file_in, spt_out)

                # (Si vous souhaitez optimiser, décommentez et adaptez)
                # for splitted_file in splitted_files:
                #     if splitted_file.endswith('.obj'):
                #         file_in_dir = os.path.join(spt_out, splitted_file)
                #         file_out_name = os.path.join(opt_out, splitted_file)
                #         # optimizing_file(file_in_dir, file_out_name, divide_by=1)

                if spt_out_prev != spt_out:
                    results_local['step_i'] += 1
                results_local['spt_out_prev'] = spt_out

            else:
                # Cas "ancienne structure"
                isNewStructure = False
                if debug:
                    print("Traitement de (ancien format) : ", files)

                file_in = os.path.join(uncom_files_dir, files)
                spt_out_name = files.split("_")
                
                spt_out = os.path.join(
                    splitted_files_dir, 
                    spt_out_name[0][4:]  # ex: "0", "1", "2", etc.
                )
                if not os.path.exists(spt_out):
                    os.makedirs(spt_out)

                if debug:
                    print("[Parallèle] Splitting + optimisation (old structure) step=", spt_out.split('\\')[-1])
                
                opt_out = os.path.join(optimized_files_dir, spt_out_name[0][4:])
                if not os.path.exists(opt_out):
                    os.makedirs(opt_out)

                splitted_files = main(file_in, spt_out)

                if spt_out_name[0][4:] == "0":
                    results_local['save_file_in'].append(file_in)

                # Exemple d'optimisation
                # for splitted_file in splitted_files:
                #     if splitted_file.endswith('.obj'):
                #         file_in_dir = os.path.join(spt_out, splitted_file)
                #         file_out_name = os.path.join(opt_out, splitted_file)
                #         # optimizing_file(file_in_dir, file_out_name, divide_by=1)

                if spt_out_prev != spt_out:
                    results_local['step_i'] += 1
                results_local['spt_out_prev'] = spt_out

            return results_local

        except Exception as ex:
            # En cas d'erreur, on peut tenter un callback
            if callback_status_func:
                try:
                    fail_step = (spt_out or "NA").split('\\')[-1]
                    callback_status_func(a_3d_o, "FAILED_" + fail_step)
                except:
                    pass
            if debug:
                print(f"[ERREUR] Fichier={files} => {ex}")
                traceback.print_exc()

            return results_local

    # --- Si generate_obj = False, on saute toute la logique ---
    if not generate_obj:
        if debug:
            print("[Parallèle] generate_obj = False, aucun splitting effectué.")
        # On retourne quand même le "list_of_obj" final
        return list_of_obj

    if debug:
        print("Splitting with optimization in progress ... (PARALLÈLE)")

    # --- Exécution en pool de threads
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_map = {}
        for f in uncompressed_files:
            fut = executor.submit(process_single_file, f)
            future_map[fut] = f

        for fut in concurrent.futures.as_completed(future_map):
            res_loc = fut.result()  # dict local
            # Mise à jour de step_i, spt_out_prev
            step_i = res_loc['step_i']
            spt_out_prev = res_loc['spt_out_prev']
            # On agrège les fichiers "save_file_in"
            if res_loc['save_file_in']:
                save_file_in.extend(res_loc['save_file_in'])

    # --- À la fin, on traite la partie "list_of_obj" depuis 'save_file_in'
    #     (selon votre code, vous rappiez main(list, save_spt_out, writing=False))
    for input_file in save_file_in:
        # On récupère spt_out depuis la dernière fois où step_number == 0
        # (Dans le code ci-dessus, on l'avait stocké localement dans step_number == "0"
        #  mais on peut le déduire si vous préférez le transmettre d'une autre manière.)
        # Pour la démo, prenons l'hypothèse qu'on a un unique "save_spt_out"
        # ou qu'on le retrouve :
        spt_out_used = spt_out_prev  # ou un spt_out stocké lors du step=0
        if spt_out_used:
            objs_found = main(input_file, spt_out_used, writing=False)
            for obj in objs_found:
                list_of_obj.append(obj)

    return list_of_obj, isNewStructure


def generateOptimizedData(
  uncom_files_dir,
  splitted_files_dir,
  optimized_files_dir,
  export_dir, 
  ipr_data_filename,
  landmark_data_filename,
  output_json_filename, 
  bolton_analysis_file,
  landmarkxls_data_filename,
  pathMovementTable,
  output_history_filename, 
  patient_name,
  af_setup_name,
  a_3d_o=None,
  callback_status_func=None
):
  """
  Main function of the script

  Used to generate all of object by splitting it out
  Optimized it
  And convert all of data in a centralized JSON 
  """
  # print("main obj_opt")

  # Used for debugging | True by default
  generate_obj = True
  
  # Début de la mesure
  start_time = time.time()

  #remove for cloud upload-------------------------------
  if(generate_obj):
    shutil.rmtree(splitted_files_dir) 
    if(os.path.exists(splitted_files_dir) == False): os.mkdir(splitted_files_dir)
    
    shutil.rmtree(optimized_files_dir) 
    if(os.path.exists(optimized_files_dir) == False): os.mkdir(optimized_files_dir)
  #------------------------------------------------------
  #------------------------------------------------------
  
  uncompressed_files = []

  step_i = 0
  output_json = {}
  
  for (dirpath, dirnames, filenames) in os.walk(uncom_files_dir):
    uncompressed_files.extend(filenames)

  if(generate_obj == False):
     print("generate_obj variable is False : Splitting and optimization of files dodged")

  # Prevent outstanding step incrementation if models are in different files
  spt_out_prev = "" 
  spt_out_to_use_for_json = "splitted_data\\0" 
  # save_file_in = ["input_data\Step0_1677_OnyxCeph3_Export_ Step 0 of 19 Lower.obj", "input_data\Step0_1677_OnyxCeph3_Export_ Step 0 of 19 Upper.obj"]
  # save_file_in = ["input_data\Step0_2674_OnyxCeph3_Export_ Step 0 of 31 Lower.obj", "input_data\Step0_2674_OnyxCeph3_Export_ Step 0 of 31 Upper.obj"]
  save_file_in = []
  save_spt_out = "splitted_data\\0"

  # Cette expression régulière va extraire le numéro de step ainsi que la mâchoire (U ou L)
  file_pattern = re.compile(r'Step (\d+) - Obj3D (U|L)\.obj')

  isNewStructure = False


  #Condition to generate the objects
  # if(generate_obj) :
  #   print("Splitting with optimization in progress ...")
    # try:
    #   for files in uncompressed_files: #we are splitting the files here
    #     print("Treatment of file :", files)
    #     # Input obj files
    #     if files.endswith('.obj'):

    #         match = file_pattern.match(files)
    #         if match:
    #             if(isNewStructure): print("Using new structure generation")

    #             isNewStructure = True

    #             step_number, jaw_side = match.groups()
    #             print(f"Traitement de : Step {step_number} - Obj3D {jaw_side}")

    #             file_in = os.path.join(uncom_files_dir, files)
                
    #             # Création du dossier pour les fichiers séparés
    #             spt_out = os.path.join(splitted_files_dir, step_number)
    #             if not os.path.exists(spt_out):
    #                 os.makedirs(spt_out)
                
    #             if(step_number == "0"):
    #               save_file_in.append(file_in)
    #               save_spt_out = spt_out 
                
    #             print(f"Splitting with optimization in progress for step: {step_number}, Jaw: {jaw_side}")
                
    #             # Création du dossier pour les fichiers optimisés
    #             opt_out = os.path.join(optimized_files_dir, step_number)
    #             if not os.path.exists(opt_out):
    #                 os.makedirs(opt_out)

    #             print("Fichier : ", file_in)
    #             # Ici, effectuez le traitement réel, comme la séparation et l'optimisation des fichiers
    #             splitted_files = main(file_in, spt_out)

    #             # Ce bloc est commenté car il dépend de vos fonctions spécifiques de traitement de fichiers
    #             # for splitted_file in splitted_files:
    #             #     if splitted_file.endswith('.obj'):
    #             #         file_in_dir = os.path.join(spt_out, splitted_file)
    #             #         file_out_name = os.path.join(opt_out, splitted_file)
    #             #         # Exemple d'appel de votre fonction d'optimisation
    #             #         # optimizing_file(file_in_dir, file_out_name, divide_by=1)

    #             if spt_out_prev != spt_out:
    #                 step_i += 1
    #             spt_out_prev = spt_out
    #         else:
    #           isNewStructure = False

    #           print("Traitement de : ", files)

    #           file_in = os.path.join(uncom_files_dir,files)
    #           #Output obj files directory
    #           spt_out_name = files.split("_")
    #           #creating folders for splitted_data
    #           spt_out = os.path.join(splitted_files_dir,spt_out_name[0][4:]) # to store each step in its folder named as 0, 1, 2, 3, 4, for each step etc..

    #           #creating directory to store splitted files
    #           if(os.path.exists(spt_out) == False): os.makedirs(spt_out)

    #           #creating folders for optimized_data
    #           print("Splitting with optimization in progress ...")
    #           print("Optimization of step : ", spt_out.split('\\')[-1])
    #           opt_out = os.path.join(optimized_files_dir,spt_out_name[0][4:])

    #           if(os.path.exists(opt_out) == False): os.makedirs(opt_out) 
                  
              
    #           #Splitting the files
    #           splitted_files = main(file_in, spt_out)
              
    #           if(spt_out_name[0][4:] == "0"):
    #             save_file_in.append(file_in)
    #             save_spt_out = spt_out 
              
                
    #             # spt_out_to_use_for_json = spt_out
              
    #           #optimizing the files
    #           # print(splitted_files)
              
    #           for splitted_file in splitted_files:
    #             if splitted_file.endswith('.obj'):
    #               file_in_dir = os.path.join(spt_out,splitted_file)
    #               file_out_name = os.path.join(opt_out,splitted_file)
                  
    #               nameFile = splitted_file.split(".")[0]
    #               nameFile = nameFile.split("_")[0]
    #               # If it's an attachment, we don't optimized it too much to not loose too much vertices
    #               # if(len(nameFile) > 2): optimizing_file(file_in_dir,file_out_name, divide_by=0.1)
    #               # # Else : we do
    #               # else: 
    #               #   optimizing_file(file_in_dir,file_out_name, divide_by=1)

    #           if(spt_out_prev != spt_out): step_i += 1
    #           spt_out_prev = spt_out

  #   except:
  #     if callback_status_func:
  #       callback_status_func(a_3d_o, "FAILED_"+ spt_out.split('\\')[-1] )
  #     return

  # list_of_obj = []

  # for list in save_file_in:
  #   for object in main(list, save_spt_out, writing=False):
  #     list_of_obj.append(object)
  
  list_of_obj, isNewStructure = parallel_process_files(
    uncompressed_files    = uncompressed_files,
    uncom_files_dir       = uncom_files_dir,
    splitted_files_dir    = splitted_files_dir,
    optimized_files_dir   = optimized_files_dir,
    file_pattern          = file_pattern,
    generate_obj          = generate_obj,
    callback_status_func  = callback_status_func,
    a_3d_o                = a_3d_o,
    main                  = main,
    isNewStructure        = isNewStructure,
    step_i                = step_i,
    spt_out_prev          = spt_out_prev,
    save_file_in          = save_file_in,
    debug                 = True  # ou False selon vos besoins
  )

  find_teeth_structure(list_of_obj, output_json)

  
  print("Splitting finished")
  

  print("Generation of data")

  nb_steps = os.listdir(splitted_files_dir)
  nb_steps = len(nb_steps)

  print("Nb steps: ", nb_steps)

  output_json['steps'] = nb_steps

  #intersection
  last_frame_files = splitted_files_dir + '/' + str(nb_steps - 1) + '/'
  first_frame_files = splitted_files_dir + '/' + str(0) + '/'
  
  list_of_teeth = []
  for obj in list_of_obj:
     if(obj[:5] == 'Tooth'):
        list_of_teeth.append(obj)

  print("Data structure generation ...")
  find_step_structure(output_json)
  jsonData={}

  spacingData = []
  try:
    print("IPR Data structure generation ...")
    # iprData = generateIPRdata(os.path.join(uncom_files_dir, ipr_data_filename),output_json)
    if os.path.exists(os.path.join(uncom_files_dir, ipr_data_filename)):
      # Traitement du fichier IPR.csv
      print("traitement du fichier IPR.csv")
      iprData = generateIPRdata(os.path.join(uncom_files_dir, ipr_data_filename), output_json)
    else:
        # Recherche et traitement des fichiers avec le step le plus élevé
        pathUpper, pathLower = find_highest_step_files_IPR(uncom_files_dir)

        print("pathUpper, pathLower :", pathUpper, pathLower)

        if pathUpper and pathLower:
            print("Traitement des fichiers IPR séparés")
            iprData = generateIPRdataSeparate(pathUpper=pathUpper, pathLower=pathLower, jsonData=output_json)
        else:
            print("Aucun fichier IPR approprié trouvé.")
    

    try:
        print("Generation de la structure des données d'espacements...")
        pathUpperSpacing, pathLowerSpacing = find_highest_step_files_Spacing(uncom_files_dir)

        print(pathUpperSpacing, pathLowerSpacing)

        if pathUpperSpacing and pathLowerSpacing:
            print("Traitement des fichiers d'espacements séparés")
            spacingData = extract_tooth_distances(pathUpper=pathUpperSpacing, pathLower=pathLowerSpacing)

            print("spacingData :", spacingData)

            jsonData["spacingData"] = spacingData

            print("Traitement des fichiers d'espacements terminé")
        else:
            print("Aucun fichier d'espacements approprié trouvé.")
    except Exception as e:
        print(f"Une erreur est survenue : {e}")
        if callback_status_func:
            callback_status_func(a_3d_o, "SPACING_FAILED")

    print("Structure des données IPR générée.")

    print("Tooth Data structure generation ...")
    print("jsonData['steps']",  output_json['steps'])
    toothData = generateToothData(output_json, splitted_files_dir)

    print("Update IPR data json ...")
    jsonData = updateJsonIpr(output_json, iprData, toothData)
     
    print("Update Moving data json ...")

    print("Is new data structure : ", isNewStructure)
    if(isNewStructure == False): jsonData = generateMovData(jsonData,uncom_files_dir)
    else: 
      print("List directory of files")
      listOfFiles = os.listdir(uncom_files_dir)

    print("Generate list of csv")
    listOfCSV = [f for f in listOfFiles if f.endswith('.csv')]
    step = 0  # Vous pouvez définir la valeur de step en fonction de vos besoins ou des données disponibles.
    pattern = re.compile(f'^Step {step} - Info\\.csv$')
    csvFilesFound = any(pattern.match(f) for f in listOfCSV)

    if csvFilesFound:
      print("Json Infos files Not Detected - Transformation Matrix with separeted files activated")
      generateMovDataForSeparatedFiles(jsonData, uncom_files_dir)
    else:
        print("Json Infos files Detected - Transformation Matrix with ids generation activated")
        extractMoveDataFromJsonInfoFile(jsonData, uncom_files_dir)
    
    try:
      # print("Update Landmark data json ...")
      # jsonData = generateLandmarkData(uncom_files_dir, landmark_data_filename, jsonData)

      # Check if landmarks.txt exists
      print("Update Landmark data json ...")
      if os.path.exists(os.path.join(uncom_files_dir, landmark_data_filename)):
          
          # Assuming generateLandmarkData is defined elsewhere and ready to be used
          jsonData = generateLandmarkData(uncom_files_dir, landmark_data_filename, jsonData)
          
      else:
          print("Landmark file not found, research of CSV File")
          landmark_filename = find_highest_files_landmarks(uncom_files_dir)

          print("landmark csv file :", landmark_filename)

          jsonData = generateLandmarkDataFromCSV(landmark_filename, jsonData)


      try:
        print("Update Movement Table data json ...")
        if os.path.exists(os.path.join(uncom_files_dir, pathMovementTable)):
          jsonData = generateTotalMoveData(os.path.join(uncom_files_dir, pathMovementTable), jsonData)
          infoCsvListOfFiles = get_csv_file_paths(uncom_files_dir)
          jsonData["transformationAttachment"], jsonData["transformationTooth"] = process_csv_matrix(infoCsvListOfFiles)
        else:
          jsonData = generateTotalMoveDataFromSeparatedFiles(uncom_files_dir, jsonData)


        # JSON ADAPTATION FOR MOVEMENT EXTRACTION => NON FUNCTIONNAL
        # if(jsonData["transformationTooth"][0] == {}):
        #   jsonData["transformationAttachment"], jsonData["transformationTooth"] = extractMoveDataFromJsonInfoFile(jsonData, uncom_files_dir)

        # console.log()
        if(jsonData["transformationTooth"][0] == {}): 
           if callback_status_func:
              callback_status_func(a_3d_o, "MOVEMENT_EXTRACTION_FAILED")
              return

        jsonData = generateArcanumMoveData(jsonData, nb_steps)


        jsonData["bolton_analysis"] = {}
        # try: jsonData["bolton_analysis"] = bolton_analysis.get_bolton_analysis(os.path.join(uncom_files_dir, bolton_analysis_file))
        # except: pass
        try:
          print("BOLTON ANALYSIS GENERATION")
          jsonData["bolton_analysis"] = ba.get_bolton_analysis(os.path.join(uncom_files_dir, bolton_analysis_file))
        except: pass
        
        try:
          if(not jsonData["bolton_analysis"]): jsonData["bolton_analysis"] = {}

          jsonData["spacingData"] = spacingData

          # print("jsonData[spacingData]", jsonData["spacingData"])

          print("AF CHECK GENERATION")
          afCheckJson = generateAFcheck(jsonData)
          

          try:
            # jsonData["ponticsData"] = find_and_copy_pontics(uncom_files_dir, optimized_files_dir, export_dir)
            print("COPY OBJECTS TO EXPORT DIRECTORY")
            # copy_other_objects('0', optimized_files_dir, export_dir)

            # morph.generateMorph("Maxilla", optimized_files_dir + "Maxilla.glb", optimized_files_dir)
            # morph.generateMorph("Mandible", optimized_files_dir + "Mandible.glb", optimized_files_dir)
            # Pour "Maxilla"
            # subprocess.run(["blender", "--background", "--python", "morphtarget.py", "--", "Maxilla", export_dir + "\\Maxilla.glb", optimized_files_dir])
            # if(BLENDER_PATH == "blender"): BLENDER_PATH = "/usr/share/blender/blender"

            print("BLENDER PATH : ", BLENDER_PATH)
            # Pour "Mandible"
            # subprocess.run(["blender", "--background", "--python", "morphtarget.py", "--", "Mandible", export_dir + "\\Mandible.glb", optimized_files_dir])
            # print("MAXILLA BLENDER GENERATION STARTED")
            # upper_jaw_process = subprocess.Popen([BLENDER_PATH, "--background", "--python", "lib/optimize/generateJaw.py", "--", optimized_files_dir, export_dir, "Upper"])
            # print("MANDIBLE BLENDER GENERATION STARTED")
            # lower_jaw_process = subprocess.Popen([BLENDER_PATH, "--background", "--python", "lib/optimize/generateJaw.py", "--", optimized_files_dir, export_dir, "Lower"])
            with open (os.path.join(export_dir, "temp_data.json"),'w') as f:
              json.dump(jsonData, f)
              
            
            blender_data_file="blender_data.msgpack.z"
              
            mouth_process = subprocess.Popen([BLENDER_PATH, "--background", "--python", "lib/optimize/generateMouthGLB.py", "--", splitted_files_dir, export_dir, blender_data_file])

            mouth_process.wait()
            
            # mouth_process = subprocess.Popen(
            #     [BLENDER_PATH, "--background", "--python", "lib/optimize/generateMouthGLB.py", "--", splitted_files_dir, export_dir],
            #     # stdout=subprocess.PIPE,
            #     # stderr=subprocess.PIPE,
            #     # text=True
            # )

            # # stdout, stderr = mouth_process.communicate()  # attend la fin du processus et récupère stdout et stderr
            
            # mouth_process.wait()

            jsonData["blender_data"] = {}
            
            
            # stdout devrait contenir le JSON imprimé à la fin
            # if os.path.exists(os.path.join(export_dir, "blender_data.json")):
              
            #   with open(os.path.join(export_dir, "blender_data.json"), "r") as f:
            #     blender_data = json.load(f)
                
            #     jsonData["blender_data"] = blender_data
                # result_data est maintenant votre dictionnaire avec les couleurs
    
            print("BLENDER GENERATION FINISHED")
            
            print("START DATA JSON EXPORT")
            # Writing the data in the data.json
            with open (os.path.join(export_dir, output_json_filename),'w') as f:
              json.dump(jsonData, f)
            print("START AFCHECK JSON EXPORT")
            
            with open (os.path.join(export_dir, "AF_check.json"),'w') as f:
              json.dump(afCheckJson,f)
            
            print("Files and data successfully generated !")
            print("BLENDER PATH : ", BLENDER_PATH)
            # Upload the optimized files onto AWS S3
            if callback_status_func:
              print("START UPLOADING AWS")
              callback_status_func(a_3d_o, 'UPLOADING_TO_AWS')
              
            # jsonData = aws.upload_optimized_files(data_json=jsonData, base_file_path=optimized_files_dir, patient_id=patient_name, af_setup_name=af_setup_name)
            jsonData = aws.upload_expert_files(data_json=jsonData, base_file_path=export_dir, patient_id=patient_name, af_setup_name=af_setup_name, blender_data_file=blender_data_file)
            
            # Fin de la mesure
            end_time = time.time()
            
            # Calcul et affichage du temps d'exécution
            elapsed_time = end_time - start_time
            print(f"Temps d'exécution : {elapsed_time:.4f} secondes")
    
            return afCheckJson, jsonData
          except:
            if callback_status_func:
              callback_status_func(a_3d_o, "BLENDER_GENERATION_FAILED")
        except:
          if callback_status_func:
            callback_status_func(a_3d_o, "AF_CHECK_GENERATION_FAILED")

        
        # except:
        #   if callback_status_func:
        #     callback_status_func(a_3d_o, "BOLTON_FAILED")
      except:
        if callback_status_func:
          callback_status_func(a_3d_o, "MOVEMENT_TABLE_FAILED")
    except:
      if callback_status_func:
        callback_status_func(a_3d_o, "LANDMARK_FAILED")
  except:
    if callback_status_func:
      callback_status_func(a_3d_o, "IPR_FAILED")
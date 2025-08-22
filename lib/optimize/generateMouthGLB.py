import bpy
import os
import bmesh
import sys
import time
import mathutils
from mathutils import Vector
from mathutils import Matrix
from mathutils.kdtree import KDTree
from mathutils.bvhtree import BVHTree
import bpy, bmesh
import math
import json
import msgpack
import zlib

detail_levels = {
    "Mandible": (1, 'COLLAPSE'),
    "Maxilla": (1, 'COLLAPSE'),
    "Tooth": (0.5, 'COLLAPSE'),
    "attachment": (1, 'COLLAPSE') 
}


def apply_decimate(obj, ratio=1, decimate_type='COLLAPSE'):
    """
    Applique un modificateur Decimate à l'objet donné avec les paramètres spécifiés.
    """
    if obj is None:
        print("Aucun objet actif pour appliquer Decimate.")
        return

    # S'assurer que Blender est en mode objet et que l'objet est sélectionné et actif
    bpy.context.view_layer.objects.active = obj  # Définir l'objet comme actif
    if bpy.context.active_object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')  # Passer en mode objet si ce n'est pas déjà le cas
    bpy.ops.object.select_all(action='DESELECT')  # Désélectionner tous les objets
    obj.select_set(True)  # Sélectionner l'objet

    # Ajout du modificateur Decimate
    decimate_mod = obj.modifiers.new(name="Decimate", type='DECIMATE')
    decimate_mod.ratio = ratio
    decimate_mod.decimate_type = decimate_type

    # Appliquer le modificateur
    bpy.ops.object.modifier_apply(modifier=decimate_mod.name)

    # Désélectionner l'objet après application
    obj.select_set(False)


def load_and_rename_objects(dossier_racine, detail_levels):
    etapes = []
    list_fichiers_a_supprimer = []
    list_fichiers_non_lowpolisables = []
    
    nb_etapes = len(os.listdir(dossier_racine))

    for nom_dossier in sorted(os.listdir(dossier_racine)):
        chemin_sous_dossier = os.path.join(dossier_racine, nom_dossier)
        
        # On vérifie si le nom du dossier est un entier (étape)
        if os.path.isdir(chemin_sous_dossier) and nom_dossier.isdigit():
            etape = int(nom_dossier)
            etapes.append(etape)

            for fichier in os.listdir(chemin_sous_dossier):
                chemin_complet = os.path.join(chemin_sous_dossier, fichier)
                
                # Construire la logique de chargement en fonction du dossier et du nom du fichier
                doit_etre_supprimer = not (nom_dossier == "0" or fichier in ["Mandible.obj", "Maxilla.obj"])
                # ne_doit_pas_etre_lowpolise = not (nom_dossier == "0" or nom_dossier == str(nb_etapes - 1) or fichier in ["Mandible.obj", "Maxilla.obj"])
                ne_doit_pas_etre_lowpolise = not (nom_dossier == "0" or fichier in ["Mandible.obj", "Maxilla.obj"])
                
                doit_charger = (nom_dossier == "0" or fichier in ["Mandible.obj", "Maxilla.obj"]) and ("Obj3D" not in fichier)
                
                if doit_charger:
                    bpy.ops.import_scene.obj(filepath=chemin_complet)
                    
                    for objet in bpy.context.selected_objects:
                        # Identifier le type d'objet pour le renommage et le decimate
                        objet_type = None
                        if "Mandible" in fichier:
                            objet_type = "Mandible"
                        elif "Maxilla" in fichier:
                            objet_type = "Maxilla"
                        elif "Tooth" in fichier:
                            objet_type = "Tooth"
                        else:
                            objet_type = "attachment"  # On considère ici tout autre objet dans '0' comme un 'attachment'
                        
                        if objet_type:
                            # Renommer si nécessaire
                            if objet_type in ["Mandible", "Maxilla"]:
                                nom_objet_nouveau = f"{objet_type}_{nom_dossier}"
                                objet.name = nom_objet_nouveau
                                objet.data.name = nom_objet_nouveau
                            
                            elif objet_type == "Tooth":
                                # Extraire le numéro de dent
                                base_name, ext = os.path.splitext(fichier)
                                # base_name peut être "Tooth 34" par exemple
                                tooth_part = base_name.replace("Tooth", "").strip()  # ex: "34"
                                nom_objet_nouveau = f"Tooth_{tooth_part}_{nom_dossier}"
                                objet.name = nom_objet_nouveau
                                objet.data.name = nom_objet_nouveau
                            
                            # Appliquer Decimate selon le type
                            ratio, decimate_type = detail_levels.get(objet_type, (1, 'COLLAPSE'))
                            apply_decimate(objet, ratio, decimate_type)
                            
                            if(doit_etre_supprimer): list_fichiers_a_supprimer.append(objet)
                            if(ne_doit_pas_etre_lowpolise): list_fichiers_non_lowpolisables.append(objet)

    return max(etapes) if etapes else 0, list_fichiers_a_supprimer, list_fichiers_non_lowpolisables



def create_lowpoly_tooth_copies(reduction_ratio=0.02, list_fichiers_a_eviter=[], list_fichiers_a_supprimer=[], etape_finale=10):
    # Désélectionner tous les objets au début pour partir sur une base propre
    bpy.ops.object.select_all(action='DESELECT')

    for obj in bpy.data.objects:
        if obj.type == 'MESH' and "Tooth" in obj.name and obj not in list_fichiers_a_eviter:
            # S'assurer que l'objet de contexte est correctement défini
            bpy.context.view_layer.objects.active = obj
            # Sélectionner l'objet original
            obj.select_set(True)

            # Dupliquer l'objet
            bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
            # Le nouvel objet duplicaté devient l'objet actif
            lowpoly_obj = bpy.context.active_object

            # S'assurer que le nouvel objet est le seul sélectionné
            obj.select_set(False)

            # Ajouter un modificateur Decimate et configurer le ratio
            decimate_modifier = lowpoly_obj.modifiers.new(name="Decimate", type='DECIMATE')
            decimate_modifier.ratio = reduction_ratio

            # Appliquer le modificateur Decimate
            bpy.ops.object.modifier_apply(modifier=decimate_modifier.name)

            # Renommer l'objet dupliqué avec le suffixe _lowpoly
            lowpoly_obj.name = f"{obj.name}_lowpoly"
            
            if(obj in list_fichiers_a_supprimer): list_fichiers_a_supprimer.append(lowpoly_obj)

            # Désélectionner l'objet dupliqué après avoir appliqué les modifications
            lowpoly_obj.select_set(False)


def apply_select_and_deform(obj_name, fichier):
    if "Mandible" in fichier:
        select_and_deform(obj_name, fromDirection=-1)
    elif "Maxilla" in fichier:
        select_and_deform(obj_name, fromDirection=1)


def select_and_deform(obj_name, fromDirection=1, offset=1, translation_strength=1, iterations=4):
    obj = bpy.data.objects[obj_name]
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(obj.data)
    
    y_coords = [v.co.y for v in bm.verts]  # Utiliser les coordonnées y
    max_y = max(y_coords)  # Max de y
    min_y = min(y_coords)  # Min de y
    target_y = max_y if fromDirection == 1 else min_y  # Cibler sur y
    
    for v in bm.verts:
        if fromDirection == 1 and v.co.y >= target_y - offset:
            v.select = True
        elif fromDirection == -1 and v.co.y <= target_y + offset:
            v.select = True
        else:
            v.select = False
            
    bmesh.update_edit_mesh(obj.data)  # Corrigé, ne prend qu'un seul argument

    # bpy.ops.object.mode_set(mode='OBJECT')
    
    for i in range(iterations):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.transform.translate(value=(0, 0, -translation_strength * fromDirection),
                                    use_proportional_edit=True,
                                    proportional_edit_falloff='SPHERE',
                                    proportional_size=translation_strength,
                                    use_proportional_connected=True,
                                    orient_type='GLOBAL')
        bpy.ops.mesh.select_more(use_face_step=True)
        bpy.ops.object.mode_set(mode='OBJECT')


def export_all_to_glb(file_path, with_blender_data=False, compression_level=6):
    """
    Exporte tous les objets de la scène au format GLB avec la compression spécifiée.

    :param file_path: Chemin complet du fichier de sortie GLB.
    :param compression_level: Niveau de compression (0 à 10).
    """
    if(with_blender_data):
        bpy.ops.export_scene.gltf(
            filepath=file_path,
            export_format='GLB',  # Choisir le format GLB pour le fichier de sortie
            export_extras=True,
            use_selection=False,  # Exporter tous les objets si False
            export_draco_mesh_compression_enable=True,  # Activer la compression Draco
            export_draco_mesh_compression_level=compression_level  # Définir le niveau de compression
        )
    else :
        bpy.ops.export_scene.gltf(
        filepath=file_path,
        export_format='GLB',
        use_selection=False,
        export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=compression_level
    )



def apply_smooth_shading_to_all_objects():
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.select_all(action='DESELECT')  # Désélectionner tous les objets
            obj.select_set(True)
            bpy.ops.object.shade_smooth()
            

def get_opposite_arcs(arch_digit):
    """
    Retourne les arcades opposées sous forme de liste.
    Haut = 1, 2
    Bas = 3, 4
    Si la dent est du haut (1 ou 2), opposées = [3,4]
    Si la dent est du bas (3 ou 4), opposées = [1,2]
    """
    arch_digit = int(arch_digit)
    if arch_digit in [1, 2]:
        return [3, 4]
    elif arch_digit in [3, 4]:
        return [1, 2]
    else:
        # Par sécurité
        return [1, 2]
    

def get_object_center(obj):
    # Centre approximatif = moyenne des coords des vertices en coordonnées monde
    verts = obj.data.vertices
    if not verts:
        return obj.matrix_world.translation
    sum_coord = Vector((0,0,0))
    for v in verts:
        sum_coord += obj.matrix_world @ v.co
    return sum_coord / len(verts)


def is_point_inside_mesh(point, bvhtree, max_tests=50, offset=1e-6):
    """
    Vérifie si un point est à l'intérieur d'une géométrie représentée par un BVHTree.
    Méthode : lancers de rayons dans une direction fixe (ex: +X) et comptage des intersections.
    """
    direction = mathutils.Vector((1, 0, 0))
    hit_count = 0
    start = point.copy()

    for _ in range(max_tests):
        hit = bvhtree.ray_cast(start, direction)
        if hit is None:
            # Aucune intersection trouvée : on arrête le lancer de rayons
            break

        location, normal, face_index, dist = hit
        if location is None:
            # Par sécurité, si location est None malgré le hit non None
            break

        hit_count += 1
        # On décale légèrement le point de départ après l'intersection
        start = location + direction * offset

    return (hit_count % 2) == 1


def check_teeth_vertex_count_consistency(debug=True):
    """
    Parcourt tous les objets 'Tooth_XX_step' dans la scène
    et vérifie si, pour un même 'XX' (ex: 11), le nombre de vertex
    est identique d'une étape à l'autre.

    Si on détecte un mismatch, on l'affiche et on renvoie un dict
    indiquant les incohérences.
    
    Retourne un dict:
      mismatches = {
        "Tooth_11": {
          stepX: vertex_count,
          stepY: vertex_count_different,
          ...
        },
        ...
      }
    où seules les dents incohérentes apparaissent.
    """
    import bpy
    from collections import defaultdict

    # Regroupe: teeth_vertex_counts["XX"][step] = vertex_count
    teeth_vertex_counts = defaultdict(dict)

    # Parcourir les objets
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and obj.name.startswith("Tooth_"):
            parts = obj.name.split("_")  # ex: ["Tooth", "11", "2"]
            if len(parts) == 3 and parts[0] == "Tooth" and parts[2].isdigit():
                tooth_number = parts[1]   # "11"
                step = int(parts[2])      # 2
                me = obj.data
                vcount = len(me.vertices)
                teeth_vertex_counts[tooth_number][step] = vcount

    # Maintenant, on vérifie la cohérence
    mismatches = {}
    for tooth_number, step_dict in teeth_vertex_counts.items():
        # ex: step_dict = {0: 1523, 1: 1523, 2: 1523, 3: 900} => mismatch
        if len(step_dict) < 2:
            # S'il n'y a qu'un step, pas d'incohérence possible
            continue

        # On récupère l'ensemble des counts
        unique_counts = set(step_dict.values())
        if len(unique_counts) > 1:
            # mismatch => on stocke dans mismatches
            mismatches[tooth_number] = step_dict

    if mismatches and debug:
        for tooth_number, step_dict in mismatches.items():
            print(f"[AVERTISSEMENT] Mismatch de vertex pour la dent Tooth_{tooth_number}:")
            for st, vcount in sorted(step_dict.items()):
                print(f"  - étape {st}: {vcount} sommets")

    return mismatches


def fix_teeth_vertex_count_mismatch(debug=True):
    """
    Parcourt tous les objets 'Tooth_XX_step' dans la scène
    et tente de corriger un mismatch de vertex count d'une étape à l'autre
    en dupliquant ou supprimant des sommets (très rudimentaire).
    -> On choisit l'étape 0 comme référence.
    -> Si la dent Tooth_XX_0 existe et qu'à l'étape i,
       on a un count différent, on corrige la topologie de l'étape i
       pour le ramener au count de l'étape 0.
    """
    import bpy
    import bmesh
    from mathutils import Vector
    from collections import defaultdict

    def add_vertices_in_mesh(obj, nb_to_add, debug=True):
        """Ajoute nb_to_add sommets en dupliquant arbitrairement."""
        me = obj.data
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(me)
        bm.verts.ensure_lookup_table()
        import random
        for _ in range(nb_to_add):
            src_v = random.choice(bm.verts)
            bm.verts.new(src_v.co)
        bmesh.update_edit_mesh(me)
        bpy.ops.object.mode_set(mode='OBJECT')
        if debug:
            print(f"[fix] Ajouté {nb_to_add} sommets à {obj.name}. New count={len(me.vertices)}")

    def remove_vertices_in_mesh(obj, n_to_remove, debug=True):
        """Supprime n_to_remove sommets aléatoirement."""
        me = obj.data
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(me)
        bm.verts.ensure_lookup_table()
        import random
        chosen = random.sample(bm.verts, k=min(n_to_remove, len(bm.verts)))
        for v in chosen:
            v.select = True
        bmesh.update_edit_mesh(me)
        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.object.mode_set(mode='OBJECT')
        if debug:
            print(f"[fix] Supprimé {n_to_remove} sommets de {obj.name}. New count={len(me.vertices)}")

    # teeth_dict["XX"][step] = (obj, vertex_count)
    from collections import defaultdict
    teeth_dict = defaultdict(dict)

    for obj in bpy.data.objects:
        if obj.type == 'MESH' and obj.name.startswith("Tooth_"):
            parts = obj.name.split("_")
            if len(parts) == 3 and parts[0] == "Tooth" and parts[2].isdigit():
                tooth_number = parts[1]
                step = int(parts[2])
                vcount = len(obj.data.vertices)
                teeth_dict[tooth_number][step] = (obj, vcount)

    for tooth_number, step_map in teeth_dict.items():
        # On ne corrige que si la dent a un step 0
        if 0 not in step_map:
            continue

        obj0, ref_count = step_map[0]
        for step_i, (obj_i, count_i) in step_map.items():
            if step_i == 0:
                continue
            if count_i == ref_count:
                continue
            diff = ref_count - count_i
            if debug:
                print(f"[fix] Dent Tooth_{tooth_number}_{step_i}: mismatch => {count_i} vs ref {ref_count}")
            if diff>0:
                # On duplique 'diff' sommets
                add_vertices_in_mesh(obj_i, diff, debug=debug)
            else:
                # On supprime 'abs(diff)'
                remove_vertices_in_mesh(obj_i, abs(diff), debug=debug)



def load_transformation_data(temp_data_path):
    """
    Lit temp_data.json et renvoie un dict:
    transform_data[step][toothName] = matrice 4x4 (mathutils.Matrix).
    """
    with open(temp_data_path, 'r') as f:
        data = json.load(f)

    result = {}
    # data["transformationTooth"] contient toutes les étapes
    transformation_dict = data["transformationTooth"]  # ex: { "0": {...}, "1": {...}, ... }
    
    for step_str, tooth_map in transformation_dict.items():
        step = int(step_str)
        result[step] = {}
        for toothName, matArray in tooth_map.items():
            # matArray => Array(4) de 16 floats => ex: [ [a11,a12,a13,a14], [a21,...], ... ]
            # On construit mathutils.Matrix( matArray )
            # On suppose matArray = liste de 4 sous-listes, chacune de 4 floats
            # ou alors un flatten de 16 floats => à clarifier.
            # On illustre ici si c'est un tableau 2D:
            mat = Matrix(matArray)  # matArray doit être [[m00,m01,m02,m03],..., [m30,m31,m32,m33]]
            result[step][toothName] = mat
    return result


def get_opposite_arcs(arch_digit):
    """1,2 => [3,4], 3,4 => [1,2]."""
    a = int(arch_digit)
    return [3,4] if a in [1,2] else [1,2]


def build_bvhtree_for_teeth(list_objs):
    """Construit un unique BVH en coords monde pour tous les objets listés."""
    if not list_objs:
        return None
    all_tris=[]
    import bmesh
    for ob in list_objs:
        mw = ob.matrix_world
        me = ob.data
        bm = bmesh.new()
        bm.from_mesh(me)
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
        bm.verts.ensure_lookup_table()
        bm.faces.ensure_lookup_table()
        verts_w = [mw @ v.co for v in bm.verts]
        for f in bm.faces:
            if len(f.verts)==3:
                tri=(
                    verts_w[f.verts[0].index],
                    verts_w[f.verts[1].index],
                    verts_w[f.verts[2].index]
                )
                all_tris.append(tri)
        bm.free()
    if not all_tris:
        return None
    
    verts=[]
    polys=[]
    idx=0
    for tri in all_tris:
        v0=(tri[0].x, tri[0].y, tri[0].z)
        v1=(tri[1].x, tri[1].y, tri[1].z)
        v2=(tri[2].x, tri[2].y, tri[2].z)
        verts.extend([v0,v1,v2])
        polys.append((idx, idx+1, idx+2))
        idx+=3
    return BVHTree.FromPolygons(verts, polys)


def is_point_inside_mesh(point, bvhtree, max_tests=50, offset=1e-5):
    """Test odd/even => rayon +X, compte intersections."""
    from mathutils import Vector
    if not bvhtree:
        return False
    direction = Vector((1,0,0))
    start = point.copy()
    hits=0
    for _ in range(max_tests):
        cast=bvhtree.ray_cast(start, direction)
        if cast is None:
            break
        location, normal, face_i, distv = cast
        if location is None:
            break
        hits+=1
        start = location + direction*offset
    return (hits%2)==1


def apply_colors_to_mesh(obj, color_array):
    """Applique color_array à OcclusionColors de obj."""
    me=obj.data
    if "OcclusionColors" not in me.vertex_colors:
        vc=me.vertex_colors.new(name="OcclusionColors")
    else:
        vc=me.vertex_colors["OcclusionColors"]
    for loop in me.loops:
        i=loop.vertex_index
        c=color_array[i]
        vc.data[loop.index].color=(c[0], c[1], c[2], 1.0)
    me.update()


def get_center_world(obj):
    """Centre en coords monde (moyenne des vertices)."""
    if not obj.data.vertices:
        return obj.matrix_world.translation
    from mathutils import Vector
    s=Vector((0,0,0))
    for v in obj.data.vertices:
        s+= (obj.matrix_world @ v.co)
    return s/len(obj.data.vertices)


def reset_all_teeth_to_identity():
    """Remet la matrix_world de tous les 'ToothXX_0' à la matrice identité."""
    for obj in bpy.data.objects:
        if obj.type=='MESH' and obj.name.startswith("Tooth") and obj.name.endswith("_0"):
            # reset
            obj.matrix_world = Matrix.Identity(4)


def calculate_occlusion_via_temp_data(temp_data_path, 
                                      red_threshold=0.2,
                                      green_threshold=0.5,
                                      debug=False):
    """
    Calcule l'occlusion pour chaque étape listée dans temp_data.json.

    Hypothèses:
     - Les dents de base s'appellent "Tooth_XX_0" (ex: "Tooth_14_0").
       => On en extrait "14" pour base_teeth_map["14"] = <OBJ>.
     - Dans temp_data.json, on a transform_data[step]["Tooth_14"] = matrice
       (ou "Tooth14", à ajuster), et on convertit/parse pour en extraire "14".
    """

    import bpy, bmesh
    from mathutils import Matrix, Vector
    from mathutils.bvhtree import BVHTree

    # === 1) Charger transform_data ===
    transform_data = load_transformation_data(temp_data_path)
    if debug:
        print("[DEBUG] ----- Contenu de 'transform_data' -----")
        for st in sorted(transform_data.keys()):
            print(f"   Étape {st}:")
            for toothName, matVal in transform_data[st].items():
                print(f"      {repr(toothName)} => {repr(matVal)}")

    # === 2) Récupérer toutes les dents de base "Tooth_XX_0" ===
    base_teeth = [
        obj for obj in bpy.data.objects
        if obj.type == 'MESH'
        and obj.name.startswith("Tooth_")
        and obj.name.endswith("_0")
    ]
    
    # Construire un map: "14" => <OBJ "Tooth_14_0">
    base_teeth_map = {}
    for obj in base_teeth:
        # ex: "Tooth_14_0" => parts = ["Tooth","14","0"]
        parts = obj.name.split("_")
        if debug:
            print(f"[DEBUG] base dent trouvée: '{obj.name}' => parts={parts}")

        if len(parts) == 3 and parts[0] == "Tooth" and parts[2] == "0":
            tooth_num_str = parts[1]  # "14"
            base_teeth_map[tooth_num_str] = obj
        else:
            if debug:
                print(f"[WARN] nom inattendu pour une dent base: '{obj.name}', on skip.")

    if debug:
        print("\n[DEBUG] base_teeth_map (étape 0) contient:")
        for k, v in base_teeth_map.items():
            print(f"   '{k}' => {v.name}")

    occlusion_data = {}
    all_steps = sorted(transform_data.keys())

    # === 3) Boucle sur chaque étape ===
    for step in all_steps:
        if debug:
            print(f"\n[DEBUG] ===== Traitement de l'étape {step} =====")

        # a) Reset identity pour chaque dent base "Tooth_XX_0"
        if debug:
            print("[DEBUG] => reset_all_teeth_to_identity()")
        reset_all_teeth_to_identity()

        step_data = transform_data[step]
        if debug:
            print(f"[DEBUG] => step_data contient {len(step_data)} dents:")
            for toothName, matVal in step_data.items():
                print(f"   * {repr(toothName)} => {repr(matVal)}")

        # b) Appliquer la matrice pour chaque dent dans step_data
        for toothName, mat in step_data.items():
            raw_str = toothName.strip()
            if debug:
                print(f"\n[DEBUG] Analyse toothName: '{toothName}' => repr: {repr(raw_str)}")
                print(f"         => Matrice lue: {repr(mat)}")

            # On suppose que le format est "Tooth_14" ou "Tooth14".
            # => On gère les 2 cas
            # 1) S'il commence par "Tooth_"
            # 2) Sinon s'il commence par "Tooth"

            number_part = None

            if raw_str.startswith("Tooth_"):
                # ex: "Tooth_14" => on enlève "Tooth_"
                number_part = raw_str[len("Tooth_"):]
            elif raw_str.startswith("Tooth"):
                # ex: "Tooth14" => on enlève "Tooth"
                number_part = raw_str[len("Tooth"):]
            else:
                if debug:
                    print(f"[WARN] step={step} => '{toothName}' ne commence pas par 'Tooth'/'Tooth_'. On skip.")
                continue

            number_part = number_part.strip()  # si jamais
            if not number_part.isdigit():
                if debug:
                    print(f"[ERROR] step={step} => toothName='{toothName}' => '{number_part}' pas numérique => skip")
                continue

            obj_0 = base_teeth_map.get(number_part)
            if not obj_0:
                if debug:
                    print(f"[WARN] step={step}, base_teeth_map['{number_part}'] introuvable => skip.")
                continue

            # On applique la transformation
            if debug:
                print(f"[INFO] step={step} => On applique la matrice sur '{obj_0.name}'")
            obj_0.matrix_world = mat

        # c) Calculer l'occlusion
        # c.1) Recalcule le centre
        current_teeth_centers = {}
        for num_str, obj in base_teeth_map.items():
            c = get_center_world(obj)
            current_teeth_centers[num_str] = c
            if debug:
                print(f"   => Dent base '{obj.name}', num_str='{num_str}', centre={c}")

        # c.2) Coloration => On parcourt base_teeth_map => on prend 3 dents opposées
        occlusion_data[step] = {}

        # Sépare bas [3,4] et haut [1,2]
        lower_list = []
        upper_list = []
        for num_str, ob in base_teeth_map.items():
            if len(num_str)>0:
                arch_dig = int(num_str[0])
                if arch_dig in [3,4]:
                    lower_list.append((num_str, ob))
                else:
                    upper_list.append((num_str, ob))
        ordered_teeth = lower_list + upper_list

        for (num_str, real_obj) in ordered_teeth:
            # init all white
            nbv = len(real_obj.data.vertices)
            all_white = [[1,1,1]] * nbv
            apply_colors_to_mesh(real_obj, all_white)

            arch_digit = int(num_str[0])
            arcs_opp = get_opposite_arcs(arch_digit)
            c_this = current_teeth_centers[num_str]

            # 3 plus proches
            opp_candidates = []
            for other_num, other_obj in base_teeth_map.items():
                if other_num == num_str:
                    continue
                if len(other_num)>0 and int(other_num[0]) in arcs_opp:
                    c_opp = current_teeth_centers[other_num]
                    d = (c_opp - c_this).length
                    opp_candidates.append((d, other_num, other_obj))
            opp_candidates.sort(key=lambda x: x[0])

            if len(opp_candidates) < 1:
                # pas de dents opposées => blanc
                occlusion_data[step][f"Tooth_{num_str}"] = all_white
                if debug:
                    print(f"[occlusion step={step}] => Tooth_{num_str}: no opp => BLANC")
                continue

            used = opp_candidates[:3]
            used_objs = [x[2] for x in used]
            used_names= [x[1] for x in used]

            if debug:
                print(f"[occlusion step={step}] => Dent '{num_str}' => used opp={used_names}")

            env_bvh = build_bvhtree_for_teeth(used_objs)
            if not env_bvh:
                occlusion_data[step][f"Tooth_{num_str}"] = all_white
                if debug:
                    print(f"[occlusion step={step}] => Tooth_{num_str}, BVH None => BLANC")
                continue

            reds=0; greens=0; whites=0
            col_array=[]
            mw=real_obj.matrix_world
            for v in real_obj.data.vertices:
                wpos = mw @ v.co
                inside = is_point_inside_mesh(wpos, env_bvh)
                if inside:
                    c=[1,0,0]
                    reds+=1
                else:
                    loc,norm,fid,distf = env_bvh.find_nearest(wpos)
                    if distf<red_threshold:
                        c=[1,0,0]; reds+=1
                    elif distf<green_threshold:
                        c=[0,1,0]; greens+=1
                    else:
                        c=[1,1,1]; whites+=1
                col_array.append(c)

            apply_colors_to_mesh(real_obj, col_array)
            # On stocke => "Tooth_{num_str}"
            occlusion_data[step][f"Tooth_{num_str}"] = col_array

            if debug:
                print(f"[occlusion step={step}] => Tooth_{num_str}, R={reds},G={greens},W={whites}")

        if debug:
            print(f"=== Fin de l'étape {step} ===")

    return occlusion_data


def apply_colors_to_mesh(obj, tooth_colors):
    """
    Applique les couleurs calculées directement dans l'attribut vertex_colors du mesh Blender.
    Ceci garantit que l'export GLB inclura les couleurs, et que l'ordre des vertices sera préservé.
    """

    me = obj.data
    # S'assurer qu'il n'y a pas déjà un attribut "OcclusionColors" ou le recréer
    if "OcclusionColors" in me.vertex_colors:
        color_layer = me.vertex_colors["OcclusionColors"]
    else:
        color_layer = me.vertex_colors.new(name="OcclusionColors")

    # Convertir les couleurs hex en (r,g,b)
    # Les vertex colors sont stockées par boucle (loop), pas par vertex
    for loop in me.loops:
        vert_idx = loop.vertex_index
        c = tooth_colors[vert_idx]
        r = c[0] 
        g = c[1] 
        b = c[2] 
        color_layer.data[loop.index].color = (r, g, b, 1.0)

    me.update()

def assign_vertex_id_to_blender_data(blender_data, max_verts):
    """
    Assigne un attribut vertex_id et stocke les indices originaux des sommets dans blender_data.
    La structure sera similaire à celle d'occlusionData, avec l'étape comme clé de niveau 1,
    puis le nom complet de la dent (ex: "Tooth_11") comme clé de niveau 2.
    
    Structure finale:
    blender_data["VertexIDMap"][step][obj_name] = [liste de vertex_id_norm]
    """

    if "VertexIDMap" not in blender_data:
        blender_data["VertexIDMap"] = {}

    for obj in bpy.data.objects:
        if obj.type == 'MESH' and "Tooth_" in obj.name and "lowpoly" not in obj.name:
            # Nom complet de la dent, ex: "Tooth_11" à partir de "Tooth_11_0"
            parts = obj.name.split("_")
            if len(parts) == 3 and parts[0] == "Tooth" and parts[1].isdigit() and parts[2].isdigit():
                # parts[0] = "Tooth", parts[1] = "11", parts[2] = "0" (l'étape)
                tooth_number = parts[1]
                step = int(parts[2])
                obj_name = f"Tooth_{tooth_number}"
            else:
                # Si le nom n'est pas conforme, on ignore
                continue

            me = obj.data

            # Créer un UV layer si nécessaire
            if "VertexIDMap" not in me.uv_layers:
                uv_layer = me.uv_layers.new(name="VertexIDMap")
            else:
                uv_layer = me.uv_layers["VertexIDMap"]

            # S'assurer que la structure est prête
            if step not in blender_data["VertexIDMap"]:
                blender_data["VertexIDMap"][step] = {}
            if obj_name not in blender_data["VertexIDMap"][step]:
                blender_data["VertexIDMap"][step][obj_name] = []

            vertex_map = blender_data["VertexIDMap"][step][obj_name]

            # Passer en mode objet
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='OBJECT')

            # Calculer les vertex_id normalisés
            # vertex_id_norm = vertex_index / max_verts
            for loop in me.loops:
                vert_idx = loop.vertex_index
                vertex_id_norm = vert_idx / max_verts
                uv_layer.data[loop.index].uv = (vertex_id_norm, 0.0)

                # Étendre la liste si nécessaire
                while len(vertex_map) <= vert_idx:
                    vertex_map.append(None)
                vertex_map[vert_idx] = vertex_id_norm


def store_original_positions():
    original_positions = {}
    for obj in bpy.data.objects:
        if obj.type=='MESH' and "Tooth_" in obj.name and obj.name.endswith("_0"):
            parts = obj.name.split("_")
            if len(parts) < 3:
                continue
            tooth_name = f"Tooth_{parts[1]}"
            if not obj.data.vertices:
                original_positions[tooth_name] = []
                continue
            verts = [obj.matrix_world @ v.co for v in obj.data.vertices]
            original_positions[tooth_name] = verts
    return original_positions


def remap_occlusion_data_according_to_positions(blender_data, original_positions, debug=True):
    if debug:
        print("\n--- Début du remapping ---")

    # Vérifier la présence des données d'occlusion
    if "OcclusionData" not in blender_data:
        if debug:
            print("[ERREUR] Aucune donnée d'occlusion trouvée dans blender_data.")
        return

    occlusion_data = blender_data["OcclusionData"]

    # On récupère la liste de toutes les étapes disponibles
    all_steps = sorted(occlusion_data.keys())
    if not all_steps:
        if debug:
            print("[ERREUR] Aucune étape trouvée dans les données d'occlusion.")
        return

    # On part du principe qu'on calcule la correspondance d'indices à l'étape 0
    # puis on appliquera la même correspondance aux autres étapes.
    reference_step = 0
    if reference_step not in occlusion_data:
        if debug:
            print(f"[ERREUR] Aucune donnée d'occlusion pour l'étape {reference_step}.")
        return

    occlusionDataRef = occlusion_data[reference_step]
    if debug:
        print(f"[INFO] Chargement des données d'occlusion pour l'étape {reference_step} : {list(occlusionDataRef.keys())}")

    # Dictionnaire pour stocker le mapping des indices pour chaque dent
    # { tooth_name: [old_index_for_vertex_0, old_index_for_vertex_1, ...] }
    tooth_index_mapping = {}

    # Construction du KDTree et du mapping pour l'étape 0
    for tooth_name in list(occlusionDataRef.keys()):
        if debug:
            print(f"\n--- Calcul du mapping pour la dent : {tooth_name} à l'étape 0 ---")

        if tooth_name not in original_positions or not original_positions[tooth_name]:
            if debug:
                print(f"[AVERTISSEMENT] Pas de positions originales trouvées pour {tooth_name}. Ignoré pour le mapping.")
            continue

        original_verts = original_positions[tooth_name]
        if len(original_verts) == 0:
            if debug:
                print(f"[AVERTISSEMENT] Pas de vertices originaux pour {tooth_name}. Ignoré pour le mapping.")
            continue

        if debug:
            print(f"[INFO] Nombre de vertices originaux pour {tooth_name} : {len(original_verts)}")

        kd = KDTree(len(original_verts))
        for i, pos in enumerate(original_verts):
            kd.insert(pos, i)
        kd.balance()
        if debug:
            print("[INFO] KDTree construit et équilibré pour l'étape 0.")

        obj_name = f"{tooth_name}_{reference_step}"
        obj = bpy.data.objects.get(obj_name)
        if not obj or obj.type != 'MESH':
            if debug:
                print(f"[ERREUR] Objet {obj_name} non trouvé ou non valide. Ignoré pour le mapping.")
            continue

        new_verts = [obj.matrix_world @ v.co for v in obj.data.vertices]

        old_colors = occlusionDataRef[tooth_name]
        if debug:
            print(f"[INFO] Nombre de nouveaux vertices pour {tooth_name} : {len(new_verts)}")
            print(f"[INFO] Nombre de couleurs anciennes : {len(old_colors)}")

        # Ajustement des couleurs si la taille ne correspond pas
        if len(old_colors) < len(new_verts):
            if debug:
                print(f"[INFO] Augmentation du nombre de couleurs anciennes de {len(old_colors)} à {len(new_verts)}.")
            old_colors.extend([[1, 1, 1]] * (len(new_verts) - len(old_colors)))
        elif len(old_colors) > len(new_verts):
            if debug:
                print(f"[INFO] Réduction du nombre de couleurs anciennes de {len(old_colors)} à {len(new_verts)}.")
            old_colors = old_colors[:len(new_verts)]

        # On va créer une liste qui donne, pour chaque nouveau vertex, l'index de l'ancien vertex le plus proche
        index_mapping = []
        reordered_colors = []
        for idx, nv in enumerate(new_verts):
            result = kd.find(nv)
            if result is None:
                if debug:
                    print(f"[AVERTISSEMENT] Aucun vertex proche trouvé pour le vertex {idx}. Couleur par défaut.")
                reordered_colors.append([1, 1, 1])
                # On met -1 pour signaler qu'on a pas trouvé de mapping
                index_mapping.append(-1)
            else:
                if len(result) == 3:
                    co, nearest_index, dist = result
                    reordered_colors.append(old_colors[nearest_index])
                    index_mapping.append(nearest_index)
                else:
                    if debug:
                        print(f"[ERREUR] Résultat inattendu pour le vertex {idx} dans KDTree. Couleur par défaut.")
                    reordered_colors.append([1, 1, 1])
                    index_mapping.append(-1)

        occlusionDataRef[tooth_name] = reordered_colors
        # On stocke la correspondance d'indices pour cette dent
        tooth_index_mapping[tooth_name] = index_mapping

    # Maintenant, on applique le même remapping à toutes les autres étapes
    # en utilisant tooth_index_mapping.
    for step in all_steps:
        if step == reference_step:
            continue  # Déjà traité
        if debug:
            print(f"\n--- Application du mapping à l'étape {step} ---")

        occlusionDataStep = occlusion_data[step]

        for tooth_name, index_mapping in tooth_index_mapping.items():
            if tooth_name not in occlusionDataStep:
                if debug:
                    print(f"[AVERTISSEMENT] Pas de données pour {tooth_name} à l'étape {step}. Ignoré.")
                continue
            step_old_colors = occlusionDataStep[tooth_name]

            # Ajustement de la taille des couleurs
            if len(step_old_colors) < len(index_mapping):
                step_old_colors.extend([[1,1,1]] * (len(index_mapping) - len(step_old_colors)))
            elif len(step_old_colors) > len(index_mapping):
                step_old_colors = step_old_colors[:len(index_mapping)]

            # Réorganisation des couleurs selon le même index_mapping
            reordered_colors = []
            for new_idx, old_idx in enumerate(index_mapping):
                if old_idx == -1:
                    # Pas de correspondance trouvée à l'étape 0, on met la couleur par défaut
                    reordered_colors.append([1,1,1])
                else:
                    reordered_colors.append(step_old_colors[old_idx])

            occlusionDataStep[tooth_name] = reordered_colors
            if debug:
                print(f"[INFO] Mise à jour des couleurs réordonnées pour {tooth_name} à l'étape {step}.")

    if debug:
        print("\n--- Fin du remapping ---")


def store_blender_data_in_scene(blender_data):
    """
    Mettre 'blender_data' dans les propriétés de la scène
    afin que l'export glTF l'intègre dans scene["extras"].
    """
    # Réduction de la précision des données
    optimized_data = reduce_precision(blender_data)
    
    # Convertir en JSON compact
    scene = bpy.context.scene
    scene["blender_data_json"] = json.dumps(optimized_data, separators=(',', ':'))


def reduce_precision(data, precision=3):
    """
    Réduit la précision des nombres dans une structure de données imbriquée.
    """
    if isinstance(data, float):
        return round(data, precision)
    elif isinstance(data, list):
        return [reduce_precision(item, precision) for item in data]
    elif isinstance(data, dict):
        return {key: reduce_precision(value, precision) for key, value in data.items()}
    else:
        return data
    
def export_blender_data(blender_data, export_directory, blender_data_file):
    data = reduce_precision(blender_data, 3)
    
    # # Convertir les données en MessagePack
    # packed_data = msgpack.packb(data, use_bin_type=True)
    
    packed_data = msgpack.packb(data, use_bin_type=True)
    
    # Compresser avec zlib
    compressed_data = zlib.compress(packed_data, level=9)  # level=9 => compression maximale
    
    # Nom de fichier de sortie (avec extension personnalisée)
    output_path = os.path.join(export_directory, blender_data_file)  
    
    # Écriture binaire du fichier compressé
    with open(output_path, "wb") as f:
        f.write(compressed_data)
    
    print(f"Données compressées sauvegardées : {output_path}")


def allInOneGLB(optimized_directory, export_directory, blender_data_file):
    """
    1) Nettoyer la scène
    2) Charger / renommer / decimate
    3) (Facultatif) Calcul occlusion
    4) Calculer la sectorisation => sur Tooth_XX_{last_step}, sans scale local
    5) Stocker positions d'origine (avant compression) pour gencive + dents
    6) Export en GLB Draco
    7) Purge la scène, réimport
    8) Remapping => occlusion, gencive, dents
    9) Sauvegarder blender_data (msgpack)
    """
    import bpy, os, json
    glb_path= os.path.join(export_directory, "mouth.glb")
    
    debug = True
    
    # with open (os.path.join(export_directory, "temp_data.json"),'w') as f:
    #     print(f)
    
    
    # 1) Nettoyer la scène
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # 2) Charger les OBJ + rename
    etape_finale, list_fichiers_a_supprimer, list_fichiers_non_lowpolisables = load_and_rename_objects(
        optimized_directory, detail_levels
    )
    # (Facultatif) create_lowpoly_tooth_copies(...) si vous voulez, 
    # mais la sectorisation n'en dépend plus.
    create_lowpoly_tooth_copies(
        0.01 / detail_levels["Tooth"][0],
        list_fichiers_non_lowpolisables,
        list_fichiers_a_supprimer,
        etape_finale
    )
    apply_smooth_shading_to_all_objects()

    # On regroupe les noms d'objets à supprimer
    objs_to_remove = set(o.name for o in list_fichiers_a_supprimer)

    # 3) Prépare le dict final
    blender_data = {}
    temp_data_path=os.path.join(export_directory, "temp_data.json")
    
    # 4) (Facultatif) Calculer l'occlusion 
    blender_data["OcclusionData"] = calculate_occlusion_via_temp_data(temp_data_path=temp_data_path)
    # blender_data["OcclusionData"] = calculate_occlusion_using_step0_clones(etape_finale=etape_finale)
    # blender_data["OcclusionData"] = calculate_vertex_colors_for_teeth(etape_finale=etape_finale)
    
    original_positions = store_original_positions()

    # 5) Calculer la sectorisation 
    #    => Sur Tooth_XX_{last_step}, sans scale local
    # generate_jaw_sectorisation_using_clones(blender_data, temp_data_path=temp_data_path, debug=debug)
    generate_jaw_sectorisation_using_clones_parallel(blender_data, temp_data_path=temp_data_path, debug=debug)
    
    # add_neighbour_weights_to_sectorization(blender_data, debug=True)
    # assign_gum_vertices_to_closest_tooth(blender_data, debug=True)

    # 6) Stocker positions d'origine (avant compression) => gencive
    original_jaw_positions = store_original_jaw_positions()  # { "Maxilla_0": [...], "Mandible_0": [...] }

    #    Stocker positions d'origine (avant compression) => dents
    #    => On cible "Tooth_XX_{last_step}"
    # original_teeth_positions = store_original_teeth_positions_for_sectorisation(etape_finale, debug=debug)

    # 7) Export en GLB (Draco)
    glb_path = os.path.join(export_directory, "mouth.glb")
    print(f"[INFO] Export en GLB => {glb_path}")

    # Supprimer les objets inutiles
    for obj in bpy.data.objects:
        if obj.name in objs_to_remove:
            bpy.data.objects.remove(obj, do_unlink=True)

    # Exporter
    export_all_to_glb(glb_path, with_blender_data=False, compression_level=10)

    if not os.path.exists(glb_path):
        raise FileNotFoundError(f"Le fichier GLB n'a pas été créé : {glb_path}")
    print("[OK] GLB exporté (Draco) avec succès.")

    # 8) Purger la scène, réimporter
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    bpy.ops.import_scene.gltf(filepath=glb_path)
    print("[INFO] GLB final Draco importé.")

    # 9) Remap => occlusion
    remap_occlusion_data_according_to_positions(blender_data, original_positions=original_positions, debug=debug)
    #   => Si vous avez stocké "original_positions" = store_original_positions()
    #      ou si vous l'appelez autrement. Mettez la bonne variable.

    # 9bis) Remap => gencive
    remap_jaw_sectorisation(blender_data, original_jaw_positions, debug=debug)

    # 9ter) Remap => dents
    remap_teeth_in_sectorisation(blender_data, original_positions, debug=debug)
    
    # remap_neighbour_weights_after_compression(blender_data, original_positions, debug=True)
    
    export_blender_data(blender_data, export_directory, blender_data_file)


def assign_gum_vertices_to_closest_tooth(blender_data, debug=True):
    """
    Assigne chaque vertex de la gencive à la dent la plus proche en termes de topologie et de centroïde.
    
    Si un vertex est plus proche d'une autre dent, il est supprimé de l'indexMap de la dent actuelle
    et assigné à la dent voisine.
    
    Cette version intègre des seuils de distance pour éviter les influences indésirables des dents voisines.
    
    Paramètres:
    - blender_data: dictionnaire contenant 'jawSectorisation' et autres données.
    - debug: booléen, si True, affiche des informations de débogage.
    """
    import bpy
    from mathutils import Vector
    from mathutils.kdtree import KDTree

    if "jawSectorisation" not in blender_data:
        if debug:
            print("[ERREUR] Pas de 'jawSectorisation' dans blender_data.")
        return

    jaw_sector = blender_data["jawSectorisation"]

    # Collecte des positions des centroïdes
    tooth_centroids = {}     # Mapping de tooth_num_str à Vector (centroïde)
    tooth_objects = {}       # Mapping de tooth_num_str à objet

    if debug:
        print("[DEBUG] Démarrage de assign_gum_vertices_to_closest_tooth")

    for tooth_num_str in jaw_sector.keys():
        obj_name = f"Tooth_{tooth_num_str}_0"
        tooth_obj = bpy.data.objects.get(obj_name)
        if not tooth_obj or tooth_obj.type != 'MESH':
            if debug:
                print(f"[WARN] Objet '{obj_name}' introuvable ou non-MESH pour tooth_num_str='{tooth_num_str}'.")
            continue

        num_vertices = len(tooth_obj.data.vertices)
        if num_vertices == 0:
            if debug:
                print(f"[WARN] Objet '{obj_name}' n'a aucun vertex.")
            continue

        # Calcul du centroïde
        total = Vector((0, 0, 0))
        for v in tooth_obj.data.vertices:
            world_pos = tooth_obj.matrix_world @ v.co
            total += world_pos
        centroid = total / num_vertices
        tooth_centroids[tooth_num_str] = centroid
        tooth_objects[tooth_num_str] = tooth_obj

        if debug:
            print(f"[DEBUG] Objet '{obj_name}' trouvé avec {num_vertices} vertices. Centroïde: {centroid}")

    if not tooth_centroids:
        if debug:
            print("[ERREUR] Aucun centroïde de dent trouvé.")
        return

    if debug:
        print(f"[INFO] Calcul des centroïdes pour {len(tooth_centroids)} dents.")

    # Préparer un KDTree pour les centroïdes
    centroid_list = list(tooth_centroids.values())
    centroid_keys = list(tooth_centroids.keys())
    kd_centroids = KDTree(len(centroid_list))
    for i, pos in enumerate(centroid_list):
        kd_centroids.insert(pos, i)
    kd_centroids.balance()

    if debug:
        print("[INFO] KDTree construit pour les centroïdes des dents.")

    # Paramètres pour la normalisation des distances au centroïde
    max_distance_centroid = 100.0  # Ajustez ce seuil en fonction de votre modèle
    influence_threshold = 50.0      # Seuil de distance pour l'influence des dents voisines

    # Parcourir chaque dent et ses vertices de gencive
    for tooth_num_str, sector_data in jaw_sector.items():
        index_map = sector_data.get("indexMap", {})
        vertices_to_remove = {}
        vertices_to_assign = {}

        num_jaw_vertices = len(index_map)
        if debug:
            print(f"[DEBUG] Traitement de la dent numéro '{tooth_num_str}' avec {num_jaw_vertices} vertices de gencive.")

        for jaw_vert_idx, info in list(index_map.items()):
            # Position du vertex de la gencive
            vertex_coords = info.get("vertex", [0, 0, 0])
            jaw_pos = Vector(vertex_coords)

            # Trouver la dent la plus proche via les centroïdes
            hits = kd_centroids.find_n(jaw_pos, 1)
            if len(hits) < 1:
                if debug:
                    print(f"[WARN] Aucun centroïde trouvé pour le vertex {jaw_vert_idx}.")
                continue

            closest_centroid_idx = hits[0][1]
            closest_tooth_num_str = centroid_keys[closest_centroid_idx]
            closest_centroid_pos = centroid_list[closest_centroid_idx]
            distance_to_centroid = (jaw_pos - closest_centroid_pos).length

            # Comparer avec la dent actuelle
            current_centroid_pos = tooth_centroids.get(tooth_num_str)
            if not current_centroid_pos:
                if debug:
                    print(f"[WARN] Aucun centroïde trouvé pour la dent '{tooth_num_str}'.")
                continue
            distance_current = (jaw_pos - current_centroid_pos).length

            # Vérifier le seuil d'influence pour éviter les attributions incorrectes
            if closest_tooth_num_str != tooth_num_str and distance_to_centroid < influence_threshold:
                # Vertex est plus proche d'une autre dent et dans le seuil d'influence
                vertices_to_remove[jaw_vert_idx] = tooth_num_str
                if closest_tooth_num_str not in vertices_to_assign:
                    vertices_to_assign[closest_tooth_num_str] = {}
                vertices_to_assign[closest_tooth_num_str][jaw_vert_idx] = info
                if debug:
                    print(f"[INFO] Jaw vertex {jaw_vert_idx} assigné à la dent '{closest_tooth_num_str}' "
                          f"au lieu de '{tooth_num_str}' (distance_centroid={distance_to_centroid:.3f} vs "
                          f"{distance_current:.3f}).")

        # Supprimer les vertices assignés à d'autres dents
        for vert_idx, from_tooth in vertices_to_remove.items():
            del jaw_sector[from_tooth]["indexMap"][vert_idx]
            if debug:
                print(f"[INFO] Jaw vertex {vert_idx} supprimé de la dent '{from_tooth}'.")

        # Assigner les vertices à la dent la plus proche
        for assign_tooth_num_str, verts in vertices_to_assign.items():
            assign_sector_data = jaw_sector.get(assign_tooth_num_str)
            if not assign_sector_data:
                if debug:
                    print(f"[WARN] Secteurisation inexistante pour la dent '{assign_tooth_num_str}'.")
                continue
            assign_index_map = assign_sector_data.get("indexMap", {})
            for jaw_vert_idx, info in verts.items():
                assign_index_map[jaw_vert_idx] = info
                if debug:
                    print(f"[INFO] Jaw vertex {jaw_vert_idx} assigné à la dent '{assign_tooth_num_str}'.")

    if debug:
        print("[INFO] Assignation des vertices de la gencive complétée.")


# NON FONCTIONNEL
def add_neighbour_weights_to_sectorization(blender_data, debug=True, num_top_neighbors=3):
    """
    Ajoute 'closestToothDataNeighbourWeight' à chaque vertex dans 'jawSectorisation'.

    Cette version calcule les poids en considérant la distance au centroid de la dent actuelle
    et aux centroides des dents voisines les plus proches, avec une normalisation pour permettre
    une répartition complète des poids de 0 à 1.

    Paramètres:
    - blender_data: dictionnaire contenant 'jawSectorisation' et autres données.
    - debug: booléen, si True, affiche des informations de débogage.
    - num_top_neighbors: nombre de dents voisines les plus proches à considérer pour le calcul des poids.
    """
    import bpy
    from mathutils import Vector
    from collections import defaultdict
    import math

    if "jawSectorisation" not in blender_data:
        if debug:
            print("[ERREUR] Pas de 'jawSectorisation' dans blender_data.")
        return

    jaw_sector = blender_data["jawSectorisation"]

    # Calculer les centroides
    tooth_centroids = calculate_centroids(blender_data, debug=debug)
    if not tooth_centroids:
        if debug:
            print("[ERREUR] Aucun centroid trouvé.")
        return

    # Identifier les dents voisines en utilisant les indices de vertices partagés
    tooth_vertex_indices = {}
    for tooth_num_str, sector_data in jaw_sector.items():
        obj_name = f"Tooth_{tooth_num_str}_0"
        tooth_obj = bpy.data.objects.get(obj_name)
        if not tooth_obj or tooth_obj.type != 'MESH':
            continue
        vertex_indices = set(v.index for v in tooth_obj.data.vertices)
        tooth_vertex_indices[tooth_num_str] = vertex_indices

    tooth_neighbors = defaultdict(set)
    tooth_nums = list(tooth_vertex_indices.keys())
    for i in range(len(tooth_nums)):
        for j in range(i + 1, len(tooth_nums)):
            tooth_a = tooth_nums[i]
            tooth_b = tooth_nums[j]
            shared_vertices = tooth_vertex_indices[tooth_a].intersection(tooth_vertex_indices[tooth_b])
            if len(shared_vertices) > 0:
                tooth_neighbors[tooth_a].add(tooth_b)
                tooth_neighbors[tooth_b].add(tooth_a)
                if debug:
                    print(f"[DEBUG] Dents '{tooth_a}' et '{tooth_b}' sont voisines avec {len(shared_vertices)} vertices partagés.")

    # Définir une distance maximale pour la normalisation
    # Vous pouvez ajuster cette valeur en fonction de l'échelle de votre modèle
    max_distance_own = 10.0
    max_distance_neighbor = 10.0

    # Pour chaque vertex de la gencive, calculer les poids
    for tooth_num_str, sector_data in jaw_sector.items():
        index_map = sector_data.get("indexMap", {})
        num_jaw_vertices = len(index_map)
        if debug:
            print(f"[DEBUG] Traitement de la dent numéro '{tooth_num_str}' avec {num_jaw_vertices} vertices de gencive.")

        own_centroid = tooth_centroids[tooth_num_str]
        neighbors = tooth_neighbors[tooth_num_str]

        for jaw_vert_idx, info in index_map.items():
            # Récupération de la position du vertex de la gencive en coordonnées mondiales
            vertex_coords = info.get("vertex", [0, 0, 0])
            try:
                jaw_pos = Vector(vertex_coords)
            except Exception as e:
                if debug:
                    print(f"[ERROR] Impossible de créer Vector pour vertex {jaw_vert_idx} avec coords {vertex_coords}: {e}")
                continue

            # Calcul de la distance à la dent actuelle
            distance_own = (jaw_pos - own_centroid).length

            # Calcul des distances aux dents voisines
            distances_neighbors = []
            for neighbor in neighbors:
                neighbor_centroid = tooth_centroids[neighbor]
                distance = (jaw_pos - neighbor_centroid).length
                distances_neighbors.append(distance)

            if distances_neighbors:
                # Considérer les n dents voisines les plus proches
                sorted_distances = sorted(distances_neighbors)
                top_distances = sorted_distances[:num_top_neighbors]
                # Moyenne des distances des top voisins
                avg_distance_neighbor = sum(top_distances) / len(top_distances)
            else:
                avg_distance_neighbor = float('inf')  # Pas de voisins

            # Normaliser les distances
            normalized_distance_own = min(distance_own / max_distance_own, 1.0)
            normalized_distance_neighbor = min(avg_distance_neighbor / max_distance_neighbor, 1.0)

            # Calcul du poids
            # Plus la distance à la dent actuelle est petite, plus le poids est élevé
            # Plus la distance aux dents voisines est grande, plus le poids est élevé
            weight_own = 1.0 - normalized_distance_own
            weight_neighbor = normalized_distance_neighbor

            # Combiner les poids
            # Vous pouvez ajuster les coefficients selon vos besoins
            weight = (weight_own + weight_neighbor) / 2.0

            # Clamper le poids entre 0 et 1
            weight = max(0.0, min(weight, 1.0))

            # Assigner le poids
            info["closestToothDataNeighbourWeight"] = weight

            if debug and (weight > 0.9 or weight < 0.1):
                print(f"[INFO] Jaw vertex {jaw_vert_idx}: distance_own={distance_own:.3f}, "
                      f"avg_distance_neighbor={avg_distance_neighbor:.3f}, "
                      f"normalized_distance_own={normalized_distance_own:.3f}, "
                      f"normalized_distance_neighbor={normalized_distance_neighbor:.3f}, "
                      f"weight_own={weight_own:.3f}, weight_neighbor={weight_neighbor:.3f}, "
                      f"weight={weight:.3f}")

    if debug:
        print("[INFO] 'closestToothDataNeighbourWeight' ajouté à 'jawSectorisation'.")


def remap_neighbour_weights_after_compression(blender_data, original_positions, debug=True):
    """
    Remappe 'closestToothDataNeighbourWeight' dans 'jawSectorisation' après compression.
    
    Cette fonction doit être appelée après 'remap_teeth_in_sectorisation' pour mettre à jour les poids
    basés sur les nouvelles positions.
    
    Elle recalcul les poids en fonction des nouvelles positions des dents et des vertices de la gencive.
    
    Paramètres:
    - blender_data: dictionnaire contenant 'jawSectorisation' et autres données.
    - original_positions: dictionnaire contenant les positions originales des vertices des dents avant compression.
    - debug: booléen, si True, affiche des informations de débogage.
    """
    import bpy
    from mathutils import Vector
    from mathutils.kdtree import KDTree

    if "jawSectorisation" not in blender_data:
        if debug:
            print("[ERREUR] Pas de 'jawSectorisation' dans blender_data.")
        return

    jaw_sector = blender_data["jawSectorisation"]

    # Collecte des positions originales des dents et calcul des centroïdes
    tooth_centroids = {}     # Mapping de tooth_num_str à Vector (centroïde)
    tooth_vertices = []      # Liste de Vector pour les vertices

    if debug:
        print("[DEBUG] Démarrage de remap_neighbour_weights_after_compression")

    for tooth_key, old_positions in original_positions.items():
        # tooth_key ex: "Tooth_11_0" ou "Tooth_11"
        parts = tooth_key.split("_")  # ["Tooth", "11", "0"] ou ["Tooth", "11"]
        if len(parts) < 2 or not parts[1].isdigit():
            if debug:
                print(f"[WARN] Nom de dent invalide dans original_positions: '{tooth_key}'.")
            continue
        tooth_num_str = parts[1]  # "11"

        # Récupérer l'objet compressé post-Draco
        # Supposer que l'étape est 0 si non spécifiée
        if len(parts) == 3 and parts[2].isdigit():
            step_reference = parts[2]
            obj_name = f"Tooth_{tooth_num_str}_{step_reference}"
        else:
            # Si l'étape n'est pas spécifiée, supposer 0
            step_reference = '0'
            obj_name = f"Tooth_{tooth_num_str}_0"

        tooth_obj = bpy.data.objects.get(obj_name)
        if not tooth_obj or tooth_obj.type != 'MESH':
            if debug:
                print(f"[WARN] Objet '{obj_name}' introuvable ou non-MESH pour tooth_key='{tooth_key}'.")
            continue

        # Collecte des positions des vertices en coordonnées mondiales après compression
        num_vertices = len(tooth_obj.data.vertices)
        if num_vertices == 0:
            if debug:
                print(f"[WARN] Objet '{obj_name}' n'a aucun vertex après compression.")
            continue

        # Calcul du centroïde après compression
        total = Vector((0, 0, 0))
        for v in tooth_obj.data.vertices:
            world_pos = tooth_obj.matrix_world @ v.co
            tooth_vertices.append(world_pos)
            total += world_pos
        centroid = total / num_vertices if num_vertices > 0 else Vector((0, 0, 0))
        tooth_centroids[tooth_num_str] = centroid

        if debug:
            print(f"[DEBUG] Objet '{obj_name}' trouvé avec {num_vertices} vertices après compression. Centroïde: {centroid}")

    if not tooth_vertices:
        if debug:
            print("[ERREUR] Aucun sommet de dent trouvé après compression.")
        return

    if debug:
        print(f"[INFO] Collecté {len(tooth_vertices)} sommets de dents après compression.")
        print(f"[INFO] Calcul des centroïdes pour {len(tooth_centroids)} dents.")

    # Préparer un KDTree pour les vertices des dents
    kd_vertices = KDTree(len(tooth_vertices))
    for i, pos in enumerate(tooth_vertices):
        kd_vertices.insert(pos, i)
    kd_vertices.balance()

    if debug:
        print("[INFO] KDTree construit pour les sommets des dents après compression.")

    # Préparer un dictionnaire des centroïdes
    tooth_centroid_list = list(tooth_centroids.values())
    tooth_centroid_keys = list(tooth_centroids.keys())
    kd_centroids = KDTree(len(tooth_centroid_list))
    for i, pos in enumerate(tooth_centroid_list):
        kd_centroids.insert(pos, i)
    kd_centroids.balance()

    if debug:
        print("[INFO] KDTree construit pour les centroïdes des dents après compression.")

    # Paramètres pour la normalisation des distances au centroïde
    max_distance_centroid = 100.0  # Ajustez ce seuil en fonction de votre modèle

    # Pour chaque vertex de la gencive, calculer les poids
    for tooth_num_str, sector_data in jaw_sector.items():
        index_map = sector_data.get("indexMap", {})
        num_jaw_vertices = len(index_map)
        if debug:
            print(f"[DEBUG] Remappage des poids pour la dent numéro '{tooth_num_str}' avec {num_jaw_vertices} vertices de gencive.")

        for jaw_vert_idx, info in index_map.items():
            # Récupération de la position du vertex de la gencive
            vertex_coords = info.get("vertex", [0, 0, 0])
            jaw_pos = Vector(vertex_coords)

            # Trouver les deux plus proches vertices de dents
            hits_vertices = kd_vertices.find_n(jaw_pos, 2)
            if len(hits_vertices) < 2:
                if debug:
                    print(f"[WARN] Moins de deux voisins trouvés pour le vertex {jaw_vert_idx}.")
                weight = 1.0
                d1 = d2 = 0.0
            else:
                d1 = hits_vertices[0][2]  # Distance au plus proche
                d2 = hits_vertices[1][2]  # Distance au deuxième plus proche

                # Trouver la dent la plus proche via les centroïdes
                hits_centroids = kd_centroids.find_n(jaw_pos, 1)
                if len(hits_centroids) < 1:
                    if debug:
                        print(f"[WARN] Aucun centroïde trouvé pour le vertex {jaw_vert_idx}.")
                    weight_centroid = 1.0
                else:
                    d_centroid = (jaw_pos - tooth_centroid_list[hits_centroids[0][1]]).length
                    # Normaliser la distance au centroïde
                    weight_centroid = max(0.0, min(1.0, 1 - (d_centroid / max_distance_centroid)))

                # Calcul du poids basé sur la distance des vertices
                if d1 + d2 == 0:
                    weight_distance = 1.0
                else:
                    weight_distance = d2 / (d1 + d2)
                    weight_distance = max(0.0, min(weight_distance, 1.0))

                # Calcul du poids final comme moyenne des deux poids
                weight = (weight_distance + weight_centroid) / 2
                weight = max(0.0, min(weight, 1.0))

            # Assignation du poids
            info["closestToothDataNeighbourWeight"] = weight

            if debug:
                print(f"[INFO] Jaw vertex {jaw_vert_idx}: d1={d1:.3f}, d2={d2:.3f}, "
                      f"d_centroid={d_centroid:.3f}, weight_distance={weight_distance:.3f}, "
                      f"weight_centroid={weight_centroid:.3f}, weight={weight:.3f}")

    if debug:
        print("[INFO] 'closestToothDataNeighbourWeight' remappé à 'jawSectorisation' après compression.")


def remap_teeth_in_sectorisation(blender_data, original_teeth_positions, debug=True):
    """
    Remappe, pour chaque dent *référencée par tooth_number*, 
    le champ meshIndex dans blender_data["jawSectorisation"][tooth_number]["indexMap"].

    On s'appuie sur l'étape 0 comme référence :
     - original_teeth_positions["Tooth_11"] = liste de positions AVANT compression (étape 0).
     - l'objet compressé post-Draco => "Tooth_11_0".

    On reconstruit un mapping : new_index -> old_index, 
    puis on applique ce mapping pour chaque "tooth_number" 
    dans la sectorisation.

    La structure de sectorisation est supposée être:
      blender_data["jawSectorisation"][tooth_number]["indexMap"][jaw_vert_idx]["meshIndex"] = old_idx
    qu'on veut re-mapper vers le nouveau "meshIndex".
    """
    import bpy
    from mathutils.kdtree import KDTree

    if "jawSectorisation" not in blender_data:
        if debug:
            print("[ERREUR] Pas de 'jawSectorisation' dans blender_data.")
        return
    
    jaw_sector = blender_data["jawSectorisation"]

    # Dictionnaire global : { "Tooth_11": [correspondance], ... }
    # correspondance => index_mapping[new_idx] = old_idx OU l'inverse
    # Mais EXACTEMENT comme occlusion_data, on part du principe 
    # qu'on calcule pour l'étape 0 => on fait un KDTree 
    # "nouveaux" vs "anciens" ?
    # Dans occlusion_data, on fait un kd "old" -> "new" pour reorder. 
    # Ici, on a original_teeth_positions = [old_pos], on doit find(nv)...

    # On va faire comme occlusion_data : 
    # KD = insertion des old_pos => find(new_pos)
    # => index_mapping[new_idx] = old_idx
    # => puis reorder le meshIndex.

    tooth_index_mapping = {}  # { tooth_name: index_mapping (taille = nb vertices post-compression) }

    for tooth_key, old_positions in original_teeth_positions.items():
        # tooth_key ex: "Tooth_11"
        # => l'objet blender s'appelle "Tooth_11_0"
        parts = tooth_key.split("_")  # ["Tooth","11"]
        if len(parts) != 2 or not parts[1].isdigit():
            if debug:
                print(f"[WARN] Nom de dent invalide : {tooth_key}")
            continue
        step_reference = 0
        obj_name = f"{tooth_key}_{step_reference}"  # ex: "Tooth_11_0"

        obj = bpy.data.objects.get(obj_name)
        if not obj or obj.type != 'MESH':
            if debug:
                print(f"[ERREUR] Objet {obj_name} introuvable post-compression Draco.")
            continue

        if debug:
            print(f"\n--- Construction du mapping pour {tooth_key} (étape 0) ---")

        # 1) KDTree = old_positions => kd.insert(old_pos, i)
        from mathutils.kdtree import KDTree
        kd = KDTree(len(old_positions))
        for i, old_pos in enumerate(old_positions):
            kd.insert(old_pos, i)
        kd.balance()
        if debug:
            print(f"[INFO] KDTree construit, {len(old_positions)} sommets insérés.")

        # 2) On parcourt les "nouveaux sommets" => new_verts = obj.matrix_world @ v.co
        new_verts = [obj.matrix_world @ v.co for v in obj.data.vertices]

        # On construit un index_mapping de la taille new_verts
        # index_mapping[new_idx] = old_idx
        index_mapping = [None]*len(new_verts)

        for new_idx, nv in enumerate(new_verts):
            hit = kd.find(nv)
            if hit is None:
                # pas trouvé
                index_mapping[new_idx] = -1
                if debug:
                    print(f"[WARN] new vertex {new_idx} pas trouvé (dent {tooth_key}).")
            else:
                if len(hit) == 3:
                    # co, old_i, dist
                    _, old_i, dist = hit
                    index_mapping[new_idx] = old_i
                else:
                    # Résultat inattendu
                    index_mapping[new_idx] = -1

        tooth_index_mapping[tooth_key] = index_mapping

    # 3) On applique ce index_mapping à la sectorisation
    #    On suppose qu'il N'Y A PAS de notion d'étape multiple 
    #    dans jawSectorisation => "Tooth_11" => {"indexMap": ...}
    #    (Si vous aviez "jawSectorisation[step][tooth_number]", adaptez)

    for tooth_number_str, sector_data in jaw_sector.items():
        # ex: tooth_number_str="11"
        # => on cherche tooth_key="Tooth_11"
        tooth_key = f"Tooth_{tooth_number_str}"
        if tooth_key not in tooth_index_mapping:
            if debug:
                print(f"[WARN] Pas de mapping pour la dent {tooth_key} (sectorisation).")
            continue
        index_mapping = tooth_index_mapping[tooth_key]

        indexMap = sector_data.get("indexMap", {})
        count_total = 0
        count_changed = 0
        for jaw_idx, info in indexMap.items():
            old_mesh_index = info.get("meshIndex", None)
            if old_mesh_index is None:
                continue
            count_total += 1
            if old_mesh_index < len(index_mapping):
                new_old_idx = index_mapping[old_mesh_index]
                # new_old_idx = -1 => pas trouvé
                if new_old_idx != -1 and new_old_idx != old_mesh_index:
                    info["meshIndex"] = new_old_idx
                    count_changed += 1
            else:
                # hors limites
                if debug:
                    print(f"[WARN] old_mesh_index {old_mesh_index} > len(index_mapping).")

        if debug:
            print(f"[INFO] Dent {tooth_number_str}: {count_changed}/{count_total} meshIndex remappés.")

    if debug:
        print("\n--- Fin du remapping des dents step=0 dans sectorisation ---")


def store_original_teeth_positions_for_sectorisation(last_step=None, debug=True):
    """
    Stocke les positions *avant compression* des dents 'Tooth_XX_{last_step}',
    c'est-à-dire la dent d'origine, non lowpoly.
    
    Retourne un dict: { "Tooth_11_5": [Vector(...), ...], ... }
    """
    import bpy
    from mathutils import Vector

    original_positions = {}
    for obj in bpy.data.objects:
        if obj.type != 'MESH':
            continue
        if not obj.name.startswith("Tooth_"):
            continue
        parts = obj.name.split("_")
        if len(parts) == 3 and parts[0] == "Tooth" and parts[2].isdigit():
            step_int = int(parts[2])
            if last_step is not None and step_int != last_step:
                continue
            # ex: "Tooth_11_5"
            obj_name = obj.name
            # On stocke en coords monde
            coords = [obj.matrix_world @ v.co for v in obj.data.vertices]
            original_positions[obj_name] = coords
            if debug:
                print(f"[store_original_teeth_positions_for_sectorisation] {obj_name}: {len(coords)} sommets stockés.")
    return original_positions


# Sans poids
def generate_jaw_sectorisation_using_clones(blender_data, 
                                            temp_data_path, 
                                            debug=True):
    """
    1) Charge transform_data = load_transformation_data(temp_data_path).
    2) Détermine la plus grande étape last_step = max des clés de transform_data.
    3) Récupère transform_data[last_step] = { "Tooth_14": matrix, "Tooth_11": matrix, ... }
       et construit un dictionnaire last_step_matrices["14"] = matrix, etc.
    4) Récupère toutes les dents de base "Tooth_XX_0", clone + applique matrix => geometry "dernière étape".
    5) Calcule la sectorisation (stacked spheres + top_center à +2.0 en local Y).
    6) Identifie la gencive (maxilla/mandible) => associe sommets => meshIndex.
    7) Stocke dans blender_data["jawSectorisation"][XX].
    8) Supprime le clone, passe à la dent suivante.
    """

    import bpy, math
    from mathutils import Vector, Matrix

    # Assure la clé
    if "jawSectorisation" not in blender_data:
        blender_data["jawSectorisation"] = {}

    # 1) Charger transform_data
    transform_data = load_transformation_data(temp_data_path)
    if debug:
        print("[DEBUG] Contenu de transform_data (depuis temp_data_path):")
        for st in sorted(transform_data.keys()):
            print(f"  Étape {st}:")
            for toothName, matVal in transform_data[st].items():
                print(f"    {toothName!r} => {matVal!r}")

    # 2) Déterminer la plus grande étape last_step
    if not transform_data:
        if debug:
            print("[WARN] transform_data est vide, aucune étape disponible.")
        return  # rien à faire

    last_step = max(transform_data.keys())  # ex: 5, 12, etc.
    if debug:
        print(f"[DEBUG] last_step déterminé = {last_step}")

    # 3) Construire last_step_matrices à partir de transform_data[last_step]
    last_step_matrices = {}
    step_data = transform_data[last_step]  # ex: { "Tooth_14": matrix, "Tooth_11": matrix, ... }
    for toothName, mat in step_data.items():
        # ex: "Tooth_14" => on veut extraire "14"
        raw_str = toothName.strip()
        # On gère "Tooth_14" ou "Tooth14"
        number_part = None
        if raw_str.startswith("Tooth_"):
            number_part = raw_str[len("Tooth_"):]
        elif raw_str.startswith("Tooth"):
            number_part = raw_str[len("Tooth"):]
        else:
            if debug:
                print(f"[WARN] last_step={last_step}, toothName={toothName!r} pas conforme => skip.")
            continue

        number_part = number_part.strip()
        if not number_part.isdigit():
            if debug:
                print(f"[WARN] last_step={last_step}, toothName={toothName!r}: '{number_part}' pas numérique => skip.")
            continue

        last_step_matrices[number_part] = mat

    if debug:
        print("[DEBUG] last_step_matrices construit :")
        for k,v in last_step_matrices.items():
            print(f"   '{k}' => {v!r}")

    # 4) Récupérer toutes les dents "Tooth_XX_0"
    base_teeth_0 = [
        obj for obj in bpy.data.objects
        if obj.type=='MESH'
        and obj.name.startswith("Tooth_")
        and obj.name.endswith("_0")
    ]
    # Construction d'un map "XX" => OBJ
    base_teeth_map = {}
    for obj in base_teeth_0:
        parts = obj.name.split("_")  # ex: ["Tooth","14","0"]
        if len(parts)==3 and parts[0]=="Tooth" and parts[2]=="0":
            tooth_num_str = parts[1]  # "14"
            base_teeth_map[tooth_num_str] = obj
        else:
            if debug:
                print(f"[WARN] dent base inattendue: '{obj.name}' => skip.")

    if debug:
        print("[DEBUG] base_teeth_map =>")
        for k,v in base_teeth_map.items():
            print(f"   {k} => {v.name}")

    # Récupérer la gencive => "Maxilla_{last_step}", "Mandible_{last_step}" (optionnel)
    maxilla_name = f"Maxilla_{last_step}"
    mandible_name = f"Mandible_{last_step}"
    maxilla_obj = bpy.data.objects.get(maxilla_name)
    mandible_obj = bpy.data.objects.get(mandible_name)
    if debug:
        print(f"[DEBUG] gencives => maxilla={maxilla_obj}, mandible={mandible_obj}")

    def get_jaw_object_for(num_str):
        arch = int(num_str[0])  # 1,2 => maxilla; 3,4 => mandible
        return maxilla_obj if arch in [1,2] else mandible_obj

    # Fonctions utilitaires
    # def compute_bounding_sphere(obj):
    #     me=obj.data
    #     coords=[v.co for v in me.vertices]
    #     if not coords:
    #         return Vector((0,0,0)),0.0
    #     minx=min(c.x for c in coords)
    #     maxx=max(c.x for c in coords)
    #     miny=min(c.y for c in coords)
    #     maxy=max(c.y for c in coords)
    #     minz=min(c.z for c in coords)
    #     maxz=max(c.z for c in coords)
    #     cx=(minx+maxx)*0.5
    #     cy=(miny+maxy)*0.5
    #     cz=(minz+maxz)*0.5
    #     center=Vector((cx,cy,cz))
    #     rx=(maxx-minx)*0.5
    #     ry=(maxy-miny)*0.5
    #     rz=(maxz-minz)*0.5
    #     radius=math.sqrt(rx*rx+ry*ry+rz*rz)
    #     return center,radius
    # Fonction utilitaire mise à jour
    def compute_bounding_sphere(obj):
        me = obj.data
        coords = [v.co for v in me.vertices]
        if not coords:
            return Vector((0, 0, 0)), 0.0

        # Calcul des limites uniquement sur les axes X et Y
        minx = min(c.x for c in coords)
        maxx = max(c.x for c in coords)
        miny = min(c.y for c in coords)
        maxy = max(c.y for c in coords)

        # Centre du cercle dans le plan XY
        cx = (minx + maxx) * 0.5
        cy = (miny + maxy) * 0.5
        cz = (min(c.z for c in coords) + max(c.z for c in coords)) * 0.5  # Hauteur inchangée

        center = Vector((cx, cy, cz))

        # Rayon basé uniquement sur les axes X et Y
        rx = (maxx - minx) * 0.5
        ry = (maxy - miny) * 0.5

        # Rayon final basé sur la plus grande extension en XY
        radius = math.sqrt(rx**2 + ry**2)
        
        return center, radius


    def get_nearest_vertex_data(gencive_vert, tooth_obj):
        me=tooth_obj.data
        mind=float('inf')
        best_idx=-1
        best_pos=None
        for i,v in enumerate(me.vertices):
            d=(v.co - gencive_vert).length
            if d<mind:
                mind=d
                best_idx=i
                best_pos=v.co
        if best_idx<0 or best_pos is None:
            return None
        direction=(gencive_vert - best_pos).normalized() if mind>1e-9 else Vector((0,0,1))
        return (best_idx,mind,direction,best_pos)

    def clone_object(obj, new_name):
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active=obj
        bpy.ops.object.duplicate(linked=False)
        c=bpy.context.active_object
        c.name=new_name
        c.select_set(False)
        return c

    # Paramètres pour la "stacked spheres"
    layer_count=5
    radius_factor_bottom=1.5
    radius_factor_top=1.5
    standard_elevation=40

    # On va remplir blender_data["jawSectorisation"]
    # => pour chaque dent XX trouvée dans base_teeth_map
    for tooth_num_str, base_obj_0 in base_teeth_map.items():
        # Chercher la matrix
        mat = last_step_matrices.get(tooth_num_str)
        if not mat:
            if debug:
                print(f"[WARN] pas de matrice last_step pour dent {tooth_num_str}, skip.")
            continue

        # Cloner
        clone = clone_object(base_obj_0, f"CLONE_{tooth_num_str}_tmp")
        clone.matrix_world = mat

        c_local, r_local = compute_bounding_sphere(clone)

        # Vérifie si la gencive associée est un maxillaire ou un mandibule
        jaw_obj = get_jaw_object_for(tooth_num_str)
        if not jaw_obj:
            if debug:
                print(f"[WARN] aucune gencive associée => skip {tooth_num_str}")
            bpy.data.objects.remove(clone, do_unlink=True)
            continue

        # Détermine la direction pour les sphères (haut ou bas)
        if jaw_obj.name.startswith("Maxilla"):  # Maxillaire
            top_center = Vector((c_local.x, c_local.y + standard_elevation, c_local.z))
        elif jaw_obj.name.startswith("Mandible"):  # Mandibule
            top_center = Vector((c_local.x, c_local.y - standard_elevation, c_local.z))
        else:
            if debug:
                print(f"[WARN] Type de gencive inconnu pour {jaw_obj.name}, skip {tooth_num_str}.")
            bpy.data.objects.remove(clone, do_unlink=True)
            continue

        # Calcul des rayons pour les sphères
        bas = r_local * radius_factor_bottom
        haut = bas * radius_factor_top
        # bas = 20
        # haut = 20

        # On crée layer_count sphères
        spheres = []
        for i in range(layer_count):
            frac = i / (layer_count - 1) if layer_count > 1 else 0
            ci = c_local.lerp(top_center, frac)
            ri = bas * (1 - frac) + haut * frac
            spheres.append((ci, ri))


        # jaw => maxilla or mandible
        jaw_obj = get_jaw_object_for(tooth_num_str)
        if not jaw_obj:
            if debug:
                print(f"[WARN] aucune gencive associée => skip {tooth_num_str}")
            bpy.data.objects.remove(clone, do_unlink=True)
            continue

        used_set=set()
        me_jaw=jaw_obj.data
        for idx_jaw,v_jaw in enumerate(me_jaw.vertices):
            jco=v_jaw.co
            inside=False
            for (cen,rad) in spheres:
                dist=(jco - cen).length
                if dist<=rad:
                    inside=True
                    break
            if inside:
                used_set.add(idx_jaw)

        indexMap={}
        for idx_jaw in used_set:
            gco=me_jaw.vertices[idx_jaw].co
            near_data=get_nearest_vertex_data(gco, clone)
            if near_data:
                (m_idx, dist_, inv_dir, pos_dent)=near_data
                indexMap[idx_jaw]={
                    "distance":dist_,
                    "vertex":[pos_dent.x,pos_dent.y,pos_dent.z],
                    "vector":[inv_dir.x,inv_dir.y,inv_dir.z],
                    "meshIndex":m_idx
                }

        vertexIndices=sorted(used_set)
        blender_data["jawSectorisation"][tooth_num_str]={
            "vertexIndices":vertexIndices,
            "indexMap":indexMap
        }

        if debug:
            print(f"[generate_jaw_sectorisation clones] Dent={tooth_num_str}, "
                  f"{len(vertexIndices)} sommets, stacked={layer_count}, "
                  f"rBas={bas:.3f}, rHaut={haut:.3f}, elev={standard_elevation}.")

        # Supprimer clone
        bpy.data.objects.remove(clone, do_unlink=True)

    if debug:
        print("[generate_jaw_sectorisation clones] Fini (clones depuis l'étape 0, matrices last_step).")
        
        
import concurrent.futures
import copy

def generate_jaw_sectorisation_using_clones_parallel(blender_data, 
                                                     temp_data_path, 
                                                     debug=True):
    """
    Variante parallèle de la fonction generate_jaw_sectorisation_using_clones.
    L'idée est de limiter l'accès direct à bpy.data ou aux ops Blender
    dans les parties parallélisées. Seules les données "pures" (listes 
    de coordonnées de vertex, matrices, etc.) sont manipulées en parallèle.
    """

    # -- 0) Vérification / initialisation du dictionnaire
    if "jawSectorisation" not in blender_data:
        blender_data["jawSectorisation"] = {}

    # -- 1) Charger la transformation
    transform_data = load_transformation_data(temp_data_path)
    if debug:
        print("[DEBUG] Contenu de transform_data (depuis temp_data_path):")
        for st in sorted(transform_data.keys()):
            print(f"  Étape {st}:")
            for toothName, matVal in transform_data[st].items():
                print(f"    {toothName!r} => {matVal!r}")

    if not transform_data:
        if debug:
            print("[WARN] transform_data est vide, aucune étape disponible.")
        return  # rien à faire

    # -- 2) Déterminer la plus grande étape
    last_step = max(transform_data.keys())
    if debug:
        print(f"[DEBUG] last_step déterminé = {last_step}")

    # -- 3) Construire last_step_matrices
    step_data = transform_data[last_step]
    last_step_matrices = {}
    for toothName, mat in step_data.items():
        raw_str = toothName.strip()
        if raw_str.startswith("Tooth_"):
            number_part = raw_str[len("Tooth_"):]
        elif raw_str.startswith("Tooth"):
            number_part = raw_str[len("Tooth"):]
        else:
            if debug:
                print(f"[WARN] last_step={last_step}, toothName={toothName!r} pas conforme => skip.")
            continue

        number_part = number_part.strip()
        if not number_part.isdigit():
            if debug:
                print(f"[WARN] last_step={last_step}, toothName={toothName!r}: '{number_part}' pas numérique => skip.")
            continue

        last_step_matrices[number_part] = mat

    if debug:
        print("[DEBUG] last_step_matrices construit :")
        for k, v in last_step_matrices.items():
            print(f"   '{k}' => {v!r}")

    # -- 4) Récupérer toutes les dents de base "Tooth_XX_0"
    base_teeth_0 = [
        obj for obj in bpy.data.objects
        if obj.type == 'MESH'
        and obj.name.startswith("Tooth_")
        and obj.name.endswith("_0")
    ]
    base_teeth_map = {}
    for obj in base_teeth_0:
        parts = obj.name.split("_")  # ex: ["Tooth","14","0"]
        if len(parts) == 3 and parts[0] == "Tooth" and parts[2] == "0":
            tooth_num_str = parts[1]
            base_teeth_map[tooth_num_str] = obj
        else:
            if debug:
                print(f"[WARN] dent base inattendue: '{obj.name}' => skip.")

    if debug:
        print("[DEBUG] base_teeth_map =>")
        for k, v in base_teeth_map.items():
            print(f"   {k} => {v.name}")

    # -- 5) Récupérer la gencive => "Maxilla_{last_step}", "Mandible_{last_step}" (optionnel)
    maxilla_name = f"Maxilla_{last_step}"
    mandible_name = f"Mandible_{last_step}"
    maxilla_obj = bpy.data.objects.get(maxilla_name)
    mandible_obj = bpy.data.objects.get(mandible_name)
    if debug:
        print(f"[DEBUG] gencives => maxilla={maxilla_obj}, mandible={mandible_obj}")

    def get_jaw_object_for(num_str):
        arch = int(num_str[0])  # 1,2 => maxilla; 3,4 => mandible
        return maxilla_obj if arch in [1, 2] else mandible_obj

    # -- Fonctions utilitaires "pures" (aucun accès direct à bpy.data/ops)

    def compute_bounding_sphere(coords):
        """
        Calcule la bounding sphere 2D (axes X, Y) + centre Z moyen.
        Paramètre : coords = liste de Vector (x, y, z)
        """
        if not coords:
            return Vector((0, 0, 0)), 0.0

        minx = min(c.x for c in coords)
        maxx = max(c.x for c in coords)
        miny = min(c.y for c in coords)
        maxy = max(c.y for c in coords)
        cz = (min(c.z for c in coords) + max(c.z for c in coords)) * 0.5

        cx = (minx + maxx) * 0.5
        cy = (miny + maxy) * 0.5
        center = Vector((cx, cy, cz))

        rx = (maxx - minx) * 0.5
        ry = (maxy - miny) * 0.5
        radius = math.sqrt(rx**2 + ry**2)

        return center, radius

    def get_nearest_vertex(coords_tooth, gencive_vert):
        """
        Recherche le vertex le plus proche d'un point gencive_vert 
        dans la liste coords_tooth (liste de Vector).
        Retourne (index, distance, direction, pos_dent).
        """
        best_idx = -1
        best_dist = float('inf')
        best_pos = None
        for i, tooth_v in enumerate(coords_tooth):
            d = (tooth_v - gencive_vert).length
            if d < best_dist:
                best_dist = d
                best_idx = i
                best_pos = tooth_v
        if best_idx < 0 or best_pos is None:
            return None
        direction = (gencive_vert - best_pos).normalized() if best_dist > 1e-9 else Vector((0, 0, 1))
        return (best_idx, best_dist, direction, best_pos)

    # -- 6) Préparation des données dentaires et gencives pour chaque dent
    #    On copie tout ce dont on a besoin en Python (pas d'accès direct BPY dans les threads).
    #    Pour la gencive, on stocke la liste de vertices, indexée pour y accéder rapidement.

    # Copie des coordonnées gencives (dans un dict { 'Maxilla': [...], 'Mandible': [...], ... })
    # Ici, on va simplement récupérer .data de l'objet maxilla/mandible, s'il existe.
    # On stocke la liste des vertices sous forme de Vector, + on garde un "object name" pour info.
    jaw_data = {}
    if maxilla_obj and maxilla_obj.data and maxilla_obj.type == 'MESH':
        jaw_data[maxilla_obj.name] = [v.co.copy() for v in maxilla_obj.data.vertices]

    if mandible_obj and mandible_obj.data and mandible_obj.type == 'MESH':
        jaw_data[mandible_obj.name] = [v.co.copy() for v in mandible_obj.data.vertices]

    # On prépare maintenant un "pack" de tâches = une liste (tooth_num_str, dataDent, dataGencive, ...)
    tasks = []
    standard_elevation = 40
    layer_count = 5
    radius_factor_bottom = 1.5
    radius_factor_top = 1.5

    for tooth_num_str, base_obj_0 in base_teeth_map.items():
        mat = last_step_matrices.get(tooth_num_str)
        if not mat:
            if debug:
                print(f"[WARN] pas de matrice last_step pour dent {tooth_num_str}, skip.")
            continue

        jaw_obj = get_jaw_object_for(tooth_num_str)
        if not jaw_obj:
            if debug:
                print(f"[WARN] aucune gencive associée => skip {tooth_num_str}")
            continue

        # On lit toutes les coordonnées de la dent "Tooth_XX_0", puis on appliquera la matrice 'mat'
        # On les stocke dans un tableau coords_dent
        coords_dent = []
        for v in base_obj_0.data.vertices:
            # Application de mat (Matrix) sur la coordonnée
            pt_world = mat @ v.co
            coords_dent.append(pt_world)

        # On identifie la liste de coords gencive correspondante
        jaw_coords = jaw_data.get(jaw_obj.name, None)
        if jaw_coords is None:
            if debug:
                print(f"[WARN] Gencive {jaw_obj.name} introuvable dans jaw_data => skip {tooth_num_str}")
            continue

        # On prépare la "tâche" de calcul
        task_data = {
            'tooth_num_str': tooth_num_str,
            'coords_dent': coords_dent,
            'jaw_obj_name': jaw_obj.name,
            'jaw_coords': jaw_coords,
            'standard_elevation': standard_elevation,
            'layer_count': layer_count,
            'radius_factor_bottom': radius_factor_bottom,
            'radius_factor_top': radius_factor_top
        }
        tasks.append(task_data)

    # -- 7) Définir la fonction qui effectue le traitement intensif pour une dent
    def process_tooth_sectorisation(task):
        """
        Calcule, pour une dent, la sectorisation des vertices gencive.
        Retourne (tooth_num_str, vertexIndices, indexMap).
        """
        tooth_num_str = task['tooth_num_str']
        coords_dent = task['coords_dent']
        jaw_coords = task['jaw_coords']
        jaw_name = task['jaw_obj_name']
        standard_elevation = task['standard_elevation']
        layer_count = task['layer_count']
        radius_factor_bottom = task['radius_factor_bottom']
        radius_factor_top = task['radius_factor_top']

        # Calcul de la bounding_sphere 2D
        c_local, r_local = compute_bounding_sphere(coords_dent)

        # Selon maxilla/mandible => on déplace en +Y ou -Y
        top_center = None
        if jaw_name.startswith("Maxilla"):
            top_center = Vector((c_local.x, c_local.y + standard_elevation, c_local.z))
        elif jaw_name.startswith("Mandible"):
            top_center = Vector((c_local.x, c_local.y - standard_elevation, c_local.z))
        else:
            # Cas inconnu
            return (tooth_num_str, [], {})

        bas = r_local * radius_factor_bottom
        haut = bas * radius_factor_top

        # Construction des sphères
        spheres = []
        for i in range(layer_count):
            frac = i / (layer_count - 1) if layer_count > 1 else 0
            ci = c_local.lerp(top_center, frac)
            ri = bas * (1 - frac) + haut * frac
            spheres.append((ci, ri))

        # Détection des sommets "inside"
        used_set = set()
        for idx_jaw, jco in enumerate(jaw_coords):
            inside = False
            for (cen, rad) in spheres:
                dist = (jco - cen).length
                if dist <= rad:
                    inside = True
                    break
            if inside:
                used_set.add(idx_jaw)

        # Mapping index => info
        indexMap = {}
        for idx_jaw in used_set:
            gco = jaw_coords[idx_jaw]
            near_data = get_nearest_vertex(coords_dent, gco)
            if near_data:
                (m_idx, dist_, inv_dir, pos_dent) = near_data
                indexMap[idx_jaw] = {
                    "distance": dist_,
                    "vertex": [pos_dent.x, pos_dent.y, pos_dent.z],
                    "vector": [inv_dir.x, inv_dir.y, inv_dir.z],
                    "meshIndex": m_idx
                }

        vertexIndices = sorted(used_set)
        return (tooth_num_str, vertexIndices, indexMap)

    # -- 8) Exécuter les tâches en parallèle
    results_map = {}  # stockage provisoire

    # Utilisation d'un ThreadPoolExecutor, on peut aussi tester ProcessPoolExecutor
    # (mais attention à la sérialisation des données !)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_task = {}
        for t in tasks:
            fut = executor.submit(process_tooth_sectorisation, t)
            future_to_task[fut] = t

        for fut in concurrent.futures.as_completed(future_to_task):
            tooth_num_str = future_to_task[fut]['tooth_num_str']
            try:
                (tnum, v_indices, i_map) = fut.result()
                results_map[tnum] = {
                    "vertexIndices": v_indices,
                    "indexMap": i_map
                }
            except Exception as ex:
                # Gestion d'erreur éventuelle
                if debug:
                    print(f"[ERREUR] lors du traitement de la dent {tooth_num_str} => {ex}")
                results_map[tooth_num_str] = {
                    "vertexIndices": [],
                    "indexMap": {}
                }

    # -- 9) Finaliser : tout est fait, on copie les résultats dans blender_data
    for tooth_num_str, data_sector in results_map.items():
        blender_data["jawSectorisation"][tooth_num_str] = data_sector

    if debug:
        print("[generate_jaw_sectorisation clones - PARALLEL] Terminé.")



def calculate_centroids(blender_data, debug=True):
    """
    Calcule les centroides de chaque dent en utilisant le centre géométrique de leur BufferGeometry.

    Paramètres:
    - blender_data: dictionnaire contenant 'jawSectorisation' et autres données.
    - debug: booléen, si True, affiche des informations de débogage.

    Retourne:
    - tooth_centroids: dictionnaire mappant chaque dent à son centroid.
    """
    import bpy
    from mathutils import Vector

    tooth_centroids = {}

    if "jawSectorisation" not in blender_data:
        if debug:
            print("[ERREUR] Pas de 'jawSectorisation' dans blender_data.")
        return tooth_centroids

    jaw_sector = blender_data["jawSectorisation"]

    for tooth_num_str, sector_data in jaw_sector.items():
        obj_name = f"Tooth_{tooth_num_str}_0"
        tooth_obj = bpy.data.objects.get(obj_name)
        if not tooth_obj or tooth_obj.type != 'MESH':
            if debug:
                print(f"[WARN] Objet '{obj_name}' introuvable ou non-MESH pour tooth_num_str='{tooth_num_str}'.")
            continue

        mesh = tooth_obj.data
        if len(mesh.vertices) == 0:
            if debug:
                print(f"[WARN] Objet '{obj_name}' n'a aucun vertex.")
            continue

        # Calcul du centre géométrique en coordonnées mondiales
        total = Vector((0.0, 0.0, 0.0))
        for v in mesh.vertices:
            world_pos = tooth_obj.matrix_world @ v.co
            total += world_pos
        centroid = total / len(mesh.vertices)
        tooth_centroids[tooth_num_str] = centroid

        if debug:
            print(f"[DEBUG] Centroid de '{obj_name}': {centroid}")

    return tooth_centroids


def apply_transforms_after_import(debug=False):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            obj.select_set(False)
    if debug:
        print("[apply_transforms_after_import] Done.")


def remap_jaw_sectorisation(blender_data, original_jaw_positions, debug=True):
    """
    Remap les indices de blender_data["jawSectorisation"] en fonction de la topologie
    réelle après compression (Draco). Le principe :
      - On construit un KDTree pour Maxilla_0 (nouvelle topologie),
        à partir de l'OBJ/GLTF compressé désormais présent en scène.
      - Idem pour Mandible_0.
      - Pour chaque index 'old_index' qui figure dans jawSectorisation (vertexIndices/indexMap),
        on retrouve l'index 'new_index' correspondant dans la nouvelle topologie.
      - On réécrit vertexIndices et indexMap en conséquence.
    
    Paramètres :
      - blender_data : Le dictionnaire global (déjà chargé) qui contient "jawSectorisation".
      - original_jaw_positions : 
          {
            "Maxilla_0": [Vector(...), Vector(...), ...],   # Positions d'origine (non compressées)
            "Mandible_0": [Vector(...), Vector(...), ...]   # Idem
          }
      - debug : bool, pour afficher des logs détaillés
    """

    if "jawSectorisation" not in blender_data:
        if debug:
            print("[ERREUR] Pas de clef 'jawSectorisation' dans blender_data.")
        return

    # -------------------------------------------------------------------------
    # 1. Récupérer les objets rechargés post-compression : "Maxilla_0" et "Mandible_0"
    # -------------------------------------------------------------------------
    maxilla_obj = bpy.data.objects.get("Maxilla_0")
    mandible_obj = bpy.data.objects.get("Mandible_0")

    if not maxilla_obj or not mandible_obj:
        if debug:
            print("[ERREUR] Impossible de trouver Maxilla_0 ou Mandible_0 dans la scène.")
        return

    # -------------------------------------------------------------------------
    # 2. Construire le KDTree pour Maxilla_0 et Mandible_0
    #    de sorte que : old_index -> new_index
    # -------------------------------------------------------------------------
    #    a) Récupérer les positions ACTUELLES (après compression) de Maxilla_0
    #    b) Comparer aux positions ORIGINALES (celles de original_jaw_positions["Maxilla_0"])
    #    c) Insérer dans le KDTree les positions ACTUELLES (new), pour pouvoir retrouver
    #       pour chaque old_pos le plus proche new_index.
    #

    def build_jaw_kdtree(obj):
        """Construit un KDTree à partir de l'objet compressé (post-Draco)."""
        mesh_verts = obj.data.vertices
        kd_size = len(mesh_verts)
        kd = KDTree(kd_size)
        for i, v in enumerate(mesh_verts):
            world_v = obj.matrix_world @ v.co
            kd.insert(world_v, i)
        kd.balance()
        return kd

    kd_maxilla = build_jaw_kdtree(maxilla_obj)
    kd_mandible = build_jaw_kdtree(mandible_obj)

    # Dictionnaires : old_index -> new_index pour maxilla et mandible
    jaw_map_maxilla = {}
    jaw_map_mandible = {}

    # -------------------------------------------------------------------------
    # 3. Construire le mapping oldIndex -> newIndex pour le jaw
    #    En itérant sur original_jaw_positions["Maxilla_0"] et ["Mandible_0"]
    #    on va trouver le nouveau sommet correspondant dans la topologie compressée.
    # -------------------------------------------------------------------------

    def build_jaw_index_map(old_positions, kd_tree, obj_label="Maxilla_0"):
        """
        old_positions : liste des positions d'origine (Vectors) 
        kd_tree : KDTree de l'objet compressé
        obj_label : juste un label pour debug
        """
        mapping = {}
        for old_idx, old_pos in enumerate(old_positions):
            # Chercher le plus proche dans la nouvelle topologie
            hit = kd_tree.find(old_pos)
            if hit is None:
                # Pas de correspondance
                mapping[old_idx] = None
            else:
                # hit => (location, index, dist)
                _, new_idx, dist = hit
                mapping[old_idx] = new_idx
        if debug:
            print(f"[INFO] build_jaw_index_map pour {obj_label} terminé. Nombre de sommets = {len(mapping)}")
        return mapping

    # Construire les mappings
    if "Maxilla_0" in original_jaw_positions:
        jaw_map_maxilla = build_jaw_index_map(original_jaw_positions["Maxilla_0"], kd_maxilla, "Maxilla_0")
    if "Mandible_0" in original_jaw_positions:
        jaw_map_mandible = build_jaw_index_map(original_jaw_positions["Mandible_0"], kd_mandible, "Mandible_0")

    # -------------------------------------------------------------------------
    # 4. Appliquer ces mappings à blender_data["jawSectorisation"] 
    #    Pour chaque dent, on regarde l'arcade (1,2 => maxilla; 3,4 => mandible).
    #    On remplace vertexIndices par leurs new_index. 
    #    On fait de même pour indexMap : { new_index: oldData }.
    # -------------------------------------------------------------------------

    jaw_sector = blender_data["jawSectorisation"]

    for tooth_number_str, data in jaw_sector.items():
        # tooth_number_str ex: "11", "24", "31", ...
        # On regarde l'arc digit
        arch_digit = None
        try:
            arch_digit = int(tooth_number_str[0])
        except:
            continue
        
        if arch_digit in [1,2]:
            # Mâchoire supérieure
            current_mapping = jaw_map_maxilla
        else:
            # Mâchoire inférieure
            current_mapping = jaw_map_mandible

        if not current_mapping:
            # Pas de mapping => on skip
            continue

        old_vertex_indices = data.get("vertexIndices", [])
        old_index_map = data.get("indexMap", {})

        new_vertex_indices = []
        new_index_map = {}

        # -- Remap vertexIndices
        for old_idx in old_vertex_indices:
            mapped_idx = current_mapping.get(old_idx, None)
            if mapped_idx is not None:
                new_vertex_indices.append(mapped_idx)

        # -- Remap indexMap
        #    Les clés 'old_idx' doivent devenir 'new_idx'.
        for old_idx_str, old_data in old_index_map.items():
            # Selon l'export Python -> JSON, old_idx_str peut être déjà converti en int
            # ou resté string => on sécurise en parse
            if isinstance(old_idx_str, str):
                try:
                    old_idx = int(old_idx_str)
                except:
                    continue
            else:
                old_idx = old_idx_str

            new_idx = current_mapping.get(old_idx, None)
            if new_idx is not None:
                new_index_map[new_idx] = old_data  # On recopie la valeur

        # On réécrit dans blender_data
        data["vertexIndices"] = new_vertex_indices
        data["indexMap"] = new_index_map

        if debug:
            print(f"[DEBUG] Dent {tooth_number_str} : "
                  f"{len(old_vertex_indices)} -> {len(new_vertex_indices)} vertexIndices remappés, "
                  f"indexMap: {len(old_index_map)} -> {len(new_index_map)}")

    if debug:
        print("[INFO] remap_jaw_sectorisation terminé.")

# -----------------------------------------------------------------------------
# Fonction pour stocker les positions originales (avant compression) des mâchoires
# -----------------------------------------------------------------------------

def store_original_jaw_positions():
    """
    Récupère les positions d'origine des sommets de Maxilla_0 et Mandible_0.
    Retourne un dict:
    {
      "Maxilla_0": [Vector(...), Vector(...)...],
      "Mandible_0": [Vector(...), Vector(...)...]
    }
    """
    original_jaw_positions = {
        "Maxilla_0": [],
        "Mandible_0": []
    }

    # Chercher les objets "Maxilla_0" et "Mandible_0" avant compression
    maxilla_0 = bpy.data.objects.get("Maxilla_0")
    mandible_0 = bpy.data.objects.get("Mandible_0")

    # On stocke leurs vertices en coordonnées monde
    if maxilla_0 and maxilla_0.type == 'MESH':
        for v in maxilla_0.data.vertices:
            world_co = maxilla_0.matrix_world @ v.co
            original_jaw_positions["Maxilla_0"].append(world_co)

    if mandible_0 and mandible_0.type == 'MESH':
        for v in mandible_0.data.vertices:
            world_co = mandible_0.matrix_world @ v.co
            original_jaw_positions["Mandible_0"].append(world_co)

    return original_jaw_positions


if __name__ == "__main__":
    export_path = sys.argv[-2]
    load_path = sys.argv[-3]
    blender_data_file = sys.argv[-1]
    allInOneGLB(load_path, export_path, blender_data_file)
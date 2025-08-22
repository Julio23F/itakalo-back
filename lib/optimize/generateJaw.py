import os
import bpy
from mathutils import Vector
import mathutils
import bmesh
import math
import numpy as np
import sys


def get_absolute_path(path):
    return os.path.abspath(os.path.expanduser(path))


def calculate_total_volume(mesh_list):
    total_volume = 0
    for mesh in mesh_list:
        if mesh.type == 'MESH':
            bpy.context.view_layer.objects.active = mesh
            mesh.select_set(True)
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.object.mode_set(mode='OBJECT')
            total_volume += mesh.dimensions.x * mesh.dimensions.y * mesh.dimensions.z
            mesh.select_set(False)
    return total_volume


def apply_all_modifiers(obj):
    for modifier in obj.modifiers:
        # if modifier.type == 'BOOLEAN':
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.modifier_apply(modifier=modifier.name)


def create_gum_material(obj_name):
    # Create a new material
    material = bpy.data.materials.new(name="Gum_Material")
    
    # Enable 'Use Nodes'
    material.use_nodes = True
    bsdf = material.node_tree.nodes["Principled BSDF"]
    
    # Create new nodes
    separate_xyz = material.node_tree.nodes.new('ShaderNodeSeparateXYZ')
    color_ramp = material.node_tree.nodes.new('ShaderNodeValToRGB')
    
    # Make connections
    material.node_tree.links.new(bsdf.inputs['Base Color'], color_ramp.outputs['Color'])
    material.node_tree.links.new(color_ramp.inputs['Fac'], separate_xyz.outputs['Z'])
    
    # Setup color ramp
    if "Upper" in obj_name:
        color_ramp.color_ramp.elements[0].color = (0.9, 0.5, 0.5, 1)  # Lighter color at the bottom
        color_ramp.color_ramp.elements[1].color = (0.8, 0.4, 0.4, 1)  # Darker color at the top
    elif "Lower" in obj_name:
        color_ramp.color_ramp.elements[0].color = (0.8, 0.4, 0.4, 1)  # Darker color at the bottom
        color_ramp.color_ramp.elements[1].color = (0.9, 0.5, 0.5, 1)  # Lighter color at the top
    
    # Other settings
    bsdf.inputs['Subsurface'].default_value = 0.3  # Subsurface
    bsdf.inputs['Roughness'].default_value = 0.6  # Roughness
    
    return material


def apply_gum_material(obj):
    # Create gum material
    gum_material = create_gum_material(obj.name)
    
    # Apply the material to the object
    if len(obj.data.materials) > 0:
        # If the object already has a material, replace it
        obj.data.materials[0] = gum_material
    else:
        # If the object has no materials, append it
        obj.data.materials.append(gum_material)


def apply_bone_scale(armature_obj, bones_ind=[]):
    # Ensure we're in pose mode
    bpy.ops.object.mode_set(mode='POSE')

    # Select the bone
    for bone in armature_obj.pose.bones:
        # bone = armature_obj.pose.bones[i]
        bone.bone.select = True

    # Apply the scale
    bpy.ops.pose.armature_apply(selected=True)

    # Deselect the bone
    bone.bone.select = False

    # Switch back to object mode
    bpy.ops.object.mode_set(mode='OBJECT')


def deform_from_points(obj, points, offset_curve={0: 0.1, 1: 0.0}, iterations=25, export_path=None, falloff='SPHERE', proportional_adaptation=False, orient_type='GLOBAL', deformation_vector=(0, -1, 0), use_scale=False):
    # If no specific export path was provided, use the script's directory
    if export_path is None:
        export_path = get_absolute_path("./")

    # Ensure we're in object mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # Set the active object to the mesh object
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    # Apply all modifiers before starting the deformation
    # apply_all_modifiers(obj)

    # Sort the offset curve keys
    offset_keys = sorted(offset_curve.keys())

    # Loop over the points
    for point in points:

        # Select the closest mesh vertex to the point
        closest_vertex = min(obj.data.vertices, key=lambda v: (obj.matrix_world @ v.co - point).length)
        distance = (obj.matrix_world @ closest_vertex.co - point).length
        proportional_size = 1
        if proportional_adaptation: proportional_size = distance / 7

        # Set the active object to the mesh object and switch to edit mode
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')

        # Deselect all vertices
        bpy.ops.mesh.select_all(action='DESELECT')

        # Get a BMesh from the current mesh
        bm = bmesh.from_edit_mesh(obj.data)

        # Ensure the internal table is up-to-date before using
        bm.verts.ensure_lookup_table()

        # Select the closest vertex using its index
        bm.verts[closest_vertex.index].select = True

        # Update the BMesh to the mesh
        bmesh.update_edit_mesh(obj.data)

        # Repeat translate and select_more operations for the specified number of iterations
        for j in range(iterations):
            # Calculate the current offset depending on the iteration
            ratio = j / iterations
            offset_key_index = max(i for i, key in enumerate(offset_keys) if key <= ratio)
            if offset_key_index == len(offset_keys) - 1:
                offset = offset_curve[offset_keys[offset_key_index]]
            else:
                next_key = offset_keys[offset_key_index + 1]
                offset = ((next_key - ratio) * offset_curve[offset_keys[offset_key_index]] + (ratio - offset_keys[offset_key_index]) * offset_curve[next_key]) / (next_key - offset_keys[offset_key_index])
            
            deformed_vector = tuple(offset * value for value in deformation_vector)
            # deformed_vector += (0,)


            # Use proportional editing to move or scale the selected vertices up or down depending on the mesh name
            if use_scale:
                pass
                # bpy.ops.transform.transform(mode='RESIZE', value=deformed_vector, use_proportional_edit=True, proportional_edit_falloff=falloff, proportional_size=proportional_size, use_proportional_connected=True, orient_type=orient_type)
            else:
                # bpy.ops.transform.transform(mode='TRANSLATION', value=deformed_vector, use_proportional_edit=True, proportional_edit_falloff=falloff, proportional_size=proportional_size, use_proportional_connected=True, orient_type=orient_type)
                bpy.ops.transform.translate(value=deformed_vector, use_proportional_edit=True, proportional_edit_falloff=falloff, proportional_size=proportional_size, use_proportional_connected=True, orient_type=orient_type)

            # Extend the selected area
            bpy.ops.mesh.select_more()

        # Switch back to object mode
        bpy.ops.object.mode_set(mode='OBJECT')

        # Make the mesh smooth
        for face in obj.data.polygons:
            face.use_smooth = True


def get_closest_point_on_mesh(point, obj):
    # Convert object to bmesh
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.transform(obj.matrix_world)
    bm.faces.ensure_lookup_table()  # Ensure the internal table is up-to-date before using
    faces = bm.faces

    # Create KDTree
    size = len(faces)
    kd = mathutils.kdtree.KDTree(size)
    for i, face in enumerate(faces):
        kd.insert(face.calc_center_median(), i)
    kd.balance()

    # Find the closest point
    co, index, dist = kd.find(point)
    closest_face = faces[index]
    closest_point = closest_face.calc_center_median()
    
    # Clean up bmesh
    bm.free()
    
    return closest_point
        
# Function to check if a point is inside a mesh
def is_inside(p, obj, direction=1):
    mat = obj.matrix_world.inverted()
    # Transformation of the point p to the local coordinates of obj
    p_local = mat @ p
    # Creation of a direction vector along the z-axis
    direction = mathutils.Vector((0, 0, direction))
    # Cast the ray from the point along the z-axis
    result, location, normal, index = obj.ray_cast(p_local, direction)
    return result


def group_points(points_to_deform, radius=0.5):
    # Compute the local density for each point
    densities = [(point, sum((other - point).length <= radius for other in points_to_deform)) for point in points_to_deform]

    # Sort the points by their density in descending order
    sorted_points = [point for point, density in sorted(densities, key=lambda x: x[1], reverse=True)]

    groups = []
    while sorted_points:
        point = sorted_points.pop(0)
        group = [point]

        for other in sorted_points[:]:
            if (other - point).length <= radius:
                group.append(other)
                sorted_points.remove(other)

        # Only add the group if it doesn't exist yet.
        if not any(point in existing_group for existing_group in groups for point in group):
            groups.append(group)

    return groups


def check_and_extrude(mesh_obj, target_mesh, upper_percentage=0.4, from_upper=False, use_average_point=True, debug_mesh=False):
    # We get the world coordinates of the bounding box
    bbox = [mesh_obj.matrix_world @ mathutils.Vector(corner) for corner in mesh_obj.bound_box]
    # We get the max and min z to determine the upper half
    min_z = min(corner.z for corner in bbox)
    max_z = max(corner.z for corner in bbox)

    direction = -1 if from_upper else 1

    # Calculate the z-threshold
    threshold_z = min_z + (max_z - min_z) * (1 - upper_percentage) if not from_upper else min_z + (max_z - min_z) * upper_percentage

    # Convert the vertices to world coordinates
    world_vertices = [mesh_obj.matrix_world @ v.co for v in mesh_obj.data.vertices]

    points_to_check = [v for v in world_vertices if (v.z > threshold_z and not from_upper) or (v.z < threshold_z and from_upper)]

    points_to_extrude = []
    extrude_vectors = []

    for point in points_to_check:
        point_inside = is_inside(point, target_mesh, direction=direction)
        if point_inside:
            # Get the closest point on the target_mesh
            closest_point = get_closest_point_on_mesh(point, target_mesh)
            extrude_vectors.append(point - closest_point)
            points_to_extrude.append(point)

    if points_to_extrude:
        if(debug_mesh): print("Some points are inside the target mesh, extruding...")

        groups = group_points(points_to_extrude, radius=2.5)
        average_points = [sum(group, Vector()) / len(group) for group in groups]

        if use_average_point:
            average_point = sum(average_points, Vector()) / len(average_points)
            average_points = [average_point]
            if(debug_mesh): print("Using average point for extrusion.")

        # First generate all the closest points on the target mesh
        closest_points_on_target_mesh = [get_closest_point_on_mesh(average_point, target_mesh) for average_point in average_points]

        i = 0
        # Then apply the extrusions
        for closest_point_on_target_mesh in closest_points_on_target_mesh:
            average_vector = sum(extrude_vectors, Vector()) / len(extrude_vectors)
            if(debug_mesh): print(average_vector.length)
            extrude_value = 0.8 if use_average_point else 0.5
            iterations_value = 20 if use_average_point else 10
            # average_vector = -average_vector
            deform_from_points(target_mesh, [closest_point_on_target_mesh], deformation_vector=average_vector, iterations=iterations_value, offset_curve={0:extrude_value, 1: 0}, falloff="SPHERE")

            if debug_mesh:
                # Create a red sphere at the closest point on the target mesh
                bpy.ops.mesh.primitive_uv_sphere_add(location=closest_point_on_target_mesh, radius=0.1)  # added radius parameter
                sphere_obj = bpy.context.object  # get the created sphere object
                sphere_mat = bpy.data.materials.new(name="RedMat")
                sphere_mat.diffuse_color = (1, 0, 0, 1)  # red color
                sphere_obj.data.materials.append(sphere_mat)
                # Create a red sphere at the closest point on the target mesh
                bpy.ops.mesh.primitive_uv_sphere_add(location=average_points[i], radius=0.1)  # added radius parameter
                sphere_obj = bpy.context.object  # get the created sphere object
                sphere_mat = bpy.data.materials.new(name="GreenMat")
                sphere_mat.diffuse_color = (0, 1, 0, 1)  # red color
                sphere_obj.data.materials.append(sphere_mat)
            i += 1
        if debug_mesh:
            # Create a new mesh and a new object
            new_mesh = bpy.data.meshes.new('deformed_points')
            new_obj = bpy.data.objects.new('DeformedPointsObj', new_mesh)

            # Link the new object to the current collection
            bpy.context.collection.objects.link(new_obj)

            # Create a bmesh, add the vertices and then convert back to a mesh
            bm = bmesh.new()
            for v in points_to_extrude:
                bm.verts.new(v)
            bm.to_mesh(new_mesh)
            bm.free()

            # Create a green material and assign it to the new object
            mat = bpy.data.materials.new(name="GreenMat")
            mat.diffuse_color = (0, 1, 0, 1)  # green color
            new_obj.data.materials.append(mat)
            
    else:
        if debug_mesh: print("All points are outside the target mesh")


def check_and_deform(mesh_obj, target_mesh, upper_percentage=0.4, from_bottom=False, debug_mesh=False):
    # We get the world coordinates of the bounding box
    bbox = [mesh_obj.matrix_world @ mathutils.Vector(corner) for corner in mesh_obj.bound_box]
    # We get the max and min z to determine the upper half
    min_z = min(corner.z for corner in bbox)
    max_z = max(corner.z for corner in bbox)

    direction = -1 if from_bottom else 1

    # Calculate the z-threshold
    threshold_z = min_z + (max_z - min_z) * (1 - upper_percentage) if not from_bottom else min_z + (max_z - min_z) * upper_percentage

    # Convert the vertices to world coordinates
    world_vertices = [mesh_obj.matrix_world @ v.co for v in mesh_obj.data.vertices]

    points_to_check = [v for v in world_vertices if (v.z > threshold_z and not from_bottom) or (v.z < threshold_z and from_bottom)]

    points_to_deform = []
    deform_vectors = []

    for point in points_to_check:
        point_inside = is_inside(point, target_mesh, direction)
        if not point_inside:
            # Get the closest point on the target_mesh
            closest_point = get_closest_point_on_mesh(point, target_mesh)
            deform_vectors.append(closest_point - point)
            points_to_deform.append(point)

    if points_to_deform:
        if(debug_mesh): print("Some points are outside the target mesh, deforming...")
        
        groups = group_points(points_to_deform, radius=2.5)
        average_points = [sum(group, Vector()) / len(group) for group in groups]
        
        # First generate all the closest points on the target mesh
        closest_points_on_target_mesh = [get_closest_point_on_mesh(average_point, target_mesh) for average_point in average_points]
        
        i = 0
        # Then apply the deformations
        for closest_point_on_target_mesh in closest_points_on_target_mesh:
            average_vector = sum(deform_vectors, Vector()) / len(deform_vectors)
            if(debug_mesh): print(average_vector.length)
            average_vector = -average_vector
            deform_from_points(target_mesh, [closest_point_on_target_mesh], deformation_vector=average_vector, iterations=15, offset_curve={0:0.10, 1: 0}, falloff="SPHERE")


            if debug_mesh:
                # Create a red sphere at the closest point on the target mesh
                bpy.ops.mesh.primitive_uv_sphere_add(location=closest_point_on_target_mesh, radius=0.1)  # added radius parameter
                sphere_obj = bpy.context.object  # get the created sphere object
                sphere_mat = bpy.data.materials.new(name="RedMat")
                sphere_mat.diffuse_color = (1, 0, 0, 1)  # red color
                sphere_obj.data.materials.append(sphere_mat)
                # Create a red sphere at the closest point on the target mesh
                bpy.ops.mesh.primitive_uv_sphere_add(location=average_points[i], radius=0.1)  # added radius parameter
                sphere_obj = bpy.context.object  # get the created sphere object
                sphere_mat = bpy.data.materials.new(name="GreenMat")
                sphere_mat.diffuse_color = (0, 1, 0, 1)  # red color
                sphere_obj.data.materials.append(sphere_mat)
            i += 1
        if debug_mesh:
            # Create a new mesh and a new object
            new_mesh = bpy.data.meshes.new('deformed_points')
            new_obj = bpy.data.objects.new('DeformedPointsObj', new_mesh)

            # Link the new object to the current collection
            bpy.context.collection.objects.link(new_obj)

            # Create a bmesh, add the vertices and then convert back to a mesh
            bm = bmesh.new()
            for v in points_to_deform:
                bm.verts.new(v)
            bm.to_mesh(new_mesh)
            bm.free()

            # Create a green material and assign it to the new object
            mat = bpy.data.materials.new(name="GreenMat")
            mat.diffuse_color = (0, 1, 0, 1)  # green color
            new_obj.data.materials.append(mat)

    else:
        if debug_mesh: print("All points are inside the target mesh")


def deform_lengthen(obj, height_interval=0.15, translation_offset=2.5, falloff='LINEAR'):
    # Ensure we're in object mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # Set the active object to the mesh object
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # Apply all modifiers before starting the deformation
    apply_all_modifiers(obj)

    # Deselect all vertices
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')

    # Select the vertices according to the name of the object
    if "Upper" in obj.name:
        # Get the highest vertex on the Z axis
        highest_vertex = max(obj.data.vertices, key=lambda v: (obj.matrix_world @ v.co).z)
        # Select all vertices within a given Z range
        for v in obj.data.vertices:
            if (obj.matrix_world @ v.co).z >= highest_vertex.co.z - height_interval:
                v.select = True
    elif "Lower" in obj.name:
        # Get the lowest vertex on the Z axis
        lowest_vertex = min(obj.data.vertices, key=lambda v: (obj.matrix_world @ v.co).z)
        # Select all vertices within a given Z range
        for v in obj.data.vertices:
            if (obj.matrix_world @ v.co).z <= lowest_vertex.co.z + height_interval:
                v.select = True

    # Switch to edit mode for translation
    bpy.ops.object.mode_set(mode='EDIT')

    to_back = 1.5

    # Perform the translation
    if "Upper" in obj.name:
        bpy.ops.transform.translate(value=(0, to_back, translation_offset), use_proportional_edit=True, proportional_edit_falloff=falloff, orient_type='GLOBAL')
    elif "Lower" in obj.name:
        bpy.ops.transform.translate(value=(0, to_back, -translation_offset), use_proportional_edit=True, proportional_edit_falloff=falloff, orient_type='GLOBAL')

    # Switch back to object mode
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')

    # Make the mesh smooth
    for face in obj.data.polygons:
        face.use_smooth = True


def find_and_deform_back(obj, offset_curve={0: 0.0, 0.7: 0.3, 0.9: 1.2, 1: 0.0}, iterations=40, falloff='SPHERE', orient_type='GLOBAL', deformation_vector=(0, 1, 0.1), z_interval=0.05, use_scale=False):
    # Ensure we're in object mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # Set the active object to the mesh object
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # Apply all modifiers before starting the deformation
    apply_all_modifiers(obj)

    # Calculate the Z coordinate of the bounding box center
    bounding_box_center_z = sum((obj.matrix_world @ Vector(b)).z for b in obj.bound_box) / len(obj.bound_box)

    # Find vertices with highest Y value and closest to the bounding box center Z
    sorted_vertices = sorted(obj.data.vertices, key=lambda v: (obj.matrix_world @ v.co).y, reverse=True)
    pos_x_vertex = None  # highest Y vertex with positive X
    neg_x_vertex = None  # highest Y vertex with negative X

    # Find the highest Y vertices closest to bounding box center with positive and negative X coordinates
    for vertex in sorted_vertices:
        global_vertex_pos = obj.matrix_world @ vertex.co
        if abs(global_vertex_pos.z - bounding_box_center_z) <= z_interval:  # check if the vertex's Z coordinate is close to the bounding box center Z
            if global_vertex_pos.x < 0 and neg_x_vertex is None:  # select the vertex with negative X coordinate
                neg_x_vertex = vertex
            if global_vertex_pos.x > 0 and pos_x_vertex is None:  # select the vertex with positive X coordinate
                pos_x_vertex = vertex
        if pos_x_vertex is not None and neg_x_vertex is not None:
            break

    # Get global position for the vertices
    pos_x_vertex_global = obj.matrix_world @ pos_x_vertex.co
    neg_x_vertex_global = obj.matrix_world @ neg_x_vertex.co

    # Call the deformation function for the vertices
    deform_from_points(obj, [pos_x_vertex_global, neg_x_vertex_global], offset_curve=offset_curve, iterations=iterations, falloff=falloff, orient_type=orient_type, deformation_vector=deformation_vector)
    if(use_scale): deform_from_points(obj, [pos_x_vertex_global, neg_x_vertex_global], offset_curve=offset_curve, iterations=iterations, falloff=falloff, orient_type=orient_type, deformation_vector=deformation_vector, use_scale=True)
    # scale_from_points(obj, [pos_x_vertex_global, neg_x_vertex_global], offset_curve=offset_curve, iterations=40, falloff=falloff, orient_type=orient_type)

    # Switch back to object mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # Make the mesh smooth
    for face in obj.data.polygons:
        face.use_smooth = True


def create_proportional_deformation_by_curve(obj, curve_object, limit_points=[], offset_curve={0: 0.15, 0.5: 0.10, 1: 0.0}, iterations=25, between=True, export_path=None, falloff='SPHERE', direction=[0,0,1], proportional_adaptation=True, orient_type='GLOBAL', surfaces=None, heights=None, only_points= None):
    
    def resize_list(lst, target_len):
        diff = target_len - len(lst)
        if diff < 0:
            return lst[:target_len]
        elif diff > 0:
            return [lst[0]] * int(diff / 2) + lst + [lst[-1]] * (diff - int(diff / 2))
        else:
            return lst


    if export_path is None:
        export_path = get_absolute_path("./")

    bpy.ops.object.mode_set(mode='OBJECT')

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    # Créer un ensemble de points seulement si la liste n'est pas vide ou None
    only_points_set = set(only_points) if only_points else None
    # apply_all_modifiers(obj)

    bpy.context.view_layer.objects.active = curve_object
    curve_object.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')

    offset_keys = sorted(offset_curve.keys())

    list_of_points = list(curve_object.data.splines[0].points)
    num_points = len(list_of_points)


    if surfaces is not None and isinstance(surfaces, list):
        surfaces = resize_list(surfaces, num_points)
    if heights is not None and isinstance(heights, list):
        heights = resize_list(heights, num_points)
        avg_height = sum(heights) / len(heights)

    for i, point in enumerate(list_of_points):
        skip_it = False

        for does_skip in limit_points:
            ind_point = does_skip
            if(does_skip < 0): ind_point = len(list_of_points) + does_skip
            if(i == ind_point):
                skip_it = True
        
        if(skip_it): 
            continue

        # Vérifier si on a seulement un ensemble de points et si le point actuel n'y est pas
        if only_points_set and i not in only_points_set:
            continue
        
        if between and i < num_points - 1:
            next_point = curve_object.data.splines[0].points[i+1]
            if surfaces is not None:
                # Inverse the surfaces before calculating the ratio
                inv_surface1 = 1 / surfaces[i]
                inv_surface2 = 1 / surfaces[i+1]
                # The ratio now gives more weight to the smaller surface
                ratio = inv_surface1 / (inv_surface1 + inv_surface2)
                curve_vertex = ratio * point.co + (1 - ratio) * next_point.co
            else:
                curve_vertex = (point.co + next_point.co) / 2
            distance = (point.co - next_point.co).length
        else:
            curve_vertex = point.co
            if i > 0:
                prev_point = curve_object.data.splines[0].points[i-1]
                distance = (point.co - prev_point.co).length
            else:
                distance = 0

        proportional_size = 1

        closest_vertex = min(obj.data.vertices, key=lambda v: (obj.matrix_world @ v.co - curve_object.matrix_world @ curve_vertex.to_3d()).length)

        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')

        bpy.ops.mesh.select_all(action='DESELECT')

        bm = bmesh.from_edit_mesh(obj.data)
        bm.verts.ensure_lookup_table()
        bm.verts[closest_vertex.index].select = True
        bmesh.update_edit_mesh(obj.data)

        for j in range(iterations):
            ratio = j / iterations
            offset_key_index = max(i for i, key in enumerate(offset_keys) if key <= ratio)
            if offset_key_index == len(offset_keys) - 1:
                offset = offset_curve[offset_keys[offset_key_index]]
            else:
                next_key = offset_keys[offset_key_index + 1]
                offset = ((next_key - ratio) * offset_curve[offset_keys[offset_key_index]] + (ratio - offset_keys[offset_key_index]) * offset_curve[next_key]) / (next_key - offset_keys[offset_key_index])
            
            if heights is not None:
                height_ratio = heights[i] / avg_height if not between else (heights[i] + heights[i+1]) / (2 * avg_height)
                offset *= height_ratio * height_ratio

            bpy.ops.transform.translate(value=(offset * direction[0], offset * direction[1], offset * direction[2]), use_proportional_edit=True, proportional_edit_falloff=falloff, proportional_size=proportional_size, use_proportional_connected=True, orient_type=orient_type)

            bpy.ops.mesh.select_more()

        bpy.ops.object.mode_set(mode='OBJECT')

        for face in obj.data.polygons:
            face.use_smooth = True


def create_proportional_deformation(obj, armature_object, offset_curve={0: 0.15, 0.5: 0.10, 1: 0.0}, iterations=25, between=True, export_path=None, falloff='SPHERE', direction=1, proportional_adaptation=True, orient_type='GLOBAL'):
    # If no specific export path was provided, use the script's directory
    if export_path is None:
        export_path = get_absolute_path("./")

    # Ensure we're in object mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # Set the active object to the mesh object
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    # Apply all modifiers before starting the deformation
    apply_all_modifiers(obj)

    # Set the armature object to edit mode to access the bones
    bpy.context.view_layer.objects.active = armature_object
    armature_object.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')

    # Sort the offset curve keys
    offset_keys = sorted(offset_curve.keys())

    # Loop over the armature bones
    for i, bone in enumerate(list(armature_object.data.edit_bones) + [armature_object.data.edit_bones[-1]]):
        # Calculate the location of the bone depending on the "between" parameter
        if between and i < len(armature_object.data.edit_bones):
            armature_vertex = (bone.head + bone.tail) / 2
        elif between and i > len(armature_object.data.edit_bones) -1:
            continue
        elif i < len(armature_object.data.edit_bones):
            armature_vertex = bone.head 
        else:
            armature_vertex = bone.tail

        distance = (bone.head - bone.tail).length

        proportional_size = 1
        if proportional_adaptation: proportional_size = distance / 7

        # Select the closest mesh vertex to the armature vertex
        closest_vertex = min(obj.data.vertices, key=lambda v: (obj.matrix_world @ v.co - armature_object.matrix_world @ armature_vertex).length)

        # Set the active object to the mesh object and switch to edit mode
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')

        # Deselect all vertices
        bpy.ops.mesh.select_all(action='DESELECT')

        # Get a BMesh from the current mesh
        bm = bmesh.from_edit_mesh(obj.data)

        # Ensure the internal table is up-to-date before using
        bm.verts.ensure_lookup_table()

        # Select the closest vertex using its index
        bm.verts[closest_vertex.index].select = True

        # Update the BMesh to the mesh
        bmesh.update_edit_mesh(obj.data)

        # Repeat translate and select_more operations for the specified number of iterations
        for j in range(iterations):
            # Calculate the current offset depending on the iteration
            ratio = j / iterations
            offset_key_index = max(i for i, key in enumerate(offset_keys) if key <= ratio)
            if offset_key_index == len(offset_keys) - 1:
                offset = offset_curve[offset_keys[offset_key_index]]
            else:
                next_key = offset_keys[offset_key_index + 1]
                offset = ((next_key - ratio) * offset_curve[offset_keys[offset_key_index]] + (ratio - offset_keys[offset_key_index]) * offset_curve[next_key]) / (next_key - offset_keys[offset_key_index])

            # Use proportional editing to move the selected vertices up or down depending on the mesh name
            if "Upper" in obj.name:
                bpy.ops.transform.translate(value=(0, 0, -offset * direction), use_proportional_edit=True, proportional_edit_falloff=falloff, proportional_size=proportional_size, use_proportional_connected=True, orient_type=orient_type)
            elif "Lower" in obj.name:
                bpy.ops.transform.translate(value=(0, 0, offset * direction), use_proportional_edit=True, proportional_edit_falloff=falloff, proportional_size=proportional_size, use_proportional_connected=True, orient_type=orient_type)

            # Extend the selected area
            bpy.ops.mesh.select_more()

        # Switch back to object mode
        bpy.ops.object.mode_set(mode='OBJECT')

        # Make the mesh smooth
        for face in obj.data.polygons:
            face.use_smooth = True


def move_spline_point(spline, point_index, translation_vector):
    # Ensure we're in object mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # Deselect all
    bpy.ops.object.select_all(action='DESELECT')

    # Set the active object to the spline
    bpy.context.view_layer.objects.active = spline
    spline.select_set(True)

    # Switch to edit mode to adjust the points
    bpy.ops.object.mode_set(mode='EDIT')

    # Deselect all the points
    bpy.ops.curve.select_all(action='DESELECT')

    # Get the point
    if point_index < 0:
        point = spline.data.splines.active.points[-point_index]
    else:
        point = spline.data.splines.active.points[point_index]

    # Select the point
    point.select = True

    # Move the point
    bpy.ops.transform.translate(value=translation_vector)

    # Switch back to object mode
    bpy.ops.object.mode_set(mode='OBJECT')


def export_to_glb(obj_list, name="test", filepath='./'):
    export_path = get_absolute_path(filepath)
    bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.select_all(action='DESELECT')

    # Select objects in the list
    for obj in obj_list:
        obj.select_set(True)

    # Export selected objects to glb
    bpy.ops.export_scene.gltf(filepath=os.path.join(export_path, name + '.glb'), use_selection=True)


def local_dimensions(obj):
    local_coords = [obj.matrix_world.inverted() @ Vector(corner) for corner in obj.bound_box]
    rotated_extents = [max(coord[i] for coord in local_coords) - min(coord[i] for coord in local_coords) for i in range(3)]
    return rotated_extents


def sort_and_calculate_dimensions(teeth, position):
    # Sorting function based on position
    def sort_upper(teeth):
        group1 = sorted([t for t in teeth if int(str(t.name[5:7])[0]) == 1], key=lambda t: int(str(t.name[5:7])[1]), reverse=True)
        group2 = sorted([t for t in teeth if int(str(t.name[5:7])[0]) == 2], key=lambda t: int(str(t.name[5:7])[1]))
        return group1 + group2

    def sort_lower(teeth):
        group1 = sorted([t for t in teeth if int(str(t.name[5:7])[0]) == 4], key=lambda t: int(str(t.name[5:7])[1]), reverse=True)
        group2 = sorted([t for t in teeth if int(str(t.name[5:7])[0]) == 3], key=lambda t: int(str(t.name[5:7])[1]))
        return group1 + group2

    # Sort the teeth based on the position
    if "Upper" in position:
        sorted_teeth = sort_upper(teeth)
    elif "Lower" in position:
        sorted_teeth = sort_lower(teeth)

    # Calculate the dimensions
    surface_list = []
    height_list = []
    for mesh in sorted_teeth:
        if mesh.type == 'MESH':
            local_dim = local_dimensions(mesh)
            surface = local_dim[0] * local_dim[1]
            height = local_dim[2]
            surface_list.append(surface)
            height_list.append(height)

    return surface_list, height_list



def create_curve(teeth, name):
    def sort_upper(teeth):
        group1 = sorted([t for t in teeth if int(str(t.name[5:7])[0]) == 1], key=lambda t: int(str(t.name[5:7])[1]), reverse=True)
        group2 = sorted([t for t in teeth if int(str(t.name[5:7])[0]) == 2], key=lambda t: int(str(t.name[5:7])[1]))
        return group1 + group2

    def sort_lower(teeth):
        group1 = sorted([t for t in teeth if int(str(t.name[5:7])[0]) == 4], key=lambda t: int(str(t.name[5:7])[1]), reverse=True)
        group2 = sorted([t for t in teeth if int(str(t.name[5:7])[0]) == 3], key=lambda t: int(str(t.name[5:7])[1]))
        return group1 + group2

    sort_func = sort_upper if "Upper" in name else sort_lower

    sorted_teeth = sort_func(teeth)

    curve_data = bpy.data.curves.new(name='Curve', type='CURVE')
    curve_data.dimensions = '3D'
    polyline = curve_data.splines.new('POLY')

    polyline.points.add(len(sorted_teeth) - 1)

    list_of_tooth_number = []  # dictionary to map tooth number to vertex

    for i, tooth in enumerate(sorted_teeth):
        bbox_center = 0.125 * sum((Vector(b) for b in tooth.bound_box), Vector())
        global_center = tooth.matrix_world @ bbox_center
        polyline.points[i].co = (*global_center, 1)

        # map tooth number to vertex
        tooth_number = tooth.name[5:7]
        list_of_tooth_number.append(tooth_number)

    curve = bpy.data.objects.new(name + '_curve', curve_data)
    bpy.context.collection.objects.link(curve)

    return curve, name, list_of_tooth_number  # return the dictionary


def duplicate_curve(curve, length=1, direction_vector=(0, 3, 0, 1)):
    # Convert direction_vector to Vector if it's not already
    if not isinstance(direction_vector, Vector):
        direction_vector = Vector(direction_vector)

    original_location = curve.location.xyz
    curve.location = (0, 0, 0)
    # Duplicate the curve
    curve_copy = curve.copy()
    curve_copy.data = curve.data.copy()  # Duplicate curve data
    bpy.context.collection.objects.link(curve_copy)  # Add duplicate to the scene

    # Create a new curve data
    new_curve_data = bpy.data.curves.new(name='extended_curve', type='CURVE')
    new_curve_data.dimensions = '3D'
    new_spline = new_curve_data.splines.new('POLY')

    # Get the curve's spline
    old_spline = curve_copy.data.splines[0]

    # Add point at the beginning of the curve
    # Calculate the position of the new point
    end_point = old_spline.points[0].co
    new_point_pos = end_point + direction_vector

    # Add the new point to the new spline
    new_spline.points[0].co = new_point_pos

    # Copy the old points to the new spline
    for old_point in old_spline.points:
        new_spline.points.add(1)
        new_spline.points[-1].co = old_point.co

    # Add point at the end of the curve
    end_point = old_spline.points[-1].co
    new_point_pos = end_point + direction_vector

    # Add the new point to the new spline
    new_spline.points.add(1)
    new_spline.points[-1].co = new_point_pos

    # Link the new curve to the same object as the old curve
    curve_copy.data = new_curve_data

    curve.location = original_location
    curve_copy.location = original_location
    curve_copy.name = curve_copy.name + "_extended"

    return curve_copy
    

def add_teeth_to_armature(armature, list_of_tooth_number, offset=2, name="", remove_original_bones=True):
    # Set the armature as the active object and enter Edit mode
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='EDIT')

    # Create a list of the initial bones
    initial_bones = list(armature.data.edit_bones)

    new_bones = []

    tooth_ind = 0

    for i, bone in enumerate(initial_bones):
        # Process both the head and tail of the bone for the last bone,
        # and only the head for all other bones
        points = [bone.head, bone.tail] if i == len(initial_bones) - 1 else [bone.head]

        for point in points:
            # Find the closest tooth to the point
            # closest_tooth_number = min(vertex_dict.keys(), key=lambda k: (vertex_dict[k].co.xyz - point).length)
            
            # Create a new bone and rename it
            new_bone = armature.data.edit_bones.new(list_of_tooth_number[tooth_ind])
            new_bones.append(new_bone)

            # Set the new bone's head at the point
            new_bone.head = point

            # Offset the new bone's tail in the Z direction
            if "Lower" in name:
                new_bone.tail = new_bone.head + Vector((0, 0, offset))
            elif "Upper" in name:
                new_bone.tail = new_bone.head + Vector((0, 0, -offset))

            # Connect the new bone to the original bone
            new_bone.parent = bone

            tooth_ind += 1

    # If the parameter is true, remove all original bones
    if remove_original_bones:
        for bone in initial_bones:
            armature.data.edit_bones.remove(bone)

    # Return to Object mode
    bpy.ops.object.mode_set(mode='OBJECT')

    return new_bones




def create_armature_from_skin(obj):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.ops.object.skin_armature_create(modifier="Skin")

    # Get the last added object, which should be the armature
    armature_object = bpy.context.scene.objects[-1]

    # Check if the added object is actually an armature
    if not isinstance(armature_object.data, bpy.types.Armature):
        raise ValueError("The last object added is not an armature.")

    return armature_object


def add_points_to_curve_copy(curve, offset=2, name=""):
    # Create a new curve object
    curve_data = bpy.data.curves.new('curve_copy', 'CURVE')
    curve_copy = bpy.data.objects.new('curve_copy', curve_data)
    bpy.context.collection.objects.link(curve_copy)

    # Create a single spline
    spline = curve_data.splines.new('POLY')
    num_points = len(curve.data.splines[0].points) * 2 - 1
    spline.points.add(num_points - 1)  # Add the required number of points

    # Create a list of the initial points
    initial_points = list(curve.data.splines[0].points)

    for i, point in enumerate(initial_points):
        # Assign the coordinates of the original point to the spline points
        spline.points[i * 2].co = point.co.to_4d()

        # If it's not the last point, add an offset point
        if i != len(initial_points) - 1:
            # Copy the original point and offset it in the Z direction
            offset_point = point.co.to_4d()
            if "Lower" in name:
                offset_point.z += offset
            elif "Upper" in name:
                offset_point.z -= offset

            spline.points[i * 2 + 1].co = offset_point

    return curve_copy


def create_curves_for_teeth_bones(armature):
    # Create a dictionary to store the curves
    curves = {}

    # Iterate over the bones in the armature
    for bone in armature.data.bones:
        # Only process bones with names ending in "_tooth"
        # if "_tooth" in bone.name:
            # Create a new curve data and object
            curve_data = bpy.data.curves.new(bone.name + '_curve', 'CURVE')
            curve_obj = bpy.data.objects.new(bone.name + '_curve', curve_data)

            # Link the curve object to the current collection
            bpy.context.collection.objects.link(curve_obj)

            # Create a new spline in the curve
            spline = curve_data.splines.new('POLY')

            # Add an extra point to the spline
            spline.points.add(1)

            # Set the coordinates of the spline points to the head and tail of the bone
            spline.points[0].co = (bone.head_local.x, bone.head_local.y, bone.head_local.z, 1)
            spline.points[1].co = (bone.tail_local.x, bone.tail_local.y, bone.tail_local.z, 1)

            curve_obj.location = armature.location

            # Add the curve to the dictionary
            curves[bone.name] = curve_obj

    return curves



def convert_curve_to_mesh(curve, name, list_of_tooth_number, thickness_jaw):
    # Duplicate the curve
    curve_copy = curve.copy()
    curve_copy.data = curve.data.copy()  # Duplicate curve data
    bpy.context.collection.objects.link(curve_copy)  # Add duplicate to the scene

    # Convert the curve to a mesh
    bpy.ops.object.select_all(action='DESELECT')
    curve.select_set(True)
    bpy.context.view_layer.objects.active = curve
    bpy.ops.object.mode_set(mode='EDIT') 
    bpy.ops.curve.select_all(action='SELECT') 
    bpy.ops.curve.spline_type_set(type='POLY')
    bpy.ops.curve.spline_weight_set(weight=1.0)
    bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.convert(target='MESH')

    # Apply the skin modifier + ADD THICKNESS FROM TOOTH SIZE
    add_jaw_modifier(curve, thickness_jaw)

    # Create armature from skin modifier
    armature = create_armature_from_skin(curve)

    add_teeth_to_armature(armature, list_of_tooth_number=list_of_tooth_number, offset=4, name=curve.name)

    # curves_by_bones = create_curves_for_teeth_bones(armature)

    zOffset = 5.5
    yOffset = 1.5
    # Apply scale
    # curve.scale = (1, 0.9, 1)
    # Apply location transform based on jaw type
    if "Upper" in name:
        curve.location = (0, yOffset, zOffset)
        curve_copy.location = (0, 0, zOffset)
        print("Maxilla mesh generation in process")
    elif "Lower" in name:
        curve.location = (0, yOffset, -zOffset)
        curve_copy.location = (0, 0, -zOffset)
        print("Mandible mesh generation in process")

    return curve, armature, curve_copy


def add_jaw_modifier(obj, skin_thickness=19):
    skin_modifier = obj.modifiers.new('Skin', 'SKIN')
    bpy.context.object.data.use_auto_texspace = False
    bpy.context.object.data.texspace_size[0] = skin_thickness
    bpy.context.object.data.texspace_size[1] = skin_thickness

    # Set all points in the curve to use this skin size
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.transform.skin_resize(value=(skin_thickness, skin_thickness, skin_thickness))
    bpy.ops.object.mode_set(mode='OBJECT')

    # Add Subdivision Surface modifier
    subsurf_modifier = obj.modifiers.new('Subsurf', 'SUBSURF')
    subsurf_modifier.levels = 5
    subsurf_modifier.render_levels = 1


def apply_smooth(obj, factor=2.0, repeat=3):
    apply_all_modifiers(obj)
    # Ensure we're in object mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # Set the active object to the mesh object
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # Add the Smooth modifier
    smooth_mod = obj.modifiers.new(name="Smooth", type='SMOOTH')

    # Set the smooth factor
    smooth_mod.factor = factor

    # Set the smooth repetitions
    smooth_mod.iterations = repeat

    # Set the smooth factor for all axes
    smooth_mod.use_x = True
    smooth_mod.use_y = True
    smooth_mod.use_z = True

    # Update the scene
    bpy.context.view_layer.update()

    # Apply the modifier
    bpy.ops.object.modifier_apply(modifier=smooth_mod.name)


def generate_shape_key(mesh_obj, armature_obj, target_curve, deformation_curve, position, index, logarithmic_curve=False, max_distance=1.8, base=2.0):
    # Store the scale values of the original bones
    original_bone_scales = {bone: bone.scale.copy() for bone in armature_obj.pose.bones}

    
    # Duplicate the mesh object and its armature
    bpy.ops.object.select_all(action='DESELECT')
    mesh_obj.select_set(True)
    armature_obj.select_set(True)
    bpy.ops.object.duplicate(linked=False)

    # Get the duplicated mesh and armature
    duplicated_mesh = bpy.context.selected_objects[0]
    duplicated_armature = bpy.context.selected_objects[1]
    duplicated_mesh.name = f"{position}_{index}"  # Renaming the duplicated mesh

    # Clear all bone constraints from the duplicated armature
    bpy.ops.object.select_all(action='DESELECT')
    duplicated_armature.select_set(True)
    bpy.context.view_layer.objects.active = duplicated_armature

    bpy.ops.object.mode_set(mode='POSE')

    bpy.ops.pose.select_all(action='DESELECT')

    for bone in duplicated_armature.pose.bones:
        bone.scale = Vector((1, 1, 1))  # or whatever scale you want

    # Apply the original scales to the duplicated armature
    # for original_bone_name, original_scale in original_bone_scales.items():
    #     duplicated_bone = duplicated_armature.pose.bones[original_bone_name]
    #     duplicated_bone.scale = original_scale
    
    # for bone in duplicated_armature.pose.bones:
    #     bone.bone.select = True
    
    # # Scale the bones on the X and Z axes
    # bpy.ops.transform.resize(value=(1, 1, 1))

    # for bone in duplicated_armature.pose.bones:
    #     bone.select = False

    bpy.ops.pose.select_all(action='DESELECT')

    for bone in duplicated_armature.pose.bones:
        for constraint in bone.constraints:
            bone.constraints.remove(constraint)

    bpy.ops.object.mode_set(mode='OBJECT')

    # Remove the Armature modifier from the duplicated mesh
    # for mod in duplicated_mesh.modifiers:
    #     if isinstance(mod, bpy.types.ArmatureModifier) and mod.object != duplicated_armature:
    #         duplicated_mesh.modifiers.remove(mod)

    # Setup teeth deformation for the duplicated armature
    new_curve_dict = setup_teeth_deformation(duplicated_mesh, duplicated_armature, use_actual_armature=True)

    # For each curve in new_curve_dict, move it to the closest point of the target curve
    for key, curve in new_curve_dict.items():
        # Calculate the center of the curve
        curve_center = sum((point.co.xyz for point in curve.data.splines[0].points), Vector()) / len(curve.data.splines[0].points)

        # Find the closest point on deformation_curve and get its index
        closest_point_on_deformation_curve, idx = min(((point, idx) for idx, point in enumerate(deformation_curve.data.splines[0].points)), 
                                                key=lambda x: (x[0].co.xyz - curve_center).length)

        # Get the corresponding point on target_curve
        corresponding_point_on_target_curve = target_curve.data.splines[0].points[idx]

        # Calculate the displacement
        # displacement = corresponding_point_on_target_curve.co.xy - closest_point_on_deformation_curve.co.xy

        displacement = corresponding_point_on_target_curve.co.xyz - closest_point_on_deformation_curve.co.xyz
        z_displacement = corresponding_point_on_target_curve.co.z - closest_point_on_deformation_curve.co.z
        # Apply a logarithmic damping to the displacement
        if logarithmic_curve:
            displacement_length = displacement.length
            if displacement_length > 0:
                if displacement_length < 1:
                    dampened_length = displacement_length  # Do not dampen if the displacement length is smaller than 1
                else:
                    dampened_length = max_distance * math.log(displacement_length, base)
                displacement = displacement.normalized() * dampened_length
            curve.location += displacement / 2
        else:
            max_length = 5  # set your maximum length
            if displacement.length > max_length:
                displacement = displacement.normalized() * max_length
            curve.location += displacement

        curve.scale.z -= z_displacement / 32
    
    return duplicated_mesh


def extract_number(tooth):
    # Split the tooth name by 'Tooth' and '_0' to get the number
    number = int(str(tooth.name.split('Tooth')[1].split('_0')[0])[1])
    return number


def get_next_filename(directory, base_filename, extension):
    counter = 0
    while True:
        path = os.path.join(directory, f"{base_filename}_{counter}.{extension}")
        if not os.path.exists(path):
            return path
        counter += 1


def calculate_rotation(obj, limit=0.1):
    # Sort vertices based on y-value
    sorted_vertices = sorted(obj.data.vertices, key=lambda v: v.co.y)

    # Calculate the 5% index
    percent_index = int(len(sorted_vertices) * limit)

    # Get the 5% highest and lowest vertices
    highest_vertices = sorted_vertices[-percent_index:]
    lowest_vertices = sorted_vertices[:percent_index]

    # Calculate the average location of these vertices
    highest_point = [0, 0, 0]
    lowest_point = [0, 0, 0]
    for v in highest_vertices:
        for i in range(3):
            highest_point[i] += v.co[i]
    for v in lowest_vertices:
        for i in range(3):
            lowest_point[i] += v.co[i]
    highest_point = [x / len(highest_vertices) for x in highest_point]
    lowest_point = [x / len(lowest_vertices) for x in lowest_point]

    # Calculate the directional vector
    directional_vector = [h - l for h, l in zip(highest_point, lowest_point)]

    # Normalize the vector
    directional_vector = [x / np.linalg.norm(directional_vector) for x in directional_vector]

    # Calculate the rotation angle in radians
    rotation_angle_rad = math.atan2(directional_vector[2], directional_vector[1])

    # Convert the rotation angle to degrees
    # rotation_angle_deg = math.degrees(rotation_angle_rad)

    return rotation_angle_rad


def calculate_offset(obj, offset, cube_height, displacement_offset=3):
    # Sort vertices based on z-value depending on the object name
    if "Upper" in obj.name or "Maxilla" in obj.name:
        sorted_vertices = sorted(obj.data.vertices, key=lambda v: v.co.z)
    elif "Lower" in obj.name or "Mandible" in obj.name:
        sorted_vertices = sorted(obj.data.vertices, key=lambda v: v.co.z, reverse=True)
    
    # Calculate the offset vertex index
    offset_index = int((len(sorted_vertices)-1) * (1 - offset))
    
    # Calculate the cube location based on the object name and the cube's height
    if "Upper" in obj.name or "Maxilla" in obj.name:
        cube_location_z = cube_height + displacement_offset + obj.location.z - 1 + cube_height
    elif "Lower" in obj.name or "Mandible" in obj.name:
        cube_location_z = -cube_height - displacement_offset + obj.location.z - cube_height + 2

    return cube_location_z


def setup_armature_deformation(mesh_obj, armature_obj, curve_copy):
    # Move the armature depending on the object name
    armature_obj.location.z = mesh_obj.location.z

    # Select the mesh object
    bpy.context.view_layer.objects.active = mesh_obj
    mesh_obj.select_set(True)

    # Add the Armature modifier
    armature_modifier = mesh_obj.modifiers.new('Armature_Deform', 'ARMATURE')
    armature_modifier.object = armature_obj

    # Reselect the mesh object and the armature object
    bpy.ops.object.select_all(action='DESELECT')
    mesh_obj.select_set(True)
    armature_obj.select_set(True)
    bpy.context.view_layer.objects.active = armature_obj

    # Switch to Pose mode
    bpy.ops.object.mode_set(mode='POSE')

    # Create the deformation weights
    bpy.ops.object.posemode_toggle()
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    bpy.ops.object.posemode_toggle()

    # Select the last bone
    armature_obj.data.bones.active = armature_obj.data.bones[-1]

    # Add a Spline IK bone constraint
    bone_constraint = armature_obj.pose.bones[-1].constraints.new('SPLINE_IK')
    bone_constraint.target = curve_copy  # Set the duplicate curve as the target
    bone_constraint.chain_count = 50  # Set the chain length to the number of splines in the curve

    bpy.ops.object.mode_set(mode='OBJECT')


def setup_teeth_deformation(mesh_obj, armature_obj, use_actual_armature=False):
    # Move the armature depending on the object name
    armature_obj.location.z = mesh_obj.location.z

    # Select the mesh object
    bpy.context.view_layer.objects.active = mesh_obj
    mesh_obj.select_set(True)

    if not use_actual_armature:
        # Add the Armature modifier
        armature_modifier = mesh_obj.modifiers.new('Armature_Deform', 'ARMATURE')
        armature_modifier.object = armature_obj
    else:
        armature_modifier = mesh_obj.modifiers[0]

    # Create the curves for each "_tooth" bone
    bone_curves = create_curves_for_teeth_bones(armature_obj)

    # Reselect the mesh object and the armature object
    bpy.ops.object.select_all(action='DESELECT')
    mesh_obj.select_set(True)
    armature_obj.select_set(True)
    bpy.context.view_layer.objects.active = armature_obj

    # Switch to Pose mode
    bpy.ops.object.mode_set(mode='POSE')

    # Create the deformation weights
    bpy.ops.object.posemode_toggle()
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    bpy.ops.object.posemode_toggle()

    # For each bone, add a Spline IK bone constraint with its corresponding curve
    for bone_name, curve in bone_curves.items():
        bone = armature_obj.pose.bones.get(bone_name)
        if bone:
            bone_constraint = bone.constraints.new('SPLINE_IK')
            bone_constraint.target = curve
            bone_constraint.chain_count = 1  # Adjust as needed
            # Set the XZ Scale Mode to Bone Original
            bone_constraint.xz_scale_mode = 'BONE_ORIGINAL'

    # Switch back to Object mode
    bpy.ops.object.mode_set(mode='OBJECT')

    if("Mandible" in mesh_obj.name):
        move_bones(curve_dict=bone_curves, vector=(-2, 0, 0), list_of_bones=[0])
        move_bones(curve_dict=bone_curves, vector=(2, 0, 0), list_of_bones=[-1])

    return bone_curves

def scale_bones(armature_obj, scale_factor=[0, 0], list_of_bones=[], find_by_names=[]):
    # Ensure we're in object mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # Deselect all
    bpy.ops.object.select_all(action='DESELECT')

    # Set the active object to the armature object
    bpy.context.view_layer.objects.active = armature_obj
    armature_obj.select_set(True)

    # Switch to pose mode to adjust the bones
    bpy.ops.object.mode_set(mode='POSE')

    # Select the first and the last bone
    p_bones = armature_obj.pose.bones

    # Deselect all bones
    bpy.ops.pose.select_all(action='DESELECT')

    for i in list_of_bones:
        # p_bones[i].bone.select = True
        p_bones[i].scale = Vector((1 + scale_factor[0], 1, 1 + scale_factor[1]))

    # Also select the bones found by name
    for name in find_by_names:
        if name in p_bones:
            # p_bones[name].bone.select = True
            p_bones[name].scale = Vector((1 + scale_factor[0], 1, 1 + scale_factor[1]))

    # Scale the bones on the X and Z axes
    # bpy.ops.transform.resize(value=(1 + scale_factor[0], 1, 1 + scale_factor[1]))

    bpy.ops.pose.select_all(action='DESELECT')

    # Switch back to object mode
    bpy.ops.object.mode_set(mode='OBJECT')


def compute_distances(spline, list_of_names=[], teeth=[], by_distance=3.5):
    # Initialize the list of distances
    distances = {}

    # Get the list of points in the spline
    points = spline.data.splines[0].points

    # Iterate over the points in the spline, skipping the first and last points
    for i in range(len(points)):
        if(teeth[i-1].name[5:7] in list_of_names): 
            distances[i] = teeth[i-1].name[5:7]

    for i in range(1, len(points) - 1):
        # Get the current point and its neighbors
        point_before = points[i - 1].co.xyz
        point = points[i].co.xyz
        point_after = points[i + 1].co.xyz

        # Compute the midpoint between the neighbors
        midpoint = (point_before + point_after) / 2

        # Compute the distance between the current point and the midpoint
        distance = (midpoint - point).length

        # Add the distance to the list
        if(distance is not None and distance > by_distance and i not in distances.keys()): distances[i] = distance

    # Return the list of distances
    return distances


def move_bones(curve_dict, vector=(0, 0, 0), list_of_bones=[0, -1]):

    list_of_key_for_curves = list(curve_dict.keys())
    # list_of_key_for_curves = sorted(list_of_key_for_curves)

    # Set the active object to the armature object
    for i in list_of_bones:
        curve_key = list_of_key_for_curves[i]
        curve = curve_dict[curve_key]

        # Ensure we're in object mode
        bpy.ops.object.mode_set(mode='OBJECT')

        # Deselect all
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = curve
        curve.select_set(True)

        # Scale the bones on the X and Z axes
        bpy.ops.transform.translate(value=vector)

    # Switch back to object mode
    bpy.ops.object.mode_set(mode='OBJECT')


def cut_model(obj, voxel_level= 0.5, offset=0.25):

    apply_all_modifiers(obj)

    # Calculate cube dimensions and add it
    cube_height = 10
    cube_location = (0, 0, calculate_offset(obj, offset, cube_height))
    # cube_rotation = (calculate_rotation(obj), 0, 0)
    cube_rotation = (0, 0, 0)
    bpy.ops.mesh.primitive_cube_add(size=1, location=cube_location, rotation=cube_rotation)
    cube = bpy.context.active_object
    cube.scale = (100, 100, cube_height)

    # Add boolean modifier
    mod = obj.modifiers.new('Boolean', 'BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = cube

    # Add remesh modifier
    remesh_mod = obj.modifiers.new('Remesh', 'REMESH')
    remesh_mod.mode = 'VOXEL'
    remesh_mod.voxel_size = voxel_level

    apply_all_modifiers(obj)
    bpy.data.objects.remove(cube)


def apply_shrinkwrap_and_join_as_shapes(base_object, objects, output_object_name, export_path):
    bpy.context.view_layer.objects.active = base_object
    last_modified_object = None

    new_objects = []

    for obj_key in sorted(objects.keys(), key=lambda name: int(name)):
        obj = objects[obj_key]
        
        # Copy the base object
        copy = base_object.copy()
        copy.data = base_object.data.copy()  # Also duplicate the mesh data
        copy.name = f"{base_object.name}_{obj_key}"  # Naming the copy as per requirement

        # Add the copy to the scene
        bpy.context.collection.objects.link(copy)

        # Add Shrinkwrap modifier to the copy with obj as target
        shrinkwrap_modifier = copy.modifiers.new(name='Shrinkwrap', type='SHRINKWRAP')
        shrinkwrap_modifier.target = obj
        shrinkwrap_modifier.wrap_mode = 'ON_SURFACE'
        shrinkwrap_modifier.wrap_method = 'NEAREST_SURFACEPOINT'
        shrinkwrap_modifier.use_positive_direction = True
        shrinkwrap_modifier.use_negative_direction = True

        # Apply all modifiers
        bpy.context.view_layer.objects.active = copy

        copy.scale = (1.15, 1.15, 1.15)

        apply_all_modifiers(copy)

        apply_smooth(copy, factor=1, repeat=8)

        # bpy.ops.object.shade_smooth()
        apply_all_modifiers(copy)  # Using the correct function here
        
        new_objects.append(copy)
        # Save this object as the last one modified
        last_modified_object = copy
        
        # copy.name = copy.name.split('.')[0]

    base_name = base_object.name

    # sorted_objects = sorted(new_objects, key=lambda obj: int(obj.name.split('.')[0].split('_')[-1]))

    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')

    # Select objects in sorted order
    for obj in new_objects:
        # if obj.name.startswith(base_name):
        obj.select_set(True)

    # Ensure that the active object is one of the selected objects
    bpy.context.view_layer.objects.active = last_modified_object
    
    # Join as shapes
    bpy.ops.object.join_shapes()

    # Rename the final object
    last_modified_object.name = "Final"

    # Delete all objects except for last_modified_object
    for obj in bpy.data.objects:
        if obj != last_modified_object:
            bpy.data.objects.remove(obj, do_unlink=True)

    return last_modified_object

def generateJaw(folder_path, export_path='./', jaw_type="Upper"):
     # Vérifie si le paramètre jaw_type est correct
    if jaw_type not in ["Upper", "Lower"]:
        print("Error: jaw_type must be either 'Upper' or 'Lower'")
        return
    
    # Delete all objects in the scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    z_adjustement = 6
    scale_adjustement = 0.05

    for subdir, dirs, files in os.walk(folder_path):
        step = os.path.basename(subdir)
        if step != "0":
            continue
        upper_teeth = []
        lower_teeth = []
        for file in files:
            if file.endswith('.obj'):
                if 'Tooth' in file:
                    tooth_num = int(file.replace('Tooth', '').replace('.obj', ''))

                    if(jaw_type == "Upper" and 30 <= tooth_num <= 49):
                        continue
                    if(jaw_type == "Lower" and 10 <= tooth_num <= 29):
                        continue

                    file_path = os.path.join(subdir, file)
                    bpy.ops.import_scene.obj(filepath=file_path)
                    obj = bpy.context.selected_objects[0]

                    obj.name = f"{obj.name}_{step}"
                    if 10 <= tooth_num <= 29:
                        upper_teeth.append(obj)
                    elif 30 <= tooth_num <= 49:
                        lower_teeth.append(obj)
                    else:
                        print(f'Warning: Unknown tooth number {tooth_num} in file {file}')

        if upper_teeth and jaw_type == "Upper":
            # Calculate the thickness of the mandible proportional to the teeth volume
            thickness_calculate = int(calculate_total_volume(upper_teeth) / 1000)
            if(thickness_calculate < 17): thickness_calculate = 17
            if(thickness_calculate > 23): thickness_calculate = 23
            thickness_jaw = thickness_calculate + 15
            # Generate the curve to begin the mesh generation
            curve_upper, name_upper, list_of_tooth_number_upper = create_curve(upper_teeth, 'Upper')
            # Convert the curve to mesh by using modifiers like skin modifier
            curve_upper, armature_upper, deformation_curve_upper = convert_curve_to_mesh(curve_upper, name_upper, list_of_tooth_number_upper, thickness_jaw)

            # Increase the back length of the gum
            # find_and_deform_back(curve_upper, deformation_vector=(0, 1, 0))

            # Add a clipping and remesh the result
            cut_model(curve_upper)
            # Lengthen the flat part of the mesh
            deform_lengthen(curve_upper)
            
            # Apply smooth for improve deformation conditions
            apply_smooth(curve_upper)

            # bpy.data.objects.remove(armature_upper, do_unlink=True)


        if lower_teeth and jaw_type == "Lower":
            # Calculate the thickness of the mandible proportional to the teeth volume
            thickness_calculate = int(calculate_total_volume(lower_teeth) / 1000)
            if(thickness_calculate < 17): thickness_calculate = 17
            if(thickness_calculate > 23): thickness_calculate = 23
            thickness_jaw = thickness_calculate + 15
            # Generate the curve to begin the mesh generation
            curve_lower, name_lower, list_of_tooth_number_lower = create_curve(lower_teeth, 'Lower')

            
            # Convert the curve to mesh by using modifiers like skin modifier
            curve_lower, armature_lower, deformation_curve_lower = convert_curve_to_mesh(curve_lower, name_lower, list_of_tooth_number_lower, thickness_jaw)

            # Increase the back length of the gum
            # find_and_deform_back(curve_lower, deformation_vector=(0, 1, 0), use_scale=True)
            # Add a clipping and remesh the result
            cut_model(curve_lower)
            # Lengthen the flat part of the mesh
            deform_lengthen(curve_lower)
            
            # Apply smooth for improve deformation conditions
            apply_smooth(curve_lower)
            
    upper_list = {}
    lower_list = {}

    main_mesh = curve_upper if jaw_type == "Upper" else curve_lower
    # main_mesh = None

    for subdir, dirs, files in os.walk(folder_path):
        step = os.path.basename(subdir)
        
        for file in files:
            if file.endswith('.obj'):
                if((jaw_type == "Upper" and 'Maxilla' in file) or (jaw_type == "Lower" and 'Mandible' in file)):

                    file_path = os.path.join(subdir, file)
                    bpy.ops.import_scene.obj(filepath=file_path)
                    obj = bpy.context.selected_objects[0]
                    obj.name = f"{obj.name}_{step}"
                    if(jaw_type == "Upper"):
                        upper_list[step] = obj
                    if(jaw_type == "Lower"):
                        lower_list[step] = obj 
                    cut_model(obj, voxel_level=0.25)
                    apply_smooth(obj, factor=1, repeat=10)

                    # if step == "0":
                    #     main_mesh = obj


    main_mesh.name = "Maxilla" if jaw_type == "Upper" else "Mandible"
    # Iterate through sorted dictionary keys
    if(jaw_type == "Upper"):
        main_mesh = apply_shrinkwrap_and_join_as_shapes(main_mesh, upper_list, "Maxilla", export_path=export_path)
        pass

    if(jaw_type == "Lower"):
        main_mesh = apply_shrinkwrap_and_join_as_shapes(main_mesh, lower_list, "Mandible", export_path=export_path)
        pass
    # Switch back to object mode
    bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.select_all(action='DESELECT')

    #/////////////////////////////////////////////////

    if(jaw_type == "Upper"): export_to_glb([main_mesh], name="Maxilla", filepath=export_path)
    if(jaw_type == "Lower"): export_to_glb([main_mesh], name="Mandible", filepath=export_path)

    # if(jaw_type == "Upper"):
    #     current_directory = get_absolute_path(export_path)
    #     base_filename = "jaw_maxilla"
    # else:
    #     current_directory = get_absolute_path(export_path)
    #     base_filename = "jaw_mandible"

    # blend_file_path = get_next_filename(current_directory, base_filename, "blend")
    # bpy.ops.wm.save_as_mainfile(filepath=blend_file_path)


if __name__ == "__main__":
    export_path = sys.argv[-2]
    load_path = sys.argv[-3]
    sideGenerated = sys.argv[-1]
    
    generateJaw(load_path, export_path, sideGenerated)

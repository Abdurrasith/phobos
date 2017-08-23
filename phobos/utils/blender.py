#!/usr/bin/python
# coding=utf-8

"""
.. module:: phobos.utils.blender
    :platform: Unix, Windows, Mac
    :synopsis: This module contains functions o manipulate blender objects and interact with blender functionalities

.. moduleauthor:: Kai von Szadowski, Ole Schwiegert

Copyright 2014, University of Bremen & DFKI GmbH Robotics Innovation Center

This file is part of Phobos, a Blender Add-On to edit robot models.

Phobos is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License
as published by the Free Software Foundation, either version 3
of the License, or (at your option) any later version.

Phobos is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with Phobos.  If not, see <http://www.gnu.org/licenses/>.
"""

import bpy
import phobos.defs as defs
import phobos.model.materials as materials
from phobos.phoboslog import log


def getBlenderVersion():
    return bpy.app.version[0] * 100 + bpy.app.version[1]


def printMatrices(obj, info=None):
    """This function prints the matrices of an object to the screen.

    :param obj: The object to print the matrices from.
    :type obj: bpy.types.Object
    :param info: If True the objects name will be included into the printed info.
    :type info: bool

    """
    if not info:
        info = obj.name
    print("\n----------------", info, "---------------------\n",
          "local:\n", obj.matrix_local,
          "\n\nworld:\n", obj.matrix_world,
          "\n\nparent_inverse:\n", obj.matrix_parent_inverse,
          "\n\nbasis:\n", obj.matrix_basis)


def createPrimitive(pname, ptype, psize, player=0, pmaterial="None", plocation=(0, 0, 0), protation=(0, 0, 0),
                    verbose=False):
    """Generates the primitive specified by the input parameters

    :param pname: The primitives new name.
    :type pname: str
    :param ptype: The new primitives type. Can be one of *box, sphere, cylinder, cone, disc*
    :type ptype: str
    :param psize: The new primitives size. Depending on the ptype it can be either a single float or a tuple.
    :type psize: float or list
    :param player: The layer bitmask for the new blender object.
    :param pmaterial: The new primitives material.
    :param plocation: The new primitives location.
    :type plocation: tuple
    :param protation: The new primitives rotation.
    :type protation: tuple
    :return: bpy.types.Object - the new blender object.

    """
    if verbose:
        log(ptype + psize, "INFO", "createPrimitive")
    try:
        # n_layer = bpy.context.scene.active_layer
        n_layer = int(player)
    except ValueError:
        n_layer = defs.layerTypes[player]
    players = defLayers([n_layer])
    bpy.context.scene.layers[n_layer] = True  # the layer has to be active to prevent problems with object placement
    if ptype == "box":
        bpy.ops.mesh.primitive_cube_add(layers=players, location=plocation, rotation=protation)
        obj = bpy.context.object
        obj.dimensions = psize
    if ptype == "sphere":
        bpy.ops.mesh.primitive_uv_sphere_add(size=psize, layers=players, location=plocation, rotation=protation)
    elif ptype == "cylinder":
        bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=psize[0], depth=psize[1], layers=players,
                                            location=plocation, rotation=protation)
    elif ptype == "cone":
        bpy.ops.mesh.primitive_cone_add(vertices=32, radius=psize[0], depth=psize[1], cap_end=True, layers=players,
                                        location=plocation, rotation=protation)
    elif ptype == 'disc':
        bpy.ops.mesh.primitive_circle_add(vertices=psize[1], radius=psize[0], fill_type='TRIFAN', location=plocation,
                                          rotation=protation, layers=players)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj = bpy.context.object
    obj.name = pname
    if pmaterial != 'None':
        materials.assignMaterial(obj, pmaterial)
    return obj


def setObjectLayersActive(obj):
    for l in range(len(obj.layers)):
        bpy.context.scene.layers[l] &= obj.layers[l]


def toggleLayer(index, value=None):
    """ This function toggles a specific layer or sets it to a desired value.

    :param index: The layer index you want to change.
    :type index: int
    :param value: True if visible, None for toggle.
    :type value: bool

    """
    if value:
        bpy.context.scene.layers[index] = value
    else:
        bpy.context.scene.layers[index] = not bpy.context.scene.layers[index]


def defLayers(layerlist):
    """Returns a list of 20 elements encoding the visible layers according to layerlist

    """
    if type(layerlist) is not list:
        layerlist = [layerlist]
    layers = 20 * [False]
    for layer in layerlist:
        layers[layer] = True
    return layers


def updateTextFile(textfilename, newContent):
    """This function updates a blender textfile or creates a new one if it is not existent.

    :param textfilename: The blender textfiles file name.
    :type textfilename: str
    :param newContent: The textfiles new content.
    :type newContent: str

    """
    try:
        bpy.data.texts.remove(bpy.data.texts[textfilename])
    except KeyError:
        pass #Not important. Just create.
    createNewTextfile(textfilename, newContent)


def readTextFile(textfilename):
    """This function returns the content of a specified text file.

    :param textfilename: The blender textfiles name.
    :type textfilename: str
    :return: str - the textfiles content.

    """
    try:
        return "\n".join([l.body for l in bpy.data.texts[textfilename].lines])
    except KeyError:
        log("No text file " + textfilename + " found. Setting", "ERROR")
        return ""


def createNewTextfile(textfilename, contents):
    """This function creates a new blender text file with the given content.

    :param textfilename: The new blender texts name.
    :type textfilename: str
    :param contents: The new textfiles content.
    :type contents: str

    """
    for text in bpy.data.texts:
        text.tag = True
    bpy.ops.text.new()
    newtext = None
    for text in bpy.data.texts:
        if not text.tag:
            newtext = text
    for text in bpy.data.texts:
        text.tag = False
    newtext.name = textfilename
    bpy.data.texts[textfilename].write(contents)


def openScriptInEditor(scriptname):
    """This function opens a script/textfile in an open blender text window. Nothing happens if there is no
    available text window.

    :param scriptname: The scripts name.
    :type scriptname: str

    """
    if scriptname in bpy.data.texts:
        for area in bpy.context.screen.areas:
            if area.type == 'TEXT_EDITOR':
                area.spaces.active.text = bpy.data.texts[scriptname]
    else:
        log("There is no script named " + scriptname + "!", "ERROR")


def cleanObjectProperties(props):
    """Cleans a predefined list of Blender-specific or other properties from the dictionary.

    """
    getridof = ['phobostype', '_RNA_UI', 'cycles_visibility', 'startChain', 'endChain', 'masschanged']
    if props:
        for key in getridof:
            if key in props:
                del props[key]
    return props


def cleanScene():
    """This function cleans up the scene and removes all blender objects, meshes, materials and lights.

    """
    # select all objects
    bpy.ops.object.select_all(action="SELECT")

    # and delete them
    bpy.ops.object.delete()

    # after that we have to clean up all loaded meshes (unfortunately
    # this is not done automatically)
    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh)

    # and all materials
    for material in bpy.data.materials:
        bpy.data.materials.remove(material)

    # and all lights (aka lamps)
    for lamp in bpy.data.lamps:
        bpy.data.lamps.remove(lamp)


def createPreview(objects, export_path, modelname, previewfile, render_resolution=256):
    """Creates a thumbnail of the given objects.

    :param obj: List of objects for the thumbnail.
    :type obj: list
    :param Resolution used for the render.
    :type int

    """
    bpy.ops.view3d.camera_to_view_selected()
    bpy.data.cameras[0].type = 'ORTHO' #'PANO'
    #bpy.ops.render.opengl() (nice and fast and needs no light but needs viewport to be square shaped to zoom in!)
    bpy.ops.render.render()

    cam_ob = bpy.context.scene.camera
    # cam = bpy.data.cameras.new("Camera")
    # delete_cam = False
    if not cam_ob:
        log("No Camera found! Can not create thumbnail", "WARNING", __name__ + ".bakeModel")
        return
        #cam_ob = bpy.data.objects.new("Camera", cam)
        #bpy.context.scene.objects.link(cam_ob)
        #delete_cam = True
    #bpy.context.scene.camera = cam_ob

    log("Creating thumbnail of model: "+modelname, "INFO",__name__+".bakeModel")
    # hide all other objects from rendering
    for ob in bpy.data.objects:
        if not (ob in objects) and not(ob.type == 'LAMP'):
            ob.hide_render = True
            ob.hide = True

    # set render settings
#    bpy.context.scene.render.resolution_x = render_resolution
#    bpy.context.scene.render.resolution_y = render_resolution
#    bpy.context.scene.render.resolution_percentage = 100
    # render
    #bpy.ops.render.render(use_viewport=True)
    bpy.ops.render.opengl(view_context=True)
    # save image
    bpy.context.scene.render.image_settings.file_format = 'PNG'
#    bpy.data.images['Render Result'].file_format = bpy.context.scene.render.image_settings.file_format

    #print(bpy.data.images['Render Result'].file_format)
    log("saving preview to: "+os.path.join(export_path,previewfile+'.png'), "INFO",__name__+".bakeModel")

    bpy.data.images['Render Result'].save_render(os.path.join(export_path,previewfile+'.png'))


    # make all objects visible again
    for ob in bpy.data.objects:
        ob.hide_render = False
        ob.hide = False

    # delete camera if needed
    #if delete_cam:
    #    bpy.ops.object.select_all(action='DESELECT')
    #    cam_ob.select = True
    #    bpy.ops.object.delete()
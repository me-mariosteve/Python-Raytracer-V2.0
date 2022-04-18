#! /bin/env python

import numpy as np
import matplotlib.pyplot as plt
import time

from vector_class import *
from objects_class import *
from textures_class import *
from shaders_class import *

# Functions=============================================================================================================================

def saveImage(image, width, height):
    imageName = input("Your image name:")

    path = 'Results/'
    fileName = path + imageName + '(%dX%d).png' % (width, height)
    plt.imsave(fileName, image)
    print("Your image was successfully saved! \nPath: " + fileName)

def render(dimensions: tuple, FOV: int, worldInfos: tuple, parameters: dict): 
    """Dimensions: tuple(height, width)
    FOV: Field Of View
    worldInfos: tuple(Objects, Lights, SkyDiffuse, Camera)
        objects: List containing all scene Objects
        lights: List containing all scene Lights
        skyDiffuse: color of the sky: Vector(red, green, blue) (value between 0 and 1)
        camera: dict(position: Vector, direction: Vector)
    parameters: dict(maxReflection: int, indirectLightingMaxBounces: int, indirectLightingSamples: int, Lighting: str)
        Lighting: type of render:
            Direct: Only direct lighting (sharp and black shadows)
            Indirect: Only Inderect Lighting (sky light and less light)
            Global: Direct and Inderirect lighting
    """
    actualTime = time.time()

    """worldInfos: [objects, light, slyDiffuse, camera]"""
    image: array = np.zeros((dimensions[1], dimensions[0], 3))

    ratio = float(dimensions[0]) / dimensions[1]
    screen = (-1, 1/ratio, 1, -1/ratio)


    for i, y in enumerate(np.linspace(screen[1], screen[3], dimensions[1])):
        for j, x in enumerate(np.linspace(screen[0], screen[2], dimensions[0])):

            # Creates vectors
            pixel = Vector(x, y, -FOV) + worldInfos[3]["position"]

            origin = worldInfos[3]["position"]
            direction = Vector.normalize(pixel - origin)
            #direction = Vector.normalize(direction + worldInfos[3]["direction"])

            nearestObject, minDistance, normal = nearestIntersectedObject(worldInfos[0], origin, direction)

            if nearestObject is None:
                color = worldInfos[2]
            else:
                intersection = origin + direction * minDistance

                color = nearestObject.shader(direction, intersection, normal, worldInfos, parameters, "all")


            # post-process
            """
            exposure = 0.66
            color.x = -(1.0 - math.exp(color.x * exposure))# + 1
            color.y = -(1.0 - math.exp(color.y * exposure))# + 1
            color.z = -(1.0 - math.exp(color.z * exposure))# + 1
            """

            gamma = 1
            color = color ** gamma

            #clip color between 0 and 1
            color.clip(0, 1)
            image[i, j] = [color.x, color.y, color.z]
        print("%d/%d" % (i+1, dimensions[1]))

    return image, time.time() - actualTime


# Main Script=============================================================================================================================
parameters = {"maxReflections": 0, "indirectLightingMaxBounces": 0, "indirectLightingSamples": 0, "Lighting": "Direct"}

width, height = 480, 360
maxDepth = 3

camera = {"position": Vector(0, 0, .8), "direction": Vector(0, 0, 0)}
FOVP = 1

objects = [
    Sphere(Vector(-0.2, 0, -1), 0.7, DiffuseShader(Vector(0.1, 0, 0), Vector(0.7, 0, 0), 0.1)),
    Sphere(Vector(0.1, -0.3, 0), 0.1, DefaultShader(Vector(0.1, 0, 0.1), Vector(0.7, 0, 0.7), Vector(1, 1, 1), 100, 0.1)),
    Sphere(Vector(-0.3, 0, 0), 0.15, DefaultShader(Vector(0, 0.1, 0), Vector(0, 0.6, 0), Vector(1, 1, 1), 100, 0.3)),
    Triangle(Vector(0, 1, 1.5), Vector(-1, 0, 0), Vector(1, 0, 0), DiffuseShader(Vector(0.1, 0.1, 0.1), Vector(1, 1, 1), 0)),
    Plane(Vector(0, 1, 0), 0.6,
        DefaultShader(
            Vector(0.1, 0.1, 0.1),
            SquareTexture(0.2,
                          Vector(1, 1, 1),
                          Vector(0, 0, 0)
                          ),
            Vector(1, 1, 1), 100, 0.5
        )
    )
    #ImportedOBJ("OBJImports/cube.obj", Vector(-.2, 0, -1), .5, DiffuseShader(Vector(.1, .1, .1), Vector(.5, .5, .5), 0)),
    ]
light = { 'position': Vector(5, 5, 5), 'ambient': Vector(1, 1, 1), 'diffuse': Vector(1, 1, 1), 'specular': Vector(1, 1, 1) }

skyDiffuse = Vector(0.41, 0.72, 1)
#skyDiffuse = Vector(0, 0, 0)

image = np.zeros((height, width, 3))

# Main loop
if __name__ == "__main__":

    render, time = render((width, height), FOVP, (objects, light, skyDiffuse, camera), parameters)
    print("Render finished! It tooks ",time, "seconds.")
    saveImage(render, width, height)


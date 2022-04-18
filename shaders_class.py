import math
import numpy as np
from random import random, uniform
from copy import copy

from objects_class import *
from vector_class import *
from textures_class import *


def nearestIntersectedObject(objects, rayOrigin, rayDirection):
    distances = []
    normals = []
    for obj in objects:
            distance, normal = obj.intersect(rayOrigin, rayDirection)
            distances.append(distance)
            normals.append(normal)

    nearestObject = None
    minDistance = np.inf
    normalToSurface = Vector(0, 0, 0)
    for i, distance in enumerate(distances):
        if distance and distance < minDistance:
            minDistance = distance
            nearestObject = objects[i]
            normalToSurface = normals[i]

    return nearestObject, minDistance, normalToSurface

# Indirect lighting functions  =======================================================================================================

def DiffuseIndirectLightning(position, normal, worldInfos, parameters):
    newParameters = copy(parameters)
    newParameters["maxReflections"] = 0
    newParameters["indirectLightingMaxBounces"] -= 1
    newParameters["directLightingShadows"] = True
    indirectLightning = Vector(0, 0, 0)

    for i in range(parameters["indirectLightingSamples"]):
        # Generate random normalized vector in half sphere
        randVector = Vector(uniform(-1, 1), uniform(-1, 1), uniform(0, 1)).normalize()

        # Rotate vector by the normal
        randVector = randVector.rotate(normal)

        # Calculate ray (with position=shiftedPoint)
        nearestObject, minDistance, objectNormal = nearestIntersectedObject(worldInfos[0], position, randVector)
        if nearestObject is None:
            indirectLightning += worldInfos[2]
        else:
            intersection = position + randVector * minDistance
            illumination = nearestObject.shader(randVector, intersection, worldInfos, newParameters, "diffuse")

            intersectionToLight = Vector.normalize(worldInfos[1]["position"]- (intersection + normal * 1e-5))
            indirectLightning += illumination * math.cos(Vector.dotProduct(intersectionToLight, objectNormal))

    indirectLightning /= parameters["indirectLightingSamples"]
    return indirectLightning


def ambientOcclusion(position, normal, worldInfos, parameters):
    aoFactor = 0

    for i in range(parameters["indirectLightingSamples"]):
        # Generate random normalized vector in half sphere
        randVector = Vector(uniform(-1, 1), uniform(-1, 1), uniform(0, 1)).normalize()

        # Rotate vector by the normal
        randVector = randVector.rotate(normal)

        # Calculate distance from nearest object
        a, minDistance, a = nearestIntersectedObject(worldInfos[0], position, randVector)

    aoFactor = aoFactor / parameters["indirectLightingSamples"]



# Basic shaders functions   ===========================================================================================================
def calculateDiffuse(position, direction, worldInfos):
    pass


# Shader class  =======================================================================================================================

# Default Shader
class DefaultShader:

    def __init__(self, ambient:Vector, diffuse:Vector, specular:Vector, shininess:float, reflection:float):
        """ambient: Color without lighting
        diffuse: Color with lighting
        specular: specular color
        shininess: factor of specular
        reflection: mix factor between its color and its reflection
        """
        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular
        self.shininess = shininess
        self.reflection = reflection

    def calculate(self, rayDirection, intersection, normal, worldInfos, parameters, renderMode):
        
        objects, light, backgroundColor, camera = worldInfos[0], worldInfos[1], worldInfos[2], worldInfos[3]

        newParameters = copy(parameters)
        newParameters["maxReflections"] -= 1
        

        shiftedPoint = intersection + normal * 1e-5
        intersectionToLight = Vector.normalize(light["position"] - shiftedPoint)

        _a, minDistance, _b = nearestIntersectedObject(objects, shiftedPoint, intersectionToLight)
        intersectionToLightDistance = Vector.length(light["position"] - intersection)
        isShadowed = minDistance < intersectionToLightDistance

        if parameters["Lighting"]=="Direct" and isShadowed:
            return Vector(0, 0, 0)

        illumination = Vector(0, 0, 0)

        # Ambient
        if renderMode=="ambient"  or renderMode=="all":
            illumination += self.ambient.getColor(intersection) * light["ambient"]

        # Diffuse
        if renderMode=="diffuse" or renderMode=="all":
            lighting = Vector(0, 0, 0)
            if parameters["indirectLightingMaxBounces"]>0 and parameters["Lighting"]=="Indirect":
                #lighting += DiffuseIndirectLightning(intersection, normal, worldInfos, newParameters)
                lighting *= AmbientOcclusion(intersection, normal, worldInfos, newParameters)

            if not(isShadowed) and parameters["Lighting"]=="Direct":
                lighting += light["diffuse"] * Vector.dotProduct(intersectionToLight, normal)

            illumination += self.diffuse.getColor(intersection) * lighting 

        # Specular
        if renderMode=="specular"  or renderMode=="all":
            intersectionToCamera = Vector.normalize(camera["position"] - intersection)
            h = Vector.normalize(intersectionToLight + intersectionToCamera)
            illumination += self.specular.getColor(intersection) * lighting * Vector.dotProduct(normal, h) ** (self.shininess / 4)

        # Shadows
        """if renderMode=="all":
            if isShadowed:
               illumination = illumination / 2
        """

        # Reflections
        if parameters["maxReflections"]>0 and self.reflection>0:
            direction = rayDirection - normal * 2 * Vector.dotProduct(rayDirection, normal)
            nearestObject, minDistance, objectNormal = nearestIntersectedObject(objects, shiftedPoint, direction)
            if nearestObject is None:
                return illumination + backgroundColor * self.reflection
            else:
                intersection = shiftedPoint + direction * minDistance
                reflectionColor = nearestObject._shader.calculate(direction, intersection, objectNormal, worldInfos, newParameters, renderMode)
                return illumination + reflectionColor * self.reflection
        else:
            return illumination

# Diffuse Shader
class DiffuseShader:
    
    def __init__(self, ambient:Vector, diffuse:Vector, reflection:float):
        """ambient: Color without lighting
        diffuse: Color with lighting
        reflection: mix factor between its color and its reflection
        """
        self.ambient = ambient
        self.diffuse = diffuse
        self.reflection = reflection

    def calculate(self, rayDirection, intersection, normal, worldInfos, parameters, renderMode):
        objects, light, backgroundColor, camera = worldInfos[0], worldInfos[1], worldInfos[2], worldInfos[3]

        newParameters = copy(parameters)
        newParameters["maxReflections"] -= 1
        

        shiftedPoint = intersection + normal * 1e-5
        intersectionToLight = Vector.normalize(light["position"] - shiftedPoint)

        _a, minDistance, _b = nearestIntersectedObject(objects, shiftedPoint, intersectionToLight)
        intersectionToLightDistance = Vector.length(light["position"] - intersection)
        isShadowed = minDistance < intersectionToLightDistance

        if parameters["Lighting"]=="Direct" and isShadowed:
            return Vector(0, 0, 0)

        illumination = Vector(0, 0, 0)

        # Ambient
        if renderMode=="ambient"  or renderMode=="all":
            illumination += self.ambient.getColor(intersection) * light["ambient"]

        # Diffuse
        if renderMode=="diffuse" or renderMode=="all":
            lighting = Vector(0, 0, 0)
            if parameters["indirectLightingMaxBounces"]>0 and parameters["Lighting"]!="Direct":
                #lighting += DiffuseIndirectLightning(intersection, normal, worldInfos, newParameters)
                lighting *= AmbientOcclusion(intersection, normal, worldInfos, newParameters)

            if not(isShadowed) and parameters["Lighting"]!="Indirect":
                lighting += light["diffuse"] * Vector.dotProduct(intersectionToLight, normal)

            illumination += self.diffuse.getColor(intersection) * lighting

        # Shadows
        """if renderMode=="all":
            if isShadowed:
               illumination = illumination / 2
        """

        # Reflections
        #print(parameters["maxReflections"])
        if parameters["maxReflections"]>0 and self.reflection>0:
            direction = rayDirection - normal * 2 * Vector.dotProduct(rayDirection, normal)
            nearestObject, minDistance, objectNormal = nearestIntersectedObject(objects, shiftedPoint, direction)
            if nearestObject is None:
                return illumination + backgroundColor * self.reflection
            else:
                intersection = shiftedPoint + direction * minDistance
                reflectionColor = nearestObject._shader.calculate(direction, intersection, objectNormal, worldInfos, newParameters, renderMode)
                return illumination + reflectionColor * self.reflection
        else:
            return illumination

# Glass Shader
class GlassShader:
    
    def __init__(self, ambient, diffuse, reflection):
        self.ambient = ambient
        self.diffuse = diffuse
        self.reflection = reflection

    def calculate(self, rayDirection, intersection, normal, worldInfos, parameters, renderMode):
        objects, light, backgroundColor, camera = worldInfos[0], worldInfos[1], worldInfos[2], worldInfos[3]
        

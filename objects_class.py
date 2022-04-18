import math
import numpy as np

from vector_class import Vector
#from shader_class import Default


# Class Sphere
class Sphere:

    def __init__(self, center:Vector, radius:float, shader):
        self.center = center
        self.radius = radius
        self._shader = shader

    def intersect(self, rayOrigin, rayDirection):
        b = rayDirection.dotProduct(rayOrigin - self.center) * 2
        c = Vector.length(rayOrigin - self.center) ** 2 - self.radius ** 2
        delta = b ** 2 - 4 * c

        if delta > 0:
            t1 = (-b + math.sqrt(delta)) / 2
            t2 = (-b - math.sqrt(delta)) / 2

            if t1 > 0 and t2 > 0:
                intersection = rayOrigin + rayDirection * min(t1, t2)
                normal = Vector.normalize(intersection - self.center)
                return min(t1, t2), normal

        return None, None
        
    def shader(self, rayDirection, intersection, normal, worldInfos, parameters, renderMode):

        return self._shader.calculate(rayDirection, intersection, normal, worldInfos, parameters, renderMode)


# Class Plane
class Plane:

    def __init__(self, normal: Vector, distance: float, shader):
        """normal: normalized vector, orientation of the plane
        distance: distance of the plane from the scene origin, aligned on the normal
        """
        self.normal = normal.normalize()
        self.distance = distance
        self._shader = shader

    def intersect(self, rayOrigin, rayDirection):
        dotDir = self.normal.dotProduct(rayDirection)
        dot = self.normal.dotProduct(rayOrigin)
        dist = (dot + self.distance) / dotDir

        if dotDir!=0 and dist<0:
            return -dist, self.normal

        else: return None, None

    def shader(self, rayDirection, intersection, normal, worldInfos, parameters, renderMode):

        return self._shader.calculate(rayDirection, intersection, self.normal, worldInfos, parameters, renderMode)


class ImportedOBJ:
    
    def __init__(self, path: str, position: Vector, size: float, shader):
        
        self._shader = shader
        vertices = []
        self.faces = []
        
        f = open(path)
        for line in f:
            if line[:2] == "v ":
                print("v")
                index1 = line.find(" ") + 1
                index2 = line.find(" ", index1 + 1)
                index3 = line.find(" ", index2 + 1)

                vertex = (
                    Vector(
                        float(line[index1:index2]),
                        float(line[index2:index3]),
                        float(line[index3:-index1])
                    ).round(2) + position
                ) * size
                vertices.append(vertex)

            elif line[:2] == "f ":
                print("f")
                string = line.replace("//", "/")
                i = string.find(" ") + 1
                face = []
                for item in range(string.count(" ")):
                    if string.find(" ", i) == -1:
                        print(string[i:-1])
                        face.append(vertices[int(string[i:-1])-1])
                        break
                    face.append(vertices[int(string[i:string.find(" ", i)])-1])
                    i = string.find(" ", i) + 1
                self.faces.append(Triangle(face[0], face[1], face[2], None))

        print(len(self.faces))

    def intersect(self, rayOrigin, rayDirection):
        distances = []
        normals = []
        for triangle in self.faces:
            distance, normal = triangle.intersect(rayOrigin, rayDirection)
            print(normal)
            distances.append(distance)
            normals.append(normal)

        minDistance = np.inf
        for i, distance in enumerate(distances):
            if distance and distance < minDistance:
                print("obj import")
                minDistance = distance
                normalToSurface = normals[i]

        return minDistance, normalToSurface

    def shader(self, rayDirection, intersection, normal, worldInfos, parameters, renderMode):

        return self._shader.calculate(rayDirection, intersection, normal, worldInfos, parameters, renderMode)


class Triangle():
    def __init__(self, point1:Vector, point2:Vector, point3:Vector, shader):
        self.p1 = point1
        self.p2 = point2
        self.p3 = point3
        self._shader = shader

    def intersect(self, rayOrigin, rayDirection):
        p1p2 = self.p2 - self.p1
        p1p3 = self.p3 - self.p1

        normal = p1p2.crossProduct(p1p3)
        denom = normal.dotProduct(normal)

        # find P
        normalDotRayDir = normal.dotProduct(rayDirection)
        if  abs(normalDotRayDir) < 1e-8:
            return None, None

        # find D
        D = normal.dotProduct(self.p1)

        #find t
        t = (normal.dotProduct(rayOrigin) + D) / normalDotRayDir
        # check if triangle is behind the ray
        if t < 0:
            return None, None

        # compute intersection point
        P = rayOrigin + rayDirection * t

        # edge 1
        edge1 = self.p2 - self.p1
        vp1 = P - self.p1
        C = edge1.crossProduct(vp1)
        if normal.dotProduct(C) < 0:
            return None, None

        # edge 2
        edge2 = self.p3 - self.p2
        vp2 = P - self.p2
        C = edge2.crossProduct(vp2)
        #u = normal.dotProduct(C)
        if normal.dotProduct(C) < 0:
            return None, None

        # edge 3
        edge3 = self.p1 - self.p3
        vp3 = P - self.p3
        C = edge3.crossProduct(vp3)
        #v = normal.dotProduct(C)
        if normal.dotProduct(C) < 0:
            return None, None

        return t, -normal
        #u /= denom
        #v /= denom

    def shader(self, rayDirection, intersection, normal, worldInfos, parameters, renderMode):

        return self._shader.calculate(rayDirection, intersection, normal, worldInfos, parameters, renderMode)

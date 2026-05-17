import numpy as np

def polygon_properties(vertices):
    """
    Calcula área, centroide y momentos de inercia (Ix, Iy, Ixy) de un polígono
    dado por una lista de vértices (x,y) en orden (antihorario u horario).
    Retorna (area, centroide, Ix, Iy, Ixy) respecto al origen (0,0).
    """
    n = len(vertices)
    if n < 3:
        raise ValueError("Se necesitan al menos 3 vértices")
    area = 0.0
    Cx = 0.0
    Cy = 0.0
    Ix = 0.0
    Iy = 0.0
    Ixy = 0.0
    for i in range(n):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i+1) % n]
        f = x1*y2 - x2*y1
        area += f
        Cx += (x1 + x2) * f
        Cy += (y1 + y2) * f
        Ix += (y1**2 + y1*y2 + y2**2) * f
        Iy += (x1**2 + x1*x2 + x2**2) * f
        Ixy += (x1*y2 + 2*x1*y1 + 2*x2*y2 + x2*y1) * f
    area = abs(area) / 2.0
    if area == 0:
        raise ValueError("Área cero")
    Cx = abs(Cx) / (6.0 * area)
    Cy = abs(Cy) / (6.0 * area)
    Ix = abs(Ix) / 12.0
    Iy = abs(Iy) / 12.0
    Ixy = abs(Ixy) / 24.0
    # Trasladar momentos al centroide (teorema de Steiner)
    Ix_c = Ix - area * Cy**2
    Iy_c = Iy - area * Cx**2
    Ixy_c = Ixy - area * Cx * Cy
    return area, (Cx, Cy), Ix_c, Iy_c, Ixy_c


class SubArea:
    def __init__(self, tipo, params, vertices, es_vacio=False):
        self.tipo = tipo          # 'rectangulo', 'triangulo', 'circulo'
        self.params = params      # diccionario con parámetros originales (para referencia)
        self.vertices = vertices  # lista de (x,y) para polígonos, None para círculo
        self.es_vacio = es_vacio
        # Calcular propiedades geométricas
        if tipo == 'circulo':
            radio = params['radio']
            centro = (params['cx'], params['cy'])
            self.area = np.pi * radio**2
            self.centroide = np.array(centro)
            self.Ix_local = (np.pi * radio**4) / 4
            self.Iy_local = self.Ix_local
            self.Ixy_local = 0.0
        else:
            # polígono: rectángulo o triángulo (o cualquier polígono dado por vértices)
            area, centroide, Ix, Iy, Ixy = polygon_properties(vertices)
            self.area = area
            self.centroide = np.array(centroide)
            self.Ix_local = Ix
            self.Iy_local = Iy
            self.Ixy_local = Ixy

    def get_area_efectiva(self):
        return -self.area if self.es_vacio else self.area

    def momento_inercia_local(self):
        return self.Ix_local, self.Iy_local


class SeccionCompuesta:
    def __init__(self):
        self.subareas = []

    def agregar_subarea(self, subarea):
        self.subareas.append(subarea)

    def calcular_propiedades(self):
        A_total = 0.0
        sum_xA = 0.0
        sum_yA = 0.0
        for sa in self.subareas:
            A_efect = sa.get_area_efectiva()
            A_total += A_efect
            sum_xA += A_efect * sa.centroide[0]
            sum_yA += A_efect * sa.centroide[1]
        if A_total == 0:
            raise ValueError("Área total cero")
        xc = sum_xA / A_total
        yc = sum_yA / A_total

        Ix_total = 0.0
        Iy_total = 0.0
        Ixy_total = 0.0
        for sa in self.subareas:
            A_efect = sa.get_area_efectiva()
            dx = sa.centroide[0] - xc
            dy = sa.centroide[1] - yc
            Ix_loc, Iy_loc = sa.momento_inercia_local()
            Ix_total += Ix_loc + A_efect * dy**2
            Iy_total += Iy_loc + A_efect * dx**2
            Ixy_total += A_efect * dx * dy

        I_prom = (Ix_total + Iy_total) / 2
        R = np.sqrt(((Ix_total - Iy_total)/2)**2 + Ixy_total**2)
        I_max = I_prom + R
        I_min = I_prom - R
        if Ixy_total == 0 and Ix_total >= Iy_total:
            theta = 0
        elif Ixy_total == 0 and Ix_total < Iy_total:
            theta = np.pi/2
        else:
            theta = 0.5 * np.arctan2(2*Ixy_total, Ix_total - Iy_total)

        return {
            'area': A_total,
            'centroide': (xc, yc),
            'Ix': Ix_total,
            'Iy': Iy_total,
            'Ixy': Ixy_total,
            'I_max': I_max,
            'I_min': I_min,
            'angulo_principal': np.degrees(theta)
        }
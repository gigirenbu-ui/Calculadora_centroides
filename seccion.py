import numpy as np

def convex_hull(pts):
    pts = list(set(pts))
    if len(pts) < 3:
        return pts
    start = min(pts, key=lambda p: (p[1], p[0]))
    def angle(p):
        return np.arctan2(p[1] - start[1], p[0] - start[0])
    pts_sorted = sorted(pts, key=lambda p: (angle(p), (p[0]-start[0])**2 + (p[1]-start[1])**2))
    hull = []
    for p in pts_sorted:
        while len(hull) >= 2 and cross(hull[-2], hull[-1], p) <= 0:
            hull.pop()
        hull.append(p)
    return hull

def cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

def polygon_properties(vertices):
    hull = convex_hull(vertices)
    if len(hull) < 3:
        raise ValueError("Se necesitan al menos 3 vértices no colineales.")
    n = len(hull)
    area = 0.0
    Cx = 0.0
    Cy = 0.0
    Ix = 0.0
    Iy = 0.0
    Ixy = 0.0
    
    for i in range(n):
        x1, y1 = hull[i]
        x2, y2 = hull[(i+1) % n]
        f = x1*y2 - x2*y1
        area += f
        Cx += (x1 + x2) * f
        Cy += (y1 + y2) * f
        Ix += (y1**2 + y1*y2 + y2**2) * f
        Iy += (x1**2 + x1*x2 + x2**2) * f
        Ixy += (x1*y2 + 2*x1*y1 + 2*x2*y2 + x2*y1) * f

    A_signed = area / 2.0
    if abs(A_signed) < 1e-9:
        raise ValueError("Área cero. Verifique los puntos.")
    
    Cx = Cx / (6.0 * A_signed)
    Cy = Cy / (6.0 * A_signed)
    
    signo = np.sign(A_signed)
    Ix = (Ix / 12.0) * signo
    Iy = (Iy / 12.0) * signo
    Ixy = (Ixy / 24.0) * signo  
    
    area_abs = abs(A_signed)
    
    Ix_c = Ix - area_abs * Cy**2
    Iy_c = Iy - area_abs * Cx**2
    Ixy_c = Ixy - area_abs * Cx * Cy
    
    return area_abs, (Cx, Cy), Ix_c, Iy_c, Ixy_c

class SubArea:
    def __init__(self, tipo, params, vertices, es_vacio=False):
        self.tipo = tipo
        self.params = params if params is not None else {}
        self.vertices = vertices
        self.es_vacio = es_vacio
        
        if tipo == 'circulo':
            radio = self.params['radio']
            centro = (self.params['cx'], self.params['cy'])
            self.area = np.pi * radio**2
            self.centroide = np.array(centro)
            self.Ix_local = (np.pi * radio**4) / 4
            self.Iy_local = self.Ix_local
            self.Ixy_local = 0.0  
            
        elif tipo == 'semicirculo':
            p1 = np.array(vertices[0])
            p2 = np.array(vertices[1])
            
            diametro = np.linalg.norm(p2 - p1)
            if diametro < 1e-9:
                raise ValueError("Los dos vértices del semicírculo no pueden ser el mismo punto.")
            radio = diametro / 2.0
            self.area = (np.pi * radio**2) / 2.0
            
            p_medio = (p1 + p2) / 2.0
            
            vector_base = p2 - p1
            
            # Control direccional
            orientacion = self.params.get('orientacion', 'Arriba')
            if orientacion == 'Arriba':
                vector_deseado = np.array([0.0, 1.0])
            elif orientacion == 'Abajo':
                vector_deseado = np.array([0.0, -1.0])
            elif orientacion == 'Izquierda':
                vector_deseado = np.array([-1.0, 0.0])
            elif orientacion == 'Derecha':
                vector_deseado = np.array([1.0, 0.0])
            else:
                vector_deseado = np.array([0.0, 1.0])

            normal_geometrica = np.array([-vector_base[1], vector_base[0]])
            norma = np.linalg.norm(normal_geometrica)
            if norma > 1e-9:
                normal_geometrica = normal_geometrica / norma

            if np.dot(normal_geometrica, vector_deseado) < 0:
                normal_geometrica = -normal_geometrica
            
            d_centroide = (4.0 * radio) / (3.0 * np.pi)
            self.centroide = p_medio + d_centroide * normal_geometrica
            
            angulo_normal = np.arctan2(normal_geometrica[1], normal_geometrica[0])
            angulo_render_deg = np.degrees(angulo_normal) - 90.0
            
            self.Ix_local = (np.pi / 8.0 - 8.0 / (9.0 * np.pi)) * (radio**4)
            self.Iy_local = (np.pi * (radio**4)) / 8.0
            self.Ixy_local = 0.0 
            
            self.params = {
                'radio': radio,
                'p_medio': p_medio,
                'angulo_base': angulo_render_deg,
                'p1': p1,
                'p2': p2,
                'orientacion': orientacion
            }
            
        else:
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
            A_ef = sa.get_area_efectiva()
            A_total += A_ef
            sum_xA += A_ef * sa.centroide[0]
            sum_yA += A_ef * sa.centroide[1]
            
        if abs(A_total) < 1e-9:
            raise ValueError("Área total cero o insignificante")
            
        xc = sum_xA / A_total
        yc = sum_yA / A_total

        Ix_total = 0.0
        Iy_total = 0.0
        Ixy_total = 0.0
        
        for sa in self.subareas:
            factor = -1.0 if sa.es_vacio else 1.0
            dx = sa.centroide[0] - xc
            dy = sa.centroide[1] - yc
            
            Ix_loc, Iy_loc = sa.momento_inercia_local()
            Ixy_loc = sa.Ixy_local
            
            Ix_total += factor * (Ix_loc + sa.area * dy**2)
            Iy_total += factor * (Iy_loc + sa.area * dx**2)
            Ixy_total += factor * (Ixy_loc + sa.area * dx * dy)

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
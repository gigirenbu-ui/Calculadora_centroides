import numpy as np

class SubArea:
    def __init__(self, tipo, params, centroide_local, area, es_vacio=False):
        self.tipo = tipo
        self.params = params
        self.centroide_local = np.array(centroide_local)
        self.area = area
        self.es_vacio = es_vacio

    def get_area_efectiva(self):
        return -self.area if self.es_vacio else self.area

    def momento_inercia_local(self):
        if self.tipo == 'rectangulo':
            b = self.params['ancho']
            h = self.params['alto']
            Ix = (b * h**3) / 12
            Iy = (h * b**3) / 12
        elif self.tipo == 'circulo':
            r = self.params['radio']
            Ix = (np.pi * r**4) / 4
            Iy = Ix
        elif self.tipo == 'triangulo':
            b = self.params['base']
            h = self.params['altura']
            Ix = (b * h**3) / 36
            Iy = (h * b**3) / 36
        else:
            raise ValueError(f"Tipo {self.tipo} no implementado")
        return Ix, Iy

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
            sum_xA += A_efect * sa.centroide_local[0]
            sum_yA += A_efect * sa.centroide_local[1]
        if A_total == 0:
            raise ValueError("Área total cero")
        xc = sum_xA / A_total
        yc = sum_yA / A_total

        Ix_total = 0.0
        Iy_total = 0.0
        Ixy_total = 0.0
        for sa in self.subareas:
            A_efect = sa.get_area_efectiva()
            dx = sa.centroide_local[0] - xc
            dy = sa.centroide_local[1] - yc
            Ix_local, Iy_local = sa.momento_inercia_local()
            Ix_total += Ix_local + A_efect * dy**2
            Iy_total += Iy_local + A_efect * dx**2
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
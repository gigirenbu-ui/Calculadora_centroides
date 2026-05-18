import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.patches import Polygon as MplPolygon, Circle as MplCircle, PathPatch
from matplotlib.path import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
                             QLabel, QLineEdit, QComboBox, QGroupBox, QFormLayout,
                             QHeaderView, QMessageBox, QFrame)
from PyQt5.QtCore import Qt

from seccion import SeccionCompuesta, SubArea

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Propiedades Geométricas - Sección Compuesta")
        self.setGeometry(100, 100, 1500, 800)
        self.seccion = SeccionCompuesta()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout_principal = QHBoxLayout(central_widget)

        # Panel izquierdo: dibujo
        panel_izquierdo = QWidget()
        layout_izq = QVBoxLayout(panel_izquierdo)
        self.figure = plt.Figure(figsize=(7, 7), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout_izq.addWidget(self.canvas)
        layout_principal.addWidget(panel_izquierdo, 3)

        # Panel derecho: controles
        panel_derecho = QWidget()
        panel_derecho.setMaximumWidth(750)
        layout_der = QVBoxLayout(panel_derecho)

        grupo_agregar = QGroupBox("Agregar Subárea")
        form_layout = QFormLayout()

        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["Rectángulo", "Triángulo", "Círculo", "Semicírculo"])
        form_layout.addRow("Tipo:", self.tipo_combo)

        # Círculo (radio, centro)
        self.radio_label = QLabel("Radio (cm):")
        self.radio_input = QLineEdit()
        self.centro_label = QLabel("Centro (X, Y):")
        self.centro_x_input = QLineEdit("0")
        self.centro_y_input = QLineEdit("0")
        centro_layout = QHBoxLayout()
        centro_layout.addWidget(QLabel("X:"))
        centro_layout.addWidget(self.centro_x_input)
        centro_layout.addWidget(QLabel("Y:"))
        centro_layout.addWidget(self.centro_y_input)
        form_layout.addRow(self.centro_label, centro_layout)
        form_layout.addRow(self.radio_label, self.radio_input)

        # Grupo dinámico para vértices (Rectángulo, Triángulo, Semicírculo)
        self.vertices_group = QGroupBox("Coordenadas")
        self.vertices_group.setVisible(False)
        self.vertices_layout = QVBoxLayout(self.vertices_group)
        self.vertices_widgets = []  # lista de (x_input, y_input)
        self.construir_vertices_dinamicos(4)  # por defecto
        form_layout.addRow(self.vertices_group)

        # Tipo de área
        self.vacio_check = QComboBox()
        self.vacio_check.addItems(["Positivo", "Vacío"])
        form_layout.addRow("Tipo de área:", self.vacio_check)

        self.btn_agregar = QPushButton("Agregar Subárea")
        form_layout.addRow(self.btn_agregar)

        grupo_agregar.setLayout(form_layout)
        layout_der.addWidget(grupo_agregar)

        # Tabla
        self.tabla_resultados = QTableWidget()
        self.tabla_resultados.setColumnCount(6)
        self.tabla_resultados.setHorizontalHeaderLabels(["Figura", "Área (cm²)", "x̄ (cm)", "ȳ (cm)", "x̄·A", "ȳ·A"])
        self.tabla_resultados.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout_der.addWidget(QLabel("Cálculo del Centroide:"))
        layout_der.addWidget(self.tabla_resultados)

        self.btn_calcular = QPushButton("Calcular y Dibujar")
        layout_der.addWidget(self.btn_calcular)

        self.resultados_label = QLabel("Resultados:\n")
        self.resultados_label.setWordWrap(True)
        layout_der.addWidget(self.resultados_label)

        self.btn_limpiar = QPushButton("Limpiar todas las subáreas")
        layout_der.addWidget(self.btn_limpiar)

        layout_principal.addWidget(panel_derecho, 2)

        # Conexiones
        self.tipo_combo.currentTextChanged.connect(self.actualizar_campos_por_tipo)
        self.btn_agregar.clicked.connect(self.agregar_subarea)
        self.btn_calcular.clicked.connect(self.calcular_y_dibujar)
        self.btn_limpiar.clicked.connect(self.limpiar_todo)

        self.actualizar_campos_por_tipo()

    def construir_vertices_dinamicos(self, num_puntos):
        """Crea num_puntos pares de campos X e Y, etiquetados según el tipo de figura."""
        for i in reversed(range(self.vertices_layout.count())):
            widget = self.vertices_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        self.vertices_widgets.clear()

        tipo = self.tipo_combo.currentText()
        etiquetas = []
        if tipo == "Rectángulo":
            etiquetas = ["Vértice 1", "Vértice 2", "Vértice 3", "Vértice 4"]
        elif tipo == "Triángulo":
            etiquetas = ["Vértice 1", "Vértice 2", "Vértice 3"]
        elif tipo == "Semicírculo":
            etiquetas = ["Punto inicial (A)", "Punto final (B)", "Punto medio (C)"]
        else:
            etiquetas = [f"Punto {i+1}" for i in range(num_puntos)]

        for i in range(num_puntos):
            frame = QFrame()
            frame_layout = QHBoxLayout(frame)
            label = QLabel(etiquetas[i] + ":")
            x_input = QLineEdit()
            x_input.setPlaceholderText("X")
            y_input = QLineEdit()
            y_input.setPlaceholderText("Y")
            frame_layout.addWidget(label)
            frame_layout.addWidget(x_input)
            frame_layout.addWidget(QLabel(","))
            frame_layout.addWidget(y_input)
            frame_layout.addStretch()
            self.vertices_layout.addWidget(frame)
            self.vertices_widgets.append((x_input, y_input))

    def actualizar_campos_por_tipo(self):
        tipo = self.tipo_combo.currentText()
        if tipo == "Círculo":
            self.vertices_group.setVisible(False)
            self.radio_label.setVisible(True)
            self.radio_input.setVisible(True)
            self.centro_label.setVisible(True)
            self.centro_x_input.setVisible(True)
            self.centro_y_input.setVisible(True)
        else:
            self.vertices_group.setVisible(True)
            self.radio_label.setVisible(False)
            self.radio_input.setVisible(False)
            self.centro_label.setVisible(False)
            self.centro_x_input.setVisible(False)
            self.centro_y_input.setVisible(False)
            if tipo == "Rectángulo":
                num = 4
            elif tipo == "Triángulo":
                num = 3
            elif tipo == "Semicírculo":
                num = 3
            else:
                num = 3
            self.construir_vertices_dinamicos(num)

    def obtener_puntos_desde_inputs(self):
        puntos = []
        for i, (x_input, y_input) in enumerate(self.vertices_widgets):
            x_text = x_input.text().strip()
            y_text = y_input.text().strip()
            if not x_text or not y_text:
                raise ValueError(f"Faltan coordenadas para el punto {i+1}")
            x = float(x_text)
            y = float(y_text)
            puntos.append((x, y))
        return puntos

    def calcular_propiedades_semicirculo(self, A, B, C):
        """Calcula área, centroide y momentos de inercia de un semicírculo definido por tres puntos."""
        # Vector AB (base)
        AB = (B[0]-A[0], B[1]-A[1])
        diametro = np.hypot(AB[0], AB[1])
        radio = diametro / 2.0
        if radio == 0:
            raise ValueError("Puntos inicial y final coinciden")
        # Centro de la base
        centro_base = ((A[0]+B[0])/2.0, (A[1]+B[1])/2.0)
        # Vector perpendicular a AB (hacia C)
        # Vector de centro_base a C
        vector_centro_C = (C[0]-centro_base[0], C[1]-centro_base[1])
        # Proyección para determinar la dirección del arco (el semicírculo se dibuja hacia C)
        # Necesitamos la distancia perpendicular (debe ser radio si C está bien elegido)
        # No verificamos estrictamente, asumimos que C define el lado del arco.
        # Calculamos el ángulo de la base
        angulo_base = np.arctan2(AB[1], AB[0])
        # El centro del círculo completo está en: centro_base + (radio * vector_unitario perpendicular)
        # Determinamos el lado: tomamos la dirección de centro_base a C, la normalizamos y multiplicamos por radio
        dist_centro_C = np.hypot(vector_centro_C[0], vector_centro_C[1])
        if dist_centro_C < 1e-9:
            raise ValueError("El punto medio C no puede estar sobre la base")
        # Vector perpendicular unitario (hacia C)
        perp_x = vector_centro_C[0] / dist_centro_C
        perp_y = vector_centro_C[1] / dist_centro_C
        centro_circulo = (centro_base[0] + perp_x * radio, centro_base[1] + perp_y * radio)
        # El área del semicírculo es (π * r^2)/2
        area = np.pi * radio**2 / 2.0
        # Centroide del semicírculo respecto al centro del círculo:
        # Para un semicírculo (con base horizontal y arco arriba) el centroide está a 4r/(3π) desde el centro de la base hacia el arco.
        # Distancia desde centro_base hacia el arco: 4r/(3π)
        dist_centroide_base = 4 * radio / (3 * np.pi)
        # El vector dirección hacia el arco es el mismo perpendicular unitario hacia C
        centroide_x = centro_base[0] + perp_x * dist_centroide_base
        centroide_y = centro_base[1] + perp_y * dist_centroide_base
        # Momentos de inercia respecto al centroide del semicírculo (orientado horizontalmente, base abajo)
        # Fórmulas para semicírculo con base en el eje X y centroide en (0, 4r/(3π))
        # Ix_c = (π r^4)/8 - (8 r^4)/(9π)  (momento respecto a eje horizontal que pasa por centroide)
        # Iy_c = (π r^4)/8
        # Ixy_c = 0 para esta orientación
        Ix_local = (np.pi * radio**4) / 8 - (8 * radio**4) / (9 * np.pi)
        Iy_local = (np.pi * radio**4) / 8
        Ixy_local = 0.0
        # Rotar momentos según el ángulo de la base + 90° (porque el semicírculo tiene su base horizontal en la orientación local)
        # La base del semicírculo local se considera horizontal. El ángulo de la base en el plano es angulo_base.
        # El semicírculo local tiene su base horizontal, y su "arriba" es el eje Y positivo.
        # Para rotar a la orientación real: debemos rotar los ejes de inercia.
        # La orientación del semicírculo: la base (línea AB) es horizontal en la orientación local? No: localmente la base es horizontal.
        # En el plano, la base tiene ángulo angulo_base. Entonces el sistema local está rotado en angulo_base.
        # Además, el arco apunta hacia la dirección del vector perpendicular (que es angulo_base + 90° si el arco está "arriba")
        # En nuestras fórmulas locales, asumimos que el arco apunta en dirección +Y (ángulo 90°). Por lo tanto, la rotación total es: theta = angulo_base + 90°?
        # En realidad: localmente, base horizontal (ángulo 0), arco hacia +Y (ángulo 90). En el plano, la base tiene ángulo angulo_base,
        # y el arco apunta hacia el ángulo que calculamos para el vector perpendicular. Por tanto, la rotación de la figura es exactamente angulo_perp = atan2(perp_y, perp_x)
        # pero cuidado: el eje local X sigue la base, el local Y sigue el arco.
        # El ángulo de rotación de la figura desde la orientación base horizontal es angulo_base.
        # No obstante, los momentos de inercia rotados se calculan como:
        # Ix' = Ix cos^2θ + Iy sin^2θ - 2 Ixy sinθ cosθ
        # Iy' = Ix sin^2θ + Iy cos^2θ + 2 Ixy sinθ cosθ
        # Ixy' = (Ix - Iy) sinθ cosθ + Ixy (cos^2θ - sin^2θ)
        # Usamos Ixy_local=0, Ix_local e Iy_local.
        # El ángulo de rotación: θ = angulo_base (alinear la base con el eje X local)
        # Pero cuidado: la base local horizontal, al rotarla por θ, queda como la base real.
        # El eje Y local (hacia el arco) queda perpendicular, que coincide con la dirección del vector perpendicular (hacia C).
        # Esto es correcto.
        theta = angulo_base
        cos_t = np.cos(theta)
        sin_t = np.sin(theta)
        Ix_rot = Ix_local * cos_t**2 + Iy_local * sin_t**2
        Iy_rot = Ix_local * sin_t**2 + Iy_local * cos_t**2
        Ixy_rot = (Ix_local - Iy_local) * sin_t * cos_t
        return area, (centroide_x, centroide_y), Ix_rot, Iy_rot, Ixy_rot, (centro_base, radio, perp_x, perp_y, angulo_base, A, B, C)

    def agregar_subarea(self):
        try:
            tipo = self.tipo_combo.currentText()
            es_vacio = (self.vacio_check.currentText() == "Vacío")
            if tipo == "Círculo":
                radio = float(self.radio_input.text())
                cx = float(self.centro_x_input.text())
                cy = float(self.centro_y_input.text())
                params = {'radio': radio, 'cx': cx, 'cy': cy}
                sa = SubArea('circulo', params, None, es_vacio)
            elif tipo == "Semicírculo":
                puntos = self.obtener_puntos_desde_inputs()
                if len(puntos) != 3:
                    raise ValueError("Se requieren exactamente 3 puntos")
                A, B, C = puntos
                area, centroide, Ix, Iy, Ixy, extra = self.calcular_propiedades_semicirculo(A, B, C)
                params = {
                    'area': area,
                    'centroide': centroide,
                    'Ix': Ix,
                    'Iy': Iy,
                    'Ixy': Ixy,
                    'extra': extra  # guardar datos para dibujo
                }
                sa = SubArea('semicirculo', params, [A, B, C], es_vacio)
                # Reemplazar momentos locales por los calculados (el constructor por defecto no los calcula)
                sa.area = area
                sa.centroide = np.array(centroide)
                sa.Ix_local = Ix
                sa.Iy_local = Iy
                # El producto Ixy_local se almacena en un atributo adicional (si se necesita para rotaciones)
                sa.Ixy_local = Ixy
            else:
                puntos = self.obtener_puntos_desde_inputs()
                if tipo == "Rectángulo" and len(puntos) != 4:
                    raise ValueError("El rectángulo debe tener 4 vértices")
                if tipo == "Triángulo" and len(puntos) != 3:
                    raise ValueError("El triángulo debe tener 3 vértices")
                params = {'vertices_manual': puntos}
                sa = SubArea(tipo.lower(), params, puntos, es_vacio)
            self.seccion.agregar_subarea(sa)
            self.actualizar_tabla()
            self.calcular_y_dibujar()
        except ValueError as e:
            QMessageBox.critical(self, "Error de datos", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo agregar la figura:\n{str(e)}")

    def actualizar_tabla(self):
        self.tabla_resultados.setRowCount(len(self.seccion.subareas))
        suma_A = 0
        suma_xA = 0
        suma_yA = 0
        for i, sa in enumerate(self.seccion.subareas):
            area_efectiva = sa.get_area_efectiva()
            x_cent = sa.centroide[0]
            y_cent = sa.centroide[1]
            xA = area_efectiva * x_cent
            yA = area_efectiva * y_cent
            suma_A += area_efectiva
            suma_xA += xA
            suma_yA += yA
            nombre = f"{sa.tipo.capitalize()} {'(vacío)' if sa.es_vacio else ''}"
            self.tabla_resultados.setItem(i, 0, QTableWidgetItem(nombre))
            self.tabla_resultados.setItem(i, 1, QTableWidgetItem(f"{area_efectiva:.2f}"))
            self.tabla_resultados.setItem(i, 2, QTableWidgetItem(f"{x_cent:.2f}"))
            self.tabla_resultados.setItem(i, 3, QTableWidgetItem(f"{y_cent:.2f}"))
            self.tabla_resultados.setItem(i, 4, QTableWidgetItem(f"{xA:.2f}"))
            self.tabla_resultados.setItem(i, 5, QTableWidgetItem(f"{yA:.2f}"))
        self.tabla_resultados.setRowCount(len(self.seccion.subareas) + 1)
        self.tabla_resultados.setItem(len(self.seccion.subareas), 0, QTableWidgetItem("TOTAL"))
        self.tabla_resultados.setItem(len(self.seccion.subareas), 1, QTableWidgetItem(f"{suma_A:.2f}"))
        self.tabla_resultados.setItem(len(self.seccion.subareas), 2, QTableWidgetItem(""))
        self.tabla_resultados.setItem(len(self.seccion.subareas), 3, QTableWidgetItem(""))
        self.tabla_resultados.setItem(len(self.seccion.subareas), 4, QTableWidgetItem(f"{suma_xA:.2f}"))
        self.tabla_resultados.setItem(len(self.seccion.subareas), 5, QTableWidgetItem(f"{suma_yA:.2f}"))

    def calcular_y_dibujar(self):
        if not self.seccion.subareas:
            self.resultados_label.setText("No hay subáreas agregadas.")
            self.figure.clear()
            self.canvas.draw()
            return
        try:
            props = self.seccion.calcular_propiedades()
            texto = (f"Centroide global: ({props['centroide'][0]:.2f}, {props['centroide'][1]:.2f}) cm\n"
                     f"Área total: {props['area']:.2f} cm²\n"
                     f"Ix: {props['Ix']:.2f} cm⁴\n"
                     f"Iy: {props['Iy']:.2f} cm⁴\n"
                     f"Ixy: {props['Ixy']:.2f} cm⁴\n"
                     f"I máx: {props['I_max']:.2f} cm⁴\n"
                     f"I mín: {props['I_min']:.2f} cm⁴\n"
                     f"Ángulo ejes principales: {props['angulo_principal']:.2f}°")
            self.resultados_label.setText(texto)
            self.dibujar_seccion(props)
            self.actualizar_tabla()
        except Exception as e:
            self.resultados_label.setText(f"Error en cálculo: {str(e)}")

    def dibujar_seccion(self, props):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_aspect('equal')
        ax.grid(True, linestyle='--', alpha=0.7, zorder=0)
        ax.set_xlabel("x (cm)")
        ax.set_ylabel("y (cm)")
        ax.set_title("Sección Compuesta")

        for sa in self.seccion.subareas:
            color = 'lightgray' if not sa.es_vacio else 'white'
            edgecolor = 'black'
            alpha = 0.6 if not sa.es_vacio else 0.8
            if sa.tipo == 'circulo':
                radio = sa.params['radio']
                cx, cy = sa.centroide
                circle = MplCircle((cx, cy), radio, facecolor=color, edgecolor=edgecolor, alpha=alpha)
                ax.add_patch(circle)
                ax.plot(cx, cy, 'bo', markersize=4, alpha=0.7)
            elif sa.tipo == 'semicirculo':
                extra = sa.params['extra']
                A, B, C = sa.vertices
                centro_base, radio, perp_x, perp_y, angulo_base, _, _, _ = extra
                # Dibujar línea de base
                ax.plot([A[0], B[0]], [A[1], B[1]], color='black', linewidth=2)
                # Dibujar arco semicircular: ángulos desde 0 a 180 grados en el sistema local
                # El centro del círculo está en (centro_base_x + perp_x*radio, centro_base_y + perp_y*radio)
                centro_circulo = (centro_base[0] + perp_x * radio, centro_base[1] + perp_y * radio)
                # El ángulo de la base local (eje X) es angulo_base. El arco va desde angulo_base hasta angulo_base+π
                start_angle = angulo_base
                end_angle = angulo_base + np.pi
                # Generar puntos del arco
                theta = np.linspace(start_angle, end_angle, 50)
                x_arc = centro_circulo[0] + radio * np.cos(theta)
                y_arc = centro_circulo[1] + radio * np.sin(theta)
                ax.plot(x_arc, y_arc, color='black', linewidth=2)
                # Rellenar el semicírculo
                # Para relleno, creamos un polígono con la base y el arco
                vertices_poly = [(A[0], A[1])] + list(zip(x_arc, y_arc)) + [(B[0], B[1])]
                from matplotlib.patches import Polygon
                semicircle_poly = Polygon(vertices_poly, facecolor=color, edgecolor='none', alpha=alpha)
                ax.add_patch(semicircle_poly)
                # Punto de referencia (opcional)
                ax.plot(C[0], C[1], 'bo', markersize=4, alpha=0.7)
            else:
                # Polígonos (rectángulo, triángulo)
                hull = None
                if sa.tipo == 'rectangulo' or sa.tipo == 'triangulo':
                    from seccion import convex_hull
                    hull = convex_hull(sa.vertices)
                else:
                    hull = sa.vertices
                polygon = MplPolygon(hull, facecolor=color, edgecolor=edgecolor, alpha=alpha)
                ax.add_patch(polygon)

        # Centroide global
        cx_glob, cy_glob = props['centroide']
        ax.plot(cx_glob, cy_glob, 'ro', markersize=8, label='Centroide global')

        # Límites
        x_vals = [0]; y_vals = [0]
        for sa in self.seccion.subareas:
            if sa.tipo == 'circulo':
                r = sa.params['radio']
                cx, cy = sa.centroide
                x_vals.extend([cx - r, cx + r])
                y_vals.extend([cy - r, cy + r])
            elif sa.tipo == 'semicirculo':
                extra = sa.params['extra']
                centro_base, radio, _, _, _, A, B, C = extra
                x_vals.extend([A[0], B[0], C[0]])
                y_vals.extend([A[1], B[1], C[1]])
                # también el arco aproximadamente
                for ang in np.linspace(0, np.pi, 20):
                    x = centro_base[0] + radio * np.cos(ang)
                    y = centro_base[1] + radio * np.sin(ang)
                    x_vals.append(x)
                    y_vals.append(y)
            else:
                for v in sa.vertices:
                    x_vals.append(v[0]); y_vals.append(v[1])
        if x_vals and y_vals:
            x_min, x_max = min(x_vals), max(x_vals)
            y_min, y_max = min(y_vals), max(y_vals)
            margin_x = 0.2 * (x_max - x_min) if (x_max - x_min) != 0 else 5
            margin_y = 0.2 * (y_max - y_min) if (y_max - y_min) != 0 else 5
            ax.set_xlim(x_min - margin_x, x_max + margin_x)
            ax.set_ylim(y_min - margin_y, y_max + margin_y)

        # Ejes cartesianos
        ax.axhline(0, color='black', linewidth=1.5, linestyle='-', zorder=1)
        ax.axvline(0, color='black', linewidth=1.5, linestyle='-', zorder=1)

        # Ejes principales
        ang = np.radians(props['angulo_principal'])
        xrange = ax.get_xlim()[1] - ax.get_xlim()[0]
        yrange = ax.get_ylim()[1] - ax.get_ylim()[0]
        L = min(xrange, yrange) * 0.6
        dx1 = L * np.cos(ang); dy1 = L * np.sin(ang)
        dx2 = L * np.cos(ang + np.pi/2); dy2 = L * np.sin(ang + np.pi/2)
        ax.plot([cx_glob - dx1, cx_glob + dx1], [cy_glob - dy1, cy_glob + dy1],
                'g-', linewidth=2, label='Eje principal 1')
        ax.plot([cx_glob - dx2, cx_glob + dx2], [cy_glob - dy2, cy_glob + dy2],
                'b-', linewidth=2, label='Eje principal 2')
        ax.legend()
        self.canvas.draw()

    def limpiar_todo(self):
        self.seccion.subareas.clear()
        self.tabla_resultados.setRowCount(0)
        self.resultados_label.setText("Resultados:\n")
        self.figure.clear()
        self.canvas.draw()

def run():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
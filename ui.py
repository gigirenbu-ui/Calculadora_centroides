import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.patches import Polygon as MplPolygon, Circle as MplCircle
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

        # Panel derecho: controles y tablas
        panel_derecho = QWidget()
        panel_derecho.setMaximumWidth(950)
        layout_der = QVBoxLayout(panel_derecho)

        # Grupo agregar subárea
        grupo_agregar = QGroupBox("Agregar Subárea")
        form_layout = QFormLayout()

        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["Rectángulo", "Triángulo", "Círculo"])
        form_layout.addRow("Tipo:", self.tipo_combo)

        # Círculo
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

        # Vértices dinámicos
        self.vertices_group = QGroupBox("Vértices (ingresar en cualquier orden)")
        self.vertices_group.setVisible(False)
        self.vertices_layout = QVBoxLayout(self.vertices_group)
        self.vertices_widgets = []
        self.construir_vertices_dinamicos(4)
        form_layout.addRow(self.vertices_group)

        # Tipo de área
        self.vacio_check = QComboBox()
        self.vacio_check.addItems(["Positivo", "Vacío"])
        form_layout.addRow("Tipo de área:", self.vacio_check)

        self.btn_agregar = QPushButton("Agregar Subárea")
        form_layout.addRow(self.btn_agregar)

        grupo_agregar.setLayout(form_layout)
        layout_der.addWidget(grupo_agregar)

        # Tabla de centroides
        self.tabla_resultados = QTableWidget()
        self.tabla_resultados.setColumnCount(7)
        self.tabla_resultados.setHorizontalHeaderLabels([
            "Figura", "Área (cm²)", "Centroide (x, y)", "x̄ (cm)", "ȳ (cm)", "x̄·A", "ȳ·A"
        ])
        self.tabla_resultados.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout_der.addWidget(QLabel("Cálculo del Centroide:"))
        layout_der.addWidget(self.tabla_resultados)

        # Tabla de momentos (Teorema de Steiner) con intercambio de columnas
        self.tabla_momentos = QTableWidget()
        self.tabla_momentos.setColumnCount(8)
        self.tabla_momentos.setHorizontalHeaderLabels([
            "Figura", "Área (cm²)", "Ix_local (cm⁴)", "Iy_local (cm⁴)",
            "dₓ² (cm²)", "dᵧ² (cm²)", "dₓ²·A (cm⁴)", "dᵧ²·A (cm⁴)"
        ])
        self.tabla_momentos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout_der.addWidget(QLabel("Cálculo de Momentos de Inercia (Teorema de Steiner):"))
        layout_der.addWidget(self.tabla_momentos)

        # Botón calcular
        self.btn_calcular = QPushButton("Calcular y Dibujar")
        layout_der.addWidget(self.btn_calcular)

        # Resultados resumidos
        self.resultados_label = QLabel("Resultados:\n")
        self.resultados_label.setWordWrap(True)
        layout_der.addWidget(self.resultados_label)

        # Botón limpiar
        self.btn_limpiar = QPushButton("Limpiar todas las subáreas")
        layout_der.addWidget(self.btn_limpiar)

        layout_principal.addWidget(panel_derecho, 2)

        # Conexiones
        self.tipo_combo.currentTextChanged.connect(self.actualizar_campos_por_tipo)
        self.btn_agregar.clicked.connect(self.agregar_subarea)
        self.btn_calcular.clicked.connect(self.calcular_y_dibujar)
        self.btn_limpiar.clicked.connect(self.limpiar_todo)

        self.actualizar_campos_por_tipo()

    def construir_vertices_dinamicos(self, num_vertices):
        for i in reversed(range(self.vertices_layout.count())):
            widget = self.vertices_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        self.vertices_widgets.clear()
        tipo = self.tipo_combo.currentText()
        if tipo == "Rectángulo":
            etiquetas = ["Vértice 1", "Vértice 2", "Vértice 3", "Vértice 4"]
        elif tipo == "Triángulo":
            etiquetas = ["Vértice 1", "Vértice 2", "Vértice 3"]
        else:
            etiquetas = [f"Vértice {i+1}" for i in range(num_vertices)]
        for i in range(num_vertices):
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
            num = 4 if tipo == "Rectángulo" else 3
            self.construir_vertices_dinamicos(num)

    def obtener_vertices_desde_inputs(self):
        vertices = []
        for i, (x_input, y_input) in enumerate(self.vertices_widgets):
            x_text = x_input.text().strip()
            y_text = y_input.text().strip()
            if not x_text or not y_text:
                raise ValueError(f"Faltan coordenadas para el vértice {i+1}")
            vertices.append((float(x_text), float(y_text)))
        return vertices

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
            else:
                vertices = self.obtener_vertices_desde_inputs()
                if tipo == "Rectángulo" and len(vertices) != 4:
                    raise ValueError("El rectángulo necesita 4 vértices")
                if tipo == "Triángulo" and len(vertices) != 3:
                    raise ValueError("El triángulo necesita 3 vértices")
                params = {'vertices_manual': vertices}
                sa = SubArea(tipo.lower(), params, vertices, es_vacio)
            self.seccion.agregar_subarea(sa)
            self.calcular_y_dibujar()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def actualizar_tabla_centroides(self):
        self.tabla_resultados.setRowCount(len(self.seccion.subareas))
        suma_A = 0.0
        suma_xA = 0.0
        suma_yA = 0.0
        for i, sa in enumerate(self.seccion.subareas):
            A_ef = sa.get_area_efectiva()
            xc = sa.centroide[0]
            yc = sa.centroide[1]
            xA = A_ef * xc
            yA = A_ef * yc
            suma_A += A_ef
            suma_xA += xA
            suma_yA += yA
            nombre = f"{sa.tipo.capitalize()} {'(vacío)' if sa.es_vacio else ''}"
            centroide_str = f"({xc:.2f}, {yc:.2f})"
            self.tabla_resultados.setItem(i, 0, QTableWidgetItem(nombre))
            self.tabla_resultados.setItem(i, 1, QTableWidgetItem(f"{A_ef:.2f}"))
            self.tabla_resultados.setItem(i, 2, QTableWidgetItem(centroide_str))
            self.tabla_resultados.setItem(i, 3, QTableWidgetItem(f"{xc:.2f}"))
            self.tabla_resultados.setItem(i, 4, QTableWidgetItem(f"{yc:.2f}"))
            self.tabla_resultados.setItem(i, 5, QTableWidgetItem(f"{xA:.2f}"))
            self.tabla_resultados.setItem(i, 6, QTableWidgetItem(f"{yA:.2f}"))
        # Fila total
        self.tabla_resultados.setRowCount(len(self.seccion.subareas) + 1)
        self.tabla_resultados.setItem(len(self.seccion.subareas), 0, QTableWidgetItem("TOTAL"))
        self.tabla_resultados.setItem(len(self.seccion.subareas), 1, QTableWidgetItem(f"{suma_A:.2f}"))
        self.tabla_resultados.setItem(len(self.seccion.subareas), 2, QTableWidgetItem(""))
        self.tabla_resultados.setItem(len(self.seccion.subareas), 3, QTableWidgetItem(""))
        self.tabla_resultados.setItem(len(self.seccion.subareas), 4, QTableWidgetItem(""))
        self.tabla_resultados.setItem(len(self.seccion.subareas), 5, QTableWidgetItem(f"{suma_xA:.2f}"))
        self.tabla_resultados.setItem(len(self.seccion.subareas), 6, QTableWidgetItem(f"{suma_yA:.2f}"))

    def actualizar_tabla_momentos(self, centroide_global):
        self.tabla_momentos.setRowCount(len(self.seccion.subareas))
        suma_A = 0.0
        suma_dx2A = 0.0   # Esta será la suma de dₓ²·A (pero en la tabla se mostrará como dₓ²·A)
        suma_dy2A = 0.0   # Suma de dᵧ²·A
        for i, sa in enumerate(self.seccion.subareas):
            A_ef = sa.get_area_efectiva()
            Ix_loc, Iy_loc = sa.momento_inercia_local()
            # Distancias reales (físicas)
            dx = sa.centroide[0] - centroide_global[0]  # distancia en X
            dy = sa.centroide[1] - centroide_global[1]  # distancia en Y
            dx2 = dx**2
            dy2 = dy**2
            term_dx2A = A_ef * dx2   # contribución a Iy total (por Steiner: Iy_total += Iy_loc + A*dx²)
            term_dy2A = A_ef * dy2   # contribución a Ix total
            suma_A += A_ef
            suma_dx2A += term_dx2A
            suma_dy2A += term_dy2A
            nombre = f"{sa.tipo.capitalize()} {'(vacío)' if sa.es_vacio else ''}"
            self.tabla_momentos.setItem(i, 0, QTableWidgetItem(nombre))
            self.tabla_momentos.setItem(i, 1, QTableWidgetItem(f"{A_ef:.2f}"))
            self.tabla_momentos.setItem(i, 2, QTableWidgetItem(f"{Ix_loc:.2f}"))
            self.tabla_momentos.setItem(i, 3, QTableWidgetItem(f"{Iy_loc:.2f}"))
            # INTERCAMBIO: columna dₓ² muestra dy², columna dᵧ² muestra dx²
            self.tabla_momentos.setItem(i, 4, QTableWidgetItem(f"{dy2:.2f}"))   # dₓ² (visual) = dy² real
            self.tabla_momentos.setItem(i, 5, QTableWidgetItem(f"{dx2:.2f}"))   # dᵧ² (visual) = dx² real
            self.tabla_momentos.setItem(i, 6, QTableWidgetItem(f"{term_dy2A:.2f}")) # dₓ²·A (visual) = dy²·A
            self.tabla_momentos.setItem(i, 7, QTableWidgetItem(f"{term_dx2A:.2f}")) # dᵧ²·A (visual) = dx²·A
        # Fila TOTAL con sumatorias (también intercambiadas para mantener coherencia visual)
        self.tabla_momentos.setRowCount(len(self.seccion.subareas) + 1)
        self.tabla_momentos.setItem(len(self.seccion.subareas), 0, QTableWidgetItem("TOTAL"))
        self.tabla_momentos.setItem(len(self.seccion.subareas), 1, QTableWidgetItem(f"{suma_A:.2f}"))
        for col in [2,3,4,5]:
            self.tabla_momentos.setItem(len(self.seccion.subareas), col, QTableWidgetItem(""))
        # En la fila TOTAL, mostramos la suma de los valores que están en las columnas visuales
        # Es decir, suma de dₓ²·A visual = suma de term_dy2A, y suma de dᵧ²·A visual = suma de term_dx2A
        self.tabla_momentos.setItem(len(self.seccion.subareas), 6, QTableWidgetItem(f"{suma_dy2A:.2f}"))
        self.tabla_momentos.setItem(len(self.seccion.subareas), 7, QTableWidgetItem(f"{suma_dx2A:.2f}"))

    def calcular_y_dibujar(self):
        if not self.seccion.subareas:
            self.resultados_label.setText("No hay subáreas agregadas.")
            self.figure.clear()
            self.canvas.draw()
            return
        try:
            props = self.seccion.calcular_propiedades()
            centroide_global = props['centroide']
            self.actualizar_tabla_centroides()
            self.actualizar_tabla_momentos(centroide_global)
            texto = (f"Centroide global: ({centroide_global[0]:.2f}, {centroide_global[1]:.2f}) cm\n"
                     f"Área total: {props['area']:.2f} cm²\n"
                     f"Ix total: {props['Ix']:.2f} cm⁴\n"
                     f"Iy total: {props['Iy']:.2f} cm⁴\n"
                     f"Ixy total: {props['Ixy']:.2f} cm⁴\n"
                     f"I máx: {props['I_max']:.2f} cm⁴\n"
                     f"I mín: {props['I_min']:.2f} cm⁴\n"
                     f"Ángulo ejes principales: {props['angulo_principal']:.2f}°")
            self.resultados_label.setText(texto)
            self.dibujar_seccion(props)
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
                ax.plot(cx, cy, 'b.', markersize=6, alpha=0.8)
            else:
                from seccion import convex_hull
                hull = convex_hull(sa.vertices)
                polygon = MplPolygon(hull, facecolor=color, edgecolor=edgecolor, alpha=alpha)
                ax.add_patch(polygon)
                cx_fig, cy_fig = sa.centroide
                ax.plot(cx_fig, cy_fig, 'b.', markersize=6, alpha=0.8)

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
        self.tabla_momentos.setRowCount(0)
        self.resultados_label.setText("Resultados:\n")
        self.figure.clear()
        self.canvas.draw()

def run():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
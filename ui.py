import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.patches import Polygon as MplPolygon, Circle as MplCircle
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
                             QLabel, QLineEdit, QComboBox, QGroupBox, QFormLayout,
                             QHeaderView, QCheckBox, QTextEdit, QMessageBox)
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

        # Panel derecho: controles y tabla
        panel_derecho = QWidget()
        panel_derecho.setMaximumWidth(650)
        layout_der = QVBoxLayout(panel_derecho)

        # Grupo agregar subárea
        grupo_agregar = QGroupBox("Agregar Subárea")
        form_layout = QFormLayout()

        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["Rectángulo", "Triángulo", "Círculo"])
        form_layout.addRow("Tipo:", self.tipo_combo)

        # --- Parámetros estándar (para generación automática) ---
        self.param1_label = QLabel("Base/Ancho (cm):")
        self.param1_input = QLineEdit()
        form_layout.addRow(self.param1_label, self.param1_input)

        self.param2_label = QLabel("Altura (cm):")
        self.param2_input = QLineEdit()
        form_layout.addRow(self.param2_label, self.param2_input)

        # Para triángulo escaleno (desplazamiento)
        self.extra_label = QLabel("Desplazamiento X (cm):")
        self.extra_input = QLineEdit("0")
        self.extra_label.setVisible(False)
        self.extra_input.setVisible(False)
        form_layout.addRow(self.extra_label, self.extra_input)

        # --- Opción de vértices manuales ---
        self.use_vertices_check = QCheckBox("Usar coordenadas manuales de vértices")
        form_layout.addRow(self.use_vertices_check)

        self.vertices_label = QLabel("Vértices (x,y; x,y; ...):")
        self.vertices_text = QTextEdit()
        self.vertices_text.setPlaceholderText("Ejemplo: 0,0; 30,0; 30,20; 0,20")
        self.vertices_text.setMaximumHeight(80)
        self.vertices_label.setVisible(False)
        self.vertices_text.setVisible(False)
        form_layout.addRow(self.vertices_label, self.vertices_text)

        self.ref_label = QLabel("Punto de referencia (solo automático):")
        self.ref_label.setStyleSheet("font-weight: bold;")
        form_layout.addRow(self.ref_label)

        self.ref_x_label = QLabel("Coordenada X:")
        self.ref_x_input = QLineEdit("0")
        form_layout.addRow(self.ref_x_label, self.ref_x_input)

        self.ref_y_label = QLabel("Coordenada Y:")
        self.ref_y_input = QLineEdit("0")
        form_layout.addRow(self.ref_y_label, self.ref_y_input)

        self.vacio_check = QComboBox()
        self.vacio_check.addItems(["Positivo", "Vacío"])
        form_layout.addRow("Tipo de área:", self.vacio_check)

        self.btn_agregar = QPushButton("Agregar Subárea")
        form_layout.addRow(self.btn_agregar)

        grupo_agregar.setLayout(form_layout)
        layout_der.addWidget(grupo_agregar)

        # Tabla de resultados intermedios (centroide)
        self.tabla_resultados = QTableWidget()
        self.tabla_resultados.setColumnCount(6)
        self.tabla_resultados.setHorizontalHeaderLabels(["Figura", "Área (cm²)", "x̄ (cm)", "ȳ (cm)", "x̄·A", "ȳ·A"])
        self.tabla_resultados.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout_der.addWidget(QLabel("Cálculo del Centroide:"))
        layout_der.addWidget(self.tabla_resultados)

        # Botón calcular y dibujar
        self.btn_calcular = QPushButton("Calcular y Dibujar")
        layout_der.addWidget(self.btn_calcular)

        # Área de resultados resumidos
        self.resultados_label = QLabel("Resultados:\n")
        self.resultados_label.setWordWrap(True)
        layout_der.addWidget(self.resultados_label)

        # Botón limpiar
        self.btn_limpiar = QPushButton("Limpiar todas las subáreas")
        layout_der.addWidget(self.btn_limpiar)

        layout_principal.addWidget(panel_derecho, 2)

        # Conexiones
        self.tipo_combo.currentTextChanged.connect(self.actualizar_campos_por_tipo)
        self.use_vertices_check.stateChanged.connect(self.toggle_vertices_mode)
        self.btn_agregar.clicked.connect(self.agregar_subarea)
        self.btn_calcular.clicked.connect(self.calcular_y_dibujar)
        self.btn_limpiar.clicked.connect(self.limpiar_todo)

        self.actualizar_campos_por_tipo()
        self.toggle_vertices_mode()

    def toggle_vertices_mode(self):
        visible = self.use_vertices_check.isChecked()
        self.vertices_label.setVisible(visible)
        self.vertices_text.setVisible(visible)
        # Ocultar/mostrar parámetros automáticos
        self.param1_input.setEnabled(not visible)
        self.param2_input.setEnabled(not visible)
        self.extra_input.setEnabled(not visible)
        self.ref_x_input.setEnabled(not visible)
        self.ref_y_input.setEnabled(not visible)

    def actualizar_campos_por_tipo(self):
        tipo = self.tipo_combo.currentText()
        if tipo == "Círculo":
            self.param1_label.setText("Radio (cm):")
            self.param2_label.setText("(No usar)")
            self.param2_input.setEnabled(False)
            self.param2_input.clear()
            self.param1_input.setEnabled(True)
            self.extra_label.setVisible(False)
            self.extra_input.setVisible(False)
            self.ref_label.setText("Punto de referencia: Centro")
            # Para círculo no aplica vértices manuales
            self.use_vertices_check.setEnabled(False)
            self.use_vertices_check.setChecked(False)
            self.toggle_vertices_mode()
        else:
            self.use_vertices_check.setEnabled(True)
            self.param2_input.setEnabled(True)
            if tipo == "Rectángulo":
                self.param1_label.setText("Ancho (cm):")
                self.param2_label.setText("Alto (cm):")
                self.extra_label.setVisible(False)
                self.extra_input.setVisible(False)
            else:  # Triángulo
                self.param1_label.setText("Base (cm):")
                self.param2_label.setText("Altura (cm):")
                self.extra_label.setVisible(True)
                self.extra_input.setVisible(True)
            # Si estaba en modo vértices, mantener
            self.toggle_vertices_mode()

    def parse_vertices(self, text):
        """Parsea una cadena con formato 'x1,y1; x2,y2; ...' y devuelve lista de (float,float)."""
        vertices = []
        text = text.replace('\n', ';')
        parts = text.split(';')
        for part in parts:
            part = part.strip()
            if not part:
                continue
            coords = part.split(',')
            if len(coords) != 2:
                raise ValueError(f"Formato incorrecto en: '{part}'. Use x,y")
            x = float(coords[0].strip())
            y = float(coords[1].strip())
            vertices.append((x, y))
        if len(vertices) < 3:
            raise ValueError("Se requieren al menos 3 vértices")
        return vertices

    def agregar_subarea(self):
        try:
            tipo = self.tipo_combo.currentText()
            es_vacio = (self.vacio_check.currentText() == "Vacío")

            if tipo == "Círculo":
                radio = float(self.param1_input.text())
                cx = float(self.ref_x_input.text())
                cy = float(self.ref_y_input.text())
                params = {'radio': radio, 'cx': cx, 'cy': cy}
                sa = SubArea('circulo', params, None, es_vacio)

            else:
                use_manual = self.use_vertices_check.isChecked()
                if use_manual:
                    vertices_text = self.vertices_text.toPlainText()
                    vertices = self.parse_vertices(vertices_text)
                    params = {'vertices_manual': vertices}
                    sa = SubArea(tipo.lower(), params, vertices, es_vacio)
                else:
                    # Generar vértices automáticamente
                    base = float(self.param1_input.text())
                    altura = float(self.param2_input.text())
                    ref_x = float(self.ref_x_input.text())
                    ref_y = float(self.ref_y_input.text())
                    if tipo == "Rectángulo":
                        vertices = [(ref_x, ref_y),
                                    (ref_x + base, ref_y),
                                    (ref_x + base, ref_y + altura),
                                    (ref_x, ref_y + altura)]
                        params = {'base': base, 'altura': altura, 'ref_x': ref_x, 'ref_y': ref_y}
                    else:  # Triángulo
                        desplazamiento = float(self.extra_input.text())
                        desplazamiento = max(0, min(desplazamiento, base))
                        vertices = [(ref_x, ref_y),
                                    (ref_x + base, ref_y),
                                    (ref_x + desplazamiento, ref_y + altura)]
                        params = {'base': base, 'altura': altura, 'desplazamiento': desplazamiento,
                                  'ref_x': ref_x, 'ref_y': ref_y}
                    sa = SubArea(tipo.lower(), params, vertices, es_vacio)

            self.seccion.agregar_subarea(sa)
            self.actualizar_tabla()
            self.calcular_y_dibujar()
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
            else:
                # polígono (rectángulo o triángulo)
                vertices = sa.vertices
                polygon = MplPolygon(vertices, facecolor=color, edgecolor=edgecolor, alpha=alpha)
                ax.add_patch(polygon)
                # Marcar el primer vértice como referencia (si se generó automáticamente, es el punto de referencia)
                ax.plot(vertices[0][0], vertices[0][1], 'bo', markersize=4, alpha=0.7)

        # Centroide global
        cx_glob, cy_glob = props['centroide']
        ax.plot(cx_glob, cy_glob, 'ro', markersize=8, label='Centroide global')

        # Calcular límites incluyendo el origen y todas las figuras
        x_vals = [0]
        y_vals = [0]
        for sa in self.seccion.subareas:
            if sa.tipo == 'circulo':
                r = sa.params['radio']
                cx, cy = sa.centroide
                x_vals.extend([cx - r, cx + r])
                y_vals.extend([cy - r, cy + r])
            else:
                for v in sa.vertices:
                    x_vals.append(v[0])
                    y_vals.append(v[1])

        if x_vals and y_vals:
            x_min, x_max = min(x_vals), max(x_vals)
            y_min, y_max = min(y_vals), max(y_vals)
            margin_x = 0.2 * (x_max - x_min) if (x_max - x_min) != 0 else 5
            margin_y = 0.2 * (y_max - y_min) if (y_max - y_min) != 0 else 5
            ax.set_xlim(x_min - margin_x, x_max + margin_x)
            ax.set_ylim(y_min - margin_y, y_max + margin_y)

        # Ejes cartesianos X=0, Y=0
        ax.axhline(0, color='black', linewidth=1.5, linestyle='-', zorder=1)
        ax.axvline(0, color='black', linewidth=1.5, linestyle='-', zorder=1)

        # Ejes principales
        ang = np.radians(props['angulo_principal'])
        xrange = ax.get_xlim()[1] - ax.get_xlim()[0]
        yrange = ax.get_ylim()[1] - ax.get_ylim()[0]
        L = min(xrange, yrange) * 0.6
        dx1 = L * np.cos(ang)
        dy1 = L * np.sin(ang)
        dx2 = L * np.cos(ang + np.pi/2)
        dy2 = L * np.sin(ang + np.pi/2)
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
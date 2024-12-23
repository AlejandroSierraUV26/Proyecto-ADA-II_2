import re
import string
import time
from PyQt5 import QtCore, QtGui, QtWidgets
from minizinc import Instance, Model, Solver


class Ui_Dialog(object):
    def __init__(self, parent=None):
        self.mzn_model = Model('./modelo.mzn')
        self.solver = Solver.lookup("gecode")
        self.mzn_instance = None
    
    def setupScene(self):
        self.scene = QtWidgets.QGraphicsScene()
        self.pen = QtGui.QPen(QtCore.Qt.gray)
        self.redPen = QtGui.QPen(QtCore.Qt.red)
        self.greenBrush = QtGui.QBrush(QtCore.Qt.green)
        self.redBrush = QtGui.QBrush(QtCore.Qt.red)
        self.graphicsView.setScene(self.scene)
        self.scale = 50 # scale of pixels to draw everything
        self.padding_y = 50 # space to move y pixels


    def drawPlane(self):
        self.scene.clear()
        matriz = self.mzn_instance._data["tamano_matriz"]
        n_ciudades = self.mzn_instance._data["num_posiciones_existentes"]
        ciudades = self.mzn_instance._data["ciudades"]
        self.max_x = matriz*self.scale
        self.max_y = matriz*self.scale

        # draw vertical lines
        for item in range(matriz+1):
            self.scene.addLine(item*self.scale, self.padding_y, item*self.scale, self.max_y+self.padding_y, self.pen)
        # draw horizontal lines
        for item in range(matriz+1):  
            self.scene.addLine(0, item*self.scale+self.padding_y, self.max_x, item*self.scale+self.padding_y, self.pen)
        # draw cities
        for item in range(n_ciudades):
            ciudad_x = ciudades[item][0] * self.scale - 5
            ciudad_y = ciudades[item][1] * self.scale + self.padding_y - 5
            self.scene.addEllipse(QtCore.QRectF(ciudad_x, ciudad_y, 10, 10), self.pen, self.greenBrush)
                # Mostrar valores de matriz_segmento_poblacion y matriz_entorno_empresarial en cada cuadro del mapa
        matriz_segmento_poblacion = self.mzn_instance._data["matriz_segmento_poblacion"]
        matriz_entorno_empresarial = self.mzn_instance._data["matriz_entorno_empresarial"]

        for y in range(matriz):
            for x in range(matriz):
                value_segmento = matriz_segmento_poblacion[y][x]
                value_entorno = matriz_entorno_empresarial[y][x]
                text_item_segmento = QtWidgets.QGraphicsTextItem(str(value_segmento))
                text_item_segmento.setDefaultTextColor(QtCore.Qt.yellow)
                text_item_segmento.setPos(x * self.scale + 5, y * self.scale + self.padding_y + 5)
                self.scene.addItem(text_item_segmento)
                text_item_entorno = QtWidgets.QGraphicsTextItem(str(value_entorno))
                text_item_entorno.setDefaultTextColor(QtCore.Qt.cyan)
                text_item_entorno.setPos(x * self.scale + 5, y * self.scale + self.padding_y + 20)
                self.scene.addItem(text_item_entorno)


    def drawSolution(self):
        self.ubicaciones = self.result["ubicaciones"]  # Matriz con las ubicaciones
        matriz = self.mzn_instance._data["tamano_matriz"]

        self.max_x = matriz * self.scale
        self.max_y = matriz * self.scale

        base = self.mzn_instance._data["ciudades"]

        # Limpia la escena antes de dibujar
        self.scene.clear()

        # Dibuja las líneas verticales
        for item in range(matriz + 1):
            self.scene.addLine(
                item * self.scale, self.padding_y,
                item * self.scale, self.max_y + self.padding_y,
                self.pen
            )
        # Dibuja las líneas horizontales
        for item in range(matriz + 1):
            self.scene.addLine(
                0, item * self.scale + self.padding_y,
                self.max_x, item * self.scale + self.padding_y,
                self.pen
            )

        # Coordenadas base y nuevas
        base_coords = [(c[0], c[1]) for c in base]
        filtered_coords = []

        for y in range(len(self.ubicaciones)):
            for x in range(len(self.ubicaciones[y])):
                if self.ubicaciones[y][x] == 1:
                    corrected_x = x + 1
                    corrected_y = y + 1

                    if (corrected_y, corrected_x) not in base_coords:
                        filtered_coords.append((corrected_x, corrected_y))

                    circle_x = corrected_x * self.scale - 5
                    circle_y = corrected_y * self.scale + self.padding_y - 5

                    # Círculo azul para nuevas ubicaciones
                    blueBrush = QtGui.QBrush(QtCore.Qt.blue)
                    self.scene.addEllipse(
                        QtCore.QRectF(circle_x, circle_y, 10, 10),
                        self.pen,
                        blueBrush
                    )

                    # Etiqueta con coordenadas
                    coord_label = QtWidgets.QGraphicsTextItem(f"({corrected_x}, {corrected_y})")
                    coord_label.setDefaultTextColor(QtCore.Qt.white)
                    coord_label.setPos(circle_x + 10, circle_y - 10)
                    self.scene.addItem(coord_label)

        # Dibuja las ubicaciones base en verde
        for bx, by in base_coords:
            circle_x = bx * self.scale - 5
            circle_y = by * self.scale + self.padding_y - 5
            self.scene.addEllipse(
                QtCore.QRectF(circle_x, circle_y, 10, 10),
                self.pen,
                self.greenBrush
            )

            # Etiqueta con coordenadas
            coord_label = QtWidgets.QGraphicsTextItem(f"({bx}, {by})")
            coord_label.setDefaultTextColor(QtCore.Qt.white)
            coord_label.setPos(circle_x + 10, circle_y - 10)
            self.scene.addItem(coord_label)

        # Mostrar valores de matriz_segmento_poblacion y matriz_entorno_empresarial en cada cuadro del mapa
        matriz_segmento_poblacion = self.mzn_instance._data["matriz_segmento_poblacion"]
        matriz_entorno_empresarial = self.mzn_instance._data["matriz_entorno_empresarial"]

        for y in range(matriz):
            for x in range(matriz):
                value_segmento = matriz_segmento_poblacion[y][x]
                value_entorno = matriz_entorno_empresarial[y][x]
                text_item_segmento = QtWidgets.QGraphicsTextItem(str(value_segmento))
                text_item_segmento.setDefaultTextColor(QtCore.Qt.yellow)
                text_item_segmento.setPos(x * self.scale + 5, y * self.scale + self.padding_y + 5)
                self.scene.addItem(text_item_segmento)
                text_item_entorno = QtWidgets.QGraphicsTextItem(str(value_entorno))
                text_item_entorno.setDefaultTextColor(QtCore.Qt.cyan)
                text_item_entorno.setPos(x * self.scale + 5, y * self.scale + self.padding_y + 20)
                self.scene.addItem(text_item_entorno)

        # Actualiza los resultados en el cuadro de texto
        obje = str(self.result.objective)
        result_str = str(self.result)
        for line in result_str.split("\n"):
            if "ganancia_ciudades:" in line:
                ganancia_ciudades = int(line.split(":")[1].strip())
                break
        filtered_coords_ = []
        for pos in filtered_coords:
            if pos not in base_coords:
                filtered_coords_.append(pos)
        text_result = (
            f"<b>Ganancia sin nuevas ubicaciones:</b> {ganancia_ciudades}<br>"
            f"<b>Ganancia con nuevas ubicaciones:</b> {obje}<br>"
            f"<b>Ubicaciones base:</b> {base_coords}<br>"
            f"<b>Nuevas ubicaciones propuestas:</b> {filtered_coords_}"
        )

        self.labelResult.setText(text_result)



        


        


    def buttonFileClicked(self):
        options = QtWidgets.QFileDialog.Options()
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(None, "QFileDialog.getOpenFileName()", "", "Dzn Files (*.dzn)", options=options)
        if filename:
            self.mzn_instance = Instance(self.solver, self.mzn_model)
            self.mzn_instance.add_file(filename, True)
            self.labelFile.setText(f"Archivo seleccionado: {filename.split('/')[-1]}")
            self.drawPlane()

    def selectSolver(self):
        self.solver = Solver.lookup(self.comboBox.itemText(self.comboBox.currentIndex()))

    def buttonSolverClicked(self):
        if self.mzn_instance is None:
            QtWidgets.QMessageBox.warning(
                None, "Error", "Por favor, seleccione un archivo."
            )
            return

        self.labelData.setText("Resolviendo el modelo...")
        QtWidgets.QApplication.processEvents()  # Actualiza la interfaz mientras procesa
        start_time = time.time()

        try:
            self.result = self.mzn_instance.solve()
            duration = time.time() - start_time

            if self.result:
                self.labelData.setText(
                    f"Tiempo de resolución: {duration:.2f} segundos."
                )
                self.drawSolution()  # Dibujar la solución encontrada
            else:
                self.labelData.setText(
                    f"No existe solución. \nTiempo de ejecución: {duration:.2f} segundos."
                )
        except Exception as e:
            self.labelData.setText("Error al resolver el modelo.")
            QtWidgets.QMessageBox.critical(None, "Error", f"Ocurrió un error al resolver el modelo:\n{str(e)}")


    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(800, 800)
        Dialog.setWindowIcon(QtGui.QIcon("relleno-sanitario.png"))

        # Ajuste principal con margen global
        self.mainLayout = QtWidgets.QVBoxLayout(Dialog)
        self.mainLayout.setContentsMargins(10, 10, 10, 10)
        self.mainLayout.setSpacing(15)

        # Fila 1: Label Message
        self.labelMessage = QtWidgets.QLabel(Dialog)
        self.labelMessage.setObjectName("labelMessage")
        self.labelMessage.setAlignment(QtCore.Qt.AlignLeft)
        self.mainLayout.addWidget(self.labelMessage)

        # Fila 2: Botones y ComboBox
        self.row2Layout = QtWidgets.QVBoxLayout()
        self.row2Layout.setAlignment(QtCore.Qt.AlignCenter)
        self.row2Layout.setSpacing(10)
        self.pushButtonFile = QtWidgets.QPushButton(Dialog)
        self.pushButtonFile.setObjectName("pushButtonFile")
        self.pushButtonFile.setFixedWidth(200)
        self.row2Layout.addWidget(self.pushButtonFile)

        self.comboBox = QtWidgets.QComboBox(Dialog)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItems(["gecode", "chuffed", "coin-bc"])
        self.comboBox.setFixedWidth(200)
        self.row2Layout.addWidget(self.comboBox)

        self.pushButtonSolver = QtWidgets.QPushButton(Dialog)
        self.pushButtonSolver.setObjectName("pushButtonSolver")
        self.row2Layout.addWidget(self.pushButtonSolver)
        self.pushButtonSolver.setFixedWidth(200)

        self.mainLayout.addLayout(self.row2Layout)

        # Fila 3: Información del archivo y datos
        self.labelFile = QtWidgets.QLabel(Dialog)
        self.labelFile.setObjectName("labelFile")
        self.mainLayout.addWidget(self.labelFile)

        self.labelData = QtWidgets.QLabel(Dialog)
        self.labelData.setObjectName("labelData")
        self.mainLayout.addWidget(self.labelData)

        # Vista gráfica
        self.graphicsView = QtWidgets.QGraphicsView(Dialog)
        self.graphicsView.setObjectName("graphicsView")
        self.graphicsView.setMinimumHeight(300)
        self.mainLayout.addWidget(self.graphicsView)

        self.labelResult = QtWidgets.QLabel(Dialog)
        self.labelResult.setObjectName("labelResult")
        self.labelResult.setWordWrap(True)
        self.labelResult.setAlignment(QtCore.Qt.AlignCenter)
        self.mainLayout.addWidget(self.labelResult)
        
        # Configurar estilos
        self.applyStyles(Dialog)

        # Retraducir y conectar
        self.retranslateUi(Dialog)
        self.pushButtonFile.clicked.connect(self.buttonFileClicked)
        self.comboBox.currentIndexChanged.connect(self.selectSolver)
        self.pushButtonSolver.clicked.connect(self.buttonSolverClicked)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        self.setupScene()

    def applyStyles(self, Dialog):
        """Aplica estilos CSS a los elementos de la interfaz"""
        Dialog.setStyleSheet("""
            QDialog {
                background-color: #2e3440; /* Fondo oscuro */
                color: #d8dee9; /* Texto claro */
                font-family: 'Segoe UI', sans-serif;
                font-size: 12pt;
            }
            QLabel {
                font-size: 12pt;
                color: #eceff4;
            }
            QPushButton {
                background-color: #5e81ac;
                color: #eceff4;
                border: 1px solid #4c566a;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #81a1c1;
            }
            QPushButton:pressed {
                background-color: #4c566a;
            }
            QComboBox {
                background-color: #3b4252;
                color: #eceff4;
                border: 1px solid #4c566a;
                padding: 3px;
            }
            QComboBox QAbstractItemView {
                background-color: #434c5e;
                selection-background-color: #5e81ac;
                selection-color: #eceff4;
            }
            QGraphicsView {
                border: 1px solid #4c566a;
                background-color: #3b4252;
            }
        """)

    
    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Proyecto ADA II"))
        self.pushButtonFile.setText(_translate("Dialog", "Seleccionar archivo"))
        self.pushButtonSolver.setText(_translate("Dialog", "Resolver"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())


#=======================================================================
# Python: 3
# Windows
#
#          ██╗  ██╗ █████╗ ███╗   ███╗██╗   ██╗███████╗
#          ██║ ██╔╝██╔══██╗████╗ ████║██║   ██║╚══███╔╝
#          █████╔╝ ███████║██╔████╔██║██║   ██║  ███╔╝ 
#          ██╔═██╗ ██╔══██║██║╚██╔╝██║██║   ██║ ███╔╝  
#          ██║  ██╗██║  ██║██║ ╚═╝ ██║╚██████╔╝███████╗
#          ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚══════╝
#                                                         By: LawlietJH
#                                                               v1.1.1
#=======================================================================

import datetime
import msvcrt
import random
import copy
import time
import sys
import os

# Requiere Instalar PyWin32: python -m pip install pywin32
import pywintypes
import win32con
import win32net
import win32security

#=======================================================================
# pip install PyQt5
from PyQt5.QtCore import Qt, QTime, QTimer, QThread, pyqtSignal
from PyQt5.QtWidgets import (
	QApplication, QMainWindow,
	QMenu, QToolBar, QWidget,
	QWidgetAction, QAction,
	QGridLayout, QFileDialog,
	QPushButton, QLabel, 
	QLineEdit, QCheckBox,
	QHBoxLayout, QProgressBar,
	QVBoxLayout, QHBoxLayout,
	QStyleFactory,
	QTableWidget, QTableWidgetItem
	)
from PyQt5.QtGui import QIcon, QPixmap

#=======================================================================
#=======================================================================
#=======================================================================
__author__  = 'LawlietJH'				# Desarrollador
__title__   = 'Kamuz'					# Nombre
__version__ = 'v1.1.1'					# Versión
#=======================================================================
#=======================================================================
#=======================================================================

class Window(QMainWindow):
	
	def __init__(self, parent=None):
		super().__init__(parent)
		self._createWindow()
		self._createGrid()
		self._createActions()
		self._createMenuBar()
		self._createToolBars()
		self._connectActions()
		self._createStatusBar()
	
	class progressBarThread(QThread):
		
		updateProgress = pyqtSignal(str, int, bool, str)
		
		def __init__(self, user, wordlist, typeAttack='wordlist'):
			super().__init__()
			
			self.typeAttack = typeAttack
			self.cancelAttack = False
			self.wordlist = wordlist
			self.isCorrectPwd = True
			self.user = user
			self.pos = 0
			self.time_init = time.time()

		def validateUserPassword(self, userName, passwd):
			# Tomado de https://github.com/LawlietJH/Utils
			try:
				win32security.LogonUser(
					userName, None, passwd,
					win32con.LOGON32_LOGON_INTERACTIVE,
					win32con.LOGON32_PROVIDER_DEFAULT
				)
				return True
			except:
				return False

		def openWordlistFile(self, fileName, chunk=1024**2):
			with open(fileName, 'r') as f:
				while True:
					data = f.read(chunk)
					if data:
						yield data
					else:
						return
		
		def yield_read(self, yield_, action):
			for y in yield_:
				if type(y).__name__ == 'generator':
					if self.yield_read(y, action):
						return True
				else:
					# ~ print('\r', y, end='')
					if action(y):
						return True
		
		def variableLengthWords(self, charset, length=1, invert=False, string=''):
			
			for char in charset:
				
				if invert:
					word = char+string
				else:
					word = string+char
				
				yield word
				
				if not len(word) == length:
					
					yield self.variableLengthWords(charset, length, invert, word)
		
		def generatorAttack(self):
			
			def attack(word):
				
				import time
				
				self.pos += 1
				
				self.isCorrectPwd = self.validateUserPassword(self.user['name'], word)
				
				if self.pos % random.randint(150, 160) == 0:
					self.updateProgress.emit(word, self.pos, False, 'generator')
				if self.isCorrectPwd:
					self.updateProgress.emit(word, self.pos, True,  'generator')
				
				return self.isCorrectPwd
			
			charset = 'zZ'
			length  = 20
			
			self.wordsTotal = 0
			for l in range(1, length+1):
				total = len(charset) ** l
				self.wordsTotal += total
			
			yield_data = self.variableLengthWords(charset, length)
			self.yield_read(yield_data, attack)
		
		def wordlistAttack(self):
			
			wordlist_data = self.user['wordlists_data'].get(self.wordlist)
			if wordlist_data and wordlist_data.get('wordsTotal'):
				self.wordsTotal = wordlist_data['wordsTotal']
			else:
				data_yield = self.openWordlistFile(self.wordlist)
				self.wordsTotal = 0
				last_word = ''
				
				for x in data_yield:
					
					if self.cancelAttack:
						self.updateProgress.emit('', self.wordsTotal, False, 'wordlist')
						return
					
					x = last_word + x
					x = x.split('\n')
					
					if x[-1]:
						last_word = x.pop()
					else:
						last_word = ''
					
					self.wordsTotal += len(x)
					self.updateProgress.emit('', self.wordsTotal, False, 'wordlist')
				
				del x
			
			data_yield = self.openWordlistFile(self.wordlist)
			self.pos = 0
			last_word = ''
			isCorrectPwd = False
			time.sleep(.01)
			
			self.time_init = time.time()
			if wordlist_data and wordlist_data.get('lastWord'):
				self.time_init -= wordlist_data['currentTime']-.03
				#print(wordlist_data['currentTime'])
			
			for data in data_yield:
				
				if self.cancelAttack: break
				
				data = last_word + data
				data = data.split('\n')
				last_word = data.pop()
				
				for word in data:
					
					if self.cancelAttack: break
					self.pos += 1
					
					if wordlist_data and wordlist_data.get('lastPos') and self.pos < wordlist_data.get('lastPos'):
						# ~ if self.pos % random.randint(150, 160) == 0:
							# ~ print(wordlist_data.get('lastPos'))
						continue
					
					isCorrectPwd = self.validateUserPassword(self.user['name'], word)
					
					if self.pos % random.randint(150, 160) == 0:
						self.updateProgress.emit(word, self.pos, False, 'wordlist')
					if isCorrectPwd:
						self.updateProgress.emit(word, self.pos, True, 'wordlist')
						break
				
				if isCorrectPwd:
					break
			
			#print(word, self.pos, last_word)
			
			if not isCorrectPwd and not self.cancelAttack:
				self.updateProgress.emit('No encontrada...'+word, self.pos, False, 'wordlist')
			else:
				self.updateProgress.emit(word, self.pos, False, 'wordlist')
		
		def run(self):
			
			if self.typeAttack == 'generator':
				self.generatorAttack()
			elif self.typeAttack == 'wordlist':
				self.wordlistAttack()
	
	#===================================================================
	# GUI
	
	def _createWindow(self):
		self.setWindowTitle(__title__+' '+__version__ + ' - By: ' + __author__)
		self.setWindowIcon(QIcon('icons/icon.png'))
		self.widthSize, self.heightSize = 720, 480
		self.setFixedSize(self.widthSize, self.heightSize)
		self.wordlist = None
	
	def _createGrid(self):
		
		self.grid = QGridLayout()
		
		w = QWidget()
		w.setLayout(self.grid)
		
		self.setCentralWidget(w)
		
		#---------------------------------------------------------------
		
		# Pos: 0, 0
		labelWordlistLoaded = QLabel('Wordlist:')
		
		# Pos: 0, 1-2
		self.lineFileName = QLineEdit('')
		self.lineFileName.setReadOnly(True)
		
		# Pos: 0, 3
		self.btnOpenFile = QPushButton(
			QIcon('icons/open.png'),
			'Cargar Archivo...'
		)
		# ~ self.btnRestoreFileTimes.setEnabled(False)
		
		#---------------------------------------------------------------
		
		# Pos: 1, 0-3
		self.usersInfo = self.getUsersInfo()
		headers = ['Usuario','Contraseña','Último Cambio','Grupo']
		y, x = len(self.usersInfo)-1, len(headers)
		
		self.tablewidgetUsers = QTableWidget()
		self.tablewidgetUsers.setRowCount(y)
		self.tablewidgetUsers.setColumnCount(x)
		self.tablewidgetUsers.setFixedWidth(self.widthSize-23)
		# ~ self.tablewidgetUsers.setFixedHeight(185)
		
		hheader = self.tablewidgetUsers.horizontalHeader()
		vheader = self.tablewidgetUsers.verticalHeader()
		hheader.setDefaultAlignment(Qt.AlignCenter)						# Alinea a la izquierda el texto de las cabeceras
		for i in range(x): hheader.setSectionResizeMode(i,1)			# Deshabilita el resize de todas las columnas
		for i in range(y): vheader.setSectionResizeMode(i,1)			# Deshabilita el resize de todas las filas
		vheader.hide()
		
		# Agrega los titulos de las cabeceras horizontales
		for i, header in enumerate(headers):
			params = [i, QTableWidgetItem(header)]
			self.tablewidgetUsers.setHorizontalHeaderItem(*params)
		# Agrega los titulos de las cabeceras verticales
		# ~ for i in range(y):
			# ~ params = [i, QTableWidgetItem('')]
			# ~ self.tablewidgetUsers.setVerticalHeaderItem(*params)
		
		# ~ item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
		
		self.updateUsersTable(x, y)
		
		self.tablewidgetUsers.resizeColumnsToContents()
		# ~ self.tablewidgetUsers.setColumnWidth(1, 200)
		self.tablewidgetUsers.resizeRowsToContents()
		
		#---------------------------------------------------------------
		
		# Pos: 3, 0-3
		self.labelBruteForceActualWord = QLabel('Probando:')
		self.labelBruteForceCurrentQty = QLabel('0/0')
		self.labelBruteForceWordsPerSecond = QLabel('0/s')
		self.labelBruteForceCurrentTime = QLabel('00:00:00')
		
		# Pos: 4, 0-3
		self.pbBruteForceProgress = QProgressBar()
		self.pbBruteForceProgress.setTextVisible(True)
		# ~ self.pbBruteForceProgress.setStyle(QStyleFactory.create('Windows'))
		self.pbBruteForceProgress.setValue(0)
		
		# Pos: 4, 0
		self.labelBruteForceRemainingTime = QLabel('Tiempo restante: 00:00:00')
		
		# Box 1
		
		hbox2 = QHBoxLayout()
		# ~ hbox2.addStretch(1)
		hbox2.addWidget(self.labelBruteForceRemainingTime, alignment=Qt.AlignLeft)
		hbox2.addWidget(self.labelBruteForceCurrentQty, alignment=Qt.AlignRight)
		hbox2.addWidget(self.labelBruteForceWordsPerSecond, alignment=Qt.AlignCenter)
		hbox2.addWidget(self.labelBruteForceCurrentTime, alignment=Qt.AlignLeft)
		vbox2 = QVBoxLayout()
		vbox2.addLayout(hbox2)
		vbox2.addWidget(self.pbBruteForceProgress)
		vbox2.addWidget(self.labelBruteForceActualWord, alignment=Qt.AlignLeft)
		
		###########
		
		# Pos: 2, 4
		labelUser = QLabel('Usuario:')
		
		# Pos: 2, 4
		self.labelUserSelected = QLabel('Ninguno...')
		
		# Pos: 3, 4
		self.btnBruteForce = QPushButton(
			QIcon('icons/continue.png'),
			'Iniciar'
		)
		self.btnBruteForce.setEnabled(False)
		
		# Pos: 3, 4
		self.btnBruteForceCancel = QPushButton(
			QIcon('icons/pause.png'),
			'Pausar'
		)
		self.btnBruteForceCancel.setVisible(False)
		self.btnBruteForceCancel.setEnabled(False)
		
		# Box 2
		hbox1 = QHBoxLayout()
		hbox1.addWidget(labelUser, alignment=Qt.AlignRight)
		hbox1.addWidget(self.labelUserSelected, alignment=Qt.AlignLeft)
		vbox1 = QVBoxLayout()
		# ~ vbox1.addStretch(1)
		vbox1.addLayout(hbox1)
		vbox1.addWidget(self.btnBruteForce)
		vbox1.addWidget(self.btnBruteForceCancel)
		
		#---------------------------------------------------------------
		
		labelSpaced = QLabel('')
		
		#---------------------------------------------------------------
		
		self.grid.setRowStretch(0, 0)
		self.grid.setRowStretch(1, 0)
		self.grid.setRowStretch(2, 0)
		self.grid.setRowStretch(3, 0)
		self.grid.setRowStretch(4, 1)
		self.grid.setRowStretch(5, 1)
		self.grid.setColumnStretch(0, 0)
		self.grid.setColumnStretch(1, 0)
		self.grid.setColumnStretch(2, 0)
		self.grid.setColumnStretch(3, 1)
		self.grid.setColumnStretch(4, 0)
		
		# Add Widgets
		self.grid.addWidget(labelWordlistLoaded,      0, 0,       alignment=Qt.AlignLeft)
		self.grid.addWidget(self.lineFileName,        0, 1, 1, 3)
		self.grid.addWidget(self.btnOpenFile,         0, 4,       alignment=Qt.AlignRight)
		self.grid.addWidget(self.tablewidgetUsers,    1, 0, 1, 5)
		self.grid.addWidget(labelSpaced,              2, 0, 1, 5)
		self.grid.addLayout(vbox1,                    3, 4, 1, 1)
		self.grid.addLayout(vbox2,                    3, 0, 1, 4)
	
	def _createActions(self):
		#===============================================================
		# 'File' Actions
		self.openAction = QAction(QIcon('icons/open.png'), '&Open...', self)
		self.exitAction = QAction(QIcon('icons/exit.png'), '&Exit', self)
		#---------------------------------------------------------------
		# Using Keys
		self.openAction.setShortcut('Ctrl+O')
		self.exitAction.setShortcut('Esc')
		#---------------------------------------------------------------
		# Adding 'File' Tips
		openTip = 'Abre el explorador para cargar archivos.'
		self.openAction.setStatusTip(openTip)							# Agrega un mensaje a la barra de estatus
		self.openAction.setToolTip(openTip)								# Modifica el mensaje de ayuda que aparece encima
	
	def _createMenuBar(self):
		menuBar = self.menuBar()
		#===============================================================
		# File menu
		fileMenu = QMenu('&File', self)
		menuBar.addMenu(fileMenu)
		fileMenu.addAction(self.openAction)
		fileMenu.addSeparator()
		fileMenu.addAction(self.exitAction)
	
	def _createToolBars(self):
		
		self.fileToolBar = QToolBar('File', self)
		self.addToolBar(Qt.BottomToolBarArea, self.fileToolBar)
		self.fileToolBar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
		self.fileToolBar.addAction(self.exitAction)
		self.fileToolBar.addSeparator()
		# ~ self.fileToolBar.addAction(self.openAction)
		self.fileToolBar.setMovable(False)
	
	def _createStatusBar(self):
		self.statusbar = self.statusBar()
		# Adding a temporary message
		self.statusbar.showMessage('Ready', 3000)
		# Adding a permanent message
		t = QTime.currentTime().toPyTime()
		t = '{}:{}'.format(str(t.hour).zfill(2),
						   str(t.minute).zfill(2))
		self.wcLabel = QLabel(t)
		self.statusbar.addPermanentWidget(self.wcLabel)
	
	def contextMenuEvent(self, event):
		# Creating a menu object with the central widget as parent
		menu = QMenu(self)
		# Populating the menu with actions
		menu.addAction(self.openAction)
		menu.addSeparator()
		# Launching the menu
		menu.exec(event.globalPos())
	
	def _connectActions(self):
		
		# Connect File actions
		self.openAction.triggered.connect(self.openWordList)
		self.exitAction.triggered.connect(self.close)
		
		# Buttons:
		self.btnOpenFile.clicked.connect(self.openWordList)
		
		# Listwidget:
		self.tablewidgetUsers.clicked.connect(self.userSelected)
		self.tablewidgetUsers.doubleClicked.connect(self.bruteForce)
		self.btnBruteForce.clicked.connect(self.bruteForce)
		self.btnBruteForceCancel.clicked.connect(self.bruteForceCancel)
		
		# Clock
		self.timer = QTimer()
		self.timer.timeout.connect(self.updateClock)
		self.timer.start(1000)
	
	#===================================================================
	# Functions
	
	def progressBarUpdate(self, currentWord, currentPos, isCorrectPwd, typeAttack):
		
		if typeAttack == 'generator':
			
			total = self.pbThread.wordsTotal
			time_init = self.pbThread.time_init
			progress = (currentPos * 100) / total
			currentT = time.time() - time_init
			perSec = int(currentPos / currentT)
			# ~ (Total - x) * (TiempoTransc / x)
			restTime = (total - currentPos) * (currentT / currentPos)
			
			actualWord = 'Contraseña: ' if isCorrectPwd else 'Probando: '
			actualWord += currentWord
			currentQty = str(currentPos) + '/' + str(total)
			wordsPerSecond = str(perSec)+'/s'
			currentTime = self.prettyTime(currentT)
			restTime = 'Tiempo restante: ' + self.prettyTime(restTime)
			
			self.labelBruteForceActualWord.setText(actualWord)
			self.labelBruteForceCurrentQty.setText(currentQty)
			self.labelBruteForceWordsPerSecond.setText(wordsPerSecond)
			self.labelBruteForceCurrentTime.setText(currentTime)
			self.labelBruteForceRemainingTime.setText(restTime)
			
			self.pbBruteForceProgress.setValue(int(progress))
		
		elif typeAttack == 'wordlist':
			
			if currentWord.startswith('No encontrada...'):
				currentWord, tempWord = currentWord.split('...')
				currentWord += '...'
			
			if not currentWord == '':
				userID = self.usersInfo['ID'][self.labelUserSelected.text()]
				currentUserInfo = self.usersInfo[userID]
				# ~ if not currentUserInfo['wordlists_data'].get(self.wordlist):
					# ~ currentUserInfo['wordlists_data'][self.wordlist] = {
						# ~ 'lastWord':    currentWord if not currentWord == 'No encontrada...' else tempWord,
						# ~ 'lastPos':     currentPos,
						# ~ 'wordsTotal':  self.pbThread.wordsTotal,
						# ~ 'currentTime': time.time() - self.pbThread.time_init,
						# ~ 'lastWordIsPwd': isCorrectPwd
					# ~ }
				
				tempy = len(self.usersInfo)-1
				for t in range(tempy):
					if not self.usersInfo[t]['wordlists_data'].get(self.wordlist):
						self.usersInfo[t]['wordlists_data'][self.wordlist] = {
							'wordsTotal':  self.pbThread.wordsTotal,
						}
				
				if not currentWord == 'No encontrada...':
					currentUserInfo['wordlists_data'][self.wordlist]['lastWord'] = currentWord
				else:
					currentUserInfo['wordlists_data'][self.wordlist]['lastWord'] = tempWord
				
				try:
					currentUserInfo['wordlists_data'][self.wordlist]['currentTime'] = time.time() - self.pbThread.time_init
				except:
					pass
				
				currentUserInfo['wordlists_data'][self.wordlist]['lastPos'] = currentPos
				if currentUserInfo['wordlists_data'][self.wordlist].get('lastWordIsPwd') in [None, False]:
					currentUserInfo['wordlists_data'][self.wordlist]['lastWordIsPwd'] = isCorrectPwd
				
				total = self.pbThread.wordsTotal
				time_init = self.pbThread.time_init
				progress = (currentPos * 100) / total
				currentT = time.time() - time_init
				perSec = int(currentPos / currentT)
				# ~ (Total - x) * (TiempoTransc / x)
				restTime = (total - currentPos) * (currentT / currentPos)
				
				actualWord = 'Contraseña: ' if isCorrectPwd else 'Probando: '
				actualWord += currentWord
				currentQty = str(currentPos) + '/' + str(total)
				wordsPerSecond = str(perSec)+'/s'
				currentTime = self.prettyTime(currentT)
				restTime = 'Tiempo restante: ' + self.prettyTime(restTime)
				
				self.labelBruteForceActualWord.setText(actualWord)
				self.labelBruteForceCurrentQty.setText(currentQty)
				self.labelBruteForceWordsPerSecond.setText(wordsPerSecond)
				self.labelBruteForceCurrentTime.setText(currentTime)
				self.labelBruteForceRemainingTime.setText(restTime)
				
				self.pbBruteForceProgress.setValue(int(progress))
			
			else:
				total = -1
				currentQty = '0/' + str(currentPos)
				self.labelBruteForceActualWord.setText('Cargando Wordlist...')
				self.labelBruteForceCurrentQty.setText(currentQty)
			
			if isCorrectPwd:
				self.bruteForceCancel()
				self.tablewidgetUsers.setFocus()
				# ~ self.tablewidgetUsers.selectRow(self.userSelectedPosition)
				self.tablewidgetUsers.setCurrentCell(self.userSelectedPosition, 1)
				
				restTime = 'Tiempo restante: 00:00:00'
				self.labelBruteForceRemainingTime.setText(restTime)
				self.statusbar.showMessage('Contraseña encontrada: '+currentWord, 300000)
				item = self.tablewidgetUsers.item(self.userSelectedPosition, 1)
				item.setText(currentWord)
			
			elif currentPos == total or currentWord == 'No encontrada...':
				
				self.bruteForceCancel()
				self.statusbar.showMessage('Contraseña NO encontrada en este Wordlist.', 300000)
	
	def bruteForce(self):
		
		self.pbBruteForceProgress.setFocus()
		
		if self.labelUserSelected.text() == 'Ninguno...': return
		if not self.wordlist:
			self.openWordList()
			if not self.wordlist:
				return
		
		self.btnOpenFile.setEnabled(False)
		self.openAction.setEnabled(False)
		self.btnBruteForce.setEnabled(False)
		self.btnBruteForce.setVisible(False)
		self.btnBruteForceCancel.setEnabled(True)
		self.btnBruteForceCancel.setVisible(True)
		# ~ self.btnBruteForceCancel.setFocus(True)
		
		userID = self.usersInfo['ID'][self.labelUserSelected.text()]
		user = self.usersInfo[userID]
		
		self.pbThread = self.progressBarThread(user, self.wordlist)
		self.pbThread.start()
		self.pbThread.updateProgress.connect(self.progressBarUpdate)
	
	def bruteForceCancel(self):
		
		userID = self.usersInfo['ID'].get(self.labelUserSelected.text())
		if userID:
			wordlists_data = self.usersInfo[userID]['wordlists_data'].get(self.wordlist)
			if wordlists_data and wordlists_data.get('lastWord'):
				self.btnBruteForce.setText('Continuar')
		
		self.pbThread.cancelAttack = True
		self.btnOpenFile.setEnabled(True)
		self.openAction.setEnabled(True)
		if wordlists_data:
			self.btnBruteForce.setEnabled(not wordlists_data.get('lastWordIsPwd'))
		else:
			self.btnBruteForce.setEnabled(True)
		self.btnBruteForce.setVisible(True)
		self.btnBruteForceCancel.setEnabled(False)
		self.btnBruteForceCancel.setVisible(False)
		self.pbBruteForceProgress.setFocus()
	
	def prettyTime(self, secs):
		
		secs  = int(secs)
		mins  = secs  // 60
		hours = mins  // 60
		days  = hours // 24
		
		output  = f'{days%365}d ' if days > 0 else ''
		output += f'{str(hours%24).zfill(2)}:'
		output += f'{str(mins%60).zfill(2)}:'
		output += f'{str(secs%60).zfill(2)}'
		
		return output
	
	def openWordList(self):
		
		options  = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		fileName, _ = QFileDialog.getOpenFileName(
			self, 'Abrir', os.getcwd(),
			'Wordlist (*.txt *.zion)'
			';;Todos los archivos (*.*)',
			options = options
		)

		if not fileName:
			return

		self.wordlist = fileName.replace('/', '\\')
		path = self.wordlist.split('\\')
		
		if len(path) > 3:
			path = '...\\' + '\\'.join(path[-3:])
		else:
			path = '\\'.join(path[-3:])
		
		self.lineFileName.setText(path)
		self.userSelected()
	
	def updateUsersTable(self, x, y):
		for j in range(y):
			for i in range(x):
				if   i == 0: val = self.usersInfo[j]['name']
				elif i == 1: val = self.usersInfo[j]['password']
				elif i == 2: val = self.usersInfo[j]['password_age']
				elif i == 3: val = self.usersInfo[j]['local_groups']
				item = QTableWidgetItem(val)
				item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
				item.setTextAlignment(Qt.AlignCenter)
				self.tablewidgetUsers.setItem(j, i, item)
	
	def updateClock(self):
		t = datetime.datetime.now().strftime('%H:%M')
		self.wcLabel.setText(t)
	
	def userSelected(self):
		
		item = self.tablewidgetUsers.currentItem()
		# ~ item = self.tablewidgetUsers.selectedItems()[0]
		user = self.tablewidgetUsers.item(item.row(), 0).text()
		upwd = self.tablewidgetUsers.item(item.row(), 1).text()
		# ~ print(item.row(), item.column(), item.text())
		
		if self.btnBruteForce.isHidden(): return
		else:
			currentUserInfo = self.usersInfo.get(item.row())
			if currentUserInfo:
				wordlists_data = currentUserInfo['wordlists_data'].get(self.wordlist)
				if wordlists_data and wordlists_data.get('lastWord'):
					self.btnBruteForce.setText('Continuar')
					currentPos = wordlists_data['lastPos']
					currentWord = wordlists_data['lastWord']
					isCorrectPwd = wordlists_data['lastWordIsPwd']
					wordsTotal = wordlists_data['wordsTotal']
					progress = (currentPos * 100) / wordsTotal
					currentTime = wordlists_data['currentTime']
					perSec = int(currentPos / currentTime)
					restTime = (wordsTotal - currentPos) * (currentTime / currentPos)
					
					actualWord = 'Contraseña: ' if isCorrectPwd else 'Probando: '
					actualWord += currentWord
					currentQty = str(currentPos) + '/' + str(wordsTotal)
					wordsPerSecond = str(perSec)+'/s'
					currentTime = self.prettyTime(currentTime)
					restTime = 'Tiempo restante: ' + self.prettyTime(restTime)
					
					self.labelBruteForceActualWord.setText(actualWord)
					self.labelBruteForceCurrentQty.setText(currentQty)
					self.labelBruteForceWordsPerSecond.setText(wordsPerSecond)
					self.labelBruteForceCurrentTime.setText(currentTime)
					self.labelBruteForceRemainingTime.setText(restTime)
					
					self.pbBruteForceProgress.setValue(int(progress))
					
				else:
					self.btnBruteForce.setText('Iniciar')
					self.labelBruteForceActualWord.setText('Probando:')
					self.labelBruteForceCurrentQty.setText('0/0')
					self.labelBruteForceWordsPerSecond.setText('0/s')
					self.labelBruteForceCurrentTime.setText('00:00:00')
					self.pbBruteForceProgress.setValue(0)
			else:
				self.btnBruteForce.setText('Iniciar')
				self.labelBruteForceActualWord.setText('Probando:')
				self.labelBruteForceCurrentQty.setText('0/0')
				self.labelBruteForceWordsPerSecond.setText('0/s')
				self.labelBruteForceCurrentTime.setText('00:00:00')
				self.pbBruteForceProgress.setValue(0)
			self.pbBruteForceProgress.setFocus()
		
		# ~ if temp_currentUserInfo:
			# ~ wld = temp_currentUserInfo['wordlists_data'].get(self.wordlist)
			# ~ print(wld)
		
		if upwd == 'Sin contraseña':
			self.labelUserSelected.setText('Ninguno...')
			self.btnBruteForce.setEnabled(False)
			self.statusbar.showMessage('El usuario no tiene contraseña.', 3000)
		else:
			if not self.labelUserSelected.text() == user:
				self.labelUserSelected.setText(user)
				self.userSelectedPosition = item.row()
				if currentUserInfo:
					wordlists_data = currentUserInfo['wordlists_data'].get(self.wordlist)
					if wordlists_data:
						print(wordlists_data)
						self.btnBruteForce.setEnabled(not wordlists_data.get('lastWordIsPwd'))
					else:
						self.btnBruteForce.setEnabled(True)
				else:
					self.btnBruteForce.setEnabled(True)
				self.statusbar.showMessage('Usuario seleccionado.', 3000)
	
	#===================================================================
	# Kamuz base utilities:
	
	def getUsersInfo(self):
		usersEnum = win32net.NetUserEnum(None, 1)
		users = {'ID': {}}
		qty = 0
		for user in usersEnum[0]:
			if user['priv'] > 0:
				havePassword = self.validateUserPasswordError(user['name'])
				if havePassword == 'Cuenta deshabilitada': continue
				users[qty] = copy.deepcopy(user)
				users[qty]['password'] = havePassword
				users[qty]['password_age'] = self.userPasswordAge(user)
				groups = win32net.NetUserGetLocalGroups(None, user['name'] , 0)
				users[qty]['local_groups'] = ', '.join(groups)
				users[qty]['wordlists_data'] = {}
				del users[qty]['home_dir']
				del users[qty]['script_path']
				users['ID'] = {**users['ID'], user['name']:qty}
				qty += 1
		# ~ print(users)
		return users
	
	def userPasswordAge(self, user):
		
		secs  = user['password_age']
		mins  = secs  // 60
		hours = mins  // 60
		days  = hours // 24
		years = days  // 365
		
		output  = f'{years}a, ' if years > 0 else ''
		output += f'{days%365}d ' if days > 0 else ''
		output += f'{str(hours%24).zfill(2)}:'
		output += f'{str(mins%60).zfill(2)}:'
		output += f'{str(secs%60).zfill(2)}'
		
		return output
	
	def validateUserPasswordError(self, userName):
		try:
			win32security.LogonUser(
				userName, None, '',
				win32con.LOGON32_LOGON_INTERACTIVE,
				win32con.LOGON32_PROVIDER_DEFAULT
			)
		except pywintypes.error as error:
			# ~ print(error.__str__())
			Err = error.__str__().replace('(','').replace(')','').replace('\'','').split(', ')[0]
			if   int(Err) == 1331: return 'Cuenta deshabilitada'
			elif int(Err) == 1327: return 'Sin contraseña'
			elif int(Err) == 1326: return 'Desconocida'
	
	#===================================================================
	#===================================================================
	#===================================================================



if __name__ == '__main__':
	app = QApplication(sys.argv)
	win = Window()
	win.show()
	sys.exit(app.exec_())








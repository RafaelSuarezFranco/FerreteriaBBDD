import mysql.connector
from prettytable import PrettyTable

miconexion = mysql.connector.connect(
  host="localhost",
  user="root",
  password="admin",
  database="ferreteria"
)
micursor=miconexion.cursor()

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
    ######################################################################################### ID FAMILIA
    sql = ""
    idfamilianuevo="id"
    #no aceptamos un ID de familia si NO es entero o ya existe o si pulsa intro
    while esEntero(idfamilianuevo) == False or duplicado("familia","idfamilia",idfamilianuevo) == True:
        idfamilianuevo = input("Introduce idfamilia de la familia (número entero, pulsa intro para generar uno automático.) ")
        if idfamilianuevo == "":# si pulsa intro, permitimos salir del bucle
            break
    if idfamilianuevo != "": #si no es id vacío, lo utilizaremos.
        idfamilianuevo = int(idfamilianuevo)
    
    ######################################################################################### NOMBRE Y DESCUENTO
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
    ######################################################################################### SQL E INSERT DE LA FAMILIA
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
        
    ######################################################################### RECUPERAR EL ID FAMILIA (PARA EL ALTA DE ARTICULO)
        
    #vamos a hacer que esta funcion devuelva el ID creado, para utilizarlo en crear articulo si esta función es llamada allí.
    if idfamilianuevo != "":#si hemos introducido el ID manualmente, lo tenemos guardado en la variable
        return idfamilianuevo
    else:
        try:#si se ha autogenerado, sacamos el ultimo de la lista. auto increment ignora que hayan números sin utilizar,
            #siempre usará un número mayor al último que encuentre, por lo que este select nos arrojará el ID que buscamos.
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


def buscarFamiliaID(idfamilia):
    tabla=PrettyTable(["ID FAMILIA","NOMBRE FAMILIA","DESCUENTO FAMILIA"])
    sql="select * from familia where idfamilia = "+idfamilia
    micursor.execute(sql)
    for columna in micursor:
        tabla.add_row(columna)
    print(tabla)    

def asignarFamilia():
    #dado que el proceso de asignar una familia a un artículo es algo complicado, mejor sacar el proceso en esta
    #función y llamarla tanto en alta como en modificación de artículo
    
    #en el caso que un ID de familia esté duplicado quiere decir que existe y que lo aceptamos.
    #si no esta duplicado, no existe y por tanto, damos la opcion de crear familia nueva.
    idfamilia = ""
    idfamilianuevo = ""
    while esEntero(idfamilia) == False and duplicado("familia","idfamilia",idfamilia) == False:
        #el bucle termina cuando se demuestra que el ID es entero y existe (o si creamos una familia nueva)
        idfamilia = input("Introduce idfamilia de artículo (número entero)")
        if duplicado("familia","idfamilia",idfamilia) == False: #si el ID no existe
            opcion = ""
            while opcion != "si" and opcion != "no":
                opcion = input("El id de familia que has introducido no existe. ¿Quieres crear una nueva familia? (si/no) ").lower()
            if opcion == "si": 
                idfamilia = altaFamilia()
                print("Al artículo que estás creando/modificando se le asignará la nueva familia una vez termines.")
                break
            else:
                print("Has respondido no. Entonces debes introducir un idfamilia que exista.")
                idfamilia = ""
        else: #si el ID existe, mostramos su info y pedimos confirmación
            print("La familia que has introducido es la siguiente.")
            buscarFamiliaID(idfamilia)
            correcto = ""
            while correcto != "si" and correcto != "no":
                correcto = input("¿Es esa la familia a la que quieres asignar el artículo?(si/no)").lower()
            if correcto == "no": #si no es esa la familia, iteramos el bucle
                idfamilia = ""
                
    idfamilia = int(idfamilia)
    return idfamilia

def altaArticulo():
    #pedimos datos y validamos.
    ######################################################################################### CODIGO Y FAMILIA
    codigo = input("Introduce codigo de artículo (número entero)")
    codigoduplicado = duplicado("articulo", "codigoarticulo",codigo)
    while codigoduplicado == True or esEntero(codigo) == False:
        codigo = input("Introduce codigo de artículo (número entero)")
        codigoduplicado = duplicado("articulo", "codigoarticulo",codigo)  
    codigo = int(codigo)

    idfamilia = asignarFamilia()
    ######################################################################################### NOMBRE Y PRECIO
    nombre=""
    while len(nombre)<1 or len (nombre)>100:
        nombre = input("Introduce nombre de artículo (1-100 caracteres)").lower()

    precio = ""
    while precio == "" and esFloat(precio) == False:
        try:
            precio = eval(input("Introduce precio de artículo (número entero o con decimales)"))
            
        except Exception:
            precio = ""
    
    ######################################################################################### INSERT ARTICULO
    try:
        sql="insert into articulo(codigoarticulo,idfamilia,nombrearticulo,preciounidad) values({},{},'{}',{})".format(codigo,idfamilia,nombre,precio)
        micursor.execute(sql)
        miconexion.commit()
        print("Artículo dado de alta con éxito.")
    except mysql.connector.Error:
        print("No se ha podido dar de alta el artículo.")
    
    ######################################################################################### INSERT STOCK
    #cláusula insert del stock. el codigo de artículo es único también, así que lo usaremos para rescatar el ID de artículo
    idarticulo="select idarticulo from articulo where codigoarticulo = "+str(codigo)
    micursor.execute(idarticulo)
    for columna in micursor:
        idarticulo = columna[0]
        
    try:
        stock="insert into stock(idarticulo,cantidadstock) values({},{})".format(idarticulo,0)
        micursor.execute(stock)
        miconexion.commit()
        print("Stock de artículo dado de alta. Stock inicial = 0")
    except mysql.connector.Error:
        print("No se ha podido dar de alta el stock del artículo.")
    ###################################################################### FIN ALTA ARTÍCULO 
   
def bajaArticulo(): #las tablas stock e historico stock tienen RESTRICT en sus cláusulas de delete, por lo que si no vamos a
    #cambiar la base de datos, la única opcion es borrar los registros de esas tablas previamente.
    
    borrarid = confirmar("eliminar")
    #este es el ID  a borrar, que se extrae de la funcion confirmar() que a su vez extrae un ID  o varios
    # de la función buscar. El parámetro sirve para describir lo que queremos confirmar dentro de la función
    
    sql = ""
    #si no se ha confirmado ningún ID, borrarid valdrá "", por lo que no se ejecutará la cláusula delete
    if borrarid != "":
        sqlarticulo="delete from articulo where idarticulo = "+str(borrarid)
        sqlstock = "delete from stock where idarticulo= "+str(borrarid)
        sqlhistorico = "delete from historicostock where idarticulo= "+str(borrarid)
        #cláusulas delete
        try:
            micursor.execute(sqlstock)
            micursor.execute(sqlhistorico)
            micursor.execute(sqlarticulo)
            miconexion.commit()
            print("Artículo dado de baja con éxito. Su stock e histórico de stock tambíen se han dado de baja.")
        except mysql.connector.Error:
            print("No se ha borrado el artículo.")

def buscar():
    print("Elige buscar por nombre de artículo (opción 1) o por codigo de artículo (opción 2)")
    op = ""
    condicion = ""
     
    while op != "1" and op != "2":
        op = input("Introduce una opción (1-2)")
        
    if op == "1":
        nombre=""
        while len(nombre)<1 or len (nombre)>100:
            nombre = input("Introduce nombre de artículo del cliente (1-100 caracteres)")
            condicion = "where nombrearticulo = '"+nombre+"'" #la consulta varía dependiendo de la opcion (nombre o codigo)
    elif op == "2":    
        codigo = input("Introduce codigo de artículo (número entero)")
        while esEntero(codigo) == False:
            codigo = input("Introduce codigo de artículo (número entero)") 
        codigo = int(codigo)
        condicion = "where codigoarticulo = "+str(codigo)
           
    #cláusula select y creacion de tabla    
    try:
        tabla=PrettyTable(["ID","CODIGO","ID FAMILIA","NOMBRE","PRECIO"])
        sql="select * from articulo "+condicion
        micursor.execute(sql)
        bufferid = []
        for columna in micursor:
            tabla.add_row(columna)
            bufferid.append(columna[0]) #almacenamos los id provisionalmente
        if len(bufferid) > 0: #si se encuentra uno o varios articulos, entonces mostramos la tabla
            #muestra los articulos
            print("Estos son los articulos que coinciden con su búsqueda")
            print(tabla)
        elif len(bufferid) == 0: #si no se ha encontrado ningún artículo, mostramos solamente este mensaje
            print("No se ha encontrado ningún articulo que coincida con los términos de búsqueda")
            
        return bufferid #lo devolvemos dado que queremos usar la funcion de buscar en baja y modificar
    except mysql.connector.Error:
        print("No se puede encontrar artículo")


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
        codigo = "codigo"
        codigoduplicado = duplicado("articulo", "codigoarticulo",codigo)
        while codigoduplicado == True or esEntero(codigo) == False:
            codigo = input("Introduce codigo de artículo (número entero)")
            codigoduplicado = duplicado("articulo", "codigoarticulo",codigo)
            if codigo != "" and esEntero(codigo) == True:
                codigo = int(codigo)
            elif codigo == "": # como permitimos nulo (para no modificar) salimos del bucle
                break
            
        
        nombre = input("Introduce nombre del artículo (0-100 caracteres)").lower()
        while len (nombre)>100:
            nombre = input("Introduce nombre del artículo (0-100 caracteres)").lower()

        precio = "precio"
        while precio != "" and esFloat(precio) == False:
            try:
                precio = input("Introduce precio de artículo (número entero o con decimales)")
                if precio == "":
                    break
                else:
                    precio = float(precio)
            except Exception:
                precio = "precio"
            
        # para el tema de la familia prefiero preguntar si quiere o no, tal como tengo la función asignarFamilia() no
        # me conviene pedir el dato aqui
        idfamilia = ""
        modfamilia = input("¿Quieres modificar la familia?(si/no)").lower()
        while modfamilia != "no" and modfamilia !="si":
            modfamilia = input("¿Quieres modificar la familia?(si/no)").lower()
            if modfamilia == "si": #si el usuario decide cambiar el id, llamamos a la funcion
                idfamilia = asignarFamilia()
       
        #A partir de aqui, concatenamos los valores que queremos modificar
        if codigo != "":
            modif = modif + " codigoarticulo = "+codigo+","
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
    #tanto en modificar como en baja, queremos pedir al usuario que confirme si quiere borrar/modificar el articulo
    #además, si hay varios articulos que coinciden con el criterio de búsqueda, esta función permite seleccionar uno.
    bufferid = buscar()
    borrarmodid = "" #este es el ID que se borrará o modificará
    confirmacion = ""
    
    if len(bufferid) == 1:#en el caso de que solo se haya encontrado un articulo
        while confirmacion != "no" and confirmacion != "si":
            confirmacion = input("¿Está seguro de que quiere "+borrarModificar+" el articulo? (si/no)").lower()
            borrarmodid = bufferid[0] #sabemos que si solo hay uno, borramos el único ID del array, en la posicion 0
            
    elif len(bufferid) > 1:#en caso de que encontremos más de uno
        idseleccion = ""
        try:
            idseleccion = int(input("Se han encontrado varios articulos, escoge el ID (1º columna) de aquel que quieras "+borrarModificar+".\n"+
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


def todosArticulos():
    tabla=PrettyTable(["ID","CODIGO","ID FAMILIA","NOMBRE","PRECIO","NOMBRE FAMILIA", "STOCK ACTUAL"])
    sql="""SELECT a.idarticulo, a.codigoarticulo, a.idfamilia, a.nombrearticulo, a.preciounidad,
    f.nombrefamilia, s.cantidadstock from articulo a, stock s, familia f
    WHERE s.idarticulo=a.idarticulo AND a.idfamilia = f.idfamilia"""
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
        print ("")
        print ("1. Alta artículo")
        print ("2. Baja artículo")
        print ("3. Buscar - Modificar artículo")
        print ("4. Mostrar todos los artículos")
        print ("5. Salir")
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
            print("Para dar de baja a un artículo, introduce nombre o el código de artículo")
            bajaArticulo()
        elif opcion == 3:
            print("Para buscar y modificar un artículo, introduce nombre o el código de artículo")
            modificar()
        elif opcion == 4:
            todosArticulos()
        elif opcion == 5:
            salir = True         
        else:
            print ("Introduce un numero entre 1 y 5")  
    print ("Fin")



menuArticulo()
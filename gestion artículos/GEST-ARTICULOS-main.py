import mysql.connector
from prettytable import PrettyTable
from datetime import date
import validaciones as val
import moduloFamilia as fam

miconexion = mysql.connector.connect(
  host="localhost",
  user="root",
  password="admin",
  database="ferreteria"
)
micursor=miconexion.cursor()

bufferid = []

"""
En general las funciones son similares a las de clientes, con los cambios necesarios, aunque en este caso he decidido
separarlas en varios archivos dado que la gestión de familias es bastante extensa.

En este archivo tenemos:
- Alta: recoge datos y ejecuta un insert (además de otro para la tabla stock). Llama a la función asignarFamilia
- Baja: Primero llama a la función confirmar que a su vez llama a buscar. Es decir, primero se hace una búsqueda de un artículo,
luego se confirma o no si se quiere borrar, y finalmente se borra si la confirmación es positiva. Se ejecutan deletes en artículo,
stock e histórico stock.
- CopiaHistorico: es llamada en baja, antes de ejecutar los deletes. Recoge datos de la tabla histórico y los vuelca en la
tabla de copia de histórico
- Modificar: Procedimiento similar a la baja, solo que en su última etapa (se la confirmación es positiva) se piden datos
y se ejecuta un update. Llama a asignarFamilia y finalmente a ejecutarMod
- EjecutarMod: ejecuta un update para modificar el artículo
- Confirmar y buscar: necesarias para la baja o modificación de un artículo. Se busca uno o varios artículos y luego se confirma
si se quiere borrar o modificar el artículo (o uno de los varios encontrados)
- Todos: muestra todos los artículos. Útil para ver rápidamente los cambios efecutados en la tabla artículo.

En el modulo de familia tenemos:
-AsignarFamilia: pide un idfamilia, si existe, muestra su información llamando a buscarFamiliaID, si no, se ofrece la opción
de crear una nueva familia, llamando a AltaFamilia. En cualquier caso, devolverá el idfamilia que se asigna al artículo, ya
sea en su alta o modificación.
-BuscarFamiliaID: muestra datos de familia con cierto ID
-AltaFamilia: similar al alta de artículo, se le da la opción al usuario de elegir un idfamilia o dejar que se autogenere.

En validaciones tenemos:
-esEntero y esFloat: para validar que un dato sea entero o float.
-duplicado: para comprobar si un dato que se introduce existe en la base de datos, a la hora de evitar IDs o códigos duplicados
"""

########################################
#FUNCIONES DE MENU
########################################

def altaArticulo():
    #pedimos datos y validamos.
    ######################################################################################### CODIGO Y FAMILIA
    codigo = ""
    while val.duplicado("articulo", "codigoarticulo",codigo) == True or val.esEntero(codigo) == False:
        codigo = input("Introduce codigo de artículo (número entero)") 
    codigo = int(codigo)

    idfamilia = fam.asignarFamilia()
    ######################################################################################### NOMBRE Y PRECIO
    nombre=""
    while len(nombre)<1 or len (nombre)>100:
        nombre = input("Introduce nombre de artículo (1-100 caracteres)").lower()

    precio = ""
    while precio == "" or val.esFloat(precio) == False:
        precio = input("Introduce precio de artículo (número entero o con decimales)")
    precio = float(precio)
    
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
   
#antes de borrar el historico de stock, hay que volcarlo a la tabla de copia. le pasamos el id de artículo que vamos a borrar
#debemos introducir los campos: idarticulo, codigoarticulo, idfamilia, nombrearticulo, cantidadhistoricostock, fechaeliminacion
def copiaHistorico(borrarid):
    # RECOGIDA DE DATOS
    infoHist = []
    try:
        recoge = """select h.idarticulo, a.codigoarticulo, a.idfamilia, a.nombrearticulo, h.cantidadhistoricostock
        from historicostock h, articulo a where a.idarticulo = h.idarticulo and h.idarticulo = """+str(borrarid)
        micursor.execute(recoge)
        for columna in micursor:
            infoHist.append(columna)
    except mysql.connector.Error:
        print("Error al obtener datos del histórico.")
    # VOLCADO DE DATOS    
    try:
        for indice in range(len(infoHist)):
            copiastock="""insert into copiahistoricostock(idarticulo, codigoarticulo, idfamilia, nombrearticulo,
            cantidadhistoricostock, fechaeliminacion) values({},{},{},'{}',{},'{}')""".format(infoHist[indice][0],infoHist[indice][1],
                                                                                            infoHist[indice][2],infoHist[indice][3],
                                                                                            infoHist[indice][4], date.today())
            #al cada insert le metemos una fila de la lista de registros que hemos guardamos, más la fecha de hoy.
            micursor.execute(copiastock)
            miconexion.commit()
    except mysql.connector.Error:
        print("Error al volcar datos en la tabla copia de histórico de stocks")
        

def bajaArticulo(): #las tablas stock e historico stock tienen RESTRICT en sus cláusulas de delete, por lo que si no vamos a
    #cambiar la base de datos, la única opcion es borrar los registros de esas tablas previamente.
    
    borrarid = confirmar("eliminar")
    #este es el ID  a borrar, que se extrae de la funcion confirmar() que a su vez extrae un ID  o varios
    # de la función buscar. El parámetro sirve para describir lo que queremos confirmar dentro de la función
    
    sql = ""
    #si no se ha confirmado ningún ID, borrarid valdrá "", por lo que no se ejecutarán los deletes.
    if borrarid != "":
        sqlarticulo="delete from articulo where idarticulo = "+str(borrarid)
        sqlstock = "delete from stock where idarticulo= "+str(borrarid)
        sqlhistorico = "delete from historicostock where idarticulo= "+str(borrarid)
        #cláusulas delete
        try:
            copiaHistorico(borrarid)
            micursor.execute(sqlstock)
            micursor.execute(sqlhistorico)
            micursor.execute(sqlarticulo)
            miconexion.commit()
            print("Artículo dado de baja con éxito. Su stock e histórico de stock tambíen se han dado de baja.")
            print("Su histórico de stock ha sido volcado a la tabla copia histórico stock.")
        except mysql.connector.Error:
            print("No se ha borrado el artículo.")


def modificarArticulo():
    modificarid = confirmar("modificar")
    #funciona de forma similar a baja(), le pasamos 'modificar' para que los mensajes de los inputs tengan sentido.
    
    #si el ID seleccionado es válido, es decir, si hemos confirmado que queremos modificar cierto ID, entonces pedimos datos
    # para modificar el registro.
    if modificarid != "":
        print("Si quieres modificar un campo, introduce algo en ese campo. Si no quieres modificar un campo, pulsa intro sin introducir nada.")
        #pedimos datos y validamos
        #EN ESTE CASO PERMITIMOS NULL, SI SE DEJA UN CAMPO VACÍO, NO SE MODIFICA
        ############################################################################################# PEDIR DATOS
        codigo = "codigo"
        while val.duplicado("articulo", "codigoarticulo",codigo) == True or val.esEntero(codigo) == False:
            codigo = input("Introduce codigo de artículo (número entero)")
            if codigo != "" and val.esEntero(codigo) == True:
                codigo = int(codigo)
            elif codigo == "": # como permitimos nulo (para no modificar) salimos del bucle
                break
             
        nombre = input("Introduce nombre del artículo (0-100 caracteres)").lower()
        while len (nombre)>100:
            nombre = input("Introduce nombre del artículo (0-100 caracteres)").lower()

        precio = "precio"
        while precio != "" and val.esFloat(precio) == False:
            precio = input("Introduce precio de artículo (número entero o con decimales)")        
        if precio != "":
            precio = float(precio)
            
        # para el tema de la familia prefiero preguntar si quiere o no, tal como tengo la función asignarFamilia() no
        # me conviene pedir el dato aqui, porque luego se pide también en esa función.
        idfamilia = ""
        modfamilia = ""
        while modfamilia != "no" and modfamilia != "si":
            modfamilia = input("¿Quieres modificar la familia?(si/no)").lower()
            if modfamilia == "si": #si el usuario decide cambiar el id, llamamos a la funcion
                idfamilia = fam.asignarFamilia()
        #ejecuta un update con los parámetros que hemos recogido, además del ID a modificar
        ejecutarMod(codigo, nombre, precio, idfamilia, modificarid)

# para que la funcion modificar no sea muy extensa, el update lo ejecuto en otra función
def ejecutarMod(codigo, nombre, precio, idfamilia, modificarid):
    sql = ""
    modif = "set"
    ############################################################################################# SENTENCIA SQL E INSERT
    #A partir de aqui, concatenamos los valores que queremos modificar
    if codigo != "":
        modif = modif + " codigoarticulo = "+str(codigo)+","
    if nombre != "":
        modif = modif + " nombrearticulo = '"+nombre+"',"
    if precio != "":
        modif = modif + " preciounidad = "+str(precio)+","
    if idfamilia != "":
        modif = modif + " idfamilia = "+str(idfamilia)+","
            
    modif = modif[:-1]
    #esto nos permite borrar la ultima coma, que sobrará en la sentencia   
    sql="update articulo "+modif+" where idarticulo = "+str(modificarid)
    try:
        micursor.execute(sql)
        miconexion.commit()
        print("Artículo modificado con éxito.")
    except mysql.connector.Error:
        print("No se ha modificado el artículo.")
        # esta excepción saltará normalmente si no se ha metido ningún dato para modificar.

def confirmar(borrarModificar):
    #tanto en modificar como en baja, queremos pedir al usuario que confirme si quiere borrar/modificar el artículo
    #además, si hay varios artículos que coinciden con el criterio de búsqueda, esta función permite seleccionar uno.
    bufferid = buscar()
    borrarmodid = "" #este es el ID que se borrará o modificará
    confirmacion = ""
    
    if len(bufferid) == 1:#en el caso de que solo se haya encontrado un articulo
        while confirmacion != "no" and confirmacion != "si":
            confirmacion = input("¿Está seguro de que quiere "+borrarModificar+" el artículo? (si/no)").lower()
            borrarmodid = bufferid[0] #sabemos que si solo hay uno, borramos/modificamos el único ID del array, en la posicion 0
            
    elif len(bufferid) > 1:#en caso de que encontremos más de uno
        idseleccion = ""
        try:
            idseleccion = int(input("Se han encontrado varios articulos, escoge el ID (1º columna) de aquel que quieras "+borrarModificar+".\n"+
                                    "Si no quieres "+borrarModificar+" ninguno, pulsa intro o introduce cualquier cosa que no sea un ID: "))
        except ValueError:
            idseleccion = ""
        
        for i in bufferid:
            if i == idseleccion: #si ha metido un id válido (dentro del buffer de IDs) entonces se lo asignamos a borrarmodid
                confirmacion = "si" #entendemos que si hemos metido un ID válido, estamos confirmando su modificación/borrado
                borrarmodid = idseleccion
    #esta funcion devuelve el ID que vamos a borrar o modificar, si no se confirma un ID a borrar/modificar, esta función devolverá ""
    if confirmacion == "si":
        return borrarmodid
    else:
        return ""

# en este programa, la búsqueda siempre se hace como paso previo a modificar o baja, por lo que esta función siempre cuenta
# con la intermediación de confirmar(), en lugar de llamarla directamente desde el menú
def buscar():
    print("Elige buscar por nombre de artículo (opción 1) o por codigo de artículo (opción 2)")
    op = ""
    condicion = ""
     
    while op != "1" and op != "2":
        op = input("Introduce una opción (1-2)")
        
    if op == "1":
        nombre=""
        while len(nombre)<1 or len (nombre)>100:
            nombre = input("Introduce nombre de artículo (1-100 caracteres)")
            condicion = "where nombrearticulo = '"+nombre+"'" #la consulta varía dependiendo de la opcion (nombre o codigo)
    elif op == "2":    
        codigo = ""
        while val.esEntero(codigo) == False:
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
            print("Estos son los artículos que coinciden con su búsqueda")
            print(tabla)
        elif len(bufferid) == 0: #si no se ha encontrado ningún artículo, mostramos solamente este mensaje
            print("No se ha encontrado ningún artículo que coincida con los términos de búsqueda")
            
        return bufferid #lo devolvemos dado que queremos usar la funcion de buscar en baja y modificar
    except mysql.connector.Error:
        print("No se puede encontrar artículo")


#función para mostrar rápidamente los artículos disponibles. también muestra el nombre de su familia y su stock
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
            opcion = int(input(""))
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
            modificarArticulo()
        elif opcion == 4:
            todosArticulos()
        elif opcion == 5:
            salir = True
        else:
            print ("Las opciones disponibles van de 1 a 5")  
    print ("Fin de la gestión de artículos.")

menuArticulo()
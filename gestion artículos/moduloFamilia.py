import mysql.connector
from prettytable import PrettyTable
import validaciones as val

miconexion = mysql.connector.connect(
  host="localhost",
  user="root",
  password="admin",
  database="ferreteria"
)
micursor=miconexion.cursor()

#muestra la familia que estamos intentando asignar a un artículo
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
    while val.esEntero(idfamilia) == False and val.duplicado("familia","idfamilia",idfamilia) == False:
        #el bucle termina cuando se demuestra que el ID es entero y existe (o si creamos una familia nueva)
        idfamilia = input("Introduce idfamilia de artículo (número entero)")
        ################################################################# SI EL ID INTRODUCIDO NO EXISTE
        if val.duplicado("familia","idfamilia",idfamilia) == False: 
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
        
        ################################################################# SI EL ID INTRODUCIDO SI EXISTE
        else: #mostramos su info y pedimos confirmación
            print("La familia que has introducido es la siguiente.")
            buscarFamiliaID(idfamilia)
            correcto = ""
            while correcto != "si" and correcto != "no":
                correcto = input("¿Es esa la familia a la que quieres asignar el artículo?(si/no)").lower()
            if correcto == "no": #si no es esa la familia, iteramos el bucle
                idfamilia = ""
                
    idfamilia = int(idfamilia)
    return idfamilia

def altaFamilia():
    ######################################################################################### ID FAMILIA
    sql = ""
    idfamilianuevo="id"
    #no aceptamos un ID de familia si NO es entero o ya existe o si pulsa intro
    while val.esEntero(idfamilianuevo) == False or val.duplicado("familia","idfamilia",idfamilianuevo) == True:
        idfamilianuevo = input("Introduce idfamilia de la familia (número entero, pulsa intro para generar uno automático.) ")
        if idfamilianuevo == "":# si pulsa intro, permitimos salir del bucle
            break
    if idfamilianuevo != "": #si no es id vacío, lo utilizaremos.
        idfamilianuevo = int(idfamilianuevo)
    
    ######################################################################################### NOMBRE Y DESCUENTO
    nombre = ""
    while len(nombre)<1 or len (nombre)>100 or val.duplicado("familia","nombrefamilia",nombre) == True: #tampoco puede estar duplicado
        nombre = input("Introduce nombre de la familia (1-100 caracteres) ").lower()
    
    descuento = "descuento"
    while descuento != "" and val.esFloat(descuento) == False:
        descuento = input("Introduce el descuento de la familia (entero o decimales, o pulsa intro si no tiene descuento) ")

    if descuento == "":#solo podemos meter floats en el campo descuento, aunque se permite null también.
        descuento = "null"
    else:
        descuento = float(descuento)
    ######################################################################################### SQL E INSERT DE LA FAMILIA
    if idfamilianuevo == "":#dependiendo de si el usuario quiere meter un id (no duplicado) o que se autogenere.
        sql = "insert into familia (nombrefamilia, descuentofamilia) values ('{}',{})".format(nombre, descuento)
    else:
        sql = "insert into familia (idfamilia, nombrefamilia, descuentofamilia) values ({},'{}',{})".format(idfamilianuevo,nombre,descuento)
    try:
        micursor.execute(sql)
        miconexion.commit()
        print("Familia dada de alta con éxito.")
    except mysql.connector.Error:
        print("No se ha podido dar de alta la familia.")
        
    ######################################################## RECUPERAR EL ID FAMILIA (PARA EL ALTA/MODIFICACION DE ARTICULO)
        
    #vamos a hacer que esta funcion devuelva el ID creado para utilizarlo en crear o modificar artículo,
    #dado que esta función es llamada allí (a través de asignarFamilia)
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


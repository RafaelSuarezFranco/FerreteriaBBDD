import mysql.connector

miconexion = mysql.connector.connect(
  host="localhost",
  user="root",
  password="admin",
  database="ferreteria"
)
micursor=miconexion.cursor()

#FUNCIONES VALIDACIÓN
#validacion para que solo se metan numeros enteros
def esEntero(num):
    try:
        entero = int(num)
        num = entero
        return True
    except ValueError:
        return False
#o floats
def esFloat(num):
    try:
        float1 = float(num)
        num = float1
        return True 
    except ValueError:
        return False


#esta función valida si un dato que intentamos introducir yá existe en la base de datos.
    
#la validación es similar a la del identificador de los clientes, en este caso
#a la funcion le pasamos la tabla y el campo porque la utilizaremos para validar en las tablas de artículo y familia
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
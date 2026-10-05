from models import Cliente

ana = Cliente(1, "  ana  ", "pérez", "ANA@Ejemplo.com", "0987654321", "guayaquil", "Av. 1")

print(ana.nombre)
print(ana.email)
print(ana.nombre_completo)
print(ana.dominio_email)
print(Cliente.total_creados)

ana.ciudad = "quito"
print(ana.ciudad)

print(ana._Cliente__nombre)

from shared.herramientas import (
    imprimir_titulo, imprimir_exito, imprimir_error, imprimir_info, confirmar
)
from views import ClienteController


class MenuClientes:
    """VISTA: muestra, pide y presenta. No decide reglas del negocio."""

    TITULO = "SISTEMA DE GESTIÓN DE CLIENTES"     # atributo de clase
    ANCHO = 85

    def __init__(self, controlador=ClienteController):
        # ATRIBUTOS DE INSTANCIA: estado de ESTE menú
        self.__controlador = controlador
        self.__activo = True
        # DICCIONARIO tecla -> (texto, método). Reemplaza al if/elif largo.
        self.__opciones = {
            "1": ("Crear cliente", self.crear),
            "2": ("Ver todos", self.listar),
            "3": ("Buscar", self.buscar),
            "4": ("Ver por id", self.ver_por_id),
            "5": ("Actualizar", self.actualizar),
            "6": ("Eliminar", self.eliminar),
            "7": ("Estadísticas", self.estadisticas),
            "0": ("Salir", self.salir),
        }

    # ===== ESTÁTICOS: utilidades de pantalla, no dependen del menú =====
    @staticmethod
    def pausa():
        input("\nPresione Enter para continuar...")

    @staticmethod
    def pedir_entero(etiqueta):
        """Devuelve un entero o None si el usuario escribió cualquier otra cosa."""
        try:
            return int(input(etiqueta))
        except ValueError:
            return None

    @staticmethod
    def mostrar_resultado(exito, mensaje):
        if exito:
            imprimir_exito(mensaje)
        else:
            imprimir_error(mensaje)

    # ===== MÉTODOS DE INSTANCIA =====
    def mostrar_tabla(self, clientes):
        print(f"{'ID':<5}{'NOMBRE':<25}{'EMAIL':<28}{'CIUDAD':<15}{'TELÉFONO':<12}")
        print("-" * self.ANCHO)
        for cliente in clientes:
            print(f"{cliente.id:<5}{cliente.nombre_completo:<25}"
                  f"{cliente.email:<28}{cliente.ciudad:<15}{cliente.telefono:<12}")
        print("-" * self.ANCHO)
        imprimir_info(f"Total: {len(clientes)} cliente(s)")

    def crear(self):
        imprimir_titulo("CREAR NUEVO CLIENTE")
        # Recorro la TUPLA de campos del Modelo: si el Modelo cambia, el formulario también
        datos = {}
        for campo in self.__controlador.MODELO.CAMPOS:
            datos[campo] = input(f"{campo.capitalize()}: ")

        exito, mensaje = self.__controlador.crear(datos)
        self.mostrar_resultado(exito, mensaje)
        self.pausa()

    def listar(self):
        imprimir_titulo("LISTA DE CLIENTES")
        clientes = self.__controlador.listar()
        if not clientes:
            imprimir_info("Todavía no hay clientes. Use la opción 1 para crear el primero.")
        else:
            self.mostrar_tabla(clientes)
        self.pausa()

    def buscar(self):
        imprimir_titulo("BUSCAR CLIENTE")
        termino = input("Nombre, email, teléfono o ciudad: ")
        encontrados = self.__controlador.buscar(termino)
        if not encontrados:
            imprimir_info(f"Ningún cliente coincide con '{termino}'.")
        else:
            self.mostrar_tabla(encontrados)
        self.pausa()

    def ver_por_id(self):
        imprimir_titulo("VER CLIENTE POR ID")
        id_cliente = self.pedir_entero("Id del cliente: ")
        if id_cliente is None:
            imprimir_error("El id debe ser un número entero")
            return self.pausa()

        cliente = self.__controlador.obtener(id_cliente)
        if cliente is None:
            imprimir_error(f"No existe un cliente con id {id_cliente}")
        else:
            for clave, valor in cliente.a_diccionario().items():
                print(f"  {clave.capitalize():<12}: {valor}")
            imprimir_info(f"Dominio del email: {cliente.dominio_email}")
        self.pausa()

    def actualizar(self):
        imprimir_titulo("ACTUALIZAR CLIENTE")
        id_cliente = self.pedir_entero("Id del cliente: ")
        if id_cliente is None:
            imprimir_error("El id debe ser un número entero")
            return self.pausa()

        cliente = self.__controlador.obtener(id_cliente)
        if cliente is None:
            imprimir_error(f"No existe un cliente con id {id_cliente}")
            return self.pausa()

        imprimir_info(f"Editando a {cliente.nombre_completo}")
        print("Deje en blanco el campo que no quiera cambiar.\n")

        cambios = {}
        for campo in self.__controlador.MODELO.CAMPOS:
            actual = getattr(cliente, campo)          # lee la PROPIEDAD
            nuevo = input(f"{campo.capitalize()} [{actual}]: ").strip()
            if nuevo:
                cambios[campo] = nuevo

        self.mostrar_resultado(*self.__controlador.actualizar(id_cliente, cambios))
        self.pausa()

    def eliminar(self):
        imprimir_titulo("ELIMINAR CLIENTE")
        id_cliente = self.pedir_entero("Id del cliente: ")
        if id_cliente is None:
            imprimir_error("El id debe ser un número entero")
            return self.pausa()

        cliente = self.__controlador.obtener(id_cliente)
        if cliente is None:
            imprimir_error(f"No existe un cliente con id {id_cliente}")
            return self.pausa()

        imprimir_info(f"Se eliminará: {cliente}")
        if confirmar("¿Confirma la eliminación?"):
            self.mostrar_resultado(*self.__controlador.eliminar(id_cliente))
        else:
            imprimir_info("Operación cancelada")
        self.pausa()

    def estadisticas(self):
        imprimir_titulo("ESTADÍSTICAS")
        datos = self.__controlador.estadisticas()
        print(f"  Clientes registrados : {datos['total']}")
        print(f"  Ciudades distintas   : {len(datos['ciudades'])} -> {', '.join(datos['ciudades'])}")
        print(f"  Dominios de email    : {', '.join(datos['dominios'])}")
        print(f"  Sin teléfono         : {len(datos['sin_telefono'])}")
        self.pausa()

    def salir(self):
        self.__activo = False          # cambia el estado del objeto
        imprimir_info("¡Hasta luego! 👋")

    def mostrar_menu(self):
        imprimir_titulo(self.TITULO)
        for tecla, (texto, _metodo) in self.__opciones.items():
            print(f"  {tecla}. {texto}")
        print()

    def ejecutar(self):
        """El bucle principal: vive mientras __activo sea True."""
        while self.__activo:
            self.mostrar_menu()
            tecla = input("Seleccione una opción: ").strip()

            if tecla not in self.__opciones:
                imprimir_error("Opción no válida")
                self.pausa()
                continue

            _texto, metodo = self.__opciones[tecla]
            metodo()          # el diccionario guarda el método: aquí se ejecuta


if __name__ == "__main__":
    try:
        MenuClientes().ejecutar()      # se crea el objeto y se lo pone a correr
    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario.")
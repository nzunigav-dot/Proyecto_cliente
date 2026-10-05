from models import Cliente
from shared.json_manager import GestorJSON


class ClienteController:
    """CONTROLADOR: las cinco operaciones. No imprime ni pide datos."""

    # ===== ATRIBUTOS DE CLASE: toda la configuración junta =====
    MODELO = Cliente
    ARCHIVO = "data/clientes.json"
    CAMPOS_BUSCABLES = ("nombre", "apellido", "email", "telefono", "ciudad")
    _gestor = GestorJSON(ARCHIVO)        # se crea una sola vez, al importar el módulo

    # ===== AYUDAS =====
    @classmethod
    def _registros(cls):
        """LISTA de diccionarios, tal como está en el archivo."""
        return cls._gestor.leer()

    @classmethod
    def emails_registrados(cls, excepto_id=None):
        """CONJUNTO de emails ya usados: permite detectar duplicados al instante."""
        return {
            registro["email"].lower()
            for registro in cls._registros()
            if registro["id"] != excepto_id
        }

    @classmethod
    def siguiente_id(cls):
        ids = [registro["id"] for registro in cls._registros()]
        return max(ids) + 1 if ids else 1

    @staticmethod
    def _coincide(registro, termino, campos):
        """Estático: no necesita la clase, solo compara textos."""
        for campo in campos:
            if termino in str(registro.get(campo, "")).lower():
                return True
        return False

    # ===== C · CREATE =====
    @classmethod
    def crear(cls, datos):
        """datos: diccionario. Devuelve la TUPLA (exito, mensaje)."""
        try:
            faltantes = [
                campo for campo in cls.MODELO.OBLIGATORIOS
                if not str(datos.get(campo, "")).strip()
            ]
            if faltantes:
                return False, f"Faltan campos obligatorios: {', '.join(faltantes)}"

            email = str(datos.get("email", "")).strip().lower()
            if email in cls.emails_registrados():
                return False, "Ese email ya está registrado"

            valores = {campo: datos.get(campo, "") for campo in cls.MODELO.CAMPOS}

            # cls.MODELO es la clase: aquí nace el objeto y sus setters validan todo
            objeto = cls.MODELO(cls.siguiente_id(), **valores)

            registros = cls._registros()
            registros.append(objeto.a_diccionario())
            if not cls._gestor.guardar(registros):
                return False, "No se pudo escribir el archivo"

            return True, f"{objeto.nombre_completo} creado con id {objeto.id}"

        except ValueError as error:
            # Los setters del Modelo lanzan ValueError con el mensaje ya listo
            return False, str(error)

    # ===== R · READ =====
    @classmethod
    def listar(cls):
        """LISTA de objetos del Modelo."""
        return [cls.MODELO.desde_diccionario(r) for r in cls._registros()]

    @classmethod
    def obtener(cls, id_registro):
        for objeto in cls.listar():
            if objeto.id == id_registro:
                return objeto
        return None

    # ===== S · SEARCH =====
    @classmethod
    def buscar(cls, termino):
        termino = str(termino).strip().lower()
        if not termino:
            return []
        return [
            cls.MODELO.desde_diccionario(registro)
            for registro in cls._registros()
            if cls._coincide(registro, termino, cls.CAMPOS_BUSCABLES)
        ]

    # ===== U · UPDATE =====
    @classmethod
    def actualizar(cls, id_registro, cambios):
        try:
            # DIFERENCIA DE CONJUNTOS: ¿mandaron campos que no existen?
            desconocidos = set(cambios) - set(cls.MODELO.CAMPOS)
            if desconocidos:
                return False, f"Campos no válidos: {', '.join(sorted(desconocidos))}"
            if not cambios:
                return False, "No se indicó ningún cambio"

            objeto = cls.obtener(id_registro)
            if objeto is None:
                return False, f"No existe un registro con id {id_registro}"

            if "email" in cambios:
                nuevo = str(cambios["email"]).strip().lower()
                if nuevo in cls.emails_registrados(excepto_id=id_registro):
                    return False, "Ese email ya lo usa otro registro"

            # setattr le asigna a la PROPIEDAD, así que cada setter valida el valor
            for campo, valor in cambios.items():
                setattr(objeto, campo, valor)

            registros = cls._registros()
            for indice, registro in enumerate(registros):
                if registro["id"] == id_registro:
                    registros[indice] = objeto.a_diccionario()
                    break

            cls._gestor.guardar(registros)
            return True, f"Registro {id_registro} actualizado ({len(cambios)} campo/s)"

        except ValueError as error:
            return False, str(error)

    # ===== D · DELETE =====
    @classmethod
    def eliminar(cls, id_registro):
        registros = cls._registros()
        # Lista nueva sin ese registro: nunca se borra mientras se recorre
        quedan = [r for r in registros if r["id"] != id_registro]

        if len(quedan) == len(registros):
            return False, f"No existe un registro con id {id_registro}"

        cls._gestor.guardar(quedan)
        return True, f"Registro {id_registro} eliminado"

    # ===== EXTRA =====
    @classmethod
    def estadisticas(cls):
        registros = cls._registros()
        ciudades = {r.get("ciudad", "") for r in registros if r.get("ciudad")}
        dominios = {r["email"].split("@")[1] for r in registros if "@" in r["email"]}
        sin_telefono = [r["nombre"] for r in registros if not r.get("telefono")]
        return {
            "total": len(registros),
            "ciudades": sorted(ciudades),
            "dominios": sorted(dominios),
            "sin_telefono": sin_telefono,
        }

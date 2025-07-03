"""Controller for handling GET requests for results"""

from config.response import get_response
from config.logger_settings import LoggerInfo
from controllers.data import data
import re
import unicodedata
from rapidfuzz import process, fuzz


class InformationHandler:
    """Handler for processing results."""

    def __init__(self, event):
        self.event = event
        self.path = event["path"]
        self.query_string_parameters = (
            event.get("queryStringParameters", {})
            if event.get("queryStringParameters")
            else {}
        )
        self.logger = LoggerInfo()
        # self.s3_service = S3Service(
        #     bucket_name=os.getenv("BUCKET_NAME", "default-bucket")
        # )

    # @paginate_list
    def get_information(self):
        try:
            district = self.query_string_parameters.get("district", "").strip()

            # extract embeddings of s3

            # self.s3_service.download_file("embedding/barrios_embeddings.npy", "/tmp/barrios_embeddings.npy")
            # self.s3_service.download_file("embedding/barrios_index.bin", "/tmp/barrios_index.bin")
            # self.s3_service.download_file("embedding/barrios_original.json", "/tmp/barrios_original.json")

            # searcher = BarrioSearcher(
            #     "/tmp/barrios_embeddings.npy",
            #     "/tmp/barrios_index.bin",
            #     "/tmp/barrios_original.json"
            # )

            # result = searcher.buscar(district)
            return get_response(200, self.buscar_barrio_mas_parecido(district))
        except Exception as e:
            self.logger.exception(e)
            return get_response(500, e)

    # Función para normalizar texto
    def normalizar(self, texto):
        texto = texto.lower()
        texto = unicodedata.normalize("NFD", texto)
        texto = texto.encode("ascii", "ignore").decode("utf-8")  # quita tildes
        texto = re.sub(
            r"[^a-z0-9]", "", texto
        )  # quita todo lo que no sea letra o número
        return texto

    def buscar_barrio_mas_parecido(self, texto_usuario):
        lista_json = data
        barrios_originales = [item["BARRIO"] for item in lista_json]
        barrios_normalizados = [self.normalizar(b) for b in barrios_originales]

        texto_normalizado = self.normalizar(texto_usuario)

        resultado, score, index = process.extractOne(
            texto_normalizado, barrios_normalizados, scorer=fuzz.ratio
        )

        return {
            "match": barrios_originales[index],
            "score": score,
            "registro": lista_json[index],
        }

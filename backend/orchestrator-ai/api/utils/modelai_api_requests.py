import io
from fastapi import HTTPException, Response
import requests
from api.routers.logging import LoggingManager

class ModelAiApi:
    def analyze_image(self, image_bytes: bytes, image_id: str, service_name: str, logger: LoggingManager) -> bytes:
        """
        Analiza la imagen enviándola a la API externa y retorna los bytes de la imagen procesada
        """
        try:
            url = f"http://{service_name}-api/analyze-image"
            logger.info(f"Model Ai URL to request: {url}")
            file_name = f"{image_id}.png"

            logger.info(f"Preparing Image for {service_name} Api request...")
            
            # Asegurarse de que image_bytes es del tipo correcto
            if isinstance(image_bytes, io.BytesIO):
                logger.info("Reading image bytes from BytesIO...")
                image_bytes = image_bytes.getvalue()
            elif not isinstance(image_bytes, (bytes, bytearray)):
                logger.error("image_bytes debe ser bytes o BytesIO")
                raise ValueError("image_bytes debe ser bytes o BytesIO")
            
            # Preparar el multipart form data
            files = {'image_file': (file_name, image_bytes, 'image/png')}
            data = {"image_id": image_id}
            
            # Hacer la petición
            response = requests.post(url, files=files, data=data, timeout=1800)
            
            if response.status_code == 200:
                logger.info(f"Image analyzed successfully by {service_name}")
                return response.content  # Retornar los bytes directamente
            else:
                logger.error(f"API returned status code: {response.status_code}")
                logger.error(f"API response: {response.text}")
                return None
        
        except Exception as error:
            logger.error(f"Error during Model Api request: {error}")
            raise HTTPException(status_code=400, detail="Error during Api request")
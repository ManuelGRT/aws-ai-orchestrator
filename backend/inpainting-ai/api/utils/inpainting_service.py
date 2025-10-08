from api.routers.logging import LoggingManager
from lama_cleaner.model_manager import ModelManager
from api.routers.logging import LoggingManager
from fastapi import UploadFile, HTTPException
from fastapi.responses import StreamingResponse
import io
import cv2
import numpy as np
from PIL import Image
import easyocr
from lama_cleaner.schema import Config


# DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
DEVICE = "cpu"
reader = easyocr.Reader(['en', 'es'], gpu=(DEVICE == "cuda"))
lama = ModelManager(name="lama", device=DEVICE)

def ocr_text_mask(pil_img: Image.Image) -> np.ndarray:
    """Detecta texto con OCR y devuelve máscara binaria lista para inpainting."""
    img = np.array(pil_img.convert("RGB"))
    h, w = img.shape[:2]
    mask = np.zeros((h, w), dtype=np.uint8)

    results = reader.readtext(img, detail=1)

    for item in results:
        if len(item) < 3:
            continue
        box, _, conf = item
        if conf < 0.45:  # confianza mínima fija
            continue

        pts = np.array(box, dtype=np.float32)
        x_min = max(int(np.floor(pts[:,0].min())) - 8, 0)
        y_min = max(int(np.floor(pts[:,1].min())) - 8, 0)
        x_max = min(int(np.ceil (pts[:,0].max())) + 8, w-1)
        y_max = min(int(np.ceil (pts[:,1].max())) + 8, h-1)

        cv2.rectangle(mask, (x_min, y_min), (x_max, y_max), 255, -1)

    if mask.any():
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
        mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel, iterations=1)

    return mask


def normalize_result(result: np.ndarray) -> np.ndarray:
    """Normaliza salida de lama a RGB uint8"""
    # Si viene en float en [0,1]
    if result.dtype in [np.float32, np.float64]:
        if result.max() <= 1.0:
            result = (result * 255).clip(0, 255).astype(np.uint8)
        else:  # ya está en [0,255]
            result = result.clip(0, 255).astype(np.uint8)
    else:
        result = result.astype(np.uint8)

    # Si trae BGR → convertir a RGB
    if result.ndim == 3 and result.shape[-1] == 3:
        result = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)

    return result

async def inpaint_image(image_file: UploadFile, logger: LoggingManager):
    logger.info(f"Opening image...")
    try:
        pil_img = Image.open(io.BytesIO(await image_file.read())).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"No se pudo abrir la imagen: {e}")
    logger.info(f"Image opened successfully")

    logger.info(f"Creating text mask...")
    mask = ocr_text_mask(pil_img)

    if mask.mean() < 1.0:  # no detectó texto
        buf = io.BytesIO()
        pil_img.save(buf, format="PNG")
        buf.seek(0)
        return StreamingResponse(buf, media_type="image/png")
    logger.info(f"Text mask created successfully")

    cfg = Config(
        ldm_steps=25,
        ldm_sampler="plms",
        hd_strategy="Original",
        hd_strategy_crop_margin=128,
        hd_strategy_crop_trigger_size=200,
        hd_strategy_resize_limit=1600,
        prompt="",
        negative_prompt="",
    )

    try:
        logger.info(f"Inpainting image...")
        img_np = np.array(pil_img)
        result = lama(img_np, mask, cfg)
        result = normalize_result(result)
        logger.info(f"Image inpainted successfully")
    except Exception as e:
        logger.error(f"Inpainting error: {e}")
        raise HTTPException(status_code=500, detail=f"Inpainting error: {e}")

    # Guardar a PNG
    logger.info(f"Saving result image...")
    buf = io.BytesIO()
    Image.fromarray(result, mode="RGB").save(buf, format="PNG")
    buf.seek(0)
    logger.info(f"Result image saved successfully")
    return StreamingResponse(buf, media_type="image/png")
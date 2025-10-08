import io
import os

import numpy as np
import torch
import torchvision.transforms as T
from PIL import Image
import pywt
from fastapi import APIRouter, UploadFile, HTTPException
from fastapi.responses import StreamingResponse

from api.routers.logging import LoggingManager

torch.backends.cudnn.benchmark = False
USE_CUDA = os.getenv("USE_CUDA", "0") == "1"
DEVICE = "cuda" if (USE_CUDA and torch.cuda.is_available()) else "cpu"

to_tensor = T.ToTensor()
to_pil    = T.ToPILImage()
router = APIRouter()

def estimate_sigma(img: Image.Image) -> float:
    gray = img.convert("L")
    arr = np.array(gray, dtype=np.float32)
    coeffs = pywt.dwt2(arr, 'db1')
    _, (_, _, HH) = coeffs
    sigma = np.median(np.abs(HH)) / 0.6745
    return float(sigma)

def load_drunet(device: str):
    try:
        from deepinv.models import DRUNet
        model = DRUNet(pretrained="download")
        model.to(device).eval()
        return model
    except Exception as e:
        print(f"[deepinv] descarga automática falló: {e}. Probando Hugging Face...")
        from huggingface_hub import hf_hub_download
        ckpt_path = hf_hub_download(repo_id="deepinv/drunet", filename="drunet_color.pth")
        from deepinv.models import DRUNet
        model = DRUNet()
        sd = torch.load(ckpt_path, map_location="cpu")
        if isinstance(sd, dict) and "params_ema" in sd:
            sd = sd["params_ema"]
        model.load_state_dict(sd, strict=True)
        model.to(device).eval()
        return model

DENOISER = load_drunet(DEVICE)


async def denoise_image(image_file: UploadFile, logger: LoggingManager):
    logger.info(f"Opening image...")
    try:
        img = Image.open(io.BytesIO(await image_file.read())).convert("RGB")
    except Exception:
        raise HTTPException(400, "No se pudo abrir la imagen.")
    logger.info(f"Image opened successfully")

    logger.info(f"Estimating sigma...")
    auto_sigma = True
    if auto_sigma:
        sigma = estimate_sigma(img)
        logger.info(f"Estimated sigma = {sigma:.2f}")
    else:
        sigma = 25.0  # valor por defecto
    logger.info("Sigma estimation completed")

    x = to_tensor(img).unsqueeze(0).to(DEVICE)
    sigma_norm = sigma / 255.0

    logger.info(f"Denoising image with sigma = {sigma:.2f}...")
    with torch.no_grad():
        y = DENOISER(x, sigma=sigma_norm).clamp(0, 1)
    logger.info(f"Denoising completed")

    logger.info(f"Saving result image...")
    buf = io.BytesIO()
    to_pil(y.squeeze(0).cpu()).save(buf, format="PNG"); buf.seek(0)
    logger.info(f"Result image saved successfully")
    return StreamingResponse(buf, media_type="image/png")
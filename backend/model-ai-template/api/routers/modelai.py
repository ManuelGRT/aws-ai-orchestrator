from fastapi import APIRouter, Form, UploadFile, File, HTTPException
from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, Request, UploadFile
from api.utils import commons as utils_commons

from api.utils import commons as utils_commons
from api.routers.logging import LoggingManager
from starlette_context import context, header_keys

from api.schemas.persistance import ModelApiPersistance

from api.utils.dynamodb import DynamoDB
from datetime import datetime
import time

router = APIRouter()

@router.post("/analyze-image",
             responses=utils_commons.RESPONSES,
             name="Model Image")
async def denoise_image(
                background_tasks: BackgroundTasks,
                request: Request,
                image_id: str = Form(..., description='Part of the vehicles', example='ai service name'), 
                image_file: UploadFile = File(..., description='Image file')):
    
    logger = LoggingManager(context.get(header_keys.HeaderKeys.request_id),image_id)
    try:
        logger.info(f"Starting model process...")
        init_time = time.time()

        # ---------------------------------------------------------
        # MODEL PROCESS
        # ---------------------------------------------------------    
        
        logger.info(f"Finishing model process...")
        response_time = time.time() - init_time
        logger.info(f"Ai model image process time: {response_time}")

        dynamodb = DynamoDB()
        background_tasks.add_task(
            dynamodb.upload_api_persistance,
            logger=logger,
            data_api=ModelApiPersistance(
                request_id=context.get(header_keys.HeaderKeys.request_id),
                api_id="model_ai_api",
                image_id=str(image_id),
                response_latency=int(response_time*1000),
                request_datetime=datetime.utcnow().isoformat(),
                http_method=request.method,
                resource_path=str(request.url.path),
                status="200",
                error_message=None
            )
        )

        return None # response
        
    except (HTTPException, Exception) as error:
        logger.error(f"Error during Ai model image: {error}")
        response_time = time.time() - init_time
        status_code = getattr(error, "status_code", 400)
        detail = getattr(error, "detail", "Error during Ai model image")

        raise HTTPException(
            status_code=status_code,
            detail=detail,
            headers={"response_time": response_time,
                     "image_id": str(image_id)}
        )
    


    
    


'''
@router.post("/denoise-sigma")
async def denoise_sigma(
    file: UploadFile = File(...),
    sigma: float = Query(25.0, ge=0.0, le=255.0, description="σ AWGN (0..255)")
):
    try:
        img = Image.open(io.BytesIO(await file.read())).convert("RGB")
    except Exception:
        raise HTTPException(400, "No se pudo abrir la imagen.")
    x = to_tensor(img).unsqueeze(0).to(DEVICE)        # [0,1]
    sigma_norm = float(sigma) / 255.0

    with torch.no_grad():
        y = DENOISER(x, sigma=sigma_norm).clamp(0, 1)

    buf = io.BytesIO()
    to_pil(y.squeeze(0).cpu()).save(buf, format="PNG"); buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")
'''

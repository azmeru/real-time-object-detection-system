from fastapi import Request
from fastapi.responses import JSONResponse


class ModelNotLoadedError(Exception):
    pass


class UnsupportedFileTypeError(Exception):
    pass


class InferenceError(Exception):
    pass


class DetectionNotFoundError(Exception):
    pass


async def model_not_loaded_handler(request: Request, exc: ModelNotLoadedError) -> JSONResponse:
    return JSONResponse(status_code=503, content={"detail": "Model not loaded yet. Please try again shortly."})


async def unsupported_file_handler(request: Request, exc: UnsupportedFileTypeError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


async def inference_error_handler(request: Request, exc: InferenceError) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": f"Inference failed: {str(exc)}"})


async def detection_not_found_handler(request: Request, exc: DetectionNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": "Detection record not found."})

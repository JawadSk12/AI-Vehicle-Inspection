from __future__ import annotations
import json
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False, protected_namespaces=("settings_",))
    app_name: str = "CAPVIA AI"
    app_env: str = "development"
    debug: bool = True
    jwt_secret: str = "your-super-secret-jwt-key-minimum-32-chars"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    database_url: str = "postgresql+asyncpg://capvia:capvia_secure_password@localhost:5432/capvia_ai"
    model_path: str = "ai_model/weights/best_faster_rcnn_mobilenet.pth"
    model_confidence: float = 0.10
    model_iou_threshold: float = 0.45
    model_img_size: int = 1024
    use_sam: bool = False
    upload_dir: str = "storage/uploads"
    result_dir: str = "storage/results"
    report_dir: str = "storage/reports"
    mask_dir: str = "storage/masks"
    max_upload_size_mb: int = 20
    default_scale_factor: float = 0.05
    default_image_dpi: int = 96
    cors_origins: str = '["http://localhost:3000","http://localhost"]'
    onnx_model_path: str = "ai_model/weights/best.onnx"
    use_onnx: bool = False

    @property
    def cors_origins_list(self) -> List[str]:
        return json.loads(self.cors_origins)

    def ensure_directories(self) -> None:
        for d in [self.upload_dir, self.result_dir, self.report_dir, self.mask_dir]:
            Path(d).mkdir(parents=True, exist_ok=True)

settings = Settings()

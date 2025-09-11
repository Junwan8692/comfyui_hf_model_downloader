# hf_model_downloader/src/nodes.py

import os
import folder_paths
from huggingface_hub import hf_hub_download
import re
import shutil

class HFModelDownloader:
    """
    Hugging Face URL에서 모델을 다운로드하여 지정된 ComfyUI 모델 카테고리에 저장하는 노드입니다.
    """
    
    CATEGORY = "utils"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("model_path",)
    FUNCTION = "download_model"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model_url": ("STRING", {
                    "multiline": False,
                    "default": "https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors"
                }),
                "model_category": ([
                    "checkpoints", 
                    "loras", 
                    "vae", 
                    "controlnet", 
                    "upscale_models", 
                    "clip_vision", 
                    "embeddings", 
                    "diffusion_models", 
                    "text_encoders", 
                    ],),
                "optional_filename": ("STRING", {
                    "multiline": False,
                    "default": ""
                }),
            }
        }

    def download_model(self, model_url, model_category, optional_filename):
        try:
            # 1. URL 분석
            match = re.search(r'huggingface\.co/([^/]+/[^/]+)/(?:blob|resolve)/main/(.+)', model_url)
            if not match:
                raise ValueError("유효한 Hugging Face 모델 URL이 아닙니다.")

            repo_id = match.group(1)
            filename_from_url = match.group(2).split('?')[0]

            # --- ✨ 여기가 최종 수정 부분입니다 ✨ ---
            # URL에 포함된 경로에서 순수한 파일 이름만 추출합니다.
            filename_from_url = os.path.basename(filename_from_url)
            # ------------------------------------
            
            print(f"Hugging Face 모델 정보: repo_id='{repo_id}', filename='{filename_from_url}'")

            # 2. 최종 저장 경로와 파일명 결정
            output_dir = folder_paths.get_folder_paths(model_category)[0]
            final_filename = optional_filename.strip() if optional_filename.strip() else filename_from_url
            final_path = os.path.join(output_dir, final_filename)
            print(f"최종 저장 경로: {final_path}")

            # 3. 임시 캐시 폴더에 파일 다운로드
            cached_path = hf_hub_download(
                repo_id=repo_id,
                filename=match.group(2).split('?')[0], # 원본 전체 경로로 다운로드 해야 함
                resume_download=True,
            )
            print(f"파일이 임시 캐시 폴더에 다운로드되었습니다: {cached_path}")

            # 4. 다운로드된 파일을 최종 목적지로 이동
            destination_dir = os.path.dirname(final_path)
            os.makedirs(destination_dir, exist_ok=True)
            shutil.move(cached_path, final_path)
            print("파일 이동 완료!")

            # 5. 최종 파일 경로를 반환
            return (final_path,)

        except Exception as e:
            print(f"다운로드 중 오류 발생: {e}")
            return ("",)
        

# ComfyUI에 이 노드 클래스를 등록하는 부분입니다.
NODE_CLASS_MAPPINGS = {
    "HF Model Downloader": HFModelDownloader
}

# ComfyUI 메뉴에 표시될 노드의 이름을 지정합니다.
NODE_DISPLAY_NAME_MAPPINGS = {
    "HF Model Downloader": "📦 HF Model Downloader"
}
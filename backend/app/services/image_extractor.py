import os
import httpx
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import re
import os
from app.models.schemas import ImageInfo
from app.utils.url_utils import make_absolute, extract_filename
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

def extract_images(soup: BeautifulSoup, url: str) -> list[ImageInfo]:
    images = []
    
    for idx, img in enumerate(soup.find_all("img")):
        src = None
        srcset = img.get("srcset") or img.get("data-srcset")
        if srcset:
            try:
                # "url 1x, url2 2x" -> get url2
                parts = [p.strip().split(" ")[0] for p in srcset.split(",")]
                if parts and parts[-1]:
                    src = parts[-1]
            except:
                pass
                
        src = src or img.get("src") or img.get("data-src")
        if not src:
            continue
            
        absolute_url = make_absolute(url, src)
        if absolute_url.startswith("data:"):
            filename = f"image_{idx}"
        else:
            filename = extract_filename(absolute_url)
            if not filename or filename == "unknown":
                filename = f"image_{idx}"
                
        # Sanitize filename for Windows/Linux
        filename = re.sub(r'[\\/*?:"<>|]', "", filename)
        if len(filename) > 100:
            filename = filename[-100:]
        
        caption = None
        figure = img.find_parent("figure")
        if figure:
            figcaption = figure.find("figcaption")
            if figcaption:
                caption = figcaption.get_text(strip=True)
                
        # Find section (nearest preceding heading)
        section = None
        for previous in img.find_all_previous(["h1", "h2", "h3", "h4", "h5", "h6"]):
            section = previous.get_text(strip=True)
            break
            
        # Find position
        position = "Unknown"
        prev_p = img.find_previous("p")
        if prev_p:
            p_idx = len(soup.find_all("p")) - len(prev_p.find_all_next("p"))
            position = f"after paragraph {p_idx}"
            
        width = None
        height = None
        try:
            if img.get("width"):
                width = int(img.get("width").replace("px", ""))
            if img.get("height"):
                height = int(img.get("height").replace("px", ""))
        except:
            pass
            
        images.append(ImageInfo(
            url=src,
            absolute_url=absolute_url,
            filename=filename,
            alt_text=img.get("alt"),
            title=img.get("title"),
            caption=caption,
            section=section,
            position=position,
            width=width,
            height=height
        ))
        
    return images

async def download_images(images: list[ImageInfo], output_dir: str) -> list[ImageInfo]:
    os.makedirs(output_dir, exist_ok=True)
    
    async with httpx.AsyncClient() as client:
        for img in images:
            try:
                response = await client.get(img.absolute_url, timeout=10.0)
                if response.status_code == 200:
                    try:
                        pil_img = Image.open(BytesIO(response.content))
                        img.format = pil_img.format
                        img.width, img.height = pil_img.size
                    except Exception as e:
                        logger.warning(f"Pillow failed for {img.absolute_url}: {e}")
                        content_type = response.headers.get("content-type", "").lower()
                        if "svg" in content_type: img.format = "SVG"
                        elif "webp" in content_type: img.format = "WEBP"
                        elif "gif" in content_type: img.format = "GIF"
                        elif "png" in content_type: img.format = "PNG"
                        elif "jpeg" in content_type or "jpg" in content_type: img.format = "JPEG"
                    
                    ext = ""
                    if img.format:
                        ext = f".{img.format.lower()}"
                        if ext == ".jpeg": ext = ".jpg"
                        
                    name, current_ext = os.path.splitext(img.filename)
                    valid_exts = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp', '.ico']
                    
                    if ext:
                        if not current_ext or current_ext.lower() not in valid_exts:
                            img.filename = img.filename + ext
                        elif current_ext.lower() != ext:
                            img.filename = name + ext
                    else:
                        if not current_ext:
                            img.filename = img.filename + ".bin"
                            
                    local_path = os.path.join(output_dir, img.filename)
                    with open(local_path, "wb") as f:
                        f.write(response.content)
                    img.local_path = local_path
            except Exception as e:
                logger.error(f"Failed to download image {img.absolute_url}: {e}")
                
    return images

import diff_match_patch as dmp_module
from bs4 import BeautifulSoup
from app.models.schemas import TextDiff, StructureDiff
from app.services.parser import extract_text, to_clean_html
from app.services.image_extractor import extract_images
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

def compare_pages(html1: str, html2: str, url1: str, url2: str) -> dict:
    dmp = dmp_module.diff_match_patch()
    
    text1 = extract_text(html1)
    text2 = extract_text(html2)
    
    diffs = dmp.diff_main(text1, text2)
    dmp.diff_cleanupSemantic(diffs)
    
    text_diffs = []
    equal_len = 0
    total_len = max(len(text1), len(text2))
    
    for op, data in diffs:
        op_type = "equal"
        if op == dmp.DIFF_INSERT:
            op_type = "add"
        elif op == dmp.DIFF_DELETE:
            op_type = "remove"
        else:
            equal_len += len(data)
            
        text_diffs.append(TextDiff(type=op_type, text=data))
        
    similarity_score = equal_len / total_len if total_len > 0 else 1.0
    
    soup1 = BeautifulSoup(html1, "lxml")
    soup2 = BeautifulSoup(html2, "lxml")
    
    images1 = {img.url: img for img in extract_images(soup1, url1)}
    images2 = {img.url: img for img in extract_images(soup2, url2)}
    
    added_images = [img for url, img in images2.items() if url not in images1]
    removed_images = [img for url, img in images1.items() if url not in images2]
    
    structure_diffs = []
    
    headings_1 = [h.name for h in soup1.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])]
    headings_2 = [h.name for h in soup2.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])]
    
    if len(headings_1) != len(headings_2):
        structure_diffs.append(StructureDiff(
            type="changed",
            element="headings",
            details=f"Heading count changed from {len(headings_1)} to {len(headings_2)}"
        ))
        
    return {
        "url1": url1,
        "url2": url2,
        "text_diffs": [d.model_dump() for d in text_diffs],
        "structure_diffs": [d.model_dump() for d in structure_diffs],
        "images_added": [i.model_dump() for i in added_images],
        "images_removed": [i.model_dump() for i in removed_images],
        "similarity_score": similarity_score
    }

from bs4 import BeautifulSoup
from app.models.schemas import ContentNode, StructureNode
from markdownify import markdownify as md
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

def parse_content(html: str, url: str) -> list[ContentNode]:
    soup = BeautifulSoup(html, "lxml")
    
    nodes = []
    
    target_tags = ["h1", "h2", "h3", "h4", "h5", "h6", "p", "ul", "ol", "table", "blockquote", "pre", "section", "article"]
    
    for tag in soup.find_all(target_tags):
        # Prevent nested tags from being processed twice if they are block level
        if tag.name in ["ul", "ol"]:
            items = [ContentNode(tag="li", text=li.get_text(strip=True)) for li in tag.find_all("li")]
            nodes.append(ContentNode(tag=tag.name, children=items, attributes=tag.attrs))
        elif tag.name == "table":
            nodes.append(ContentNode(tag=tag.name, text=tag.get_text(separator=" ", strip=True), attributes=tag.attrs))
        else:
            text = tag.get_text(strip=True)
            if text or tag.name in ["section", "article"]:
                nodes.append(ContentNode(tag=tag.name, text=text, attributes=tag.attrs))
                
    return nodes

def build_structure_tree(html: str) -> StructureNode:
    soup = BeautifulSoup(html, "lxml")
    
    def _build_node(tag) -> StructureNode:
        if not hasattr(tag, "name") or not tag.name:
            return None
            
        classes = tag.get("class", [])
        if isinstance(classes, str):
            classes = [classes]
            
        text_preview = tag.get_text(strip=True)[:50] if tag.get_text(strip=True) else None
        
        children = []
        for child in tag.children:
            child_node = _build_node(child)
            if child_node:
                children.append(child_node)
                
        return StructureNode(
            tag=tag.name,
            id=tag.get("id"),
            classes=classes,
            text_preview=text_preview,
            children=children
        )
        
    body = soup.find("body")
    if body:
        return _build_node(body)
    return _build_node(soup.find("html"))

def extract_text(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    return soup.get_text(separator="\n", strip=True)

def to_markdown(html: str, url: str) -> str:
    return md(html, heading_style="ATX")

def to_clean_html(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "iframe", "noscript"]):
        tag.decompose()
        
    return str(soup)

from bs4 import BeautifulSoup
from app.models.schemas import MetadataInfo
from app.utils.url_utils import make_absolute
import json

def extract_metadata(soup: BeautifulSoup, url: str) -> MetadataInfo:
    meta_info = MetadataInfo()
    
    if soup.title:
        meta_info.title = soup.title.string.strip() if soup.title.string else None
        
    description = soup.find("meta", attrs={"name": "description"})
    if description and description.get("content"):
        meta_info.description = description["content"].strip()
        
    author = soup.find("meta", attrs={"name": "author"})
    if author and author.get("content"):
        meta_info.author = author["content"].strip()
        
    publish_date = soup.find("meta", attrs={"property": "article:published_time"})
    if publish_date and publish_date.get("content"):
        meta_info.publish_date = publish_date["content"].strip()
        
    favicon = soup.find("link", rel=lambda x: x and 'icon' in x.lower())
    if favicon and favicon.get("href"):
        meta_info.favicon = make_absolute(favicon["href"], url)
        
    canonical = soup.find("link", rel="canonical")
    if canonical and canonical.get("href"):
        meta_info.canonical_url = make_absolute(canonical["href"], url)
        
    html_tag = soup.find("html")
    if html_tag and html_tag.get("lang"):
        meta_info.language = html_tag["lang"]
        
    for meta in soup.find_all("meta"):
        property_name = meta.get("property", "")
        name = meta.get("name", "")
        content = meta.get("content")
        
        if content:
            if property_name.startswith("og:"):
                meta_info.og_tags[property_name[3:]] = content
            elif name.startswith("twitter:"):
                meta_info.twitter_tags[name[8:]] = content
                
    schema_script = soup.find("script", type="application/ld+json")
    if schema_script and schema_script.string:
        try:
            meta_info.schema_org = json.loads(schema_script.string)
        except:
            pass
            
    return meta_info

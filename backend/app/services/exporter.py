import os
import json
import zipfile
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

class ExportService:
    def export_zip(self, analysis_data: dict, output_dir: str, filename: str = "export.zip") -> str:
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        
        # 1. Create JSON data string
        json_content = json.dumps(analysis_data, indent=2, ensure_ascii=False)
        
        # 2. Create Clean HTML string
        html_content = analysis_data.get('clean_html', '') or ''
        
        # 3. Create Markdown Report
        url = analysis_data.get('url', 'URL Desconhecida')
        title = analysis_data.get('title', 'Sem Título')
        md_content = f"# {title}\n**URL Original:** {url}\n\n"
        
        md_content += "## Conteúdo em Texto\n\n"
        md_content += analysis_data.get('markdown', '') or analysis_data.get('text_content', '')
        
        md_content += "\n\n## Galeria de Imagens e Posicionamento\n\n"
        images = analysis_data.get("images") or []
        for img in images:
            img_filename = img.get("filename", "image.jpg")
            alt = img.get("alt_text") or "Sem alt"
            titulo = img.get("title") or "Sem título"
            pos = img.get("position") or "Desconhecida"
            sec = img.get("section") or "Geral"
            
            md_content += f"### {img_filename}\n"
            md_content += f"![{alt}](images/{img_filename})\n\n"
            md_content += f"- **Título:** {titulo}\n"
            md_content += f"- **Alt Text:** {alt}\n"
            md_content += f"- **Seção:** {sec}\n"
            md_content += f"- **Posição na Tela:** {pos}\n\n"
        
        # 4. Write directly to ZIP
        with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.writestr("database.json", json_content)
            zipf.writestr("page.html", html_content)
            zipf.writestr("relatorio_completo.md", md_content.encode('utf-8'))
            
            for img in images:
                local_path = img.get("local_path")
                if local_path and os.path.exists(local_path):
                    img_filename = img.get("filename", os.path.basename(local_path))
                    zipf.write(local_path, arcname=f"images/{img_filename}")
                    
        return filepath

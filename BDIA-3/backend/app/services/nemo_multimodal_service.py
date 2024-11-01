from typing import Dict, List, Optional
import torch
import numpy as np
from PIL import Image
from pdf2image import convert_from_path
import nemo.collections.nlp as nemo_nlp
import nemo.collections.multimodal as nemo_multimodal
from ..config.nemo_config import NeMoConfig
from pathlib import Path
import tempfile
import os

class NeMoMultimodalService:
    def __init__(self):
        self.config = NeMoConfig()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Initialize NeMo models
        self.multimodal_model = nemo_multimodal.models.MultiModalModel.from_pretrained(
            self.config.NEMO_MODEL_PATH
        ).to(self.device)
        
    async def query_document(
        self,
        query: str,
        document_content: str,
        visual_content: Optional[Dict] = None
    ) -> Dict:
        """Query document using multimodal RAG"""
        try:
            # Process query and document
            query_embedding = self.multimodal_model.encode_text(query)
            doc_embedding = self.multimodal_model.encode_text(document_content)
            
            # Process visual content if available
            if visual_content:
                visual_embedding = self.multimodal_model.encode_image(visual_content['image'])
                # Combine embeddings for multimodal search
                doc_embedding = self.multimodal_model.combine_embeddings(
                    [doc_embedding, visual_embedding]
                )
            
            # Generate answer using RAG
            response = self.multimodal_model.generate_answer(
                query_embedding=query_embedding,
                context_embedding=doc_embedding,
                max_length=self.config.MAX_OUTPUT_LENGTH,
                temperature=self.config.TEMPERATURE
            )
            
            return {
                "answer": response['answer'],
                "confidence": response['confidence'],
                "references": response['references']
            }
            
        except Exception as e:
            raise Exception(f"Error querying document: {str(e)}")

    async def process_image(self, image_path: str) -> Dict:
        """Process and analyze image content"""
        try:
            image = Image.open(image_path)
            # Convert image to tensor and preprocess
            image_tensor = self.multimodal_model.preprocess_image(image).to(self.device)
            
            # Generate image analysis
            analysis = self.multimodal_model.analyze_image(image_tensor)
            
            return {
                "type": "image",
                "analysis": analysis,
                "embedding": self.multimodal_model.encode_image(image_tensor)
            }
        except Exception as e:
            raise Exception(f"Error processing image: {str(e)}")

    async def process_pdf(self, pdf_path: str) -> List[Dict]:
        """Process PDF and extract visual elements"""
        try:
            # Convert PDF pages to images
            images = convert_from_path(pdf_path)
            visual_elements = []
            
            for idx, image in enumerate(images):
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                    image.save(tmp.name)
                    # Process each page
                    element = await self.process_image(tmp.name)
                    element["page"] = idx + 1
                    visual_elements.append(element)
                    os.unlink(tmp.name)
                    
            return visual_elements
        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")

    async def generate_visual_summary(self, document: Dict) -> Dict:
        """Generate summary incorporating visual elements"""
        try:
            # Process text content
            text_embedding = self.multimodal_model.encode_text(document.get("content", ""))
            
            # Process visual content
            visual_content = None
            if document.get("image_link"):
                visual_content = await self.process_image(document["image_link"])
            elif document.get("pdf_link"):
                visual_content = await self.process_pdf(document["pdf_link"])
            
            # Generate summary prompt
            summary_prompt = (
                "Generate a comprehensive summary of this document, "
                "including descriptions of key visual elements, graphs, "
                "and tables. Format the response with clear sections."
            )
            
            # Generate summary
            summary_embedding = await self.generate_multimodal_embedding(
                text=summary_prompt,
                visual_content=visual_content[0] if isinstance(visual_content, list) else visual_content
            )
            
            summary = self.multimodal_model.generate(
                query_embedding=summary_embedding,
                max_length=self.config.MAX_OUTPUT_LENGTH * 2,  # Longer for summaries
                temperature=self.config.TEMPERATURE,
                top_k=self.config.TOP_K,
                top_p=self.config.TOP_P
            )
            
            return {
                "summary": summary,
                "visual_elements_processed": bool(visual_content),
                "source_document": document.get("id")
            }
        except Exception as e:
            raise Exception(f"Error generating visual summary: {str(e)}")

    async def generate_multimodal_embedding(
        self,
        text: str,
        visual_content: Optional[Dict] = None
    ) -> torch.Tensor:
        """Generate combined embedding from text and visual content"""
        try:
            # Generate text embedding
            text_embedding = self.multimodal_model.encode_text(text)
            
            if not visual_content:
                return text_embedding
                
            # Generate visual embedding
            visual_embedding = visual_content.get("embedding")
            if not visual_embedding:
                return text_embedding
                
            # Combine embeddings
            return self.multimodal_model.combine_embeddings(
                [text_embedding, visual_embedding]
            )
        except Exception as e:
            raise Exception(f"Error generating multimodal embedding: {str(e)}")

    async def analyze_content_trend(self, contents: List[str]) -> Dict:
        """Analyze trends in content"""
        try:
            # Generate embeddings for all content
            embeddings = [
                self.multimodal_model.encode_text(content)
                for content in contents
            ]
            
            # Analyze temporal patterns
            trend_analysis = self.multimodal_model.analyze_trends(embeddings)
            
            return {
                "trend_summary": trend_analysis.get("summary", ""),
                "key_changes": trend_analysis.get("changes", []),
                "confidence": trend_analysis.get("confidence", 0.0)
            }
        except Exception as e:
            raise Exception(f"Error analyzing content trend: {str(e)}")
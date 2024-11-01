from nvidia.dali import pipeline_def
import nvidia.dali.fn as fn
import nvidia.dali.types as types
from nvidia.dali.pipeline import Pipeline
import nemo.collections.nlp as nemo_nlp
import nemo.collections.multimodal as nemo_multimodal
from typing import Optional, Dict, List
from pathlib import Path
import tempfile
import os
from PIL import Image
from pdf2image import convert_from_path

class SummarizationService:
    def __init__(self):
        # Initialize NeMo models
        self.text_model = nemo_nlp.models.TextModel.from_pretrained("nvidia/nemo-text")
        self.vision_model = nemo_multimodal.models.VisionModel.from_pretrained("nvidia/nemo-vision")
        self.multimodal_model = nemo_multimodal.models.MultimodalModel.from_pretrained("nvidia/nemo-multimodal")
        
    @pipeline_def
    def image_processing_pipeline(self):
        """DALI pipeline for efficient image processing"""
        images = fn.external_source(device="cpu", name="images")
        images = fn.image_decoder(images, device="mixed")
        images = fn.resize(images, resize_x=224, resize_y=224)
        images = fn.crop_mirror_normalize(images,
                                       mean=[0.485 * 255, 0.456 * 255, 0.406 * 255],
                                       std=[0.229 * 255, 0.224 * 255, 0.225 * 255])
        return images

    async def process_multimodal_input(self, text: str, image_path: str = None):
        """Process both text and image inputs"""
        # Process text
        text_embedding = self.text_model.encode(text)
        
        # Process image if provided
        image_embedding = None
        if image_path:
            pipe = self.image_processing_pipeline(batch_size=1, num_threads=4, device_id=0)
            pipe.build()
            image_embedding = self.vision_model.encode_image(pipe.run())
            
        # Combine embeddings
        return self.multimodal_model.combine_embeddings(text_embedding, image_embedding)

    async def generate_document_summary(self, document_content: str, pdf_path: Optional[str] = None) -> Dict:
        """Generate a comprehensive document summary using NeMo"""
        try:
            # Process text content
            text_embedding = await self.process_multimodal_input(document_content)
            
            # Process PDF if provided
            visual_embeddings = []
            if pdf_path:
                # Convert PDF pages to images
                images = convert_from_path(pdf_path)
                for img in images:
                    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                        img.save(tmp.name)
                        visual_embedding = await self.process_multimodal_input("", tmp.name)
                        visual_embeddings.append(visual_embedding)
                        os.unlink(tmp.name)

            # Generate summary using multimodal model
            summary_prompt = (
                "Generate a comprehensive summary of this document, "
                "including key findings, methodology, and conclusions. "
                "Format the response with clear sections."
            )
            
            # Combine all embeddings
            combined_embedding = self.multimodal_model.combine_embeddings(
                text_embedding,
                visual_embeddings if visual_embeddings else None
            )
            
            # Generate summary
            summary = self.multimodal_model.generate_text(
                prompt=summary_prompt,
                embeddings=combined_embedding
            )

            return {
                "summary": summary,
                "metadata": {
                    "visual_elements_processed": len(visual_embeddings),
                    "text_processed": True,
                    "generated_at": str(datetime.now())
                }
            }

        except Exception as e:
            raise Exception(f"Error generating summary: {str(e)}")

    async def generate_research_note_summary(self, qa_interactions: List[Dict]) -> str:
        """Generate a summary from Q&A interactions using NeMo"""
        try:
            # Prepare context from Q&A interactions
            qa_context = "\n\n".join([
                f"Q: {qa['question']}\nA: {qa['answer']}"
                for qa in qa_interactions
            ])

            # Process Q&A context
            qa_embedding = await self.process_multimodal_input(qa_context)
            
            # Generate research note
            research_note_prompt = (
                "Based on the Q&A interactions, provide a coherent "
                "research note that synthesizes the key insights and findings. "
                "Include relevant cross-references and maintain academic tone."
            )
            
            research_note = self.multimodal_model.generate_text(
                prompt=research_note_prompt,
                embeddings=qa_embedding
            )

            return research_note

        except Exception as e:
            raise Exception(f"Error generating research note summary: {str(e)}")

    async def extract_visual_elements(self, pdf_path: str) -> List[Dict]:
        """Extract and analyze visual elements from PDF"""
        try:
            visual_elements = []
            images = convert_from_path(pdf_path)
            
            for idx, img in enumerate(images):
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                    img.save(tmp.name)
                    
                    # Process image
                    image_embedding = await self.process_multimodal_input("", tmp.name)
                    
                    # Analyze visual content
                    visual_analysis = self.vision_model.analyze_image(image_embedding)
                    
                    visual_elements.append({
                        "page": idx + 1,
                        "type": visual_analysis["type"],  # graph, table, image, etc.
                        "caption": visual_analysis["caption"],
                        "embedding": image_embedding
                    })
                    
                    os.unlink(tmp.name)
                    
            return visual_elements

        except Exception as e:
            raise Exception(f"Error extracting visual elements: {str(e)}")

    async def analyze_content_trend(self, contents: List[str]) -> Dict:
        """Analyze trends in content using NeMo"""
        try:
            # Process all content
            content_embeddings = [
                await self.process_multimodal_input(content)
                for content in contents
            ]
            
            # Analyze trends
            trend_analysis = self.text_model.analyze_trends(content_embeddings)
            
            return {
                "trend_summary": trend_analysis["summary"],
                "key_changes": trend_analysis["changes"],
                "confidence": trend_analysis["confidence"]
            }

        except Exception as e:
            raise Exception(f"Error analyzing content trend: {str(e)}")
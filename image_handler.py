"""
Image Handling Module for EN Writer
Supports image processing, captioning, and metadata management
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageHandler:
    """Handles image processing and metadata for EN Writer"""
    
    def __init__(self, base_dir: str = "images"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        self.metadata_file = self.base_dir / "image_metadata.json"
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load image metadata from file"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading image metadata: {e}")
                return {}
        return {}
    
    def _save_metadata(self):
        """Save image metadata to file"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving image metadata: {e}")
    
    def generate_image_placeholder(self, image_number: int, caption: str = "", 
                                 description: str = "", tags: List[str] = None) -> str:
        """Generate image placeholder with metadata"""
        if tags is None:
            tags = []
        
        # Create metadata entry
        image_id = f"image_{image_number}"
        self.metadata[image_id] = {
            'number': image_number,
            'caption': caption,
            'description': description,
            'tags': tags,
            'created_at': datetime.now().isoformat(),
            'file_path': None,
            'status': 'placeholder'
        }
        
        self._save_metadata()
        
        # Generate placeholder text
        placeholder = f"[image {image_number}]"
        if caption:
            placeholder += f" - {caption}"
        
        return placeholder
    
    def add_image_file(self, image_path: str, image_number: int, 
                      caption: str = "", description: str = "", 
                      tags: List[str] = None) -> bool:
        """Add actual image file and update metadata"""
        if tags is None:
            tags = []
        
        try:
            source_path = Path(image_path)
            if not source_path.exists():
                logger.error(f"Image file not found: {image_path}")
                return False
            
            # Create destination path
            dest_path = self.base_dir / f"image_{image_number}{source_path.suffix}"
            
            # Copy file
            import shutil
            shutil.copy2(source_path, dest_path)
            
            # Calculate file hash
            file_hash = self._calculate_file_hash(dest_path)
            
            # Update metadata
            image_id = f"image_{image_number}"
            self.metadata[image_id] = {
                'number': image_number,
                'caption': caption,
                'description': description,
                'tags': tags,
                'created_at': datetime.now().isoformat(),
                'file_path': str(dest_path),
                'file_size': dest_path.stat().st_size,
                'file_hash': file_hash,
                'status': 'active'
            }
            
            self._save_metadata()
            logger.info(f"Image {image_number} added successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error adding image file: {e}")
            return False
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating file hash: {e}")
            return ""
    
    def get_image_metadata(self, image_number: int) -> Optional[Dict[str, Any]]:
        """Get metadata for specific image"""
        image_id = f"image_{image_number}"
        return self.metadata.get(image_id)
    
    def list_images(self) -> List[Dict[str, Any]]:
        """List all images with their metadata"""
        images = []
        for image_id, metadata in self.metadata.items():
            images.append({
                'id': image_id,
                'number': metadata.get('number'),
                'caption': metadata.get('caption', ''),
                'description': metadata.get('description', ''),
                'tags': metadata.get('tags', []),
                'status': metadata.get('status', 'unknown'),
                'file_path': metadata.get('file_path'),
                'created_at': metadata.get('created_at')
            })
        
        # Sort by image number
        images.sort(key=lambda x: x.get('number', 0))
        return images
    
    def update_image_metadata(self, image_number: int, updates: Dict[str, Any]) -> bool:
        """Update metadata for specific image"""
        try:
            image_id = f"image_{image_number}"
            if image_id in self.metadata:
                self.metadata[image_id].update(updates)
                self.metadata[image_id]['updated_at'] = datetime.now().isoformat()
                self._save_metadata()
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating image metadata: {e}")
            return False
    
    def remove_image(self, image_number: int) -> bool:
        """Remove image and its metadata"""
        try:
            image_id = f"image_{image_number}"
            if image_id in self.metadata:
                # Remove file if it exists
                file_path = self.metadata[image_id].get('file_path')
                if file_path and Path(file_path).exists():
                    Path(file_path).unlink()
                
                # Remove metadata
                del self.metadata[image_id]
                self._save_metadata()
                return True
            return False
        except Exception as e:
            logger.error(f"Error removing image: {e}")
            return False
    
    def generate_image_report(self) -> Dict[str, Any]:
        """Generate comprehensive image report"""
        images = self.list_images()
        
        report = {
            'total_images': len(images),
            'active_images': len([img for img in images if img['status'] == 'active']),
            'placeholder_images': len([img for img in images if img['status'] == 'placeholder']),
            'images_with_files': len([img for img in images if img['file_path']]),
            'images_without_files': len([img for img in images if not img['file_path']]),
            'total_file_size': sum(img.get('file_size', 0) for img in images if img.get('file_size')),
            'images': images
        }
        
        return report
    
    def extract_image_references(self, text: str) -> List[Dict[str, Any]]:
        """Extract image references from text"""
        import re
        
        # Find all [image N] references
        pattern = r'\[image\s+(\d+)\](?:\s*-\s*(.+?))?(?=\n|$)'
        matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
        
        references = []
        for match in matches:
            image_number = int(match[0])
            caption = match[1].strip() if match[1] else ""
            
            # Get metadata for this image
            metadata = self.get_image_metadata(image_number)
            
            references.append({
                'number': image_number,
                'caption': caption,
                'metadata': metadata,
                'has_file': metadata and metadata.get('file_path') is not None
            })
        
        return references
    
    def validate_image_references(self, text: str) -> Dict[str, Any]:
        """Validate all image references in text"""
        references = self.extract_image_references(text)
        
        validation = {
            'total_references': len(references),
            'valid_references': 0,
            'missing_files': [],
            'missing_metadata': [],
            'issues': []
        }
        
        for ref in references:
            if ref['metadata']:
                validation['valid_references'] += 1
                if not ref['has_file']:
                    validation['missing_files'].append(ref['number'])
            else:
                validation['missing_metadata'].append(ref['number'])
                validation['issues'].append(f"Image {ref['number']} referenced but no metadata found")
        
        return validation


class ImageCaptionGenerator:
    """Generate captions for images using AI models"""
    
    def __init__(self):
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize image captioning model"""
        try:
            from transformers import BlipProcessor, BlipForConditionalGeneration
            from PIL import Image
            
            self.processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            self.model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
            logger.info("BLIP image captioning model initialized successfully")
        except Exception as e:
            logger.warning(f"BLIP model not available: {e}")
            self.model = None
    
    def generate_caption(self, image_path: str) -> str:
        """Generate caption for image"""
        if not self.model:
            return "Image captioning not available"
        
        try:
            from PIL import Image
            
            image = Image.open(image_path).convert('RGB')
            inputs = self.processor(image, return_tensors="pt")
            
            out = self.model.generate(**inputs, max_length=50)
            caption = self.processor.decode(out[0], skip_special_tokens=True)
            
            return caption
        except Exception as e:
            logger.error(f"Error generating caption: {e}")
            return f"Error generating caption: {str(e)}"
    
    def is_available(self) -> bool:
        """Check if captioning is available"""
        return self.model is not None


# Enhanced EN Writer with image handling
class ImageEnhancedENWriter:
    """EN Writer with integrated image handling"""
    
    def __init__(self, base_dir: str, planning_file: str = "planning_sheet.json"):
        from en_writer import ENWriter
        
        self.en_writer = ENWriter(base_dir, planning_file)
        self.image_handler = ImageHandler()
        self.caption_generator = ImageCaptionGenerator()
    
    def add_image_to_section(self, section_name: str, image_path: str, 
                           caption: str = "", description: str = "", 
                           tags: List[str] = None) -> bool:
        """Add image to a specific section"""
        try:
            # Get next available image number
            existing_images = self.image_handler.list_images()
            next_number = max([img['number'] for img in existing_images], default=0) + 1
            
            # Add image file
            success = self.image_handler.add_image_file(
                image_path, next_number, caption, description, tags
            )
            
            if success:
                # Generate placeholder text
                placeholder = self.image_handler.generate_image_placeholder(
                    next_number, caption, description, tags
                )
                
                # Add to section content
                if section_name in self.en_writer.en_writer.sections:
                    content = self.en_writer.en_writer.sections[section_name]
                    content += f"\n\n{placeholder}"
                    self.en_writer.en_writer.sections[section_name] = content
                    self.en_writer.en_writer.save_en_files({section_name: content})
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error adding image to section: {e}")
            return False
    
    def auto_caption_image(self, image_path: str) -> str:
        """Automatically generate caption for image"""
        return self.caption_generator.generate_caption(image_path)
    
    def get_section_images(self, section_name: str) -> List[Dict[str, Any]]:
        """Get all images referenced in a section"""
        if section_name not in self.en_writer.en_writer.sections:
            return []
        
        content = self.en_writer.en_writer.sections[section_name]
        return self.image_handler.extract_image_references(content)
    
    def validate_section_images(self, section_name: str) -> Dict[str, Any]:
        """Validate all images in a section"""
        if section_name not in self.en_writer.en_writer.sections:
            return {'error': 'Section not found'}
        
        content = self.en_writer.en_writer.sections[section_name]
        return self.image_handler.validate_image_references(content)


# Example usage
if __name__ == "__main__":
    # Test image handler
    image_handler = ImageHandler()
    
    # Generate placeholder
    placeholder = image_handler.generate_image_placeholder(1, "System Architecture", "Main system components")
    print(f"Placeholder: {placeholder}")
    
    # List images
    images = image_handler.list_images()
    print(f"Images: {images}")
    
    # Generate report
    report = image_handler.generate_image_report()
    print(f"Report: {report}")

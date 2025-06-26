"""
Multi-Format Content Generation API Routes
Handles generation of content across multiple platforms
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import asyncio
import json

from ..database import get_db
from ..auth import get_current_user
from ..models import User, ContentGeneration
from ..mcp_servers.multi_format_generator import MultiFormatContentGenerator

router = APIRouter()


class MultiFormatGenerationRequest(BaseModel):
    """Request model for multi-format content generation"""
    source_content: Union[str, List[Dict[str, Any]]] = Field(..., description="Source content or articles")
    topic: Optional[str] = Field("", description="Main topic or theme")
    target_audience: str = Field("general", description="Target audience")
    tone: str = Field("professional", description="Writing tone")
    selected_formats: Optional[List[str]] = Field(None, description="Specific formats to generate")
    custom_instructions: str = Field("", description="Additional custom instructions")


class SingleFormatGenerationRequest(BaseModel):
    """Request model for single format generation"""
    source_content: Union[str, List[Dict[str, Any]]] = Field(..., description="Source content or articles")
    format_name: str = Field(..., description="Content format to generate")
    topic: Optional[str] = Field("", description="Main topic or theme")
    target_audience: str = Field("general", description="Target audience")
    tone: str = Field("professional", description="Writing tone")
    custom_instructions: str = Field("", description="Additional custom instructions")


class ContentRepurposeRequest(BaseModel):
    """Request model for content repurposing"""
    source_format: str = Field(..., description="Original content format")
    target_formats: List[str] = Field(..., description="Target formats for repurposing")
    content: str = Field(..., description="Original content")
    preserve_core_message: bool = Field(True, description="Whether to preserve core message")


# Initialize the multi-format generator
from ..mcp_servers.multi_format_generator import create_multi_format_generator
generator = create_multi_format_generator()


@router.post("/generate-multi-format")
async def generate_multi_format_content(
    request: MultiFormatGenerationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate content in multiple formats from source material
    """
    try:
        # Generate content using the multi-format generator
        result = await generator.generate_all_formats(
            source_content=request.source_content,
            topic=request.topic,
            target_audience=request.target_audience,
            tone=request.tone,
            selected_formats=request.selected_formats,
            custom_instructions=request.custom_instructions
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Generation failed"))
        
        # Store generation record in background
        background_tasks.add_task(
            store_generation_record,
            db=db,
            user_id=current_user.id,
            generation_type="multi_format",
            input_data=request.dict(),
            result_data=result,
            formats_generated=list(result["generated_content"].keys())
        )
        
        return {
            "success": True,
            "generated_content": result["generated_content"],
            "metadata": result["metadata"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate content: {str(e)}")


@router.post("/generate-single-format")
async def generate_single_format_content(
    request: SingleFormatGenerationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate content in a single specified format
    """
    try:
        # Generate content using the multi-format generator
        result = await generator.generate_single_format(
            source_content=request.source_content,
            format_name=request.format_name,
            topic=request.topic,
            target_audience=request.target_audience,
            tone=request.tone,
            custom_instructions=request.custom_instructions
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Generation failed"))
        
        # Store generation record in background
        background_tasks.add_task(
            store_generation_record,
            db=db,
            user_id=current_user.id,
            generation_type="single_format",
            input_data=request.dict(),
            result_data=result,
            formats_generated=[request.format_name]
        )
        
        return {
            "success": True,
            "content": result["content"],
            "metadata": result["metadata"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate content: {str(e)}")


@router.post("/repurpose-content")
async def repurpose_content(
    request: ContentRepurposeRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Repurpose existing content from one format to others
    """
    try:
        # Repurpose content using the multi-format generator
        result = await generator.repurpose_content(
            source_format=request.source_format,
            target_formats=request.target_formats,
            content=request.content,
            preserve_core_message=request.preserve_core_message
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Repurposing failed"))
        
        # Store generation record in background
        background_tasks.add_task(
            store_generation_record,
            db=db,
            user_id=current_user.id,
            generation_type="repurpose",
            input_data=request.dict(),
            result_data=result,
            formats_generated=request.target_formats
        )
        
        return {
            "success": True,
            "repurposed_content": result["repurposed_content"],
            "metadata": result["metadata"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to repurpose content: {str(e)}")


@router.get("/supported-formats")
async def get_supported_formats():
    """
    Get list of all supported content formats with their specifications
    """
    formats = []
    
    from ..mcp_servers.multi_format_generator import ContentFormat, MultiFormatContentGenerator
    temp_generator = MultiFormatContentGenerator()
    
    for format_enum in ContentFormat:
        spec = temp_generator.PLATFORM_SPECS[format_enum]
        formats.append({
            "id": format_enum.value,
            "name": format_enum.value.replace('_', ' ').title(),
            "character_limit": spec.character_limit,
            "word_limit": spec.word_limit,
            "style_notes": spec.style_notes,
            "include_hashtags": spec.include_hashtags,
            "include_call_to_action": spec.include_call_to_action,
            "platform_features": spec.platform_specific_features
        })
    
    return {
        "success": True,
        "formats": formats,
        "total_count": len(formats)
    }


@router.get("/generation-history")
async def get_generation_history(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's content generation history
    """
    try:
        generations = db.query(ContentGeneration)\
            .filter(ContentGeneration.user_id == current_user.id)\
            .order_by(ContentGeneration.created_at.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()
        
        history = []
        for gen in generations:
            history.append({
                "id": gen.id,
                "generation_type": gen.generation_type,
                "formats_generated": gen.formats_generated,
                "created_at": gen.created_at.isoformat(),
                "metadata": json.loads(gen.result_data).get("metadata", {}) if gen.result_data else {}
            })
        
        total = db.query(ContentGeneration)\
            .filter(ContentGeneration.user_id == current_user.id)\
            .count()
        
        return {
            "success": True,
            "history": history,
            "total": total,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get generation history: {str(e)}")


@router.get("/generation/{generation_id}")
async def get_generation_details(
    generation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed results of a specific generation
    """
    try:
        generation = db.query(ContentGeneration)\
            .filter(
                ContentGeneration.id == generation_id,
                ContentGeneration.user_id == current_user.id
            )\
            .first()
        
        if not generation:
            raise HTTPException(status_code=404, detail="Generation not found")
        
        return {
            "success": True,
            "generation": {
                "id": generation.id,
                "generation_type": generation.generation_type,
                "formats_generated": generation.formats_generated,
                "created_at": generation.created_at.isoformat(),
                "input_data": json.loads(generation.input_data) if generation.input_data else {},
                "result_data": json.loads(generation.result_data) if generation.result_data else {}
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get generation details: {str(e)}")


async def store_generation_record(
    db: Session,
    user_id: int,
    generation_type: str,
    input_data: Dict[str, Any],
    result_data: Dict[str, Any],
    formats_generated: List[str]
):
    """
    Store content generation record in database (background task)
    """
    try:
        generation = ContentGeneration(
            user_id=user_id,
            generation_type=generation_type,
            formats_generated=formats_generated,
            input_data=json.dumps(input_data),
            result_data=json.dumps(result_data)
        )
        
        db.add(generation)
        db.commit()
        
    except Exception as e:
        print(f"Failed to store generation record: {e}")
        db.rollback()


# Utility endpoints for content management

@router.post("/validate-content")
async def validate_content_for_format(
    content: str,
    format_name: str
):
    """
    Validate if content meets format requirements
    """
    try:
        format_enum = generator.ContentFormat(format_name)
        spec = generator.PLATFORM_SPECS[format_enum]
        
        validation_result = {
            "format": format_name,
            "character_count": len(content),
            "word_count": len(content.split()),
            "valid": True,
            "warnings": [],
            "errors": []
        }
        
        # Check character limit
        if spec.character_limit and len(content) > spec.character_limit:
            validation_result["valid"] = False
            validation_result["errors"].append(
                f"Content exceeds character limit: {len(content)}/{spec.character_limit}"
            )
        
        # Check word limit
        if spec.word_limit and len(content.split()) > spec.word_limit:
            validation_result["valid"] = False
            validation_result["errors"].append(
                f"Content exceeds word limit: {len(content.split())}/{spec.word_limit}"
            )
        
        # Format-specific validations
        if format_name == "twitter_post" and len(content) > 280:
            validation_result["errors"].append("Twitter posts must be under 280 characters")
        
        if format_name == "twitter_thread":
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if len(line) > 280:
                    validation_result["warnings"].append(f"Thread line {i+1} exceeds 280 characters")
        
        return {
            "success": True,
            "validation": validation_result
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid format: {format_name}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@router.get("/format-templates")
async def get_format_templates():
    """
    Get example templates and best practices for each format
    """
    templates = {
        "newsletter": {
            "structure": ["Subject Line", "Introduction", "Main Content", "Call to Action"],
            "example": "📧 Weekly AI Insights\n\nHi there!\n\nThis week in AI...\n\n[Main content sections]\n\nWhat did you think? Reply and let me know!\n\nBest,\n[Your name]",
            "best_practices": [
                "Start with engaging subject line",
                "Personal greeting",
                "Clear sections",
                "Strong call-to-action"
            ]
        },
        "twitter_thread": {
            "structure": ["Hook Tweet", "Main Points (numbered)", "Conclusion", "Call to Action"],
            "example": "1/6 🧵 The biggest mistake I see creators make...\n\n2/6 They try to be everywhere at once\n\n[Continue thread]\n\n6/6 What's your biggest content challenge? Let me know below! 👇",
            "best_practices": [
                "Strong hook in first tweet",
                "Number your tweets",
                "One idea per tweet",
                "End with engagement question"
            ]
        },
        "linkedin_post": {
            "structure": ["Hook", "Story/Insight", "Takeaway", "Question"],
            "example": "I used to think more content = more success.\n\nI was wrong.\n\nHere's what I learned after analyzing 100+ successful creators:\n\n→ Quality beats quantity\n→ Consistency beats perfection\n→ Engagement beats reach\n\nWhat's been your biggest content lesson?",
            "best_practices": [
                "Professional but personal tone",
                "Share genuine insights",
                "Use bullet points",
                "Ask engaging questions"
            ]
        }
    }
    
    return {
        "success": True,
        "templates": templates
    }

from fastapi import APIRouter, HTTPException

from app.models.schemas import AnalysisRequest, AnalysisResponse, TechnicalIndicators
from app.services import llm, stock_data, technical

router = APIRouter()


@router.post("/chat", response_model=AnalysisResponse)
async def chat(request: AnalysisRequest):
    """Chat with LLM about stock analysis."""
    indicators = None
    context = ""

    if request.ticker:
        df = stock_data.get_history(request.ticker, period="6mo")
        ind_dict = technical.calculate_indicators(df)
        if ind_dict:
            indicators = TechnicalIndicators(ticker=request.ticker, **ind_dict)
            context = llm.build_context(ticker=request.ticker, indicators=ind_dict)

    try:
        response_text, conv_id = llm.chat(
            message=request.message,
            conversation_id=request.conversation_id,
            context=context,
        )
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM API error: {e}")

    return AnalysisResponse(
        response=response_text,
        conversation_id=conv_id,
        indicators=indicators,
    )

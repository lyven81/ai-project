# app.py
import httpx
import os
import io
import sys
import base64
import logging
import socket
import ssl
import time
from typing import Optional, List

from PIL import Image
from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Request, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# ---------- Make stdout/stderr UTF-8 safe on Windows ----------
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Python 3.7+
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# ---------- Setup logging ----------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def log_safe(msg: str) -> None:
    """Log ASCII-only to avoid terminal emoji/Unicode issues on Windows."""
    try:
        sys.stdout.write((msg.encode("ascii", "ignore").decode("ascii") + "\n"))
        sys.stdout.flush()
    except Exception:
        pass

# ---------- Load .env locally (no-op on Cloud Run) ----------
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

# ---------- Startup validation (fail fast) ----------
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

if not ANTHROPIC_API_KEY or not ANTHROPIC_API_KEY.startswith("sk-ant"):
    error_msg = "ANTHROPIC_API_KEY missing or malformed (expected Anthropic API key format)."
    logger.error(error_msg)
    raise RuntimeError(error_msg)

logger.info(f"[init] API key validated: length={len(ANTHROPIC_API_KEY)}, prefix=sk-ant***")

# ---------- Hardened HTTP client with timeouts + retries ----------
HTTP_TIMEOUT = httpx.Timeout(connect=30.0, read=60.0, write=60.0, pool=30.0)
transport = httpx.HTTPTransport(retries=3)  # simple built-in retry for idempotent steps
http_client = httpx.Client(timeout=HTTP_TIMEOUT, transport=transport)

# ---------- Anthropic client with diagnostics ----------
anthropic_client = None
APIStatusError = Exception
APIConnectionError = Exception
try:
    from anthropic import Anthropic, APIStatusError as _APIStatusError, APIConnectionError as _APIConnectionError
    APIStatusError = _APIStatusError
    APIConnectionError = _APIConnectionError
    
    # Initialize Anthropic client with Cloud Run optimized settings
    anthropic_client = Anthropic(
        api_key=ANTHROPIC_API_KEY,
        timeout=120.0,  # Simpler timeout configuration for Cloud Run
        max_retries=3,  # Enable built-in retries
    )
    logger.info("[init] Anthropic client initialized successfully with Cloud Run settings")
except Exception as e:
    logger.error(f"[init] Failed to init Anthropic client: {e}")
    raise RuntimeError(f"Failed to initialize Anthropic client: {e}")


# ---------- FastAPI app ----------
app = FastAPI(
    title="AI Recipe Generator",
    version="1.0.2",
    description="Generate creative recipes from food photos using AI",
)
templates = Jinja2Templates(directory=".")

# ---------- Network diagnostics router ----------
router = APIRouter()

@router.get("/netcheck")
def netcheck():
    """Live network diagnostics endpoint to test DNS, TLS, and Anthropic reachability"""
    out = {"dns": None, "tls": None, "anthropic_health": None, "proxy_info": None}
    
    # Check proxy environment variables
    proxy_vars = {
        "HTTP_PROXY": os.getenv("HTTP_PROXY"),
        "HTTPS_PROXY": os.getenv("HTTPS_PROXY"), 
        "NO_PROXY": os.getenv("NO_PROXY")
    }
    out["proxy_info"] = {k: v for k, v in proxy_vars.items() if v}
    
    # DNS check
    try:
        host_ip = socket.gethostbyname("api.anthropic.com")
        out["dns"] = f"api.anthropic.com -> {host_ip}"
    except Exception as e:
        out["dns"] = f"DNS_FAILED: {e}"

    # TLS check
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection(("api.anthropic.com", 443), timeout=10) as sock:
            with ctx.wrap_socket(sock, server_hostname="api.anthropic.com") as ssock:
                out["tls"] = f"TLS_OK: {ssock.version()}"
    except Exception as e:
        out["tls"] = f"TLS_FAILED: {e}"

    # Anthropic API health check (without consuming tokens)
    try:
        r = http_client.get(
            "https://api.anthropic.com/health", 
            headers={"anthropic-version": "2023-06-01"}
        )
        out["anthropic_health"] = f"HTTP_{r.status_code}"
    except Exception as e:
        out["anthropic_health"] = f"REQ_FAILED: {e}"

    return out

app.include_router(router)

# ---------- Anthropic call wrapper with diagnostics ----------
def call_anthropic_with_diagnostics(messages, system_prompt, model="claude-3-5-sonnet-20241022", max_tokens=1500, temperature=0.3):
    """
    Call Anthropic API with comprehensive error handling and diagnostics
    """
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            logger.info(f"[API] Attempt {attempt + 1}/{max_retries}: Calling Anthropic API with model {model}")
            resp = anthropic_client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=messages
            )
            logger.info(f"[API] Success on attempt {attempt + 1}")
            return resp
            
        except APIConnectionError as e:
            logger.error(f"[API] APIConnectionError on attempt {attempt + 1}: {e}")
            
            if attempt < max_retries - 1:
                logger.info(f"[API] Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2
                continue
            
            # Final attempt failed - run diagnostics
            dns_status = "UNKNOWN"
            try:
                socket.gethostbyname("api.anthropic.com")
                dns_status = "DNS_OK"
            except Exception as dns_err:
                dns_status = f"DNS_FAILED: {dns_err}"

            # Check proxy settings
            proxy_info = []
            for var in ["HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY"]:
                if os.getenv(var):
                    proxy_info.append(f"{var}={os.getenv(var)}")
            proxy_status = "; ".join(proxy_info) if proxy_info else "NO_PROXY_VARS"
            
            error_msg = f"APIConnectionError after {max_retries} attempts: {e}; DNS: {dns_status}; Proxy: {proxy_status}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
            
        except APIStatusError as e:
            logger.error(f"[API] APIStatusError on attempt {attempt + 1}: status={e.status_code} body={getattr(e, 'message', str(e))}")
            # Don't retry on status errors - they're usually not transient
            error_msg = f"APIStatusError: status={e.status_code} body={getattr(e, 'message', str(e))}"
            raise RuntimeError(error_msg)
            
        except Exception as e:
            logger.error(f"[API] Unexpected error on attempt {attempt + 1}: {type(e).__name__}: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2
                continue
            error_msg = f"Unexpected Anthropic error after {max_retries} attempts: {type(e).__name__}: {e}"
            raise RuntimeError(error_msg)

# ---------- Response model ----------
class RecipeResponse(BaseModel):
    recipe_name: str
    ingredients: List[str]
    instructions: List[str]
    prep_time: Optional[str] = None
    cook_time: Optional[str] = None
    servings: Optional[int] = None
    difficulty: str
    tips: Optional[List[str]] = None
    encouragement: Optional[str] = None

# ---------- System prompt ----------
RECIPE_SYSTEM_PROMPT = """You are a friendly, encouraging AI cooking companion who helps people create delicious meals from whatever ingredients they have available. Your goal is to make cooking accessible, fun, and confidence-building for everyone, regardless of their skill level.

## Critical First Step - Image Analysis:
**BEFORE generating any recipe, you MUST:**
1. **Identify if the image contains food ingredients** - If the image shows non-food items, politely decline and explain you can only generate recipes from food images
2. **Identify specific ingredients** - List the exact food items you can see in the image
3. **Inform the user** what ingredients you've identified before proceeding

## Response Guidelines:
1. **First analyze if image contains food** - If not food, politely decline with: "I can see this image doesn't contain food ingredients. I can only generate recipes from images of food items. Please upload an image with ingredients like vegetables, meat, eggs, or other cooking ingredients."
2. **Identify visible ingredients** and tell user what you see
3. **Create a unique recipe** that uses those specific ingredients
4. **Match the difficulty** to the user's specified skill level
5. **Incorporate cuisine style** requested by user
6. **Adapt to dietary restrictions** if specified
7. **Use encouraging language** throughout

## Response Format:

🔍 **What I Can See:**
[List the specific ingredients identified in the image]

🍽️ [Creative Recipe Name Based on Identified Ingredients]

[Brief encouraging intro about the recipe using the specific ingredients]

📋 Ingredients You'll Need:
• [List each identified ingredient with quantities]
• [Include any additional pantry items needed]

👨‍🍳 Let's Cook Together! (Step-by-Step):

1. [First step - specific to identified ingredients]
2. [Second step - include helpful tips]
3. [Continue with numbered steps tailored to the ingredients]
4. [Final step with presentation tips]

⏱️ Time & Details:
• Prep Time: [X minutes]
• Cook Time: [X minutes]
• Serves: [X people]
• Difficulty: [Beginner/Intermediate/Advanced]

💡 Chef's Tips for Success:
• [Helpful tip #1 specific to these ingredients]
• [Helpful tip #2 specific to these ingredients]
• [Helpful tip #3 specific to these ingredients]

✨ You've Got This!
[Encouraging closing message specific to this recipe]

## Important Rules:
- **NEVER generate recipes for non-food images**
- **ALWAYS identify ingredients first**
- **Make recipes truly unique** based on what you see
- **No hardcoded responses** - everything should be based on the actual image
- **Be specific** about ingredients and cooking methods
"""

# ---------- Helpers ----------
def encode_image_to_base64(image_file: UploadFile) -> str:
    try:
        b = image_file.file.read()
        img = Image.open(io.BytesIO(b))
        max_side = 1600
        w, h = img.size
        if max(w, h) > max_side:
            if w >= h:
                new_w, new_h = max_side, int(h * (max_side / w))
            else:
                new_h, new_w = max_side, int(w * (max_side / h))
            img = img.resize((new_w, new_h))
        out = io.BytesIO()
        img.save(out, format="JPEG", quality=85, optimize=True)
        return base64.b64encode(out.getvalue()).decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")
        
def create_recipe_prompt(
    cuisine_style: str,
    cooking_level: str,
    meal_type: str,
    dietary_restrictions: Optional[str],
) -> str:
    base = f"""**CRITICAL: First determine if this image contains food ingredients. If not, respond with: "I can see this image doesn't contain food ingredients. I can only generate recipes from images of food items. Please upload an image with ingredients like vegetables, meat, eggs, or other cooking ingredients."**

If the image DOES contain food ingredients, then:

1. **FIRST**: Identify and list the specific food ingredients you can see in the image
2. **THEN**: Create a {cuisine_style} recipe suitable for a {cooking_level.lower()} cook using those exact ingredients

**Requirements:**
- Cuisine Style: {cuisine_style}
- Cooking Level: {cooking_level}
- Meal Type: {meal_type}"""
    if dietary_restrictions:
        base += f"\n- Dietary Restrictions: {dietary_restrictions}"
    base += """

**Critical Guidelines:**
1. **MUST identify if image contains food first** - reject non-food images politely
2. **MUST list specific ingredients** you see before creating recipe
3. **Use ONLY the visible ingredients** as main components
4. **Create unique recipe** based on the actual ingredients in THIS image
5. **No generic responses** - everything must be tailored to what you see
6. You may suggest common pantry items (salt, pepper, oil, etc.) not visible
7. Write in encouraging tone and break down steps clearly
8. Include timing estimates and helpful tips specific to these ingredients

Create a personalized recipe based on the specific ingredients you identify in this image!"""
    return base

def create_error_response(error_message: str, cooking_level: str) -> RecipeResponse:
    return RecipeResponse(
        recipe_name="Unable to Generate Recipe",
        ingredients=["Please upload an image with food ingredients"],
        instructions=["Upload a clear image of food ingredients for recipe generation"],
        prep_time=None,
        cook_time=None,
        servings=None,
        difficulty=cooking_level,
        tips=["Make sure your image shows food items clearly"],
        encouragement=error_message,
    )

def parse_recipe_response(text: str, cooking_level: str) -> RecipeResponse:
    import re

    try:
        # Non-food detection (from model reply)
        if ("doesn't contain food ingredients" in text) or (
            "can only generate recipes from images of food" in text
        ):
            return create_error_response(
                "I can see this image doesn't contain food ingredients. I can only generate recipes from images of food items. Please upload an image with ingredients like vegetables, meat, eggs, or other cooking ingredients.",
                cooking_level,
            )

        # Initialize defaults
        recipe_name = "Recipe from Your Ingredients"
        ingredients = []
        instructions = []
        tips = []
        encouragement = "You've got this! Every ingredient tells a story, and yours will be delicious!"
        prep_time = None
        cook_time = None
        servings = None
        
        # Extract recipe name
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('🍽️') and len(line) > 3:
                recipe_name = line[3:].strip().lstrip('*').strip()
                break
        
        # Extract ingredients
        in_ingredients = False
        for line in lines:
            line = line.strip()
            if '📋' in line and ('Ingredients' in line or 'ingredients' in line):
                in_ingredients = True
                continue
            elif in_ingredients and ('👨‍🍳' in line or '🍳' in line or line.startswith('##')):
                in_ingredients = False
            elif in_ingredients and line and (line.startswith('•') or line.startswith('-') or line.startswith('*')):
                ingredients.append(line.lstrip('•-*').strip())
        
        # Extract instructions
        in_instructions = False
        step_counter = 1
        for line in lines:
            line = line.strip()
            if ('👨‍🍳' in line or '🍳' in line) and ('Instructions' in line or 'Cook' in line or 'Step' in line):
                in_instructions = True
                continue
            elif in_instructions and ('⏱️' in line or '💡' in line or line.startswith('##')):
                in_instructions = False
            elif in_instructions and line:
                if line.startswith(str(step_counter) + '.'):
                    instructions.append(line)
                    step_counter += 1
                elif len(line) > 20 and not line.startswith('•') and not line.startswith('-'):
                    instructions.append(line)
        
        # Extract tips
        in_tips = False
        for line in lines:
            line = line.strip()
            if '💡' in line and ('Tips' in line or 'tips' in line):
                in_tips = True
                continue
            elif in_tips and ('✨' in line or line.startswith('##')):
                in_tips = False
            elif in_tips and line and (line.startswith('•') or line.startswith('-') or line.startswith('*')):
                tips.append(line.lstrip('•-*').strip())
        
        # Extract timing info
        for line in lines:
            line = line.strip()
            if 'Prep Time:' in line:
                try:
                    prep_time = line.split('Prep Time:')[1].split('•')[0].split('Cook Time:')[0].strip()
                except:
                    pass
            if 'Cook Time:' in line:
                try:
                    cook_time = line.split('Cook Time:')[1].split('•')[0].split('Serves:')[0].strip()
                except:
                    pass
            if 'Serves:' in line or 'Servings:' in line:
                try:
                    import re as regex
                    match = regex.search(r'(\d+)', line)
                    if match:
                        servings = int(match.group(1))
                except:
                    pass

        return RecipeResponse(
            recipe_name=recipe_name,
            ingredients=ingredients if ingredients else ["Ingredients from your uploaded image"],
            instructions=instructions if instructions else ["Please check the full AI response above for detailed cooking steps"],
            prep_time=prep_time,
            cook_time=cook_time,
            servings=servings,
            difficulty=cooking_level,
            tips=tips if tips else ["Cook with confidence and taste as you go!"],
            encouragement=encouragement,
        )

    except Exception as e:
        log_safe(f"ERROR in parse_recipe_response: {e}")
        return create_error_response(
            "There was an issue parsing the recipe. Please try again!",
            cooking_level,
        )

# ---------- Routes ----------
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": "AI Recipe Generator"})

@app.get("/healthz")
def health():
    return {"status": "ok", "message": "AI Recipe Generator is running"}

@app.get("/debug/env")
def debug_env():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    return {
        "has_api_key": bool(api_key),
        "api_key_length": len(api_key) if api_key else 0,
        "api_key_starts_with": api_key[:10] + "..." if api_key else None,
        "client_initialized": bool(anthropic_client is not None),
        "client_type": str(type(anthropic_client)) if anthropic_client else None,
        "environment_vars": {
            key: "***" if "key" in key.lower() or "secret" in key.lower() else value
            for key, value in os.environ.items()
            if key.startswith(("ANTHROPIC", "GOOGLE", "GCLOUD", "CLOUD"))
        },
    }

@app.get("/debug/net")
def debug_net():
    """Quick outbound egress test."""
    results = {}
    try:
        import httpx as _httpx
        for url in ["https://www.google.com", "https://api.anthropic.com"]:
            try:
                r = _httpx.get(url, timeout=10)
                results[url] = {"ok": True, "status": r.status_code}
            except Exception as e:
                results[url] = {"ok": False, "error": repr(e)}
    except Exception as e:
        results["error"] = f"httpx import failed: {e}"
    return results

@app.post("/analyze-recipe", response_model=RecipeResponse)
async def analyze_recipe(
    image: UploadFile = File(..., description="Image of food ingredients or cooking ingredients"),
    cuisine_style: str = Form(..., description="Preferred cuisine style"),
    cooking_level: str = Form(..., description="Cooking skill level"),
    meal_type: str = Form(default="Any", description="Type of meal"),
    dietary_restrictions: Optional[str] = Form(default=None, description="Dietary restrictions"),
):
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload a valid image file showing food ingredients")

    image.file.seek(0, 2)
    size = image.file.tell()
    image.file.seek(0)
    if size > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image file too large. Please upload an image smaller than 10MB.")

    if not anthropic_client:
        return create_error_response(
            "I can see your image, but I need my AI capabilities to analyze ingredients and generate recipes. Please check the API configuration.",
            cooking_level,
        )

    try:
        log_safe(f"DEBUG Processing image: name={image.filename} type={image.content_type}")
        b64 = encode_image_to_base64(image)
        log_safe(f"DEBUG Image encoded, len={len(b64)}")

        user_prompt = create_recipe_prompt(cuisine_style, cooking_level, meal_type, dietary_restrictions)
        log_safe("DEBUG Prompt created")

        # Test API connectivity first
        logger.info(f"Making API call to Anthropic with model claude-3-5-sonnet-20241022")
        
        # Use diagnostic wrapper for Anthropic call
        resp = call_anthropic_with_diagnostics(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {"type": "base64", "media_type": "image/jpeg", "data": b64},
                        },
                        {"type": "text", "text": user_prompt},
                    ],
                }
            ],
            system_prompt=RECIPE_SYSTEM_PROMPT
        )

        ai_text = (resp.content[0].text if resp and getattr(resp, "content", None) else "").strip()
        if not ai_text:
            log_safe("ERROR Empty AI text response")
            return create_error_response(
                "The AI service returned an empty response. Please try again!",
                cooking_level,
            )

        recipe = parse_recipe_response(ai_text, cooking_level)
        logger.info(f"Successfully parsed recipe: {recipe.recipe_name}")
        return recipe

    except RuntimeError as e:
        # Our diagnostic wrapper converts API errors to RuntimeError with detailed info
        error_msg = str(e)
        logger.error(f"Anthropic API error with diagnostics: {error_msg}")
        
        # Provide actionable error messages based on diagnostic info
        if "DNS_FAILED" in error_msg:
            user_message = "DNS resolution failed. Check your internet connection or DNS settings."
        elif "APIConnectionError" in error_msg:
            user_message = "Connection error with AI service. Check network connectivity and proxy settings."
        elif "APIStatusError" in error_msg and "401" in error_msg:
            user_message = "Authentication failed. Please check your API key configuration."
        elif "APIStatusError" in error_msg and "429" in error_msg:
            user_message = "Rate limit exceeded. Please wait a moment before trying again."
        elif "APIStatusError" in error_msg and "500" in error_msg:
            user_message = "AI service is temporarily unavailable. Please try again in a few minutes."
        else:
            user_message = "AI service error. Please try again or check /netcheck for diagnostics."
            
        return create_error_response(user_message, cooking_level)
        
    except (httpx.ConnectError, httpx.TimeoutException, httpx.RequestError) as e:
        logger.error(f"Network/Connection Error: {type(e).__name__}: {e}")
        return create_error_response(
            "Network connection error. Check your internet connection and proxy settings.",
            cooking_level,
        )
    except Exception as e:
        logger.error(f"Unexpected Exception: {type(e).__name__}: {e}", exc_info=True)
        return create_error_response(
            "An unexpected error occurred. Check the logs or /netcheck endpoint for diagnostics.",
            cooking_level,
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting server on host 0.0.0.0 and port {port}")
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        access_log=True,
        log_level="info"
    )

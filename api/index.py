from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import os
import sys
from pathlib import Path

# إضافة المسارات للملفات
current_dir = Path(__file__).parent.parent
sys.path.append(str(current_dir / "utils"))
sys.path.append(str(current_dir / "protobufs"))

app = FastAPI(
    title="FreeFire Web Panel",
    version="1.0.0",
    description="لوحة تحكم FreeFire مع نظام كودات تفعيل مدفوعة"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# تقديم الملفات الثابتة من مجلد frontend
frontend_path = current_dir / "frontend"
if frontend_path.exists():
    from fastapi.staticfiles import StaticFiles
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

# API routes
@app.get("/")
async def root():
    """الصفحة الرئيسية"""
    index_path = frontend_path / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"message": "FreeFire Web Panel API"}

@app.get("/api/health")
async def health_check():
    """فحص صحة الخادم"""
    return {
        "status": "healthy",
        "service": "FreeFire Web Panel",
        "version": "1.0.0"
    }

@app.post("/api/validate-code")
async def validate_code(request: dict):
    """التحقق من كود التفعيل"""
    try:
        from services.code_generator import CodeGenerator
        code = request.get("code")
        username = request.get("username")
        
        if not code or not username:
            return JSONResponse(
                status_code=400,
                content={"error": "الرجاء إدخال الكود واسم المستخدم"}
            )
        
        # هنا سيتم التحقق من الكود
        return {
            "valid": True,
            "message": "الكود صالح",
            "username": username,
            "code_type": "premium",
            "duration_days": 30
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

# Serve HTML pages
@app.get("/{page_name}")
async def serve_page(page_name: str):
    """تقديم صفحات HTML"""
    page_path = frontend_path / f"{page_name}.html"
    
    # إذا كان المجلد admin
    if page_name == "admin":
        admin_path = frontend_path / "admin" / "index.html"
        if admin_path.exists():
            return FileResponse(str(admin_path))
    
    if page_path.exists():
        return FileResponse(str(page_path))
    
    return JSONResponse(
        status_code=404,
        content={"error": "الصفحة غير موجودة"}
    )

# API endpoints for FreeFire actions
@app.post("/api/send-invite")
async def send_invite(request: dict):
    """إرسال دعوة"""
    try:
        target_id = request.get("target_id")
        account_id = request.get("account_id")
        
        # هنا سيتم إرسال الدعوة
        return {
            "success": True,
            "message": f"تم إرسال دعوة إلى {target_id}",
            "from": account_id,
            "to": target_id
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

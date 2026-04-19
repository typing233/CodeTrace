from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import json
import uuid
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape

app = FastAPI(title="程序员个人作品集", version="1.0.0")

app.mount("/static", StaticFiles(directory="static"), name="static")

jinja_env = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=select_autoescape(["html", "xml"]),
    cache_size=0,
)

DATA_FILE = "data/profile.json"
UPLOAD_DIR = "static/uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


class Skill(BaseModel):
    name: str
    category: str = "技术"


class Project(BaseModel):
    id: Optional[str] = None
    title: str
    description: str
    tech_stack: List[str]
    link: Optional[str] = None
    image: Optional[str] = None


class Contact(BaseModel):
    email: str
    github: Optional[str] = None
    wechat: Optional[str] = None
    website: Optional[str] = None


class Profile(BaseModel):
    name: str = "张三"
    avatar: Optional[str] = None
    tagline: str = "全栈开发工程师"
    bio: str = "热爱编程，专注于Web开发和人工智能领域。"
    skills: List[Skill] = []
    projects: List[Project] = []
    contact: Contact = Contact(email="example@example.com")


def load_profile() -> Profile:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return Profile(**data)
    return Profile()


def save_profile(profile: Profile):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(profile.dict(), f, ensure_ascii=False, indent=2)


def get_default_profile() -> Profile:
    return Profile(
        name="李明",
        tagline="全栈开发工程师 | 开源爱好者",
        bio="5年全栈开发经验，专注于构建高性能、可扩展的Web应用。热爱开源，积极参与社区贡献。擅长Python、JavaScript，对云原生和AI有浓厚兴趣。",
        skills=[
            Skill(name="Python", category="后端"),
            Skill(name="FastAPI", category="框架"),
            Skill(name="JavaScript", category="前端"),
            Skill(name="React", category="前端框架"),
            Skill(name="Vue", category="前端框架"),
            Skill(name="Docker", category="DevOps"),
            Skill(name="Kubernetes", category="DevOps"),
            Skill(name="PostgreSQL", category="数据库"),
            Skill(name="MongoDB", category="数据库"),
            Skill(name="Git", category="工具"),
            Skill(name="Linux", category="系统"),
            Skill(name="AWS", category="云服务"),
        ],
        projects=[
            Project(
                id="1",
                title="智能任务管理系统",
                description="基于AI的智能任务调度系统，支持自然语言任务拆解、自动优先级排序和智能提醒功能。已服务超过10000名用户。",
                tech_stack=["Python", "FastAPI", "Vue.js", "PostgreSQL", "Redis"],
                link="https://github.com/example/task-manager",
            ),
            Project(
                id="2",
                title="电商微服务平台",
                description="分布式电商系统，采用微服务架构设计，支持高并发秒杀、分布式事务和实时库存管理。",
                tech_stack=["Go", "gRPC", "Kubernetes", "MySQL", "RabbitMQ"],
                link="https://github.com/example/ecommerce",
            ),
            Project(
                id="3",
                title="开源CLI工具集",
                description="一系列提高开发效率的命令行工具，包括代码生成器、日志分析器和云资源管理工具。",
                tech_stack=["Python", "Click", "Rich", "PyTest"],
                link="https://github.com/example/cli-tools",
            ),
            Project(
                id="4",
                title="实时协作白板",
                description="基于WebRTC的实时协作白板应用，支持多人同时编辑、图形绘制和代码块高亮显示。",
                tech_stack=["TypeScript", "React", "Socket.IO", "Canvas API"],
                link="https://github.com/example/whiteboard",
            ),
        ],
        contact=Contact(
            email="liming@example.com",
            github="https://github.com/liming",
            wechat="liming_dev",
        ),
    )


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    profile = load_profile()
    if not profile.name or profile.name == "张三":
        profile = get_default_profile()
    template = jinja_env.get_template("index.html")
    html_content = template.render(request=request, profile=profile.dict())
    return HTMLResponse(content=html_content)


@app.get("/api/profile")
async def get_profile():
    profile = load_profile()
    if not profile.name or profile.name == "张三":
        profile = get_default_profile()
    return profile.dict()


@app.post("/api/profile")
async def update_profile(profile: Profile):
    save_profile(profile)
    return {"message": "保存成功", "success": True}


@app.post("/api/upload/avatar")
async def upload_avatar(file: UploadFile = File(...)):
    file_ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{file_ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    with open(filepath, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    return {"url": f"/static/uploads/{filename}", "success": True}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=2334)

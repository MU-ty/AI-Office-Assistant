from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..schemas.task import Task, TaskCreate, TaskUpdate
from ..models.task import Task as TaskModel, TaskStatus, TaskType
from ..services.meeting_service import meeting_service
from ..models.user import User as UserModel

router = APIRouter()

# 模拟获取当前用户 (后续集成真实 Auth)
def get_current_user(db: Session = Depends(get_db)):
    user = db.query(UserModel).first()
    if not user:
        # 创建默认测试用户
        user = UserModel(username="testuser", email="test@example.com", hashed_password="...")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

@router.post("/meeting-minutes", response_model=Task)
async def create_meeting_minutes_task(
    *,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks,
    input_text: str,
    current_user: UserModel = Depends(get_current_user)
) -> Any:
    """创建会议纪要生成任务"""
    task = TaskModel(
        user_id=current_user.id,
        title="会议纪要生成",
        task_type=TaskType.MEETING_MINUTES,
        status=TaskStatus.PENDING,
        input_data=input_text
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # 异步执行任务
    background_tasks.add_task(process_meeting_task, task.id, db)
    
    return task

async def process_meeting_task(task_id: int, db: Session):
    """后台处理会议纪要任务"""
    # 重新获取数据库连接（如果需要）
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        return
    
    task.status = TaskStatus.IN_PROGRESS
    db.commit()
    
    try:
        result = await meeting_service.process_meeting_minutes(task.input_data)
        # 转换为Markdown存储在output_data
        md_result = meeting_service.format_to_markdown(result)
        
        task.output_data = md_result
        task.status = TaskStatus.COMPLETED
    except Exception as e:
        task.status = TaskStatus.FAILED
        task.error_message = str(e)
    
    db.commit()

@router.get("/", response_model=List[Task])
def read_tasks(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(get_current_user)
) -> Any:
    """获取用户所有任务"""
    tasks = db.query(TaskModel).filter(TaskModel.user_id == current_user.id).offset(skip).limit(limit).all()
    return tasks

@router.get("/{task_id}", response_model=Task)
def read_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
) -> Any:
    """获取特定任务详情"""
    task = db.query(TaskModel).filter(TaskModel.id == task_id, TaskModel.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

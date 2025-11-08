"""Bot endpoints"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.bot import Bot
from app.models.bot_scenario import BotScenario
from app.schemas.bot import BotCreate, BotUpdate, BotResponse, BotListResponse
from app.schemas.bot_scenario import BotScenarioCreate, BotScenarioUpdate, BotScenarioResponse

router = APIRouter()


@router.get("/", response_model=List[BotListResponse])
async def list_bots(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Получить список всех ботов бизнеса текущего пользователя
    """
    query = db.query(Bot).filter(Bot.business_id == current_user.business_id)
    
    if is_active is not None:
        query = query.filter(Bot.is_active == is_active)
    
    bots = query.offset(skip).limit(limit).all()
    
    # Добавляем подсчет сценариев для каждого бота
    result = []
    for bot in bots:
        bot_dict = {
            "id": bot.id,
            "name": bot.name,
            "description": bot.description,
            "welcome_message": bot.welcome_message,
            "default_response": bot.default_response,
            "is_active": bot.is_active,
            "whatsapp_number_id": bot.whatsapp_number_id,
            "business_id": bot.business_id,
            "created_at": bot.created_at,
            "updated_at": bot.updated_at,
            "scenarios_count": db.query(BotScenario).filter(BotScenario.bot_id == bot.id).count(),
        }
        result.append(bot_dict)
    
    return result


@router.post("/", response_model=BotResponse, status_code=status.HTTP_201_CREATED)
async def create_bot(
    bot_data: BotCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Создать новый бот
    """
    # Проверяем, что WhatsApp номер принадлежит бизнесу пользователя
    from app.models.whatsapp_number import WhatsAppNumber
    whatsapp_number = db.query(WhatsAppNumber).filter(
        and_(
            WhatsAppNumber.id == bot_data.whatsapp_number_id,
            WhatsAppNumber.business_id == current_user.business_id
        )
    ).first()
    
    if not whatsapp_number:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WhatsApp number not found or doesn't belong to your business"
        )
    
    # Создаем бота
    bot = Bot(
        business_id=current_user.business_id,
        whatsapp_number_id=bot_data.whatsapp_number_id,
        name=bot_data.name,
        description=bot_data.description,
        welcome_message=bot_data.welcome_message,
        default_response=bot_data.default_response,
        is_active=bot_data.is_active if bot_data.is_active is not None else True,
        settings=bot_data.settings or {},
    )
    
    db.add(bot)
    db.commit()
    db.refresh(bot)
    
    return bot


@router.get("/{bot_id}", response_model=BotResponse)
async def get_bot(
    bot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Получить информацию о конкретном боте
    """
    bot = db.query(Bot).filter(
        and_(
            Bot.id == bot_id,
            Bot.business_id == current_user.business_id
        )
    ).first()
    
    if not bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bot not found"
        )
    
    return bot


@router.put("/{bot_id}", response_model=BotResponse)
async def update_bot(
    bot_id: int,
    bot_data: BotUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Обновить информацию о боте
    """
    bot = db.query(Bot).filter(
        and_(
            Bot.id == bot_id,
            Bot.business_id == current_user.business_id
        )
    ).first()
    
    if not bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bot not found"
        )
    
    # Обновляем только переданные поля
    update_data = bot_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(bot, field, value)
    
    db.commit()
    db.refresh(bot)
    
    return bot


@router.delete("/{bot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bot(
    bot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Удалить бота
    """
    bot = db.query(Bot).filter(
        and_(
            Bot.id == bot_id,
            Bot.business_id == current_user.business_id
        )
    ).first()
    
    if not bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bot not found"
        )
    
    db.delete(bot)
    db.commit()
    
    return None


# === Сценарии бота ===

@router.get("/{bot_id}/scenarios", response_model=List[BotScenarioResponse])
async def list_bot_scenarios(
    bot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Получить все сценарии конкретного бота
    """
    # Проверяем, что бот принадлежит бизнесу пользователя
    bot = db.query(Bot).filter(
        and_(
            Bot.id == bot_id,
            Bot.business_id == current_user.business_id
        )
    ).first()
    
    if not bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bot not found"
        )
    
    scenarios = db.query(BotScenario).filter(BotScenario.bot_id == bot_id).all()
    return scenarios


@router.post("/{bot_id}/scenarios", response_model=BotScenarioResponse, status_code=status.HTTP_201_CREATED)
async def create_bot_scenario(
    bot_id: int,
    scenario_data: BotScenarioCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Создать новый сценарий для бота
    """
    # Проверяем, что бот принадлежит бизнесу пользователя
    bot = db.query(Bot).filter(
        and_(
            Bot.id == bot_id,
            Bot.business_id == current_user.business_id
        )
    ).first()
    
    if not bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bot not found"
        )
    
    # Если это дефолтный сценарий, снимаем флаг с других
    if scenario_data.is_default:
        db.query(BotScenario).filter(BotScenario.bot_id == bot_id).update(
            {"is_default": False}
        )
    
    # Создаем сценарий
    scenario = BotScenario(
        bot_id=bot_id,
        name=scenario_data.name,
        description=scenario_data.description,
        flow_data=scenario_data.flow_data,
        trigger_keywords=scenario_data.trigger_keywords or [],
        is_default=scenario_data.is_default if scenario_data.is_default is not None else False,
        is_active=scenario_data.is_active if scenario_data.is_active is not None else True,
        version=1,
    )
    
    db.add(scenario)
    db.commit()
    db.refresh(scenario)
    
    return scenario


@router.get("/{bot_id}/scenarios/{scenario_id}", response_model=BotScenarioResponse)
async def get_bot_scenario(
    bot_id: int,
    scenario_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Получить конкретный сценарий бота
    """
    # Проверяем, что бот принадлежит бизнесу пользователя
    bot = db.query(Bot).filter(
        and_(
            Bot.id == bot_id,
            Bot.business_id == current_user.business_id
        )
    ).first()
    
    if not bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bot not found"
        )
    
    scenario = db.query(BotScenario).filter(
        and_(
            BotScenario.id == scenario_id,
            BotScenario.bot_id == bot_id
        )
    ).first()
    
    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario not found"
        )
    
    return scenario


@router.put("/{bot_id}/scenarios/{scenario_id}", response_model=BotScenarioResponse)
async def update_bot_scenario(
    bot_id: int,
    scenario_id: int,
    scenario_data: BotScenarioUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Обновить сценарий бота
    """
    # Проверяем, что бот принадлежит бизнесу пользователя
    bot = db.query(Bot).filter(
        and_(
            Bot.id == bot_id,
            Bot.business_id == current_user.business_id
        )
    ).first()
    
    if not bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bot not found"
        )
    
    scenario = db.query(BotScenario).filter(
        and_(
            BotScenario.id == scenario_id,
            BotScenario.bot_id == bot_id
        )
    ).first()
    
    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario not found"
        )
    
    # Если меняем на дефолтный, снимаем флаг с других
    if scenario_data.is_default and not scenario.is_default:
        db.query(BotScenario).filter(
            and_(
                BotScenario.bot_id == bot_id,
                BotScenario.id != scenario_id
            )
        ).update({"is_default": False})
    
    # Обновляем только переданные поля
    update_data = scenario_data.dict(exclude_unset=True)
    
    # Увеличиваем версию при изменении flow_data
    if "flow_data" in update_data:
        update_data["version"] = scenario.version + 1
    
    for field, value in update_data.items():
        setattr(scenario, field, value)
    
    db.commit()
    db.refresh(scenario)
    
    return scenario


@router.delete("/{bot_id}/scenarios/{scenario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bot_scenario(
    bot_id: int,
    scenario_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Удалить сценарий бота
    """
    # Проверяем, что бот принадлежит бизнесу пользователя
    bot = db.query(Bot).filter(
        and_(
            Bot.id == bot_id,
            Bot.business_id == current_user.business_id
        )
    ).first()
    
    if not bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bot not found"
        )
    
    scenario = db.query(BotScenario).filter(
        and_(
            BotScenario.id == scenario_id,
            BotScenario.bot_id == bot_id
        )
    ).first()
    
    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario not found"
        )
    
    db.delete(scenario)
    db.commit()
    
    return None


@router.post("/{bot_id}/toggle", response_model=BotResponse)
async def toggle_bot_status(
    bot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Включить/выключить бота
    """
    bot = db.query(Bot).filter(
        and_(
            Bot.id == bot_id,
            Bot.business_id == current_user.business_id
        )
    ).first()
    
    if not bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bot not found"
        )
    
    bot.is_active = not bot.is_active
    db.commit()
    db.refresh(bot)
    
    return bot

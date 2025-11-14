"""
Initialize bot templates with ready-to-use scenarios
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.business import Business
from app.models.whatsapp_number import WhatsAppNumber
from app.models.bot import Bot, BotScenario
from app.core.security import get_password_hash
import json
import os


def create_bot_templates():
    """Create bot templates with scenarios"""
    db = SessionLocal()
    
    try:
        # Get first WhatsApp number
        whatsapp_number = db.query(WhatsAppNumber).first()
        
        if not whatsapp_number:
            print("⚠️  WhatsApp номер не найден. Создаю тестовые данные...")
            
            # Create test user and business
            from app.models.business import Business
            from app.core.security import get_password_hash
            import os
            
            # Check if user exists
            user = db.query(User).filter(User.email == 'admin@chatbot.com').first()
            
            if not user:
                user = User(
                    email='admin@chatbot.com',
                    full_name='Admin User',
                    hashed_password=get_password_hash('admin123'),
                    role='owner',
                    is_active=True,
                    is_verified=True
                )
                db.add(user)
                db.flush()
                print(f"✓ User created: {user.email}")
            
            # Check if business exists
            business = db.query(Business).filter(Business.owner_id == user.id).first()
            
            if not business:
                business = Business(
                    name='Demo Business',
                    description='Demo business for testing',
                    owner_id=user.id,
                    is_active=True
                )
                db.add(business)
                db.flush()
                
                # Update user with business_id
                user.business_id = business.id
                print(f"✓ Business created: {business.name}")
            
            # Create WhatsApp number
            phone_number = os.getenv('WHATSAPP_PHONE_NUMBER', '+1234567890')
            phone_number_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID', 'demo_phone_id')
            
            whatsapp_number = WhatsAppNumber(
                business_id=business.id,
                phone_number=phone_number,
                display_name='Demo WhatsApp',
                provider='meta',
                phone_number_id=phone_number_id,
                status='connected',
                is_active=True
            )
            db.add(whatsapp_number)
            db.flush()
            
            print(f"✓ WhatsApp number created: {whatsapp_number.phone_number}")
            print()
        
        business_id = whatsapp_number.business_id
        print(f"✓ WhatsApp номер найден: {whatsapp_number.phone_number}")
        
        # Check if bots already exist
        existing_bot = db.query(Bot).filter(Bot.business_id == business_id).first()
        if existing_bot:
            print("✓ Боты уже существуют")
            return
        
        # Template 1: Салон красоты
        beauty_salon_bot = Bot(
            business_id=business_id,
            whatsapp_number_id=whatsapp_number.id,
            name="Салон красоты - Автоответчик",
            description="Автоматические ответы для салона красоты с меню услуг и записью",
            welcome_message="Здравствуйте! 👋 Добро пожаловать в наш салон красоты!\n\nЯ виртуальный ассистент, помогу вам записаться на услугу.\n\nВыберите интересующую услугу:\n1️⃣ Стрижка и укладка\n2️⃣ Окрашивание\n3️⃣ Маникюр/Педикюр\n4️⃣ Косметология\n5️⃣ Массаж\n\nНапишите номер услуги или свой вопрос.",
            default_response="Спасибо за сообщение! ❤️\n\nДля записи напишите:\n• Желаемую услугу\n• Удобную дату и время\n\nИли выберите из меню:\n1️⃣ Стрижка\n2️⃣ Окрашивание\n3️⃣ Маникюр\n4️⃣ Косметология\n5️⃣ Массаж",
            is_active=True,
            settings={
                "auto_reply": True,
                "working_hours": {
                    "enabled": True,
                    "monday": "09:00-20:00",
                    "tuesday": "09:00-20:00",
                    "wednesday": "09:00-20:00",
                    "thursday": "09:00-20:00",
                    "friday": "09:00-20:00",
                    "saturday": "10:00-18:00",
                    "sunday": "closed"
                },
                "off_hours_message": "Спасибо за обращение! 🌙\n\nСейчас мы не работаем.\nРабочие часы: Пн-Пт 09:00-20:00, Сб 10:00-18:00\n\nОставьте заявку, мы свяжемся с вами утром!"
            }
        )
        db.add(beauty_salon_bot)
        db.flush()
        
        # Scenarios for beauty salon
        scenarios = [
            BotScenario(
                bot_id=beauty_salon_bot.id,
                name="Стрижка и укладка",
                trigger_type="keyword",
                trigger_value=json.dumps(["стрижка", "укладка", "1", "стрижку", "подстричься"]),
                response_message="💇 Стрижка и укладка\n\n📋 Наши услуги:\n• Женская стрижка - от 3000₸\n• Мужская стрижка - от 2000₸\n• Детская стрижка - от 1500₸\n• Укладка - от 2500₸\n\n📅 Для записи напишите:\n- Желаемую дату\n- Удобное время\n\nМы свяжемся с вами для подтверждения!",
                is_active=True,
                priority=1
            ),
            BotScenario(
                bot_id=beauty_salon_bot.id,
                name="Окрашивание",
                trigger_type="keyword",
                trigger_value=json.dumps(["окрашивание", "покрасить", "2", "цвет", "краска"]),
                response_message="🎨 Окрашивание волос\n\n📋 Наши услуги:\n• Полное окрашивание - от 5000₸\n• Мелирование - от 6000₸\n• Балаяж - от 8000₸\n• Тонирование - от 3000₸\n\n⏱ Длительность: 2-4 часа\n\n📅 Для записи напишите желаемую дату и время",
                is_active=True,
                priority=2
            ),
            BotScenario(
                bot_id=beauty_salon_bot.id,
                name="Маникюр/Педикюр",
                trigger_type="keyword",
                trigger_value=json.dumps(["маникюр", "педикюр", "3", "ногти", "нейл"]),
                response_message="💅 Маникюр и Педикюр\n\n📋 Наши услуги:\n• Классический маникюр - 2500₸\n• Аппаратный маникюр - 3000₸\n• Гель-лак - 3500₸\n• Педикюр - 4000₸\n• Наращивание - от 5000₸\n\n⏱ Длительность: 1-2 часа\n\n📅 Запись: укажите дату и время",
                is_active=True,
                priority=3
            ),
            BotScenario(
                bot_id=beauty_salon_bot.id,
                name="Косметология",
                trigger_type="keyword",
                trigger_value=json.dumps(["косметология", "чистка", "4", "пилинг", "уход"]),
                response_message="✨ Косметология\n\n📋 Популярные процедуры:\n• Чистка лица - 5000₸\n• Пилинг - от 4000₸\n• Уход за лицом - от 6000₸\n• Массаж лица - 3500₸\n• Биоревитализация - от 15000₸\n\n👩‍⚕️ Консультация косметолога - бесплатно\n\n📅 Запишитесь на консультацию!",
                is_active=True,
                priority=4
            ),
            BotScenario(
                bot_id=beauty_salon_bot.id,
                name="Массаж",
                trigger_type="keyword",
                trigger_value=json.dumps(["массаж", "5", "релакс", "спа"]),
                response_message="💆 Массаж и SPA\n\n📋 Виды массажа:\n• Классический массаж - 5000₸/час\n• Антицеллюлитный - 6000₸/час\n• Массаж лица - 3000₸\n• Лимфодренажный - 7000₸\n• SPA программы - от 10000₸\n\n🎁 При покупке абонемента - скидка 15%!\n\n📅 Запись: напишите дату и время",
                is_active=True,
                priority=5
            ),
            BotScenario(
                bot_id=beauty_salon_bot.id,
                name="Цены",
                trigger_type="keyword",
                trigger_value=json.dumps(["цены", "прайс", "стоимость", "сколько", "цена"]),
                response_message="💰 Прайс-лист\n\n💇 Стрижки: от 1500₸\n🎨 Окрашивание: от 3000₸\n💅 Маникюр: от 2500₸\n✨ Косметология: от 4000₸\n💆 Массаж: от 3000₸\n\n🎁 Акции:\n• Первое посещение -10%\n• Абонементы -15%\n• Приведи друга -20% обоим!\n\n📞 Подробности по телефону или в WhatsApp",
                is_active=True,
                priority=6
            ),
            BotScenario(
                bot_id=beauty_salon_bot.id,
                name="График работы",
                trigger_type="keyword",
                trigger_value=json.dumps(["график", "время", "работаете", "часы", "расписание"]),
                response_message="🕐 График работы\n\n📅 Пн-Пт: 09:00 - 20:00\n📅 Сб: 10:00 - 18:00\n📅 Вс: Выходной\n\n📍 Адрес: [Укажите ваш адрес]\n📞 Телефон: [Укажите телефон]\n\n🎯 Запись онлайн - круглосуточно!",
                is_active=True,
                priority=7
            ),
            BotScenario(
                bot_id=beauty_salon_bot.id,
                name="Запись",
                trigger_type="keyword",
                trigger_value=json.dumps(["записаться", "запись", "бронь", "хочу", "нужно"]),
                response_message="📅 Запись на услугу\n\nДля записи укажите:\n1️⃣ Услугу (стрижка, маникюр и т.д.)\n2️⃣ Желаемую дату\n3️⃣ Удобное время\n\nПример:\n\"Хочу записаться на маникюр 15 ноября в 14:00\"\n\nМы подтвердим запись в течение 5 минут! ⏰",
                is_active=True,
                priority=8
            )
        ]
        
        for scenario in scenarios:
            db.add(scenario)
        
        db.commit()
        
        print("✅ Бот для салона красоты создан!")
        print(f"   - Основной бот: {beauty_salon_bot.name}")
        print(f"   - Сценариев: {len(scenarios)}")
        print("\n📋 Активные триггеры:")
        for s in scenarios:
            triggers = json.loads(s.trigger_value)
            print(f"   • {s.name}: {', '.join(triggers[:3])}")
        
        print("\n✅ Готово! Бот активен и готов отвечать на сообщения!")
        print("📱 Отправьте любое сообщение на ваш WhatsApp номер для теста")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("  Инициализация шаблонов ботов")
    print("=" * 60)
    print()
    create_bot_templates()

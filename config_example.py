from pathlib import Path

BOT_TOKEN = "PUT_YOUR_BOT_TOKEN_HERE"
ADMIN_CHAT_ID = 12345678910  # group chat id where admins will review verifications

BASE_DIR = Path(__file__).parent
MEDIA_DIR = BASE_DIR / "media"
PROFILE_PHOTOS_DIR = MEDIA_DIR / "profiles"
ID_PHOTOS_DIR = MEDIA_DIR / "ids"
for d in (MEDIA_DIR, PROFILE_PHOTOS_DIR, ID_PHOTOS_DIR):
    d.mkdir(parents=True, exist_ok=True)

STRINGS = {
    "start_welcome": (
        "Привет! Это бот для знакомства студентов.\n"
        "Продолжая, вы соглашаетесь с нашей политикой конфиденциальности (см. PDF).\n\n"
        "Нажмите «Начать регистрацию», чтобы создать профиль."
    ),
    "begin_registration": "Начать регистрацию",
    "privacy_pdf_caption": "Политика конфиденциальности",
    "ask_course": "1) Номер курса (1-4). Пример: 1, 2, 3, 4 или '1-ый курс'.",
    "ask_direction": "2) Название направления обучения (короткое). Пример: 'Прикладная математика'.",
    "ask_age": "3) Возраст (цифрами). Пример: 20.",
    "ask_name": "4) Имя (как вас называть).",
    "ask_description": "5) Краткое описание себя (макс 300 символов).",
    "ask_photo": "6) Пришлите фото профиля или нажмите «Пока продолжить без фото».",
    "skip_photo": "Пока продолжить без фото",
    "invalid_course": "Неверный курс. Введите число от 1 до 4 или '1-ый курс'.",
    "invalid_age": "Неверный возраст. Введите число от 16 до 100.",
    "invalid_name": "Неверное имя. Укажите от 1 до 60 символов без странных символов.",
    "invalid_description": "Описание слишком длинное (макс 300 символов).",
    "registration_cancelled": "Регистрация отменена. Возвращаемся в начало.",
    "profile_preview_title": "Ваш профиль (как видят другие):",
    "menu_view_profile": "Просмотреть профиль",
    "menu_edit_profile": "Редактировать профиль",
    "menu_verify_profile": "Подать на верификацию",
    "menu_choose_events": "Выбрать события",
    "verify_pending": "Статус: Ожидает верификации",
    "verify_denied": "Верификация отклонена — нажмите, чтобы отправить документ снова",
    "verify_approved": "Верифицирован ✅",
    "ask_id_photo": "Пришлите фото вашего студенческого билета (ID).",
    "verification_sent_admin": "Запрос на верификацию отправлен админам.",
    "verification_approved_notify": "Ваш профиль подтверждён администрацией — теперь доступен поиск!",
    "verification_denied_notify": "Ваша верификация отклонена. Пожалуйста, пришлите корректное фото ID и повторите.",
    "admin_new_verification": "Новая заявка на верификацию от @{username} (id={user_id}).",
    "admin_buttons_approve": "✅ Подтвердить",
    "admin_buttons_deny": "❌ Отклонить",
    "admin_buttons_ban": "🚫 Забанить",
    "search_begin": "Начать поиск",
    "search_next": "Следующий",
    "search_prev": "Предыдущий",
    "like_button": "❤ Нравится",
    "dislike_button": "✖ Не нравится",
    "match_notify": "У вас совпадение! @{other_username}",
    "no_profiles": "Нет подходящих профилей для поиска.",
    "edit_menu_prompt": "Что хотите изменить?",
    "saved_changes": "Изменения сохранены.",
    "cancel_button": "/cancel"
}

EVENTS = [
    "Кино",
    "Музей",
    "Театр",
    "Коворкинг",
    "Настолки"
]

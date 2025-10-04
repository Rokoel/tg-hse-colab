# All user-facing strings for the bot

# Welcome messages
WELCOME_MESSAGE = """
Добро пожаловать в бот для знакомств студентов! 🎓

Продолжая использование бота, вы соглашаетесь с политикой конфиденциальности.

Нажмите кнопку ниже, чтобы начать регистрацию.
"""

# Registration messages
REG_COURSE_QUESTION = "На каком курсе вы учитесь?"
REG_PROGRAM_QUESTION = "Введите название вашего направления обучения:"
REG_AGE_QUESTION = "Введите ваш возраст:"
REG_NAME_QUESTION = "Как вас зовут?"
REG_DESCRIPTION_QUESTION = "Напишите краткое описание о себе (до 500 символов):"
REG_PHOTO_QUESTION = "Отправьте ваше фото или продолжите без фото:"

# Validation errors
ERROR_INVALID_AGE = "❌ Пожалуйста, введите корректный возраст (от 16 до 100 лет)."
ERROR_INVALID_DESCRIPTION = "❌ Описание слишком длинное. Максимум 500 символов."
ERROR_INVALID_PHOTO = "❌ Пожалуйста, отправьте фото."
ERROR_INVALID_INPUT = "❌ Некорректный ввод. Попробуйте снова."

# Registration complete
REG_COMPLETE = """
✅ Регистрация завершена!

Вы можете сразу начать поиск или пройти верификацию для повышения доверия.

Ваш профиль:
"""

# Profile messages
PROFILE_TEMPLATE = """
👤 Имя: {name}
📚 Курс: {course}
🎓 Направление: {program}
🎂 Возраст: {age}
📝 О себе: {description}
🎭 Интересы: {events}
{verification_status}
"""

VERIFICATION_STATUS_NOT_VERIFIED = "⚠️ Профиль не верифицирован"
VERIFICATION_STATUS_PENDING = "⏳ Проверка на рассмотрении"
VERIFICATION_STATUS_VERIFIED = "✅ Профиль верифицирован"
VERIFICATION_STATUS_DENIED = "❌ Верификация отклонена. Повторите попытку."

# Verification messages
VERIFY_SEND_ID = "Отправьте фото вашего студенческого билета для верификации:"
VERIFY_SUBMITTED = "✅ Фото отправлено на проверку! Ожидайте подтверждения администрации."
VERIFY_APPROVED = "🎉 Ваш профиль верифицирован! Теперь вы можете начать поиск."
VERIFY_DENIED = "❌ Ваша верификация отклонена. Попробуйте отправить другое фото студенческого билета."

# Edit profile messages
EDIT_PROFILE_CHOOSE = "Выберите, что хотите изменить:"
EDIT_COMPLETE = "✅ Профиль обновлен!"

# Events selection
EVENTS_CHOOSE = "Выберите интересующие вас типы мероприятий (можно выбрать несколько):"
EVENTS_SELECTED = "✅ Ваши интересы сохранены!"

# Matching messages
MATCHING_NO_USERS = "😔 К сожалению, больше профилей нет. Попробуйте позже!"
MATCHING_PROFILE = "Профиль пользователя:"
MATCH_NOTIFICATION = """
🎉 У вас новое совпадение!

Вы понравились друг другу с пользователем {name}.
Telegram: @{username}

Напишите им!
"""

# Admin messages
ADMIN_NEW_VERIFICATION = """
🔔 Новая заявка на верификацию

ID пользователя: {user_id}
"""

ADMIN_VERIFICATION_APPROVED = "✅ Верификация подтверждена администратором {admin_name}"
ADMIN_VERIFICATION_DENIED = "❌ Верификация отклонена администратором {admin_name}"
ADMIN_USER_BANNED = "🚫 Пользователь заблокирован администратором {admin_name}"

# Button texts
BTN_BEGIN_REGISTRATION = "Начать регистрацию"
BTN_SKIP_PHOTO = "Пока продолжить без фото"
BTN_VIEW_PROFILE = "Посмотреть профиль"
BTN_EDIT_PROFILE = "Редактировать профиль"
BTN_VERIFY_PROFILE = "Верифицировать профиль (опционально)"
BTN_CHOOSE_EVENTS = "Выбрать мероприятия"
BTN_BEGIN_SEARCH = "Начать поиск"
BTN_NEXT = "Далее ➡️"
BTN_PREVIOUS = "⬅️ Назад"
BTN_LIKE = "❤️ Нравится"
BTN_DISLIKE = "👎 Не нравится"
BTN_CANCEL = "Отменить"

# Admin button texts
BTN_ADMIN_APPROVE = "✅ Подтвердить"
BTN_ADMIN_DENY = "❌ Отклонить"
BTN_ADMIN_BAN = "🚫 Заблокировать"

# Event types
EVENT_TYPES = [
    "Кино",
    "Музей",
    "Театр",
    "Концерт",
    "Спорт",
    "Выставка",
    "Кафе/Рестораны",
    "Активный отдых"
]

# Course options
COURSES = ["1-ый курс", "2-ой курс", "3-ий курс", "4-ый курс"]

# Cancel message
CANCEL_MESSAGE = "❌ Действие отменено. Введите /start для начала."
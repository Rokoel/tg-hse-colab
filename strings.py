# All user-facing strings for the bot

# Registration messages
WELCOME_MESSAGE = """
Привет! Я – твой карманный помощник для поиска компании. Хочешь сходить на концерт или театра с кем-то, посмотреть новый фильм или сделай крутой проект, но все твои друзья и одногруппники заняты? Не беда! Я помогу тебе решить эту проблему и найти не просто случайных людей, а тех, с кем будет действительно интересно — и в зале, и потом, в фойе или в баре, когда захочется обсудить, что это было. 😉

Давай попробуем? Но прежде, чем начать, прочти пожалуйста политику конфиденциальности. Продолжая, ты соглашаешься с ней.
"""
REG_NAME_QUESTION = "А теперь скажи, пожалуйста, как тебя зовут:"
REG_AGE_QUESTION = "{name} — отличное имя! Рад познакомиться. Сколько тебе лет?"
REG_DESCRIPTION_QUESTION = "Расскажи о себе 😊 (c какого ты курса и факультета, чем увлекаешься и так далее, максимум 500 символов):"
REG_COURSE_QUESTION = "На каком курсе ты учишься?"
REG_PROGRAM_QUESTION = "Введи название своего направления обучения:"
REG_PHOTO_QUESTION = "Отправь свое фото или продолжи без него:"

EDIT_AGE_QUESTION = "Сколько тебе лет?"
EDIT_NAME_QUESTION = "Как тебя зовут?"

# Validation errors
ERROR_INVALID_AGE = "❌ Пожалуйста, введи корректный возраст (от 16 до 100 лет)."
ERROR_INVALID_DESCRIPTION = "❌ Описание слишком длинное. Максимум 500 символов."
ERROR_INVALID_PHOTO = "❌ Пожалуйста, отправь фото."
ERROR_INVALID_INPUT = "❌ Некорректный ввод. Попробуй снова."

# Registration complete
REG_COMPLETE = """
✅ Регистрация завершена!

Ты можешь сразу начать поиск или пройти верификацию для того, чтобы быть выше при поиске.

Твой профиль:
"""
REG_COMPLETE_CHOOSE_ACTION = "Супер! Ну что, {name}, чем хочешь заняться?"

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
VERIFICATION_MESSAGE_PENDING = "⏳ Твоя заявка на верификацию на рассмотрении. Пожалуйста, подожди решения администрации."
VERIFICATION_STATUS_VERIFIED = "✅ Профиль верифицирован"
VERIFICATION_STATUS_DENIED = "❌ Верификация отклонена. Пожалуйста, попробуй еще раз."
USER_ALREADY_VERIFIED = "✅ Твой профиль уже верифицирован."

# Verification messages
VERIFY_SEND_ID = "Отправь фото своего студенческого билета для верификации:"
VERIFY_SUBMITTED = "✅ Фото отправлено на проверку! Ожидай подтверждения администрации."
VERIFY_APPROVED = "🎉 Твой профиль верифицирован! Теперь твой профиль будет иметь приоритет при поиске."
VERIFY_DENIED = "❌ Твоя верификация отклонена. Попробуй отправить другое фото студенческого билета."

# Edit profile messages
EDIT_PROFILE_CHOOSE = "Выбери, что хочешь изменить:"
EDIT_COMPLETE = "✅ Профиль обновлен!"

# Events selection
EVENTS_CHOOSE = "Выбери интересующие тебя типы мероприятий (можно выбрать несколько):"
EVENTS_SELECTED = "✅ Твои интересы сохранены!"

# Matching messages
MATCHING_NO_USERS = "😔 К сожалению, больше профилей нет. Попробуй позже!"
MATCHING_PROFILE = "Профиль пользователя:"
MATCH_NOTIFICATION = """
🎉 У тебя новый мэтч!

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
BTN_BEGIN_REGISTRATION = "Готово!"
BTN_SKIP_PHOTO = "Пока продолжить без фото"
BTN_VIEW_PROFILE = "Посмотреть профиль"
BTN_EDIT_PROFILE = "Редактировать профиль"
BTN_VERIFY_PROFILE = "Верифицировать профиль (опционально)"
BTN_RETRY_VERIFICATION = "❌ Повторить верификацию"
BTN_ALREADY_VERIFIED = "✅ Верифицирован"
BTN_VERIFICATION_PENDING = "⏳ Проверка"
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
    "Выставка",
    "Кафе/Рестораны",
    "Активный отдых",
    "Коворкинг",
    "Создание проектов",
]

# Course options
COURSES = ["1-ый курс", "2-ой курс", "3-ий курс", "4-ый курс"]

# Cancel message
CANCEL_MESSAGE = "❌ Действие отменено. Введи /start для начала."

# Other messages
USER_BLOCKED_MESSAGE = "🚫 Ты заблокирован и не можешь использовать бота. Если ты считаешь, что это ошибка, обратись к администраторам для разблокировки."
USER_ALREADY_REGISTERED = "Ты уже зарегистрирован! Используй главное меню для навигации."
PROFILE_NOT_FOUND = "Профиль не найден. Используй /start для начала регистрации."
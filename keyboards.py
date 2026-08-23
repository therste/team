from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

class PremiumButton(InlineKeyboardButton):
    def __init__(self, text: str, emoji_id: str = None, callback_data: str = None, url: str = None, style: str = "default"):
        super().__init__(text=text, callback_data=callback_data, url=url, icon_custom_emoji_id=emoji_id)
        self.style = style

def get_start_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        PremiumButton(text="Я готов", emoji_id="6041720006973067267", callback_data="success", style="danger"), 
        PremiumButton(text="Я не готов", emoji_id="5994368422031397063", callback_data="danger", style="danger")
    )
    return builder.as_markup()

def get_question3_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(PremiumButton(text="Я новичок.", emoji_id="5895669571058142797", url="https://t.me/vabupa", style="danger"))
    builder.row(PremiumButton(text="Есть непонятные темы.", emoji_id="6043960760130868895", callback_data="q3_normal", style="danger"))
    builder.row(PremiumButton(text="Мне всё понятно.", emoji_id="5773677501825945508", callback_data="q3_success", style="danger"))
    return builder.as_markup()

def get_final_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(PremiumButton(
        text="Проверить статус заявки", 
        emoji_id="6028435952299413210", 
        callback_data="check_status", 
        style="danger"
    ))
    return builder.as_markup()

def get_admin_keyboard(user_id: int, app_number: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        PremiumButton(
            text="Принять", 
            emoji_id="6041720006973067267", 
            callback_data=f"success_accept_{user_id}_{app_number}", 
            style="danger"
        ),
        PremiumButton(
            text="Отклонить", 
            emoji_id="6041716699848249286", 
            callback_data=f"danger_decline_{user_id}_{app_number}", 
            style="danger"
        )
    )
    return builder.as_markup()

def get_accepted_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(PremiumButton(
        text="Главное меню", 
        emoji_id="6041933986538721961", 
        callback_data="main_menu", 
        style="danger"
    ))
    return builder.as_markup()

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    # Первый ряд: Профиль | Заявка на выплату
    builder.row(
        PremiumButton(
            text="Профиль", 
            emoji_id="6037083366438737901", 
            callback_data="profile", 
            style="danger"
        ),
        PremiumButton(
            text="Заявка на выплату", 
            emoji_id="5904359114531675993", 
            callback_data="payout", 
            style="danger"
        )
    )
    
    # Второй ряд: Рефка 10% | Парсер
    builder.row(
        PremiumButton(
            text="Рефка 10%", 
            emoji_id="6028171274939797252", 
            callback_data="traffic", 
            style="danger"
        ),
        PremiumButton(
            text="Парсер", 
            emoji_id="6030400221232501136", 
            url="https://t.me/vabupa", 
            style="danger"
        )
    )
    
    # Третий ряд: Чат | Боты
    builder.row(
        PremiumButton(
            text="Чат", 
            emoji_id="6041716699848249286",
            url="https://t.me/+zApO7O3oEpJkMjQx", 
            style="danger"
        ),
        PremiumButton(
            text="Боты", 
            emoji_id="6041716699848249286",
            url="https://t.me/otcforjob", 
            style="danger"
        )
    )
    
    # Четвёртый ряд: Связаться с владельцем
    builder.row(
        PremiumButton(
            text="Связаться с владельцем", 
            emoji_id="6041716699848249286",
            url="https://t.me/vabupa", 
            style="danger"
        )
    )
    
    return builder.as_markup()

def get_profile_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(PremiumButton(
        text="TON адрес", 
        emoji_id="6042069608721027027", 
        callback_data="ton_address", 
        style="danger"
    ))
    builder.row(PremiumButton(
        text="История", 
        emoji_id="5850317551090800862", 
        callback_data="history", 
        style="danger"
    ))
    builder.row(PremiumButton(
        text="Главное меню", 
        emoji_id="6041933986538721961", 
        callback_data="main_menu", 
        style="danger"
    ))
    return builder.as_markup()

def get_ton_address_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(PremiumButton(
        text="Добавить", 
        emoji_id="5258108352008823107", 
        callback_data="ton_add", 
        style="danger"
    ))
    builder.row(PremiumButton(
        text="Назад", 
        emoji_id="6041933986538721961", 
        callback_data="ton_back", 
        style="danger"
    ))
    return builder.as_markup()

def get_ton_address_list_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(PremiumButton(
        text="Добавить", 
        emoji_id="5258108352008823107", 
        callback_data="ton_add", 
        style="danger"
    ))
    builder.row(PremiumButton(
        text="Назад", 
        emoji_id="6041933986538721961", 
        callback_data="ton_back", 
        style="danger"
    ))
    return builder.as_markup()

def get_traffic_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(PremiumButton(
        text="Получить ссылку", 
        emoji_id="6028171274939797252", 
        callback_data="get_link", 
        style="danger"
    ))
    builder.row(PremiumButton(
        text="Главное меню", 
        emoji_id="6041933986538721961", 
        callback_data="main_menu", 
        style="danger"
    ))
    return builder.as_markup()

def get_traffic_link_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(PremiumButton(
        text="Главное меню", 
        emoji_id="6041933986538721961", 
        callback_data="main_menu", 
        style="danger"
    ))
    return builder.as_markup()

def get_payout_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(PremiumButton(
        text="Главное меню", 
        emoji_id="6041933986538721961", 
        callback_data="main_menu", 
        style="danger"
    ))
    return builder.as_markup()

def get_payout_admin_keyboard(user_id: int, payout_number: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        PremiumButton(
            text="Принять", 
            emoji_id="6041720006973067267", 
            callback_data=f"success_payout_{user_id}_{payout_number}", 
            style="danger"
        ),
        PremiumButton(
            text="Отклонить", 
            emoji_id="6041716699848249286", 
            callback_data=f"danger_payout_{user_id}_{payout_number}", 
            style="danger"
        )
    )
    return builder.as_markup()

def get_payout_screenshot_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(PremiumButton(
        text="Далее", 
        emoji_id="5881806211195605908", 
        callback_data="payout_next", 
        style="danger"
    ))
    return builder.as_markup()
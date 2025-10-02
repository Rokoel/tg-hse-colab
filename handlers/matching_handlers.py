from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
import database as db
import strings
import keyboards as kb
import utils
from states import MatchingStates

router = Router()


@router.message(F.text == strings.BTN_BEGIN_SEARCH)
async def begin_search(message: Message, state: FSMContext):
    """Begin searching for matches"""
    user = db.get_user(message.from_user.id)
    if not user:
        return
    
    # Check if verified
    if user['verification_status'] != 'verified':
        await message.answer("Сначала необходимо пройти верификацию!")
        return
    
    # Get potential matches
    potential_matches = db.get_potential_matches(message.from_user.id)
    
    if not potential_matches:
        await message.answer(
            strings.MATCHING_NO_USERS,
            reply_markup=kb.get_main_menu_keyboard(user['verification_status'])
        )
        return
    
    # Store matches in state
    await state.update_data(
        matches=potential_matches,
        current_index=0
    )
    await state.set_state(MatchingStates.browsing)
    
    # Show first profile
    await show_profile_at_index(message, state, 0)


@router.message(MatchingStates.browsing, F.text == strings.BTN_NEXT)
async def next_profile(message: Message, state: FSMContext):
    """Show next profile"""
    data = await state.get_data()
    current_index = data.get('current_index', 0)
    matches = data.get('matches', [])
    
    if current_index + 1 < len(matches):
        new_index = current_index + 1
        await state.update_data(current_index=new_index)
        await show_profile_at_index(message, state, new_index)
    else:
        await message.answer(strings.MATCHING_NO_USERS)


@router.message(MatchingStates.browsing, F.text == strings.BTN_PREVIOUS)
async def previous_profile(message: Message, state: FSMContext):
    """Show previous profile"""
    data = await state.get_data()
    current_index = data.get('current_index', 0)
    
    if current_index > 0:
        new_index = current_index - 1
        await state.update_data(current_index=new_index)
        await show_profile_at_index(message, state, new_index)


@router.message(MatchingStates.browsing, F.text == strings.BTN_LIKE)
async def like_profile(message: Message, state: FSMContext):
    """Like current profile"""
    data = await state.get_data()
    current_index = data.get('current_index', 0)
    matches = data.get('matches', [])
    
    if current_index >= len(matches):
        return
    
    liked_user = matches[current_index]
    
    # Add like and check for match
    is_match = db.add_like(message.from_user.id, liked_user['user_id'])
    
    if is_match:
        # Notify both users about the match
        await notify_match(message, liked_user)
    
    # Move to next profile
    if current_index + 1 < len(matches):
        new_index = current_index + 1
        await state.update_data(current_index=new_index)
        await show_profile_at_index(message, state, new_index)
    else:
        user = db.get_user(message.from_user.id)
        await message.answer(
            strings.MATCHING_NO_USERS,
            reply_markup=kb.get_main_menu_keyboard(user['verification_status'])
        )
        await state.clear()


@router.message(MatchingStates.browsing, F.text == strings.BTN_DISLIKE)
async def dislike_profile(message: Message, state: FSMContext):
    """Dislike current profile"""
    data = await state.get_data()
    current_index = data.get('current_index', 0)
    matches = data.get('matches', [])
    
    if current_index >= len(matches):
        return
    
    disliked_user = matches[current_index]
    
    # Add dislike
    db.add_dislike(message.from_user.id, disliked_user['user_id'])
    
    # Move to next profile
    if current_index + 1 < len(matches):
        new_index = current_index + 1
        await state.update_data(current_index=new_index)
        await show_profile_at_index(message, state, new_index)
    else:
        user = db.get_user(message.from_user.id)
        await message.answer(
            strings.MATCHING_NO_USERS,
            reply_markup=kb.get_main_menu_keyboard(user['verification_status'])
        )
        await state.clear()


@router.message(MatchingStates.browsing, F.text == strings.BTN_CANCEL)
async def cancel_search(message: Message, state: FSMContext):
    """Cancel search and return to main menu"""
    user = db.get_user(message.from_user.id)
    await state.clear()
    await message.answer(
        "Поиск остановлен.",
        reply_markup=kb.get_main_menu_keyboard(user['verification_status'])
    )


async def show_profile_at_index(message: Message, state: FSMContext, index: int):
    """Show profile at specific index"""
    data = await state.get_data()
    matches = data.get('matches', [])
    
    if index >= len(matches):
        return
    
    profile = matches[index]
    profile_text = strings.MATCHING_PROFILE + "\n\n" + utils.format_profile(profile, show_verification=False)
    
    # Determine which navigation buttons to show
    has_previous = index > 0
    has_next = index < len(matches) - 1
    
    await utils.send_profile_with_photo(message, profile, profile_text)
    await message.answer(
        f"Профиль {index + 1} из {len(matches)}",
        reply_markup=kb.get_matching_keyboard(has_previous, has_next)
    )


async def notify_match(message: Message, matched_user: dict):
    """Notify both users about a match"""
    # Notify current user
    current_user = db.get_user(message.from_user.id)
    
    matched_username = matched_user['username'] if matched_user['username'] else "нет username"
    await message.answer(
        strings.MATCH_NOTIFICATION.format(
            name=matched_user['name'],
            username=matched_username
        )
    )
    
    # Notify matched user
    current_username = current_user['username'] if current_user['username'] else "нет username"
    try:
        await message.bot.send_message(
            chat_id=matched_user['user_id'],
            text=strings.MATCH_NOTIFICATION.format(
                name=current_user['name'],
                username=current_username
            )
        )
    except Exception:
        pass  # User might have blocked the bot
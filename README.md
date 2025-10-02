# Telegram Student Networking Bot

A Telegram bot for helping students network and connect with each other based on shared interests and characteristics.

## Features

- **User Registration**: Multi-step registration process collecting course, program, age, name, description, and optional photo
- **Profile Management**: View and edit profile information
- **Event Interests**: Select types of events users are interested in (Cinema, Museums, Theatre, etc.)
- **Verification System**: Admin-moderated verification using student ID photos
- **Smart Matching**: Algorithm that matches users based on:
  - Event interests (primary)
  - Study program similarity (secondary)
  - Age proximity (tertiary)
- **Like/Dislike System**: Browse verified users and like/dislike profiles
- **Match Notifications**: Both users are notified when they like each other
- **Admin Panel**: Approve, deny, or ban users through an admin group chat

## Project Structure

```
telegram-student-bot/
├── main.py                 # Main bot application
├── config.py              # Configuration and settings
├── strings.py             # All user-facing text messages
├── states.py              # FSM states for conversations
├── database.py            # Database operations
├── keyboards.py           # Keyboard layouts
├── utils.py               # Utility functions
├── handlers/
│   ├── user_handlers.py         # Registration handlers
│   ├── profile_handlers.py      # Profile management
│   ├── verification_handlers.py # Verification process
│   ├── matching_handlers.py     # Matching system
│   └── admin_handlers.py        # Admin operations
├── photos/                # User profile photos
├── student_ids/          # Student ID photos (temporary)
├── privacy_policy.pdf    # Privacy policy document
├── bot_database.db       # SQLite database
├── .env                  # Environment variables (create from .env.example)
├── .env.example          # Template for environment variables
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Installation

### 1. Prerequisites

- Python 3.9 or higher
- A Telegram Bot Token (get it from [@BotFather](https://t.me/BotFather))
- An admin group chat ID

### 2. Clone or Download

Download all the project files into a directory.

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your bot token:
   ```
   BOT_TOKEN=your_bot_token_here
   ADMIN_CHAT_ID=your_admin_chat_id_here
   ```

3. To get your admin chat ID:
   - Create a group chat
   - Add your bot to the group
   - Send a message in the group
   - Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Look for `"chat":{"id":-1001234567890}` in the response
   - Use that negative number as your ADMIN_CHAT_ID

### 5. Privacy Policy

Place a `privacy_policy.pdf` file in the root directory. This will be sent to users when they start registration.

### 6. Run the Bot

```bash
python main.py
```

## Usage

### For Users

1. **Start**: `/start` - Begin registration or return to main menu
2. **Register**: Complete the step-by-step registration form
3. **View Profile**: See your profile as others see it
4. **Edit Profile**: Update any field of your profile
5. **Choose Events**: Select event types you're interested in
6. **Verify**: Submit student ID photo for verification
7. **Search**: Once verified, browse other verified users
8. **Like/Dislike**: Swipe through profiles
9. **Match**: Get notified when someone likes you back

### For Admins

In the admin group chat, the bot sends verification requests with:
- User profile information
- Profile photo (if provided)
- Student ID photo

Admins can:
- ✅ **Approve**: Verify the user
- ❌ **Deny**: Reject verification (user can retry)
- 🚫 **Ban**: Permanently ban user from the bot

## Database Schema

### users
- `user_id`: Telegram user ID (PRIMARY KEY)
- `username`: Telegram username
- `course`: Current course (1-4)
- `program`: Study program
- `age`: User age
- `name`: Display name
- `description`: Profile description
- `photo_id`: Telegram file ID for profile photo
- `events`: JSON array of selected events
- `verification_status`: not_verified, pending, verified, or denied
- `student_id_photo`: Telegram file ID for student ID
- `is_banned`: Ban status
- `created_at`: Registration timestamp

### likes
- Tracks user likes
- `from_user_id` → `to_user_id`

### dislikes
- Tracks user dislikes
- `from_user_id` → `to_user_id`

### matches
- Stores mutual likes
- `user1_id` ↔ `user2_id`

## Photo Management

The bot automatically manages photos:
- **Profile photos**: Stored in `photos/` directory
- **Student IDs**: Stored in `student_ids/` directory
- **Cleanup**: Old photos are deleted when:
  - User updates their photo
  - Verification is approved/denied (student ID deleted)
  - User is banned

## Matching Algorithm

Users are sorted by compatibility score:

1. **Event Interests** (10 points per match): Primary matching factor
2. **Program Similarity** (5 points exact, 2 points partial): Secondary factor
3. **Age Proximity** (up to 5 points): Tertiary factor

## Commands

- `/start` - Start the bot / return to main menu
- `/cancel` - Cancel current operation

## Security Features

- User ban system
- Admin-only verification approval
- Automatic photo cleanup
- Privacy policy agreement

## Customization

All user-facing text is in `strings.py`. You can easily translate or modify:
- Messages
- Button texts
- Error messages
- Notification texts

Event types can be modified in `strings.py` under `EVENT_TYPES`.

## Troubleshooting

### Bot doesn't respond
- Check if bot token is correct in `.env`
- Verify bot is running: `python main.py`
- Check logs for errors

### Admin commands don't work
- Verify ADMIN_CHAT_ID is correct
- Make sure bot is admin in the group
- ID must include the minus sign: `-1001234567890`

### Photos not saving
- Check folder permissions for `photos/` and `student_ids/`
- Ensure folders exist (bot creates them automatically)

### Database errors
- Delete `bot_database.db` and restart bot to recreate tables
- Check Python SQLite3 is available

## Development

Built with:
- **aiogram 3.x**: Modern Telegram Bot framework
- **SQLite**: Lightweight database
- **FSM**: Finite State Machine for conversation flows

## License

This project is provided as-is for educational purposes.

## Support

For issues or questions, please check:
- Aiogram documentation: https://docs.aiogram.dev/
- Telegram Bot API: https://core.telegram.org/bots/api
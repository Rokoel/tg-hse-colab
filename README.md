# Telegram Student Networking Bot

A Telegram bot for helping university students meet people with similar interests.

The bot was deployed for real users and at one point had **more than 100 registered users**. It supports profile creation, interest-based discovery, likes and matches, optional student verification, reports and moderation.

Built with **Python, aiogram 3 and SQLite**.

## Features

- Multi-step registration using aiogram FSM
- User profiles with name, age, study program, course, description and optional photo
- Event and activity interests
- Profile editing
- Browse and rank potential matches
- Likes, dislikes and mutual matches
- Notifications when another user likes or matches with you
- A separate view for people who already liked you
- Optional student verification through an admin group
- User reports and admin bans
- Automatic cleanup of verification photos after review

### Matching

Profiles are ranked using a simple compatibility score based on:

1. verification status,
2. shared event interests,
3. similarity of study programs,
4. age difference.

Users who have already been liked or disliked are excluded from future search results.

## Project structure

```text
tg_hse_colab/
├── main.py
├── config.py
├── database.py
├── keyboards.py
├── states.py
├── strings.py
├── utils.py
├── handlers/
│   ├── user_handlers.py
│   ├── profile_handlers.py
│   ├── verification_handlers.py
│   ├── matching_handlers.py
│   └── admin_handlers.py
├── .env.example
├── requirements.txt
└── README.md
```

Runtime data is deliberately excluded from Git. The SQLite database, uploaded profile photos, student-ID photos, environment variables and privacy-policy PDF stay local.

## Setup

Requires Python 3.9+ and a Telegram bot token.

Clone the repository and install dependencies:

```bash
git clone https://github.com/Rokoel/tg_hse_colab.git
cd tg_hse_colab
pip install -r requirements.txt
```

Create a local `.env` file from the example:

```bash
cp .env.example .env
```

Set:

```env
BOT_TOKEN=your_bot_token_here
ADMIN_CHAT_ID=your_admin_group_chat_id
```

The admin chat is used for verification requests and moderation actions.

The bot also expects a local `privacy_policy.pdf` in the project root. It is intentionally ignored by Git.

Run the bot with:

```bash
python main.py
```

The SQLite database and upload directories are created locally as needed.

## Database

The bot uses four main SQLite tables:

- `users` - profiles, interests, verification status and ban state
- `likes` - directed likes between users
- `dislikes` - profiles a user has skipped
- `matches` - mutual likes

The matching logic and database operations are implemented in `database.py`.

## Administration and privacy

Verification is optional. A user can submit a student-ID photo, which is forwarded to the configured admin group for approval or rejection. The stored reference is removed after the review.

Admins can approve or deny verification requests and ban users. Reported profiles are also handled through the admin workflow.

Secrets and runtime user data are excluded through `.gitignore`, including:

- `.env`
- SQLite databases
- `photos/`
- `student_ids/`
- `privacy_policy.pdf`

## Tech stack

- Python
- aiogram 3
- SQLite
- python-dotenv

User-facing text is kept separately in `strings.py`, while Telegram handlers are split by responsibility under `handlers/`.

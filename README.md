# Py Telegram Message Scheduler

A simple Python-based message scheduler for Telegram that lets you schedule messages to be sent at specific times using
the Telegram Bot API.

---

## Features

- Schedule messages to be sent to specific chats or groups.
- Supports recurring messages (daily, weekly, etc.).
- Easy to configure and customize.
- Utilizes the Telegram Bot API for seamless integration.

---

## Prerequisites

Before using this project, ensure you have:

1. Python 3. (due to use of Enums) or higher installed.
2. A Telegram bot token. You can create one using the [BotFather](https://core.telegram.org/bots#botfather) on Telegram.
3. Required Python libraries (install via `pip` as outlined below).

---

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/lbaumdev/py-telegram-message-scheduler.git
   cd py-telegram-message-scheduler
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file in the project root directory and add your bot token:
   ```env
   TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN_FROM_BOTFATHER
   TELEGRAM_BOT_OWNER_ID=YOUR_TELEGRAM_USER_ID
   ```

---

## Usage

1. Run the script:
   ```bash
   python main.py
   ```

2. Follow the prompts to:
    - Specify the chat or group ID.
    - Enter the message text.
    - Set the desired date and time for the message.

3. The bot will handle the rest and send your message at the scheduled time.

---

## Customization

You can customize the script to add new features, such as:

- Additional scheduling options (e.g., monthly messages).
- Improved user interfaces.
- Integration with external scheduling services.

Modify the code as needed and feel free to submit a pull request if you make improvements.

---

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add feature-name"
   ```
4. Push to your branch:
   ```bash
   git push origin feature-name
   ```
5. Open a pull request on GitHub.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Acknowledgments

- Thanks to [Telegram](https://core.telegram.org/bots/api) for providing an awesome Bot API.
- Inspired by the need for efficient message scheduling in Telegram workflows.

---

## Contact

For questions or suggestions, feel free to reach out or create an issue in the repository.

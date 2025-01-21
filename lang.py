locales = {
    "de": {
        "greeting": "Hallo!\n",
        "questions": "1. Wie lautet der Name deines Auftrags?\n2. Wähle eine Gruppe aus\n3. Wähle aus, wie oft deine Nachricht wiederholt werden soll (Zeit, zu der die Nachricht gesendet wird)\n4. Wie lautet dein Werbetext?\nSende /cancel, um das Gespräch zu beenden.\n\n",
        "question-1": "Gib einen benutzerdefinierten Namen für diesen Auftrag ein (z. B. Newsletter-Erinnerung)",
        "question-2": "Bitte wähle einen Chat aus, an den die Nachricht gesendet werden soll (Bot muss Mitglied sein):",
        "question-3": "Wann soll deine Nachricht gesendet werden? (Zeitplan)\n",
        "question-4": "Was ist die Nachricht, die du senden möchtest?",
        "no-chats-found": "Keine verfügbaren Chats in der Datenbank gefunden. Das Gespräch ist beendet.",
        "open-scheduler-web-app": "Öffne den Generator",
        "job-created": "Fantastisch. Der Auftrag ist nun registriert und bereit. Das Gespräch ist beendet.",
        "conversation-canceled-by-user": "Tschüss! Ich hoffe, wir können irgendwann wieder sprechen.",
        "command.create": "Erstellt einen geplanten Auftrag, um eine benutzerdefinierte Nachricht zu senden",
        "command.list": "Liste alle registrierten Aufträge auf",
        "command.help": "Erhalte eine Beschreibung der verfügbaren Befehle",
        "start-greeting-bot": "Hallo, ich kann Aufträge zum Senden geplanter Nachrichten erstellen. Verwende einen der aufgeführten Befehle.",
        "available-commands": "Verfügbare Befehle:",
        "registered-jobs": "Registrierte Aufträge: ",
        "no-jobs-registered": "Keine Aufträge registriert",
        "job.name": "Name",
        "job.schedule": "Zeitplan",
        "job.chat_id": "ChatID",
        "job.message": "Nachricht",
        "choose-job-for-deletion": "Bitte wähle einen Auftrag zum Löschen aus:",
        "job-deleted-successfully": "Auftrag erfolgreich gelöscht!"
    },
    "en": {
        "greeting": "Hi!\n",
        "questions": "1. What is the name of your job?\n2. Choose a group\n3. Choose how often your message should be repeated (time the message will be sent)\n4. What is your advertising text?\nSend /cancel to stop talking to me.\n\n",
        "question-1": "Enter a custom name for this job (e.g. newsletter reminder)",
        "question-2": "Please choose a chat to send the message to (bot must be a member):",
        "question-3": "When should your message be sent? (Schedule)\n",
        "question-4": "What is the message you would like to send?",
        "no-chats-found": "No available chats found in database. Conversation is over",
        "open-scheduler-web-app": "Open the Generator",
        "job-created": "Fantastic. The order is now registered and ready. The conversation is finished.",
        "conversation-canceled-by-user": "Bye! I hope we can talk again some day.",
        "command.create": "Creates a scheduled job to send a custom message",
        "command.list": "List all scheduled jobs",
        "command.help": "Get description of available commands",
        "start-greeting-bot": "Hello, I can create jobs for sending scheduled messages. Use one of the listed commands.",
        "available-commands": "Available commands:",
        "registered-jobs": "Registered jobs: ",
        "no-jobs-registered": "No jobs registered",
        "job.name": "Name",
        "job.schedule": "Schedule",
        "job.chat_id": "ChatID",
        "job.message": "Message",
        "choose-job-for-deletion": "Please choose a job to delete:",
        "job-deleted-successfully": "Job deleted successfully!"
    }
}
default_locale = "de"


def translate(key: str) -> str:
    translation = locales.get(default_locale).get(key)
    return translation or key

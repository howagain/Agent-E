import inspect
import os
from typing import Annotated
import traceback

from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError

from ae.core.playwright_manager import PlaywrightManager
from ae.core.skills.skill_registry import skill
from ae.core.skills.enter_text_using_selector import do_entertext
from ae.utils.logger import logger
from ae.utils.ui_messagetype import MessageType

@skill(description="Compose an email in Gmail without sending it.", name="compose_email_in_gmail")
async def compose_email(
    recipient: Annotated[str, "The email address of the recipient."],
    subject: Annotated[str, "The subject of the email."],
    body: Annotated[str, "The body content of the email."]
) -> Annotated[str, "Result message indicating success or failure."]:
    """
    Opens Gmail and composes an email without sending it.
    """
    logger.info(f"Starting compose_email function with recipient: {recipient}, subject: {subject}")

    browser_manager = PlaywrightManager(browser_type='chromium', headless=False)
    page = await browser_manager.get_current_page()
    if page is None:
        error_message = "Error: No active page found. OpenURL command opens a new page."
        logger.error(error_message)
        raise ValueError(error_message)

    function_name = inspect.currentframe().f_code.co_name

    try:
        await browser_manager.take_screenshots(f"{function_name}_start", page)
        # Navigate to Gmail if not already there
        if "mail.google.com" not in page.url:
            logger.info("Navigating to Gmail...")
            await page.goto('https://mail.google.com/', wait_until='networkidle')
            logger.info(f"Current URL after navigation: {page.url}")

        # Check if sign-in is required
    #      page.get_by_role("button", name="Next").click()
    # page.get_by_label("Enter your password").click()
    # page.get_by_label("Enter your password").fill(password)
    # page.get_by_label("Enter your password").press("Enter")
    # page.get_by_role("button", name="Compose").click()
    # page.get_by_label("To recipients").click()
    # page.get_by_label("To recipients").fill("phil@creativelaunch.io")
    # page.get_by_role("option", name="phil@creativelaunch.io phil@").click()
    # page.get_by_placeholder("Subject").click()
    # page.get_by_placeholder("Subject").fill("AI agents are the future!")
    # page.get_by_role("textbox", name="Message Body").click()
    # page.get_by_role("textbox", name="Message Body").fill("I just wanted to pass along that ai agents are the future!")
       
        
        
        sign_in_button = page.get_by_role("link", name="Sign in")
        if await sign_in_button.is_visible():
            logger.info("Sign-in button detected. Attempting to sign in...")
            email = os.environ.get('EMAIL')
            password = os.environ.get('PASSWORD')
            
            if not email or not password:
                raise ValueError("EMAIL or PASSWORD environment variables are not set.")

            await sign_in_button.click()

            # Enter email
            await page.get_by_label("Email or phone").fill(email)
            await page.get_by_role("button", name="Next").click()
            
            # Wait for password field and enter password
            await page.wait_for_selector('input[type="password"]', state='visible')
            password_field = page.get_by_label("Enter your password")
            await password_field.click()
            await password_field.fill(password)
            await password_field.press("Enter")
            
            # Wait for Gmail to load after sign-in
            await page.wait_for_url("https://mail.google.com/mail/u/0/", timeout=30000)
            logger.info("Successfully signed in to Gmail.")
        else:
            logger.info("No sign-in required. Proceeding with email composition.")

    
        # Click on the "Compose" button
        await page.get_by_role("button", name="Compose").click()
        
        # Wait for the compose window to appear
        # logger.info("Waiting for compose window to appear...")
        # await page.wait_for_selector('div[aria-label="New Message"]', state='visible', timeout=5000)

        # Use the do_compose_email function for the actual composition
        # await page.pause()
        await page.get_by_text("New Message", exact=True).wait_for(state='visible')
        logger.info("Calling do_compose_email function...")
        result = await do_compose_email(page, recipient, subject, body)

        if "Error" in result["summary_message"]:
            raise ValueError(result["detailed_message"])

        success_message = result["summary_message"]
        logger.info(success_message)
        await browser_manager.notify_user(success_message, message_type=MessageType.ACTION)

        await browser_manager.take_screenshots(f"{function_name}_end", page)

        return success_message

    except PlaywrightTimeoutError as e:
        error_message = f"Timeout error: {str(e)}. The page might be loading slowly or the element might not be present."
        logger.error(error_message)
        await browser_manager.notify_user(error_message, message_type=MessageType.ERROR)
        raise ValueError(error_message) from e

    except Exception as e:
        error_message = f"Failed to compose email. Error: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_message)
        await browser_manager.notify_user(error_message, message_type=MessageType.ERROR)
        raise ValueError(error_message) from e

async def do_compose_email(page: Page, recipient: str, subject: str, body: str):
    """
    Performs the email composition operation on the Gmail page.

    This function composes an email on the Gmail page by filling in the recipient,
    subject, and body fields.

    Args:
        page (Page): The Playwright Page object representing the browser tab with Gmail open.
        recipient (str): The email address of the recipient.
        subject (str): The subject of the email.
        body (str): The body content of the email.

    Returns:
        dict[str, str]: Explanation of the outcome of this operation represented as a dictionary 
                        with 'summary_message' and 'detailed_message'.

    Example:
        result = await do_compose_email(page, 'example@example.com', 'Test Subject', 'This is a test email.')

    Note:
        - This function assumes that the Gmail compose window is already open.
        - It uses Playwright's locator functions to interact with elements.
    """
    try:
        # Debug: Log the start of the function
        logger.debug(f"Starting do_compose_email with recipient: {recipient}, subject: {subject}")

        # Fill in recipient
        # logger.debug("Attempting to fill recipient")
        # Type in recipient directly as field is already focused
        # await page.keyboard.type(recipient)
        # logger.debug(f"Typed recipient: {recipient}")
        
        # Wait for and click the matching recipient suggestion
        # await page.get_by_role("option", name=recipient).click()
        # logger.debug("Selected recipient from suggestion")
        # Fill in recipient
        logger.debug("Attempting to fill recipient")
        await page.keyboard.type(recipient)
        await page.keyboard.press("Tab")
        logger.debug("Recipient filled and confirmed")

        # Fill in subject
        logger.debug("Attempting to fill subject")
        await page.keyboard.type(subject)
        await page.keyboard.press("Tab")
        logger.debug("Subject filled successfully")

        # Fill in email body
        logger.debug("Attempting to fill email body")
        await page.keyboard.type(body)
        logger.debug("Email body filled successfully")

        success_msg = f"Email composed successfully for {recipient}."
        logger.info(success_msg)
        return {"summary_message": success_msg, "detailed_message": f"{success_msg} Subject: '{subject}', Body: '{body[:50]}...'"}

    except Exception as e:
        error = f"Error composing email for {recipient}."
        logger.error(f"{error} Error details: {str(e)}")
        return {"summary_message": error, "detailed_message": f"{error} Error: {e}"}
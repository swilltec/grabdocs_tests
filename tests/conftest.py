import os
import re

import pytest
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()


@pytest.fixture(scope="session", autouse=True)
def base_url():
    return "https://app.grabdocs.com/"


@pytest.fixture(scope="session")
def email():
    return os.getenv("EMAIL")


@pytest.fixture(scope="session")
def member():
    return os.getenv("MEMBER")


@pytest.fixture(scope="session")
def member_name():
    return os.getenv("MEMBER_NAME")


@pytest.fixture(scope="session")
def password():
    return os.getenv("PASSWORD")


@pytest.fixture(scope="session")
def browser_context():
    """Launch a single browser for the test session."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=600)
        context = browser.new_context()
        yield context
        browser.close()


@pytest.fixture(scope="session")
def authenticated_context(browser_context, base_url, email, password):
    """Log in once per session and reuse the authenticated session."""
    page = browser_context.new_page()
    page.goto(f"{base_url}login")

    # Fill login form
    page.get_by_placeholder("Email").fill(email)
    page.get_by_placeholder("Password").fill(password)
    page.locator("div").filter(has_text=re.compile(r"^Remember me$")).click()

    page.get_by_role("button", name="Sign in").click()

    page.get_by_role("textbox", name="Enter 6-digit code").fill("335577")
    page.get_by_role("button", name="Verify Code").click()

    # Wait for dashboard to confirm successful login.
    page.wait_for_url(re.compile(r".*/upload"), timeout=90000)

    # Save authentication state
    storage_state_path = "logged_in.json"
    browser_context.storage_state(path=storage_state_path)
    page.close()

    # Create a new context with saved state
    new_context = browser_context.browser.new_context(storage_state=storage_state_path)
    yield new_context
    new_context.close()


@pytest.fixture(scope="session")
def member_context(browser_context, base_url, member, password):
    """Log in once per session and reuse the authenticated session for member."""
    page = browser_context.new_page()
    page.goto(f"{base_url}login")

    # Fill login form
    page.get_by_placeholder("Email").fill(member)
    page.get_by_placeholder("Password").fill(password)
    page.locator("div").filter(has_text=re.compile(r"^Remember me$")).click()

    page.get_by_role("button", name="Sign in").click()

    page.get_by_role("textbox", name="Enter 6-digit code").fill("335577")
    page.get_by_role("button", name="Verify Code").click()

    # Wait for dashboard to confirm successful login.
    page.wait_for_url(re.compile(r".*/upload"), timeout=90000)

    # Save authentication state
    storage_state_path = "logged_in_2.json"
    browser_context.storage_state(path=storage_state_path)
    page.close()

    # Create a new context with saved state
    new_context = browser_context.browser.new_context(storage_state=storage_state_path)
    yield new_context
    new_context.close()

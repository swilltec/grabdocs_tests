import re

from playwright.sync_api import Page, expect


FILE_NAME = "Grabdocs Test Plan"


def test_file_upload(authenticated_context, base_url):
    """
    Test Case: Upload a File

    Objective:
        Verify that a user can successfully upload a PDF file.

    Steps:
        1. Open the 'Upload' page using an authenticated session.
        2. Confirm that the 'Chat' heading is visible (indicating correct page).
        3. Verify that no files are uploaded initially (placeholder message shown).
        4. Upload a test file (e.g., 'Grabdocs Test Plan.pdf').
        5. Wait for the upload process to complete.
        6. Validate that the uploaded file appears in the list.

    Expected Result:
        The uploaded file should appear, and the "No documents uploaded yet" message should disappear.
    """
    page = authenticated_context.new_page()
    page.goto(f"{base_url}upload")

    # Ensure the upload page is loaded
    expect(page.get_by_role("heading", name="Chat")).to_be_visible()

    # Confirm initial state — no files present
    expect(page.get_by_text("No documents uploaded yet")).to_be_visible()

    # Upload a sample file
    page.set_input_files("input[type='file']", f"{FILE_NAME}.pdf")

    # Allow some time for the upload to complete
    page.wait_for_timeout(10000)

    # Verify that the uploaded file name appears
    expect(page.get_by_text(FILE_NAME)).to_be_visible(timeout=10000)

    page.close()


def test_file_download(authenticated_context, base_url):
    """
    Test Case: Download a File

    Objective:
        Verify that a user can download an uploaded file successfully.

    Steps:
        1. Open the 'Upload' page with an authenticated session.
        2. Ensure that the test file ('Grabdocs Test Plan.pdf') is visible.
        3. Expand the file item action menu.
        4. Click the 'Download' button.
        5. Wait for the browser to trigger a file download event.

    Expected Result:
        The download should start successfully (Playwright detects the download event).
    """
    page = authenticated_context.new_page()
    page.goto(f"{base_url}upload")

    # Validate correct page load
    expect(page.get_by_role("heading", name="Chat")).to_be_visible()

    # Ensure uploaded file is visible
    expect(page.get_by_text(FILE_NAME)).to_be_visible()

    # Open file action menu
    page.get_by_role("listitem").get_by_role("button").click()

    # Expect browser download event when button clicked
    with page.expect_download() as download_info:
        page.get_by_role("button", name="Download").click()

    download = download_info.value
    assert download.suggested_filename.endswith(
        ".pdf"
    ), "Downloaded file should be a PDF"

    page.close()


def test_file_delete(authenticated_context, base_url):
    """
    Test Case: Delete a File

    Objective:
        Verify that a user can delete a previously uploaded file.

    Steps:
        1. Navigate to the 'Upload' page using an authenticated session.
        2. Confirm that the uploaded file is visible.
        3. Open the file action menu.
        4. Click 'Delete' and accept the confirmation dialog.
        5. Wait for the success alert to appear.
        6. Confirm that the page displays the 'No documents uploaded yet' message again.

    Expected Result:
        The success alert message appears, and the file entry disappears from the list.
    """
    page = authenticated_context.new_page()
    page.goto(f"{base_url}upload")

    # Ensure the upload page is visible
    expect(page.get_by_role("heading", name="Chat")).to_be_visible()

    # Verify that the uploaded file is available
    expect(page.get_by_text(FILE_NAME)).to_be_visible()

    # Open file action menu
    page.get_by_role("listitem").get_by_role("button").click()

    # Accept the delete confirmation dialog
    page.once("dialog", lambda dialog: dialog.accept())

    # Click delete button
    page.get_by_role("button", name="Delete").click()

    # Confirm success alert appears
    alert = page.get_by_role("alert").filter(has_text="successfully")
    expect(alert).to_be_visible(timeout=8000)

    # Verify that the placeholder message is now visible again
    expect(page.get_by_text("No documents uploaded yet")).to_be_visible()

    page.close()


def test_bookmarks(authenticated_context, base_url):
    """
    Test Case: Toggle 'Bookmarks' Panel

    Objective:
        Verify that a user can show and hide the 'Bookmarks' sidebar.

    Steps:
        1. Open the 'Upload' page.
        2. Confirm that the 'Bookmarks' section is hidden initially.
        3. Click 'Show Bookmarks' to display it.
        4. Confirm the section becomes visible, along with the 'Hide Bookmarks' button.
        5. Click 'Hide Bookmarks' and verify that the section is hidden again.

    Expected Result:
        The 'Bookmarks' section toggles visibility correctly.
    """
    page = authenticated_context.new_page()
    page.goto(f"{base_url}upload")

    # Validate initial hidden state
    expect(page.get_by_role("heading", name="Bookmarks")).not_to_be_visible()

    # Show bookmarks
    page.get_by_role("button", name="Show Bookmarks").click()
    page.wait_for_timeout(1000)

    # Confirm bookmarks section visible
    expect(page.get_by_role("heading", name="Bookmarks")).to_be_visible()
    expect(page.get_by_role("button", name="Hide Bookmarks")).to_be_visible()

    # Hide bookmarks again
    page.get_by_role("button", name="Hide Bookmarks").click()
    expect(page.get_by_role("heading", name="Bookmarks")).not_to_be_visible()

    page.close()


def test_reference(authenticated_context, base_url):
    """
    Test Case: Toggle 'References' Panel

    Objective:
        Verify that the user can show or hide the 'References' section on the upload page.

    Steps:
        1. Open the 'Upload' page.
        2. Confirm that the 'References' header is initially hidden.
        3. Click 'Show References' button.
        4. Verify the section and its 'Hide References' button appear.
        5. Click 'Hide References' and confirm the section disappears.

    Expected Result:
        The 'References' section toggles visibility correctly.
    """
    page = authenticated_context.new_page()
    page.goto(f"{base_url}upload")

    # Check initial hidden state
    expect(page.get_by_role("heading", name="References")).not_to_be_visible()

    # Show references section
    page.get_by_role("button", name="Show References").click()
    page.wait_for_timeout(1000)

    expect(page.get_by_role("heading", name="References")).to_be_visible()
    expect(page.get_by_role("button", name="Hide References")).to_be_visible()

    # Hide references section again
    page.get_by_role("button", name="Hide References").click()
    expect(page.get_by_role("heading", name="References")).not_to_be_visible()

    page.close()


def test_history(authenticated_context, base_url):
    """
    Test Case: Toggle 'Chat History' Panel

    Objective:
        Verify that the user can open and close the Chat History section.

    Steps:
        1. Open the 'Upload' page.
        2. Confirm that 'Chat History' is initially hidden.
        3. Click 'Show History' to expand it.
        4. Confirm that the panel and 'Hide History' button appear.
        5. Click 'Hide History' to collapse the panel.

    Expected Result:
        The 'Chat History' section toggles visibility correctly.
    """
    page = authenticated_context.new_page()
    page.goto(f"{base_url}upload")

    # Validate initial hidden state
    expect(page.get_by_role("heading", name="Chat History")).not_to_be_visible()

    # Show chat history section
    page.get_by_role("button", name="Show History").click()
    page.wait_for_timeout(1000)

    # Confirm visibility
    expect(page.get_by_role("heading", name="Chat History")).to_be_visible()
    expect(page.get_by_role("button", name="Hide History")).to_be_visible()

    # Hide history panel again
    page.get_by_role("button", name="Hide History").click()
    expect(page.get_by_role("heading", name="Chat History")).not_to_be_visible()

    page.close()


def test_chat(authenticated_context, base_url):
    """
    Test Case: Send and Receive a Chat Message

    Objective:
        Verify that the chat interface sends a message and displays a response.

    Steps:
        1. Open the 'Upload' page via an authenticated session.
        2. Confirm that there are no chat responses initially.
        3. Enter a test question into the chat input.
        4. Send the message.
        5. Wait for a response to appear on-screen.
        6. Validate that the response (identified as 'GD') appears.

    Expected Result:
        After sending a message, the system-generated 'GD' response is displayed.
    """
    page = authenticated_context.new_page()
    page.goto(f"{base_url}upload")

    # Confirm that no earlier messages (GD responses) exist
    expect(page.get_by_text("GD")).not_to_be_visible()

    # Type and send a chat message
    page.get_by_role("textbox", name=re.compile("Ask anything", re.I)).fill(
        "Why is file upload failing?"
    )
    page.get_by_role("button", name=re.compile("Send message", re.I)).click()

    # Wait briefly for a system response
    page.wait_for_timeout(1000)

    # Verify the presence of a response (GD)
    expect(page.get_by_text("GD")).to_be_visible()

    page.close()

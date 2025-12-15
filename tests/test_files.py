from playwright.sync_api import expect

FILE_NAME = "Grabdocs Test Plan"


from playwright.sync_api import expect


def test_file_upload(authenticated_context, base_url):
    """
    Test Case: Upload a File

    Objective:
        Verify that a user can successfully upload a file.

    Steps:
        1. Navigate to the 'Files' page using an authenticated context.
        2. Confirm that the 'Quick Files' heading is visible (page loaded).
        3. Verify that no files are uploaded initially.
        4. Select and upload a test file (e.g., 'Grabdocs Test Plan.pdf').
        5. Wait for the file upload process to complete.
        6. Validate that the uploaded file appears in the list.

    Expected Result:
        The uploaded file should appear on the page and the "No files yet" message should disappear.
    """
    page = authenticated_context.new_page()
    page.goto(f"{base_url}files")

    # Ensure upload page loaded successfully
    expect(page.get_by_role("heading", name="Quick Files")).to_be_visible()

    # Confirm initial empty state (no files uploaded)
    expect(page.get_by_text("No files yet")).to_be_visible()

    # Select and upload the file
    page.set_input_files("input[type='file']", f"{FILE_NAME}.pdf")

    # Wait for processing to complete
    page.wait_for_timeout(12000)

    # Validate that uploaded file appears
    expect(page.get_by_text(FILE_NAME, exact=True)).to_be_visible(timeout=10000)

    page.close()


def test_file_open(authenticated_context, base_url):
    """
    Test Case: Open a File in Viewer

    Objective:
        Verify that a user can open an uploaded file from the file list.

    Steps:
        1. Navigate to the 'Files' page.
        2. Confirm that the uploaded file is visible in the list.
        3. Click the 'Open' button and handle the popup window.
        4. Verify that the new page (popup) opens successfully.

    Expected Result:
        A new browser tab or window should open, displaying the contents of the selected file.
    """
    page = authenticated_context.new_page()
    page.goto(f"{base_url}files")

    # Verify that the uploaded file exists
    expect(page.get_by_text(FILE_NAME)).to_be_visible()

    # Attempt to open the file and expect a new tab or popup to appear
    with page.expect_popup() as popup_info:
        page.get_by_role("button", name="Open", exact=True).click()

    # Confirm that new popup is created
    opened_page = popup_info.value
    opened_page.close()

    page.close()


def test_file_download(authenticated_context, base_url):
    """
    Test Case: Download a File

    Objective:
        Verify that a user can download a file from the 'Files' page.

    Steps:
        1. Navigate to the 'Files' page.
        2. Confirm that the uploaded file is visible.
        3. Click the 'Download' button and handle the popup download event.

    Expected Result:
        The download action should trigger successfully (popup or download window appears).
    """
    page = authenticated_context.new_page()
    page.goto(f"{base_url}files")

    # Verify that the uploaded file exists
    expect(page.get_by_text(FILE_NAME)).to_be_visible()

    # Trigger file download
    with page.expect_popup() as popup_info:
        page.get_by_role("button", name="Download").click()

    # Confirm popup or download action occurred
    downloaded_page = popup_info.value
    downloaded_page.close()

    page.close()


def test_file_rename(authenticated_context, base_url):
    """
    Test Case: Rename a File

    Objective:
        Verify that a user can successfully rename an existing file.

    Steps:
        1. Navigate to the 'Files' page.
        2. Confirm that the file to rename is visible.
        3. Click the 'Rename' button.
        4. Enter a new name and confirm.
        5. Validate that the file name is updated in the list.

    Expected Result:
        The old file name disappears, and the new name appears in the file list.
    """
    page = authenticated_context.new_page()
    page.goto(f"{base_url}files")
    new_name = "Renamed Test File"

    # Verify that the original file exists
    expect(page.get_by_text(FILE_NAME)).to_be_visible()

    # Open rename dialog
    page.get_by_role("button", name="Rename").click()
    expect(page.get_by_role("heading", name="Rename File")).to_be_visible()

    # Enter new name and confirm
    page.get_by_role("textbox", name="Enter new filename").fill(new_name)
    page.locator("form").get_by_role("button", name="Rename").click()

    page.wait_for_timeout(2000)

    expect(page.get_by_text(new_name)).to_be_visible()

    page.close()


def test_file_delete(authenticated_context, base_url):
    """
    Test Case: Delete a File

    Objective:
        Verify that a user can delete a file and the UI updates accordingly.

    Steps:
        1. Navigate to the 'Files' page using an authenticated context.
        2. Confirm that the uploaded file is visible.
        3. Click the 'Delete' button and accept the confirmation dialog.
        4. Wait for the success message to appear.
        5. Verify that the deleted file no longer appears and placeholder message reappears.

    Expected Result:
        The file is successfully removed, a success alert is visible, and the "No files yet" message returns.
    """
    page = authenticated_context.new_page()
    page.goto(f"{base_url}files")

    # Automatically accept delete confirmation dialog
    page.once("dialog", lambda dialog: dialog.accept())

    # Trigger delete action
    page.get_by_role("button", name="Delete").click()

    # Verify success message appears within timeout
    alert = page.get_by_role("alert").filter(has_text="successfully")
    expect(alert).to_be_visible(timeout=8000)

    # Confirm that the file list is now empty
    expect(page.get_by_text("No files yet")).to_be_visible()

    page.close()

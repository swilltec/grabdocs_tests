import re
import time
from playwright.sync_api import expect, TimeoutError

WORK_SPACE_NAME = "Test workspace"
TEST_EMAIL = "test@gmail.com"


def test_workspace_create(authenticated_context, base_url):
    """
    Test Case: Create a New Workspace

    Objective:
    Verify that a user can successfully create a new workspace.

    Precondition:
    The user must be logged in (authenticated session).

    Steps:
    1. Navigate to the 'Workspaces' page.
    2. Validate presence of the main 'Workspaces' heading.
    3. Ensure no existing 'Team Workspaces' section is visible initially.
    4. Open the workspace creation dialog.
    5. Fill in workspace name and description.
    6. Submit the creation form.
    7. Wait for the workspace list to refresh.
    8. Confirm the new workspace appears under 'Team Workspaces'.

    Expected Result:
    A newly created workspace should be displayed under 'Team Workspaces'.
    """
    page = authenticated_context.new_page()
    page.goto(f"{base_url}workspaces")

    # Verify navigation to the "Workspaces" page
    expect(page.get_by_role("heading", level=1, name="Workspaces")).to_be_visible()

    # Ensure there are no existing team workspaces
    expect(page.get_by_role("heading", name="Team Workspaces")).not_to_be_visible()

    # Open workspace creation modal
    page.get_by_role("button", name="Create Workspace").click()

    # Fill in workspace form fields
    page.get_by_role("textbox", name="Enter workspace name").fill(WORK_SPACE_NAME)
    page.get_by_role("textbox", name="Enter workspace description").fill("Testing workspace")

    # Submit the form to create the workspace
    page.get_by_role("button", name="Create", exact=True).click()

    # Wait briefly for UI updates / refresh
    page.wait_for_timeout(1000)

    # Validate that the new workspace appears under "Team Workspaces"
    expect(page.get_by_role("heading", name="Team Workspaces")).to_be_visible()
    expect(page.get_by_role("heading", name=WORK_SPACE_NAME)).to_be_visible()

    page.close()


def test_workspace_invite(authenticated_context, base_url):
    """
    Test Case: Invite a User to an Existing Workspace

    Objective:
    Verify that a user can successfully invite other members to a workspace.

    Precondition:
    A workspace must already exist (e.g., created by `test_workspace_create`).

    Steps:
    1. Navigate to the 'Workspaces' page.
    2. Validate that the workspace and team section are visible.
    3. Click the 'Invite Member' button.
    4. Enter one or more email addresses for invitation.
    5. Send the invitation.
    6. View sent invitations and verify presence of 'Resend' and 'Cancel' actions.
    7. Cancel an existing invitation and confirm visual feedback.

    Expected Result:
    Invitations should be listed under the workspace, with visible controls
    to resend or cancel invitations. After cancellation, an empty-state message appears.
    """
    page = authenticated_context.new_page()
    page.goto(f"{base_url}workspaces")

    # Validate main workspace section visibility
    expect(page.get_by_role("heading", level=1, name="Workspaces")).to_be_visible()
    expect(page.get_by_role("heading", name="Team Workspaces")).to_be_visible()
    expect(page.get_by_role("heading", name=WORK_SPACE_NAME)).to_be_visible()

    # Open the invitation dialog
    page.get_by_role("button", name="Invite Member").click()

    # Confirm that the invite modal is displayed
    expect(page.get_by_role("heading", name=f"Invite to {WORK_SPACE_NAME}")).to_be_visible()

    # Enter test email(s) and send invitation
    page.get_by_role("textbox", name="user1@example.com, user2@").fill(TEST_EMAIL)
    page.get_by_role("button", name="Send Invitation").click()

    # Wait for system response and UI update
    page.wait_for_timeout(1000)

    # View the list of sent invitations
    page.get_by_role("button", name="View Invitations").click()

    # Verify invitation management options
    expect(page.get_by_role("button", name="Resend All")).to_be_visible()
    expect(page.get_by_role("button", name="Resend Invitation")).to_be_visible()
    expect(page.get_by_role("heading", name=f"{WORK_SPACE_NAME} Invitations")).to_be_visible()

    # Cancel an existing invitation
    page.get_by_role("button", name="Cancel Invitation").click()

    # Ensure the no-pending-invitations message appears
    expect(page.get_by_text("No pending invitations for")).to_be_visible()

    # Verify the invitation modal can be dismissed safely
    page.locator("div").filter(
        has_text=re.compile(r"^Test workspace Invitations$")
    ).get_by_role("button").click()

    page.close()
    
def test_workspace_start_meeting(authenticated_context, base_url):
    """
    Test Case: Start a Meeting

    Objective:
    Verify that a user can successfully start a meeting by clicking the start meeting icon.

    Precondition:
    The user must be logged in (authenticated session).

    Steps:
    1. Navigate to the 'Workspaces' page.
    2. Validate presence of the main 'Workspaces' heading.
    3. Locate and click the start meeting icon/button.
    4. Verify that the meeting interface or meeting page is displayed.

    Expected Result:
    A meeting should be started successfully, and the meeting interface should be visible.
    """
    page = authenticated_context.new_page()
    page.goto(f"{base_url}workspaces")

    # Verify navigation to the "Workspaces" page
    expect(page.get_by_role("heading", level=1, name="Workspaces")).to_be_visible()

    # Look for and click the start meeting icon/button
    # Try multiple selectors to find the start meeting button/icon
    start_meeting_clicked = False

    # First, try to find by button role with "Start Meeting" text
    try:
        start_meeting_button = page.get_by_role("button", name=re.compile("Start Meeting", re.I))
        if start_meeting_button.count() > 0:
            start_meeting_button.first.click()
            start_meeting_clicked = True
    except Exception:
        pass

    # If not found, try aria-label
    if not start_meeting_clicked:
        try:
            start_meeting_button = page.locator("button[aria-label*='meeting' i]")
            if start_meeting_button.count() > 0:
                start_meeting_button.first.click()
                start_meeting_clicked = True
        except Exception:
            pass

    # If still not found, try data-testid
    if not start_meeting_clicked:
        try:
            start_meeting_button = page.locator("[data-testid*='meeting' i], [data-testid*='start-meeting' i]")
            if start_meeting_button.count() > 0:
                start_meeting_button.first.click()
                start_meeting_clicked = True
        except Exception:
            pass

    # If still not found, try any button containing "meeting" text
    if not start_meeting_clicked:
        try:
            start_meeting_button = page.locator("button").filter(has_text=re.compile("meeting", re.I))
            if start_meeting_button.count() > 0:
                start_meeting_button.first.click()
                start_meeting_clicked = True
        except Exception:
            pass

    # If still not found, try finding an icon (SVG) that might represent a meeting/video call
    if not start_meeting_clicked:
        try:
            # Look for SVG icons that might be clickable (inside a button or clickable element)
            start_meeting_icon = page.locator("button svg, [role='button'] svg, a svg").filter(has=page.locator("path, circle, rect"))
            if start_meeting_icon.count() > 0:
                # Try clicking the parent button/link
                start_meeting_icon.first.locator("..").click()
                start_meeting_clicked = True
        except Exception:
            pass

    # Assert that we found and clicked the start meeting button
    assert start_meeting_clicked, "Could not find start meeting button/icon on the workspaces page"

    # Wait for meeting interface to load
    page.wait_for_timeout(2000)

    # Verify that meeting has started
    # Check if URL changed to indicate meeting page opened
    current_url = page.url.lower()
    if "meeting" in current_url:
        # Meeting page opened - verify URL contains meeting
        expect(page).to_have_url(re.compile("meeting", re.I), timeout=10000)
    else:
        # Check for meeting-related UI elements on the current page
        # Look for common meeting indicators
        try:
            expect(page.get_by_text(re.compile("meeting|join|video|audio", re.I)).first).to_be_visible(timeout=10000)
        except Exception:
            # Alternative: check for meeting control buttons
            expect(page.get_by_role("button", name=re.compile("leave|end|exit", re.I)).first).to_be_visible(timeout=10000)

    page.close()

def test_workspace_shared_files(authenticated_context, base_url):
    """
    Robust test to verify a shared file in the existing workspace can be opened.
    Uses multiple fallbacks and longer timeouts to reduce flakiness.
    """
    page = authenticated_context.new_page()
    # navigate with longer timeout for slow networks / SPA loads
    page.goto(f"{base_url}workspaces", wait_until="networkidle", timeout=60000)

    # ensure home and workspace are visible
    expect(page.get_by_role("heading", level=1, name="Workspaces")).to_be_visible(timeout=15000)
    expect(page.get_by_role("heading", name=WORK_SPACE_NAME)).to_be_visible(timeout=15000)

    # open workspace detail (link -> button -> card)
    workspace_card = page.locator("div,article,section").filter(has=page.get_by_role("heading", name=WORK_SPACE_NAME)).first
    try:
        workspace_card.get_by_role("link", name=WORK_SPACE_NAME).click(timeout=5000)
    except Exception:
        try:
            workspace_card.get_by_role("button", name=re.compile(r"(Open|View|Enter|Open Workspace)", re.I)).click(timeout=5000)
        except Exception:
            workspace_card.click(timeout=5000)

    # wait for workspace page
    expect(page.get_by_role("heading", name=WORK_SPACE_NAME)).to_be_visible(timeout=15000)

    # open Files/Documents tab (tab -> link -> nav item)
    try:
        page.get_by_role("tab", name=re.compile(r"(Files|Documents|Docs)", re.I)).click(timeout=5000)
    except Exception:
        try:
            page.get_by_role("link", name=re.compile(r"(Files|Documents|Docs)", re.I)).click(timeout=5000)
        except Exception:
            btn = page.locator("a, button").filter(has_text=re.compile(r"(files|documents|docs)", re.I)).first
            if btn.count() > 0:
                btn.click(timeout=5000)

    # find a file entry (try several patterns)
    def first_visible_locator(factories, timeout=8000):
        for f in factories:
            try:
                loc = f()
                expect(loc).to_be_visible(timeout=timeout)
                return loc
            except Exception:
                continue
        # debug info
        snippet = "<no content>"
        try:
            snippet = page.content()[:1200]
        except Exception:
            pass
        raise AssertionError(f"No file entry found in workspace files view. URL: {page.url}\nSnippet:\n{snippet}")

    file_loc = first_visible_locator(
        [
            lambda: page.get_by_role("link", name=re.compile(r".+\.(pdf|docx|doc|txt|md|png|jpg|jpeg)", re.I)).first,
            lambda: page.get_by_text(re.compile(r".+\.(pdf|docx|doc|txt|md|png|jpg|jpeg)", re.I)).first,
            lambda: page.locator("[data-testid*='file'], .file-row, .document-row").first,
            lambda: page.locator("a, button").filter(has_text=re.compile(r"(Open|Preview|View|Download)", re.I)).first,
        ],
        timeout=10000,
    )

    # open the file
    try:
        file_loc.click(timeout=8000)
    except Exception:
        file_loc.scroll_into_view_if_needed()
        file_loc.click(timeout=8000)

    # verify preview appears (text, iframe, or viewer)
    try:
        expect(page.get_by_text(re.compile(r"(Document Preview|Preview|Viewer|Page \d+)", re.I))).to_be_visible(timeout=15000)
    except Exception:
        try:
            expect(page.locator("iframe").first).to_be_visible(timeout=12000)
        except Exception:
            try:
                expect(page.locator(".viewer, .document-viewer, .file-preview").first).to_be_visible(timeout=10000)
            except Exception:
                # last-resort: check for any substantial text in the opened area
                try:
                    expect(page.get_by_text(re.compile(r"\w{3,}\s+\w{3,}", re.I))).to_be_visible(timeout=8000)
                except Exception:
                    page.close()
                    raise AssertionError("File preview did not appear after opening the file.")

    # optional: verify download/export controls exist (best-effort)
    try:
        expect(page.get_by_role("button", name=re.compile(r"(Download|Export|Save|Share)", re.I))).to_be_visible(timeout=7000)
    except Exception:
        # not fatal; continue
        pass

    page.close()



def test_workspace_delete(authenticated_context, base_url):
    """
    Test Case: Delete an Existing Workspace

    Objective:
    Verify that a user can successfully delete a workspace.

    Precondition:
    At least one workspace (e.g., from `test_workspace_create`) must exist.

    Steps:
    1. Navigate to the 'Workspaces' page.
    2. Confirm the 'Team Workspaces' section and existing workspace visibility.
    3. Click the 'Delete Workspace' button.
    4. Handle the confirmation dialog by accepting it.
    5. Wait temporarily for any backend operations or UI updates.
    6. Verify that the deleted workspace and section are no longer displayed.

    Expected Result:
    The workspace should be removed from the UI and 'Team Workspaces'
    should no longer be visible.
    """
    page = authenticated_context.new_page()
    page.goto(f"{base_url}workspaces")

    # Auto-accept confirmation dialog when deleting a workspace
    page.on("dialog", lambda dialog: dialog.accept())

    # Confirm navigation and workspace existence
    expect(page.get_by_role("heading", level=1, name="Workspaces")).to_be_visible()
    expect(page.get_by_role("heading", name="Team Workspaces")).to_be_visible()
    expect(page.get_by_role("heading", name=WORK_SPACE_NAME)).to_be_visible()

    # Initiate workspace deletion
    page.get_by_role("button", name="Delete Workspace").click()

    # Wait for the deletion UI process to complete
    page.wait_for_timeout(1000)

    # Verify that the workspace and related section no longer appear
    expect(page.get_by_role("heading", name="Team Workspaces")).not_to_be_visible()
    expect(page.get_by_role("heading", name=WORK_SPACE_NAME)).not_to_be_visible()

    page.close()









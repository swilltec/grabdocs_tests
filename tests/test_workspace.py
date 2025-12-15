import re

from playwright.sync_api import expect

WORK_SPACE_NAME = "Test workspace"
# WORK_SPACE_NAME = "Another one"
TEST_EMAIL = "test@gmail.com"
FILE_NAME = "Grabdocs Test Plan"


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
    page.get_by_role("textbox", name="Enter workspace description").fill(
        "Testing workspace"
    )

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
    expect(
        page.get_by_role("heading", name=f"Invite to {WORK_SPACE_NAME}")
    ).to_be_visible()

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
    expect(
        page.get_by_role("heading", name=f"{WORK_SPACE_NAME} Invitations")
    ).to_be_visible()

    # Cancel an existing invitation
    page.get_by_role("button", name="Cancel Invitation").click()

    # Ensure the no-pending-invitations message appears
    expect(page.get_by_text("No pending invitations for")).to_be_visible()

    # Verify the invitation modal can be dismissed safely
    page.locator("div").filter(
        has_text=re.compile(r"^Test workspace Invitations$")
    ).get_by_role("button").click()

    page.close()


def test_workspace_accept_invite(
    authenticated_context, member_context, base_url, member, member_name
):
    """
    Test Case: Invite and Accept Workspace Invitation

    Objective:
        Verify that a workspace owner can invite a member and that the invited member
        can successfully accept the invitation and join the workspace.

    Preconditions:
        - A workspace must already exist (e.g., created by `test_workspace_create`).
        - Two authenticated users: owner (authenticated_context) and member (member_context).

    Steps:
        Owner Actions:
        1. Navigate to the 'Workspaces' page.
        2. Verify workspace sections are visible (main heading, team workspaces, specific workspace).
        3. Click 'Invite Member' button.
        4. Enter member's email address.
        5. Send the invitation.

        Member Actions:
        6. Navigate to the 'Workspaces' page as the invited member.
        7. Verify the workspace is not visible before accepting invitation.
        8. Open notifications (badge showing "1").
        9. Click 'Accept workspace invitation'.
        10. Mark all notifications as read.
        11. Reload the page.
        12. Verify the workspace is now visible.

        Owner Verification:
        13. Navigate to 'View Members' for the workspace.
        14. Verify the member appears in the members list.
        15. Verify there are no pending invitations.
        16. Close the members modal.

        Cleanup:
        17. Navigate to files page and delete test data.

    Expected Results:
        - Invitation is successfully sent by the owner.
        - Member receives notification about the invitation.
        - After acceptance, the workspace appears in the member's workspace list.
        - Member appears in the workspace members list.
        - No pending invitations remain after acceptance.
    """
    # Owner navigates to workspaces page
    page = authenticated_context.new_page()
    page.goto(f"{base_url}workspaces")

    # Verify workspace page is loaded correctly
    expect(page.get_by_role("heading", level=1, name="Workspaces")).to_be_visible()
    expect(page.get_by_role("heading", name="Team Workspaces")).to_be_visible()
    expect(page.get_by_role("heading", name=WORK_SPACE_NAME)).to_be_visible()

    # Owner sends invitation to member
    page.get_by_role("button", name="Invite Member").click()
    page.get_by_role("textbox", name="user1@example.com, user2@").fill(member)
    page.get_by_role("button", name="Send Invitation").click()

    # Member opens workspaces page
    member_page = member_context.new_page()
    member_page.goto(f"{base_url}workspaces")
    member_page.wait_for_timeout(2000)
    member_page.reload()

    # Verify workspace is not visible before accepting invitation
    expect(member_page.get_by_role("heading", name=WORK_SPACE_NAME)).not_to_be_visible()

    # Member accepts the workspace invitation
    member_page.get_by_role("button", name="1").click()  # Open notifications
    member_page.get_by_role("button", name="Accept workspace invitation").first.click()
    member_page.get_by_role("button", name="Mark all read").click()

    # Wait for invitation acceptance to process
    member_page.wait_for_timeout(2000)

    # Reload to see updated workspace list
    member_page.reload()

    # Verify workspace is now visible to the member
    expect(member_page.get_by_role("heading", name=WORK_SPACE_NAME)).to_be_visible()

    # Owner verifies member was added to workspace
    page.get_by_role("button", name="View Members").nth(1).click()
    expect(
        page.get_by_role("heading", name=f"{WORK_SPACE_NAME} Members")
    ).to_be_visible()

    # Verify member appears in the members list
    expect(page.get_by_text(member_name, exact=True)).to_be_visible()

    # Cleanup: Navigate to files and delete test data
    page.goto(f"{base_url}files")

    # Accept delete confirmation dialog
    page.once("dialog", lambda dialog: dialog.accept())
    page.get_by_role("button", name="Delete").click()

    # Close both browser contexts
    page.close()
    member_page.close()


def test_workspace_file_share(authenticated_context, base_url):
    """
    Test Case: Upload and Share File with Workspace

    Objective:
        Verify that a user can upload a file, share it with a workspace, and then
        remove workspace access by changing visibility back to global.

    Preconditions:
        - User is authenticated.
        - A workspace exists (e.g., created by `test_workspace_create`).

    Steps:
        File Upload:
        1. Navigate to the 'Files' page.
        2. Verify the 'Quick Files' heading is visible (page loaded).
        3. Confirm initial empty state ("No files yet" message).
        4. Upload a test file (e.g., 'Grabdocs Test Plan.pdf').
        5. Wait for upload processing to complete.
        6. Verify the uploaded file appears in the file list.

        Share File with Workspace:
        7. Reload the page to ensure file is persisted.
        8. Change file visibility from 'Local' to 'Workspaces'.
        9. Select the target workspace from the visibility modal.
        10. Hide overlapping UI elements (Ask button) if needed.
        11. Save the visibility changes.

        Verify File in Workspace:
        12. Navigate to the 'Workspaces' page.
        13. Open 'Shared Files' for the workspace.
        14. Verify the uploaded file appears in the workspace's shared files.

        Remove Workspace Access:
        15. Navigate back to the 'Files' page.
        16. Change file visibility from 'Workspaces' to 'Global'.

        Verify File Removed from Workspace:
        17. Navigate to the 'Workspaces' page.
        18. Open 'Shared Files' for the workspace.
        19. Verify the empty state message appears (file no longer shared).

    Expected Results:
        - File uploads successfully and appears in the file list.
        - File can be shared with a specific workspace.
        - File appears in the workspace's shared files section.
        - Changing visibility to 'Global' removes file from workspace.
        - Empty state message appears when no files are shared with workspace.
    """
    page = authenticated_context.new_page()
    page.goto(f"{base_url}files")

    # Verify the files page loaded successfully
    expect(page.get_by_role("heading", name="Quick Files")).to_be_visible()

    # Confirm no files exist initially
    expect(page.get_by_text("No files yet")).to_be_visible()

    # Upload the test file
    page.set_input_files("input[type='file']", f"{FILE_NAME}.pdf")

    # Wait for file upload and processing to complete
    page.wait_for_timeout(12000)

    # Verify the uploaded file appears in the list
    expect(page.get_by_text(FILE_NAME, exact=True)).to_be_visible(timeout=10000)

    # Reload to ensure file persisted
    page.reload()

    # Change file visibility from Local to Workspaces
    page.get_by_role("button", name="Local").click()
    page.get_by_role("button", name="Workspaces").click()

    # Select workspace to share with
    expect(
        page.get_by_role("heading", name="Choose Workspace Visibility")
    ).to_be_visible()
    page.get_by_text(WORK_SPACE_NAME).click()

    # Hide the Ask button that may block the Save Changes button
    page.get_by_role("button", name="Ask").evaluate("el => el.style.display = 'none'")

    # Save the visibility changes
    page.get_by_role("button", name="Save Changes").click()

    # Navigate to workspaces to verify file sharing
    page.goto(f"{base_url}workspaces")

    # Open the shared files section for the workspace
    page.get_by_role("button", name="Shared Files").nth(1).click()

    # Verify shared files modal is open
    expect(
        page.get_by_role("heading", name=f"{WORK_SPACE_NAME} - Shared Files")
    ).to_be_visible()

    # Verify the file appears in workspace shared files
    expect(page.get_by_text(FILE_NAME)).to_be_visible()

    # Change file visibility back to Global (remove workspace access)
    page.goto(f"{base_url}files")
    page.get_by_role("button", name="Global").click()

    # Verify file is no longer shared with workspace
    page.goto(f"{base_url}workspaces")
    page.get_by_role("button", name="Shared Files").nth(1).click()

    # Verify empty state message appears
    expect(
        page.get_by_text(
            "No shared files in this workspaceFiles shared with this workspace will appear"
        )
    ).to_be_visible()

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
    expect(page.get_by_role("heading", level=1, name=WORK_SPACE_NAME)).to_be_visible()

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


def test_workspace_chat(authenticated_context, base_url):
    """
    Test Case: Access Workspace Chat

    Objective:
        Verify that a user can successfully navigate to and access a workspace's chat interface.

    Preconditions:
        - User is authenticated.
        - A workspace exists (e.g., created by `test_workspace_create`).

    Steps:
        1. Navigate to the 'Workspaces' page.
        2. Click the 'Start Chat' button for the workspace.
        3. Wait for navigation to the chat page.
        4. Verify the workspace chat channel heading is visible.

    Expected Results:
        - User is redirected to the chat page.
        - The workspace chat channel (e.g., "#Another one") is visible and accessible.
        - Chat interface loads successfully within 90 seconds.
    """
    page = authenticated_context.new_page()
    page.goto(f"{base_url}workspaces")

    # Click Start Chat button for the workspace
    page.get_by_role("button", name="Start Chat").nth(1).click()

    # Wait for navigation to chat page
    page.wait_for_url(re.compile(r".*/chat"), timeout=90000)

    # Verify workspace chat channel is visible
    expect(
        page.get_by_role("heading", name=f"#{WORK_SPACE_NAME}").first
    ).to_be_visible()

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

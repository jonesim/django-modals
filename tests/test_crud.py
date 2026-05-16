"""Tests for CRUD modal operations: Create, Read, Edit, Delete companies."""
import pytest
from playwright.sync_api import expect

from helpers import wait_for_modal_ready, wait_modal_closed, click_modal_button


@pytest.fixture()
def crud_page(page, base_url):
    page.goto(f"{base_url}/crud")
    page.wait_for_load_state("networkidle")
    return page


class TestCrudCreate:

    def test_create_modal_opens_empty_form(self, crud_page):
        """Create button should open a 'New Company' modal with an empty name field."""
        crud_page.get_by_role("link", name="Create", exact=True).first.click()
        modal = crud_page.locator(".modal.show .modal-content")
        expect(modal).to_be_visible()
        expect(modal.locator(".modal-header")).to_contain_text("New Company")

        name_input = modal.locator("input[name='name']")
        expect(name_input).to_have_value("")

        submit_btn = modal.get_by_role("button", name="Submit")
        expect(submit_btn).to_be_visible()
        cancel_btn = modal.get_by_role("button", name="Cancel")
        expect(cancel_btn).to_be_visible()

    def test_create_company_success(self, crud_page):
        """Filling in the form and submitting should create a new company."""
        crud_page.get_by_role("link", name="Create", exact=True).first.click()
        modal = crud_page.locator(".modal.show .modal-content")
        expect(modal).to_be_visible()

        wait_for_modal_ready(crud_page)
        modal.locator("input[name='name']").fill("Playwright Test Co")
        modal.locator("label[for='id_active']").click()
        click_modal_button(crud_page, "Submit")
        wait_modal_closed(crud_page)

    def test_create_company_empty_name_keeps_modal(self, crud_page):
        """Submitting an empty name should keep the modal open (HTML5 validation)."""
        crud_page.get_by_role("link", name="Create", exact=True).first.click()
        modal = crud_page.locator(".modal.show .modal-content")
        expect(modal).to_be_visible()

        wait_for_modal_ready(crud_page)
        modal.get_by_role("button", name="Submit").click()
        expect(modal).to_be_visible()


class TestCrudView:

    def test_view_modal_shows_readonly(self, crud_page):
        """View button should open a read-only modal showing company details."""
        crud_page.get_by_role("link", name="View", exact=True).first.click()
        modal = crud_page.locator(".modal.show .modal-content")
        expect(modal).to_be_visible()
        expect(modal.locator(".modal-header")).to_contain_text("View Company")

        name_input = modal.locator("input[name='name']")
        expect(name_input).to_have_attribute("disabled", "")

        cancel_btn = modal.get_by_role("button", name="Cancel")
        expect(cancel_btn).to_be_visible()


class TestCrudEdit:

    def test_edit_modal_opens_with_data(self, crud_page):
        """Edit button should open a modal pre-filled with existing company data."""
        crud_page.get_by_role("link", name="Edit", exact=True).first.click()
        modal = crud_page.locator(".modal.show .modal-content")
        expect(modal).to_be_visible()
        expect(modal.locator(".modal-header")).to_contain_text("Edit Company")

        name_input = modal.locator("input[name='name']")
        expect(name_input).not_to_have_value("")

        submit_btn = modal.get_by_role("button", name="Submit")
        expect(submit_btn).to_be_visible()

    def test_edit_company_and_submit(self, crud_page):
        """Editing the company name and submitting should succeed."""
        crud_page.get_by_role("link", name="Edit", exact=True).first.click()
        modal = crud_page.locator(".modal.show .modal-content")
        expect(modal).to_be_visible()

        wait_for_modal_ready(crud_page)
        name_input = modal.locator("input[name='name']")
        original_name = name_input.input_value()
        name_input.clear()
        name_input.fill("Edited Name")
        click_modal_button(crud_page, "Submit")
        wait_modal_closed(crud_page)

        crud_page.get_by_role("link", name="Edit", exact=True).first.click()
        modal = crud_page.locator(".modal.show .modal-content")
        expect(modal).to_be_visible()
        wait_for_modal_ready(crud_page)
        name_input = modal.locator("input[name='name']")
        name_input.clear()
        name_input.fill(original_name)
        click_modal_button(crud_page, "Submit")
        wait_modal_closed(crud_page)


class TestCrudEditDelete:

    def test_edit_delete_modal_has_delete_button(self, crud_page):
        """Edit/Delete modal should have both Submit and Delete buttons."""
        crud_page.get_by_role("link", name="Edit/Delete", exact=True).first.click()
        modal = crud_page.locator(".modal.show .modal-content")
        expect(modal).to_be_visible()

        submit_btn = modal.get_by_role("button", name="Submit")
        expect(submit_btn).to_be_visible()
        delete_btn = modal.get_by_role("button", name="Delete")
        expect(delete_btn).to_be_visible()


class TestCrudCancel:

    def test_cancel_closes_modal(self, crud_page):
        """Clicking Cancel should close the modal without saving."""
        crud_page.get_by_role("link", name="Create", exact=True).first.click()
        modal = crud_page.locator(".modal.show .modal-content")
        expect(modal).to_be_visible()

        wait_for_modal_ready(crud_page)
        modal.locator("input[name='name']").fill("Should Not Be Saved")
        click_modal_button(crud_page, "Cancel")
        wait_modal_closed(crud_page)


class TestDifferentViews:

    def test_view_configured_view(self, crud_page):
        """'Different Views' section - View button opens read-only modal."""
        crud_page.get_by_role("link", name="View", exact=True).nth(1).click()
        modal = crud_page.locator(".modal.show .modal-content")
        expect(modal).to_be_visible()
        name_input = modal.locator("input[name='name']")
        expect(name_input).to_have_attribute("disabled", "")

    def test_view_configured_edit(self, crud_page):
        """'Different Views' section - Edit button opens editable modal."""
        crud_page.get_by_role("link", name="Edit", exact=True).nth(1).click()
        modal = crud_page.locator(".modal.show .modal-content")
        expect(modal).to_be_visible()
        submit_btn = modal.get_by_role("button", name="Submit")
        expect(submit_btn).to_be_visible()

    def test_view_configured_edit_delete(self, crud_page):
        """'Different Views' section - Edit/Delete button."""
        crud_page.get_by_role("link", name="Edit/Delete", exact=True).nth(1).click()
        modal = crud_page.locator(".modal.show .modal-content")
        expect(modal).to_be_visible()
        delete_btn = modal.get_by_role("button", name="Delete")
        expect(delete_btn).to_be_visible()

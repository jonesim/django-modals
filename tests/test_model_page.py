"""Tests for the Model examples page: datatables, company/person forms."""
import pytest
from playwright.sync_api import expect


@pytest.fixture()
def model_page(page, base_url):
    page.goto(f"{base_url}/Model")
    page.wait_for_load_state("networkidle")
    return page


class TestModelPage:

    def test_page_loads_with_tables(self, model_page):
        """Model page should display company and people datatables."""
        expect(model_page.locator("table").first).to_be_visible()

    def test_company_create_prefilled(self, model_page):
        """'Company Create pre filled name' should open modal with prefilled name."""
        model_page.get_by_role("link", name="Company Create pre filled name").click()
        modal = model_page.locator(".modal-content")
        expect(modal).to_be_visible()
        name_input = modal.locator("input[name='name']")
        expect(name_input).to_have_value("Prefilled Name")

    def test_company_people_modal_opens(self, model_page):
        """'Company/People modal' should open a create form."""
        model_page.get_by_role("link", name="Company/People modal").click()
        modal = model_page.locator(".modal-content")
        expect(modal).to_be_visible()
        expect(modal.locator("input[name='name']")).to_be_visible()

    def test_separate_form_modal(self, model_page):
        """'Separate Form' should open a company form defined with a separate form class."""
        model_page.get_by_role("link", name="Separate Form").click()
        modal = model_page.locator(".modal-content")
        expect(modal).to_be_visible()
        expect(modal.locator("input[name='name']")).to_be_visible()


class TestFieldSetup:

    def test_field_setup_modal(self, model_page):
        """Field Setup modal should show custom labels and help text."""
        model_page.get_by_role("link", name="Field Setup").click()
        modal = model_page.locator(".modal-content")
        expect(modal).to_be_visible()
        expect(modal).to_contain_text("Title (field)")
        expect(modal).to_contain_text("Title help text from field definition")

    def test_view_setup_modal(self, model_page):
        """View Setup modal should show view-level label overrides."""
        model_page.get_by_role("link", name="View Setup").click()
        modal = model_page.locator(".modal-content")
        expect(modal).to_be_visible()
        expect(modal).to_contain_text("First Name (View)")

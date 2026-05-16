"""Tests for widget examples: Select2, Toggle, TinyMCE, colour picker, etc."""
import pytest
from playwright.sync_api import expect


@pytest.fixture()
def widgets_page(page, base_url):
    page.goto(f"{base_url}/Widgets")
    page.wait_for_load_state("networkidle")
    return page


class TestWidgetsPage:

    def test_page_loads(self, widgets_page):
        """Widgets page should load successfully."""
        expect(widgets_page.locator("nav.navbar")).to_be_visible()

    def test_many_to_many_modal(self, widgets_page):
        """Many to Many button should open a tag/company select2 form."""
        widgets_page.get_by_role("link", name="Many to Many", exact=True).click()
        modal = widgets_page.locator(".modal-content")
        expect(modal).to_be_visible()
        expect(modal.locator("input[name='tag']")).to_be_visible()

    def test_reverse_many_to_many_modal(self, widgets_page):
        """Reverse Many to Many should open a company form with tag selection."""
        widgets_page.get_by_role("link", name="Reverse Many to Many", exact=True).click()
        modal = widgets_page.locator(".modal-content")
        expect(modal).to_be_visible()

    def test_ajax_modal(self, widgets_page):
        """AJAX button should open a modal with AJAX-powered Select2."""
        widgets_page.get_by_role("link", name="AJAX", exact=True).click()
        modal = widgets_page.locator(".modal-content")
        expect(modal).to_be_visible()

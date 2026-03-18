"""Tests for layout modal variations: Regular, Horizontal, sizes, etc."""
import pytest
from playwright.sync_api import expect


MODAL_CLOSE_TIMEOUT = 10000


def _wait_modal_closed(page, timeout=MODAL_CLOSE_TIMEOUT):
    page.locator(".modal.show").wait_for(state="hidden", timeout=timeout)


@pytest.fixture()
def layout_page(page, base_url):
    page.goto(f"{base_url}/layout")
    page.wait_for_load_state("networkidle")
    return page


class TestLayoutPage:

    def test_page_has_sections(self, layout_page):
        """Layout page should have Regular, Horizontal, Manual, and Size sections."""
        expect(layout_page.locator("body")).to_contain_text("Regular")
        expect(layout_page.locator("body")).to_contain_text("Horizontal")

    def test_regular_modal(self, layout_page):
        """Regular modal should open with a person form."""
        layout_page.get_by_role("link", name="Regular", exact=True).click()
        modal = layout_page.locator(".modal.show .modal-content")
        expect(modal).to_be_visible()
        expect(modal.locator("input[name='first_name']")).to_be_visible()
        expect(modal.locator("input[name='surname']")).to_be_visible()

    def test_regular_2_column_modal(self, layout_page):
        """2-column regular modal should open successfully."""
        layout_page.get_by_role("link", name="Regular 2 column").click()
        modal = layout_page.locator(".modal.show .modal-content")
        expect(modal).to_be_visible()
        expect(modal.locator("input[name='first_name']")).to_be_visible()

    def test_horizontal_modal(self, layout_page):
        """Horizontal layout modal should open with label-field pairs."""
        layout_page.get_by_role("link", name="Horizontal", exact=True).click()
        modal = layout_page.locator(".modal.show .modal-content")
        expect(modal).to_be_visible()
        expect(modal.locator("input[name='first_name']")).to_be_visible()

    def test_horizontal_placeholder_modal(self, layout_page):
        """Horizontal Placeholder modal should show placeholders."""
        layout_page.get_by_role("link", name="Horizontal Placeholder").click()
        modal = layout_page.locator(".modal.show .modal-content")
        expect(modal).to_be_visible()
        expect(modal.locator("input[name='first_name']")).to_be_visible()

    def test_manual_modal(self, layout_page):
        """Manual field layout modal should open."""
        layout_page.get_by_role("link", name="Manual", exact=True).click()
        modal = layout_page.locator(".modal.show .modal-content")
        expect(modal).to_be_visible()

    def test_no_labels_modal(self, layout_page):
        """No labels modal should open successfully."""
        layout_page.get_by_role("link", name="No labels").click()
        modal = layout_page.locator(".modal.show .modal-content")
        expect(modal).to_be_visible()
        expect(modal.locator("input[name='first_name']")).to_be_visible()

    def test_note_field_modal(self, layout_page):
        """Note Field modal should open with a textarea."""
        layout_page.get_by_role("link", name="Note Field").click()
        modal = layout_page.locator(".modal.show .modal-content")
        expect(modal).to_be_visible()
        expect(modal.locator("textarea[name='notes']")).to_be_visible()


class TestModalSizes:

    @pytest.mark.parametrize("size", ["Small", "Medium", "Large", "Extra Large"])
    def test_size_variants_open(self, layout_page, size):
        """Each size variant should open a modal successfully."""
        layout_page.get_by_role("link", name=size, exact=True).click()
        modal = layout_page.locator(".modal.show .modal-content")
        expect(modal).to_be_visible()
        expect(modal.locator("input[name='first_name']")).to_be_visible()

    def test_large_2_columns(self, layout_page):
        """Large - 2 Columns should open a two-column layout."""
        layout_page.get_by_role("link", name="Large - 2 Columns").click()
        modal = layout_page.locator(".modal.show .modal-content")
        expect(modal).to_be_visible()

"""Tests for the Basic modals page: SimpleModal, TemplateModal, and Ajax Confirm."""
import pytest
from playwright.sync_api import expect

from helpers import wait_for_modal_ready, wait_modal_closed, click_modal_button


@pytest.fixture()
def basic_page(page, base_url):
    page.goto(f"{base_url}/Basic")
    page.wait_for_load_state("networkidle")
    return page


class TestSimpleModal:

    def test_simple_message_opens_and_closes(self, basic_page):
        """Clicking 'Simple Message' should open a modal with a hello message."""
        basic_page.get_by_role("link", name="Simple Message").click()
        modal = basic_page.locator(".modal.show .modal-content")
        expect(modal).to_be_visible()
        expect(modal).to_contain_text("Hello")
        expect(modal).to_contain_text("Message no title default OK button")

        click_modal_button(basic_page, "OK")
        wait_modal_closed(basic_page)

    def test_message_with_title(self, basic_page):
        """'Message with title' modal should display a title bar."""
        basic_page.get_by_role("link", name="Message with title").click()
        modal = basic_page.locator(".modal.show .modal-content")
        expect(modal).to_be_visible()
        expect(modal.locator(".modal-header")).to_contain_text("Modal Title")
        expect(modal).to_contain_text("Message with title default OK button")

        click_modal_button(basic_page, "OK")
        wait_modal_closed(basic_page)

    def test_confirm_modal_opens_and_cancels(self, basic_page):
        """The Confirm button should open a modal with custom buttons."""
        basic_page.get_by_role("link", name="Confirm", exact=True).click()
        modal = basic_page.locator(".modal.show .modal-content")
        expect(modal).to_be_visible()
        expect(modal).to_contain_text("Custom buttons with confirm stacked modal")

        wait_for_modal_ready(basic_page)
        confirm_btn = basic_page.locator(".modal.show").get_by_role("button", name="Confirm")
        expect(confirm_btn).to_be_visible()
        cancel_btn = basic_page.locator(".modal.show").get_by_role("button", name="Cancel")
        expect(cancel_btn).to_be_visible()

        click_modal_button(basic_page, "Cancel")
        wait_modal_closed(basic_page)


class TestTemplateModal:

    def test_template_modal_opens(self, basic_page):
        """Template Modal should render from a Django template."""
        basic_page.get_by_role("link", name="Template Modal", exact=True).click()
        modal = basic_page.locator(".modal.show .modal-content")
        expect(modal).to_be_visible()
        expect(modal).to_contain_text("From view")

    def test_template_modal_with_ajax_button(self, basic_page):
        """Template Modal with ajax button should have a functional ajax button."""
        links = basic_page.get_by_role("link", name="Template Modal with ajax button")
        links.first.click()
        modal = basic_page.locator(".modal.show .modal-content")
        expect(modal).to_be_visible()


class TestForwardingModal:

    def test_forward_example_opens(self, basic_page):
        """Forward_example modal should show Replace, Redirect, Confirm, Message buttons."""
        basic_page.get_by_role("link", name="Forward_example").click()
        modal = basic_page.locator(".modal.show .modal-content")
        expect(modal).to_be_visible()
        expect(modal.locator(".modal-header")).to_contain_text("Forwarding Example")

        wait_for_modal_ready(basic_page)
        active_modal = basic_page.locator(".modal.show")
        expect(active_modal.get_by_role("button", name="Replace")).to_be_visible()
        expect(active_modal.get_by_role("button", name="Redirect")).to_be_visible()
        expect(active_modal.get_by_role("button", name="Confirm")).to_be_visible()
        expect(active_modal.get_by_role("button", name="Message")).to_be_visible()

    def test_forward_replace_replaces_modal(self, basic_page):
        """Clicking Replace should replace the current modal content."""
        basic_page.get_by_role("link", name="Forward_example").click()
        modal = basic_page.locator(".modal.show .modal-content")
        expect(modal).to_be_visible()

        click_modal_button(basic_page, "Replace")
        expect(modal).to_contain_text("Forward by replace", timeout=10000)

    def test_forward_redirect_opens_new_modal(self, basic_page):
        """Clicking Redirect should open the redirect modal."""
        basic_page.get_by_role("link", name="Forward_example").click()
        modal = basic_page.locator(".modal.show .modal-content").first
        expect(modal).to_be_visible()

        click_modal_button(basic_page, "Redirect")
        basic_page.wait_for_timeout(2000)
        expect(basic_page.locator(".modal-content")).to_contain_text(
            "Forwarding Example", timeout=5000
        )

    def test_forward_message_opens_stacked(self, basic_page):
        """Clicking Message should open a stacked message modal on top."""
        basic_page.get_by_role("link", name="Forward_example").click()
        modal = basic_page.locator(".modal.show .modal-content").first
        expect(modal).to_be_visible()

        click_modal_button(basic_page, "Message")
        basic_page.wait_for_timeout(2000)
        expect(basic_page.locator(".modal-content").last).to_contain_text("Message", timeout=5000)


class TestAjaxConfirm:

    def test_confirm_ajax_method(self, basic_page):
        """The 'Confirm ajax method' button should trigger a confirmation dialog."""
        basic_page.get_by_role("link", name="Confirm ajax method").click()
        modal = basic_page.locator(".modal.show")
        expect(modal).to_be_visible(timeout=5000)
        expect(modal).to_contain_text("Would you like to confirm")

    def test_yes_or_no_ajax_method(self, basic_page):
        """The 'Yes or No ajax method' button should show yes/no options."""
        basic_page.get_by_role("link", name="Yes or No ajax method").click()
        modal = basic_page.locator(".modal.show")
        expect(modal).to_be_visible(timeout=5000)
        expect(modal).to_contain_text("Press yes or no")

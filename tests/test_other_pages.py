"""Tests for remaining pages: Unbound, Adaptive, Multi Form, Validation, Formset, etc."""
import pytest
from playwright.sync_api import expect


class TestUnbound:

    def test_unbound_page_loads(self, page, base_url):
        """Unbound page should load with unbound form modal buttons."""
        page.goto(f"{base_url}/unbound")
        page.wait_for_load_state("networkidle")
        expect(page.locator("nav.navbar")).to_be_visible()

    def test_simple_unbound_modal_opens(self, page, base_url):
        """The 'Simple' unbound modal should open and display form fields."""
        page.goto(f"{base_url}/unbound")
        page.wait_for_load_state("networkidle")
        page.get_by_role("link", name="Simple").click()
        modal = page.locator(".modal.show .modal-content")
        expect(modal).to_be_visible()
        expect(modal.locator(".modal-header")).to_contain_text("Enquiry Form")
        expect(modal.locator("input[name='Name']")).to_be_visible()

    def test_field_configuration_modal(self, page, base_url):
        """The 'Field Configuration' modal should open."""
        page.goto(f"{base_url}/unbound")
        page.wait_for_load_state("networkidle")
        page.get_by_role("link", name="Field Configuration").click()
        modal = page.locator(".modal.show .modal-content")
        expect(modal).to_be_visible()
        expect(modal.locator(".modal-header")).to_contain_text("Payment Form")

    def test_field_layout_modal(self, page, base_url):
        """The 'Field Layout' modal should open."""
        page.goto(f"{base_url}/unbound")
        page.wait_for_load_state("networkidle")
        page.get_by_role("link", name="Field Layout").click()
        modal = page.locator(".modal.show .modal-content")
        expect(modal).to_be_visible()


class TestAdaptive:

    def test_adaptive_page_loads(self, page, base_url):
        """Adaptive page should load."""
        page.goto(f"{base_url}/adaptive")
        page.wait_for_load_state("networkidle")
        expect(page.locator("nav.navbar")).to_be_visible()

    def test_adaptive_modal_opens(self, page, base_url):
        """Adaptive Modal should open with radio buttons for selection."""
        page.goto(f"{base_url}/adaptive")
        page.wait_for_load_state("networkidle")
        page.get_by_role("link", name="Adaptive Modal", exact=True).click()
        modal = page.locator(".modal.show .modal-content")
        expect(modal).to_be_visible()
        expect(modal).to_contain_text("Test Title")

    def test_adaptive_boolean_modal(self, page, base_url):
        """Adaptive Modal Boolean should open with a toggle."""
        page.goto(f"{base_url}/adaptive")
        page.wait_for_load_state("networkidle")
        page.get_by_role("link", name="Adaptive Modal Boolean").click()
        modal = page.locator(".modal.show .modal-content")
        expect(modal).to_be_visible()

    def test_adaptive_select_modal(self, page, base_url):
        """Adaptive Select modal should open with a dropdown."""
        page.goto(f"{base_url}/adaptive")
        page.wait_for_load_state("networkidle")
        page.get_by_role("link", name="Adaptive Select").click()
        modal = page.locator(".modal.show .modal-content")
        expect(modal).to_be_visible()


class TestMultiForm:

    def test_multi_form_page_loads(self, page, base_url):
        """Multi Form page should load."""
        page.goto(f"{base_url}/multi-form")
        page.wait_for_load_state("networkidle")
        expect(page.locator("nav.navbar")).to_be_visible()


class TestValidation:

    def test_validation_page_loads(self, page, base_url):
        """Validation page should load."""
        page.goto(f"{base_url}/Validation")
        page.wait_for_load_state("networkidle")
        expect(page.locator("nav.navbar")).to_be_visible()


class TestFormset:

    def test_formset_page_loads(self, page, base_url):
        """Formset page should load with a datatable."""
        page.goto(f"{base_url}/formset")
        page.wait_for_load_state("networkidle")
        expect(page.locator("nav.navbar")).to_be_visible()

    def test_add_formset_modal(self, page, base_url):
        """'Add' button should open a formset modal."""
        page.goto(f"{base_url}/formset")
        page.wait_for_load_state("networkidle")
        page.get_by_role("link", name="Add", exact=True).click()
        modal = page.locator(".modal.show .modal-content")
        expect(modal).to_be_visible()
        expect(modal.locator("input[name='name']")).to_be_visible()


class TestMfFormset:

    def test_mf_formset_page_loads(self, page, base_url):
        """MF Formset page should load."""
        page.goto(f"{base_url}/mf-formset")
        page.wait_for_load_state("networkidle")
        expect(page.locator("nav.navbar")).to_be_visible()


class TestDatatables:

    def test_datatables_page_loads(self, page, base_url):
        """Datatables page should load with an interactive table."""
        page.goto(f"{base_url}/datatables")
        page.wait_for_load_state("networkidle")
        expect(page.locator("nav.navbar")).to_be_visible()
        expect(page.locator("table").first).to_be_visible()


class TestUpload:

    def test_upload_page_loads(self, page, base_url):
        """Upload page should load."""
        page.goto(f"{base_url}/Upload")
        page.wait_for_load_state("networkidle")
        expect(page.locator("nav.navbar")).to_be_visible()


class TestAjax:

    def test_ajax_page_loads(self, page, base_url):
        """Ajax page should load."""
        page.goto(f"{base_url}/Ajax")
        page.wait_for_load_state("networkidle")
        expect(page.locator("nav.navbar")).to_be_visible()


class TestPermissions:

    def test_permissions_page_loads(self, page, base_url):
        """Permissions page should load."""
        page.goto(f"{base_url}/Permissions")
        page.wait_for_load_state("networkidle")
        expect(page.locator("nav.navbar")).to_be_visible()


class TestUsers:

    def test_users_page_loads(self, page, base_url):
        """Users page should load with user management buttons."""
        page.goto(f"{base_url}/Users")
        page.wait_for_load_state("networkidle")
        expect(page.locator("nav.navbar")).to_be_visible()


class TestBase64:

    def test_base64_page_loads(self, page, base_url):
        """Base64 page should load."""
        page.goto(f"{base_url}/base64")
        page.wait_for_load_state("networkidle")
        expect(page.locator("nav.navbar")).to_be_visible()


class TestNoModal:

    def test_no_modal_page_loads(self, page, base_url):
        """No modal page should load a non-modal form."""
        resp = page.goto(f"{base_url}/nomodal/-")
        assert resp.status == 200

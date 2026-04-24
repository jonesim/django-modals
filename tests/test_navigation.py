"""Tests for page navigation and loading across all main pages."""
import pytest
from playwright.sync_api import expect


PAGES = [
    ("/Basic", "Basic"),
    ("/unbound", "Unbound"),
    ("/layout", "Layout"),
    ("/crud", "CRUD"),
    ("/Model", "Model"),
    ("/multi-form", "Multi Form"),
    ("/adaptive", "Adaptive"),
    ("/Users", "Users"),
    ("/Permissions", "Permissions"),
    ("/Widgets", "Widgets"),
    ("/Upload", "Upload"),
    ("/Ajax", "Ajax"),
    ("/Validation", "Validation"),
    ("/base64", "Base64"),
    ("/formset", "Formset"),
    ("/mf-formset", "MF Formset"),
    ("/datatables", "Datatables"),
]


@pytest.mark.parametrize("path,label", PAGES)
def test_page_loads_successfully(page, base_url, path, label):
    """Each main page should load with a 200 status and show the navbar."""
    resp = page.goto(f"{base_url}{path}")
    assert resp.status == 200, f"{label} page returned {resp.status}"
    expect(page.locator("nav.navbar")).to_be_visible()


def test_navbar_links_present(page, base_url):
    """The navbar should contain links to all major sections."""
    page.goto(f"{base_url}/Basic")
    nav = page.locator("nav.navbar")
    for _, label in [("/Basic", "Basic"), ("/crud", "CRUD"), ("/Model", "Model"),
                     ("/Widgets", "Widgets"), ("/formset", "Formset")]:
        expect(nav.get_by_text(label, exact=True)).to_be_visible()


def test_root_redirects_to_basic(page, base_url):
    """The root URL should redirect to the Basic page."""
    page.goto(f"{base_url}/")
    page.wait_for_url("**/Basic")
    expect(page.get_by_role("heading", name="SimpleModal")).to_be_visible()


def test_favicon_redirect(page, base_url):
    """favicon.ico should redirect to a static file."""
    resp = page.goto(f"{base_url}/favicon.ico")
    assert resp.status == 200


def test_admin_accessible(page, base_url):
    """Django admin should be accessible."""
    resp = page.goto(f"{base_url}/admin/")
    assert resp.status == 200

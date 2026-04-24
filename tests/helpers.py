"""Shared test helpers for the Playwright test suite."""


def wait_for_modal_ready(page, timeout=10000):
    """Wait until ajax_helpers.ajax_busy is false (modal animation finished)."""
    page.wait_for_function(
        "typeof ajax_helpers !== 'undefined' && !ajax_helpers.ajax_busy",
        timeout=timeout,
    )


def wait_modal_closed(page, timeout=10000):
    """Wait until all modals are closed (removed from DOM)."""
    page.wait_for_function(
        "typeof django_modal === 'undefined' || "
        "typeof window.djangoModalCount === 'undefined' || "
        "window.djangoModalCount === 0",
        timeout=timeout,
    )


def click_modal_button(page, button_name, timeout=10000):
    """Wait for modal to be ready, then click a button inside the active modal."""
    wait_for_modal_ready(page, timeout)
    page.locator(".modal.show").last.get_by_role("button", name=button_name).click()

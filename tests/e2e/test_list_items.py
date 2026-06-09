from evebs.models import eve_items_users


def test_list_items_shows_root_groups(page, live_server_url, root_group):
    """Market groups render on /list_items without authentication."""
    page.goto(live_server_url + '/list_items')
    assert page.locator('.list-group-item').count() > 0
    assert root_group.name in page.content()


def test_list_items_shows_items_in_leaf_group(page, live_server_url, leaf_group, eve_item):
    """Navigating into a leaf group shows item rows with checkboxes."""
    page.goto(live_server_url + f'/list_items?group_id={leaf_group.id}')
    assert page.locator('.item_checkbox').count() > 0
    assert eve_item.name in page.content()


def test_select_all_checks_all_items(auth_page, live_server_url, leaf_group, eve_item):
    """Select all button checks every checkbox and updates the badge count."""
    auth_page.goto(live_server_url + f'/list_items?group_id={leaf_group.id}')

    btn = auth_page.get_by_role('button', name='Select all')
    badge = auth_page.locator('#selected_count')
    checkboxes = auth_page.locator('.item_checkbox')
    total = checkboxes.count()

    btn.click()

    auth_page.wait_for_function(
        'document.querySelectorAll(".item_checkbox:not(:checked)").length === 0'
    )
    assert auth_page.locator('.item_checkbox:checked').count() == total
    assert str(total) + ' selected' in badge.text_content()
    assert btn.text_content().strip() == 'Deselect all'


def test_deselect_all_unchecks_all_items(auth_page, live_server_url, leaf_group, eve_item):
    """Clicking the button twice selects then deselects all items."""
    auth_page.goto(live_server_url + f'/list_items?group_id={leaf_group.id}')

    btn = auth_page.get_by_role('button', name='Select all')
    btn.click()
    auth_page.wait_for_function(
        'document.querySelectorAll(".item_checkbox:not(:checked)").length === 0'
    )

    btn.click()
    auth_page.wait_for_function(
        'document.querySelectorAll(".item_checkbox:checked").length === 0'
    )
    assert '0 selected' in auth_page.locator('#selected_count').text_content()


def test_select_group_selects_all_sub_items(auth_page, live_server_url, root_group, leaf_group, eve_item, db, user):
    """Select-all-in-sub-groups button selects every item recursively and turns green."""
    auth_page.goto(live_server_url + f'/list_items?group_id={root_group.id}')

    btn = auth_page.locator('#select_group_btn')
    btn.click()

    auth_page.wait_for_function(
        'document.getElementById("select_group_btn").classList.contains("btn-success")'
    )
    assert 'All items selected' in btn.text_content()
    assert '1' in btn.text_content()

    db.session.expire_all()
    count = db.session.execute(
        db.select(db.func.count()).select_from(eve_items_users).where(
            eve_items_users.c.user_id == user.id,
            eve_items_users.c.eve_item_id == eve_item.id,
        )
    ).scalar()
    assert count == 1


def test_deselect_group_removes_all_sub_items(auth_page, live_server_url, root_group, leaf_group, eve_item, db, user):
    """Unselect-all-in-sub-groups button removes every item from the watch list."""
    auth_page.goto(live_server_url + f'/list_items?group_id={root_group.id}')

    select_btn   = auth_page.locator('#select_group_btn')
    deselect_btn = auth_page.locator('#deselect_group_btn')

    select_btn.click()
    auth_page.wait_for_function(
        'document.getElementById("select_group_btn").classList.contains("btn-success")'
    )

    deselect_btn.click()
    auth_page.wait_for_function(
        'document.getElementById("deselect_group_btn").classList.contains("btn-success")'
    )
    assert 'All items unselected' in deselect_btn.text_content()
    assert '1' in deselect_btn.text_content()

    db.session.expire_all()
    count = db.session.execute(
        db.select(db.func.count()).select_from(eve_items_users).where(
            eve_items_users.c.user_id == user.id,
            eve_items_users.c.eve_item_id == eve_item.id,
        )
    ).scalar()
    assert count == 0

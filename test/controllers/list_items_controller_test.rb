require 'test_helper'

class ListItemsControllerTest < ActionDispatch::IntegrationTest

  def setup
    esi_fake_login

    @user.update( last_changes_in_choices: Time.now - 120 )
    @user.reload

    @item = create( :inferno_fury_cruise_missile )
  end

  test 'should change selection state' do
    assert_changes '@user.eve_items.reload.count' do
      post selection_change_list_items_url, params: { id: @item.id, check_state: 'true' }
    end

    assert_changes '@user.eve_items.reload.count', -1 do
      post selection_change_list_items_url, params: { id: @item.id, check_state: 'false' }
    end
  end

end

require 'test_helper'

class ListItemsControllerTest < ActionDispatch::IntegrationTest

  def setup
    @user = create( :user, last_changes_in_choices: Time.now - 120 )
    post '/auth/developer/callback', params: { name: @user.name }
    @user.reload

    @item = create( :inferno_fury_cruise_missile )
  end

  test 'should get edit' do
    get edit_list_items_url
    assert_response :success
  end

  test 'should get update' do
    patch list_items_url, params: { items: { 1 => :dummy } }
    assert_redirected_to edit_list_items_url
  end

  test 'should change selection state' do
    assert_changes '@user.eve_items.count' do
      post selection_change_list_items_url, params: { id: @item.id, check_state: 'true' }
    end

    assert_changes '@user.eve_items.count', -1 do
      post selection_change_list_items_url, params: { id: @item.id, check_state: 'false' }
    end
  end

  test 'should select all items for user' do
    assert_changes '@user.eve_items.count' do
      get all_list_items_url
    end
    assert_redirected_to saved_list_list_items_url
  end

end

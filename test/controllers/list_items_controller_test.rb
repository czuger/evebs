require 'test_helper'

class ListItemsControllerTest < ActionDispatch::IntegrationTest

  def setup
    esi_fake_login

    @user.update( last_changes_in_choices: Time.now - 120 )
    @user.reload

    @item = create( :inferno_fury_cruise_missile )
  end

  # test 'should get edit' do
  #   get edit_list_items_url
  #   assert_response :success
  # end

  # test 'should get update' do
  #   patch list_items_url, params: { items: { 1 => :dummy } }
  #   assert_redirected_to edit_list_items_url
  # end

  test 'should change selection state' do
    assert_changes '@user.eve_items.reload.count' do
      post selection_change_list_items_url, params: { id: @item.id, check_state: 'true' }
    end

    assert_changes '@user.eve_items.reload.count', -1 do
      post selection_change_list_items_url, params: { id: @item.id, check_state: 'false' }
    end
  end

  # test 'should select all items for user' do
  #   assert_changes '@user.eve_items.count' do
  #     get all_list_items_url
  #   end
  # end

  test 'should save current user items list, clear list and reload it' do
    assert_changes '@user.eve_items.count' do
      post selection_change_list_items_url, params: { id: @item.id, check_state: 'true' }
    end

    assert_changes 'EveItemsSavedList.count' do
      post save_list_items_url, params: { description: 'Test save' }
    end

    get clear_list_items_url
    assert_equal 0, @user.eve_items.count
    assert_redirected_to saved_list_list_items_url

    assert_changes '@user.eve_items.count' do
      get restore_list_items_url( EveItemsSavedList.first )
    end
    assert_redirected_to saved_list_list_items_url
  end

  # test 'show my items list' do
  #   post selection_change_list_items_url, params: { id: @item.id, check_state: 'true' }
  #   get my_items_list_list_items_url
	#
  #   # puts response.body
	#
	#
  #   assert :success
  #   assert_select 'a', 'Inferno Fury Cruise Missile'
  # end

  # test 'show my saved list' do
  #   post selection_change_list_items_url, params: { id: @item.id, check_state: 'true' }
  #   post save_list_items_url, params: { description: 'Test save' }
  #   get saved_list_list_items_url
	#
  #   assert :success
  #   assert_select 'td', 'Test save'
  # end


end

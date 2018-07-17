require 'test_helper'

class ProductionListsControllerTest < ActionDispatch::IntegrationTest

  def setup
    @user = create( :user )
    post '/auth/developer/callback', params: { name: @user.name }

    @blueprint = create( :blueprint )
    @eve_item = create( :inferno_fury_cruise_missile, blueprint_id: @blueprint.id )
    @trade_hub = create( :rens )

    @second_user = create( :user )
  end

  def set_pl
    @pl = create( :production_list, user_id: @user.id, eve_item_id: @eve_item.id,
                  trade_hub_id: @trade_hub.id )
  end

  test 'should get edit' do
    get edit_production_list_url( @user )
    assert_response :success
  end

  test 'should update' do
    set_pl
    patch production_list_url( @user, params: { quantity_to_produce: { @pl.id => 500 } } )
    assert_redirected_to edit_production_list_url( @user )
  end

  test 'add item in basket' do
    assert_difference 'ProductionList.count' do
      post production_lists_url, params: { trade_hub_id: @trade_hub.id, eve_item_id: @eve_item.id }
    end
    assert_response :success
  end

  test 'remove item from basket' do
    set_pl
    assert_difference 'ProductionList.count', -1 do
      post remove_production_list_check_url, params: { trade_hub_id: @trade_hub.id, eve_item_id: @eve_item.id }
    end
    assert_response :success
  end

  test 'should get character_share_list' do
    get character_share_list_url( @user )
    assert_response :success
  end

  test 'should character_share_list_update' do
    post character_share_list_update_url( @user, params: { user_id: @user.id, user: { id: @second_user.id } } )
    assert_redirected_to character_share_list_url( @user )
  end

  test 'should get accept_shared_list' do
    get character_accept_shared_list_url( @user )
    assert_response :success
  end

  test 'should accept_shared_list_update' do
    post character_accept_shared_list_update_url( @user, params: { sending_user_id: @second_user.id } )
    assert_redirected_to character_accept_shared_list_url( @user )
  end

end
require 'test_helper'

class ProductionListsControllerTest < ActionDispatch::IntegrationTest

  def setup
    esi_fake_login

    @blueprint = create( :blueprint )
    @eve_item = create( :inferno_fury_cruise_missile, blueprint_id: @blueprint.id )
    @trade_hub = create( :rens )
    create( :jita )

    @second_user = create( :user )
  end

  def set_pl
    @pl = create( :production_list, user_id: @user.id, eve_item_id: @eve_item.id,
                  trade_hub_id: @trade_hub.id )
  end

  test 'should get edit' do
    get edit_production_lists_url( @user )
    assert_response :success
  end

  test 'should update' do
    set_pl
    patch production_lists_url( @user, params: { runs_count: { @pl.id => 7 } } )
    assert_redirected_to edit_production_lists_url
  end

  test 'should create a production list from buy orders screen' do
    post create_from_prices_advices_buy_orders_production_lists_path,
         params: { eve_item_id: @eve_item.id, trade_hub_id: @trade_hub.id, runs_count: 50 }

    assert_redirected_to buy_orders_path
  end

  test 'should create a production list from prices advices immediate' do
    post create_from_prices_advices_immediate_production_lists_path,
         params: { eve_item_id: @eve_item.id, trade_hub_id: @trade_hub.id, runs_count: 50 }

    assert_redirected_to price_advices_advice_prices_path
  end

  test 'should create a production list from prices advices weekly' do
    post create_from_prices_advices_weekly_production_lists_path,
         params: { eve_item_id: @eve_item.id, trade_hub_id: @trade_hub.id, runs_count: 50 }

    assert_redirected_to price_advices_advice_prices_weekly_path
  end

  test 'add item in basket' do
    assert_difference 'ProductionList.count' do
      post production_lists_url, params: { trade_hub_id: @trade_hub.id, eve_item_id: @eve_item.id }
    end
    assert_response :success
  end

  test 'add item in basket without trade_hub' do
    assert_difference 'ProductionList.count' do
      post production_lists_url, params: { eve_item_id: @eve_item.id }
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

end
require 'test_helper'

class BuyOrdersControllerTest < ActionDispatch::IntegrationTest

  def setup
    @user = create( :user )
    post '/auth/developer/callback', params: { name: @user.name }

    @blueprint = create( :blueprint )

    @eve_item = create( :inferno_fury_cruise_missile, blueprint_id: @blueprint.id )
    @trade_hub = create( :jita )

    @user.eve_items << @eve_item
    @user.trade_hubs << @trade_hub

    create( :buy_orders_analytic, trade_hub_id: @trade_hub.id, eve_item_id: @eve_item.id )
  end

  test 'should show buy orders page' do
    get buy_orders_url
    assert_response :success

    assert_select 'td', 'Jita (The Forge)'
    assert_select 'a', 'Inferno Fury Cruise Missile'
  end
end

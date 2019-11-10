require 'test_helper'

class MarketDataControllerTest < ActionDispatch::IntegrationTest

  def setup
    esi_fake_login

    @blueprint = create( :blueprint )

    @eve_item = create( :inferno_fury_cruise_missile, blueprint_id: @blueprint.id  )
    @trade_hub = @jita

    create( :prices_min, eve_item: @eve_item, trade_hub: @trade_hub )
    create( :prices_advice, eve_item: @eve_item, trade_hub: @trade_hub )
  end

  test 'should show market overview for complex item' do
    get market_data_market_overview_url( @eve_item )
    assert_response :success

    assert_select 'a', 'Inferno Fury Cruise Missile'
    assert_select 'td', 'Jita (The Forge)'
  end

end

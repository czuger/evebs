require 'test_helper'

class ProductionCostsControllerTest < ActionDispatch::IntegrationTest

  def setup
    region = create( :the_forge )
    @jita = create( :jita, region_id: region.id  )
    @blueprint = create( :blueprint )
    @eve_item = create( :inferno_fury_cruise_missile, blueprint_id: @blueprint.id )
    create( :prices_advice, eve_item_id: @eve_item.id, trade_hub_id: @jita.id )
    # @trade_hub = TradeHub.find_by_eve_system_id( 30002544 )

    create( :eve_market_history, region: region, eve_item: @eve_item, )

    @morphite = create( :morphite )
    create( :weekly_price_detail, eve_item: @morphite, trade_hub_id: @jita.id )

    @user = create( :user )
    post '/auth/developer/callback', params: { name: @user.name }
  end

  test 'should get items costs' do
    get production_cost_url( @eve_item )
    assert_response :success
  end

  test 'should get production_cost_dailies_avg_prices' do
    get production_cost_dailies_avg_prices_url( @morphite, @jita )
    assert_response :success

    assert_select 'a', 'Morphite'
    assert_select 'td', '2018-10-01'
  end

  test 'should get production_cost_market_histories_url' do
    get production_cost_market_histories_url( @eve_item )
    assert_response :success

    assert_select 'a', 'Inferno Fury Cruise Missile'
    assert_select 'td', 'The Forge'
  end

end

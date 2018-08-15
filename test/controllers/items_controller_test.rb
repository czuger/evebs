require 'test_helper'

class ItemsControllerTest < ActionDispatch::IntegrationTest

  def setup
    region = create( :the_forge )
    @jita = create( :jita, region_id: region.id  )
    @blueprint = create( :blueprint )
    @eve_item = create( :inferno_fury_cruise_missile, blueprint_id: @blueprint.id )
    create( :prices_advice, eve_item_id: @eve_item.id, trade_hub_id: @jita.id, region_id: region.id )
    # @trade_hub = TradeHub.find_by_eve_system_id( 30002544 )

    @user = create( :user )
    post '/auth/developer/callback', params: { name: @user.name }
  end

  test 'should get items costs' do
    get item_cost_url( @eve_item.id )
    assert_response :success
  end

  test 'should show item detail' do
    get item_url( @eve_item )
    assert_response :success
  end

  test 'should show item detail of an item.' do
    get item_url( @eve_item )
    assert_response :success
  end

  test 'should show trade_hub detail' do
    get item_trade_hub_detail_url( item_id: @eve_item.id, trade_hub_id: @jita.id )
    assert_response :success
  end

end

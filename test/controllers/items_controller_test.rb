require 'test_helper'

class ItemsControllerTest < ActionDispatch::IntegrationTest

  def setup
    region = create( :the_forge )
    @jita = create( :jita, region_id: region.id  )
    @blueprint = create( :blueprint )
    @eve_item = create( :inferno_fury_cruise_missile, blueprint_id: @blueprint.id )
    create( :prices_advice, eve_item_id: @eve_item.id, trade_hub_id: @jita.id )
    # @trade_hub = TradeHub.find_by_eve_system_id( 30002544 )
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
    get market_data_trade_hub_detail_url( @eve_item.id, @jita.id )
    assert_response :success
	end

	test 'should show root groups' do
		get list_items_url
		assert_response :success
	end

	test 'should show item groups' do
		get list_items_url( group_id: @eve_item.market_group_id )
		assert_response :success
	end

end

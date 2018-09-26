require 'test_helper'

class ProductionCostsControllerTest < ActionDispatch::IntegrationTest

  def setup
    region = create( :the_forge )
    @jita = create( :jita, region_id: region.id  )
    @blueprint = create( :blueprint )
    @eve_item = create( :inferno_fury_cruise_missile, blueprint_id: @blueprint.id )
    create( :prices_advice, eve_item_id: @eve_item.id, trade_hub_id: @jita.id )
    # @trade_hub = TradeHub.find_by_eve_system_id( 30002544 )

    @user = create( :user )
    post '/auth/developer/callback', params: { name: @user.name }
  end

  test 'should get items costs' do
    get production_cost_url( @eve_item )
    assert_response :success
  end

end

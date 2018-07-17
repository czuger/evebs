require 'test_helper'

class ItemsControllerTest < ActionDispatch::IntegrationTest

  def setup
    @heimatar = create( :heimatar )
    @blueprint = create( :blueprint )
    @eve_item = create( :inferno_fury_cruise_missile, blueprint_id: @blueprint.id )
    # @trade_hub = TradeHub.find_by_eve_system_id( 30002544 )

    @user = create( :user, last_changes_in_choices: Time.now - 120, region: @heimatar )
    post '/auth/developer/callback', params: { name: @user.name }
  end

  test "should get items costs" do
    get item_cost_url( @eve_item.id )
    assert_response :success
  end

  test "should show item detail" do
    get @eve_item.id
    assert_response :success
  end

  test "should show item detail of an item that has no CrestPricesLastMonthAverage information" do
    # We create a region with no CrestPricesLastMonthAverage informations
    @domain = create( :domain, items: EveItem.all )
    get @eve_item.id
    assert_response :success
  end

end

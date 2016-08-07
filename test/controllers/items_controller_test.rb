require 'test_helper'

class ItemsControllerTest < ActionController::TestCase

  def setup
    @heimatar = create( :heimatar )
    @user = create( :user, last_changes_in_choices: Time.now - 120, region: @heimatar )
    @eve_item = EveItem.find_by_cpp_eve_item_id( 2621 )
    @trade_hub = TradeHub.find_by_eve_system_id( 30002544 )
    session[:user_id] = @user.id
  end

  test "should get items costs" do
    get :cost, item_id: @eve_item.id
    assert_response :success
  end

  test "should show item detail" do
    get :show, id: @eve_item.id
    assert_response :success
  end

  test "should show item detail of an item that has no CrestPricesLastMonthAverage information" do
    # We create a region with no CrestPricesLastMonthAverage informations
    @domain = create( :domain, items: EveItem.all )
    get :show, id: @eve_item.id
    assert_response :success
  end

end

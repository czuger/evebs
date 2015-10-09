require 'test_helper'

class PriceAdvicesControllerTest < ActionController::TestCase

  def setup
    @heimatar = create( :heimatar )
    @user = create( :user, last_changes_in_choices: Time.now - 120, region: @heimatar )
    @eve_item = EveItem.find_by_cpp_eve_item_id( 2621 )
    @trade_hub = TradeHub.find_by_eve_system_id( 30002544 )
    session[:user_id] = @user.id
  end

  test "should show prices for current user" do
    get :advice_prices
    assert_response :success
  end

  test "should show prices for current user with last months averages" do
    get :advice_prices
    assert_response :success
  end

  test "should advice monthly prices" do
    get :advice_prices_monthly
    assert_response :success
  end


  test "should show challenged prices without min prices" do
    MinPrice.find_by_eve_item_id_and_trade_hub_id( @eve_item, @trade_hub ).destroy
    create( :trade_order, user: @user, trade_hub: @trade_hub, eve_item: @eve_item, new_order: true )
    get :show_challenged_prices
    assert_response :success
  end

  test "should show challenged prices with min prices" do
    create( :trade_order, user: @user, trade_hub: @trade_hub, eve_item: @eve_item, new_order: true )
    get :show_challenged_prices
    assert_response :success
  end

  test "should show item detail" do
    get :show_item_detail, item_id: @eve_item.id
    assert_response :success
  end

  test "should show item detail of an item that has no CrestPricesLastMonthAverage information" do
    # We create a region with no CrestPricesLastMonthAverage informations
    @domain = create( :domain, items: EveItem.all )
    get :show_item_detail, item_id: @eve_item.id
    assert_response :success
  end

  test "update basket" do
    get :update_basket, item_code: "#{@user.id}|#{@trade_hub.id}|#{@eve_item.id}", checked: 'true'
    assert_response :success
  end

end

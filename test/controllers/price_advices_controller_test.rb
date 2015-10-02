require 'test_helper'

class PriceAdvicesControllerTest < ActionController::TestCase

  def setup
    @user = create( :user, last_changes_in_choices: Time.now - 120 )
    session[:user_id] = @user.id
    @trade_hub = create( :trade_hub )
    @user.trade_hubs << @trade_hub
    @blueprint = create( :blueprint )
    @user.eve_items << @blueprint.eve_item
    create( :trade_order, user: @user, trade_hub: @trade_hub, eve_item: @blueprint.eve_item, new_order: true )
    @min_price = create( :min_price, eve_item: @blueprint.eve_item, trade_hub: @trade_hub  )
  end

  test "should show prices for current user" do
    get :advice_prices
    assert_response :success
  end

  test "should show prices for current user with last months averages" do
    create( :crest_prices_last_month_average, region: @trade_hub.region, eve_item: @blueprint.eve_item )
    get :advice_prices
    assert_response :success
  end

  test "should advice monthly prices" do
    create( :crest_prices_last_month_average, region: @trade_hub.region, eve_item: @blueprint.eve_item, avg_price_avg: 50000000 )
    create( :crest_prices_last_month_average, region: @trade_hub.region, eve_item: @user.eve_items.first, avg_price_avg: 50000000 )
    get :advice_prices_monthly
    assert_response :success
  end


  test "should show challenged prices without min prices" do
    @min_price.destroy
    get :show_challenged_prices
    assert_response :success
  end

  test "should show challenged prices with min prices" do
    get :show_challenged_prices
    assert_response :success
  end

end

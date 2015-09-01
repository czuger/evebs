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
  end

  test "should show prices for current user" do
    get :advice_prices
    assert_response :success
  end

  test "should show challenged prices without min prices" do
    get :show_challenged_prices
    assert_response :success
  end

  test "should show challenged prices with min prices" do
    create( :min_price, eve_item: @blueprint.eve_item, trade_hub: @trade_hub )
    get :show_challenged_prices
    assert_response :success
  end

end

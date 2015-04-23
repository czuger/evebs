require 'test_helper'

class PriceAdvicesControllerTest < ActionController::TestCase

  def setup
    @user = create( :user, last_changes_in_choices: Time.now - 120 )
    session[:user_id] = @user.id
    @trade_hub = create( :trade_hub )
    @user.trade_hubs << @trade_hub
    @blueprint = create( :blueprint )
    @min_price = create( :min_price, eve_item: @blueprint.eve_item, trade_hub: @trade_hub )
    @user.eve_items << @blueprint.eve_item
  end
  test "should show prices for current user" do
    get :show
    assert_response :success
  end

end

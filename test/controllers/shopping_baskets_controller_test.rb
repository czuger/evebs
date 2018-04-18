require 'test_helper'

class ShoppingBasketsControllerTest < ActionDispatch::IntegrationTest

  test "should get show" do
    @user = create( :user, last_changes_in_choices: Time.now - 120, region: @heimatar )
    post '/auth/developer/callback', params: { name: @user.name }
    get shopping_baskets_url
    assert_response :success
  end

end

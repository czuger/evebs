require 'test_helper'

class ShoppingBasketsControllerTest < ActionController::TestCase

  test "should get show" do
    @user = create( :user, last_changes_in_choices: Time.now - 120, region: @heimatar )
    session[:user_id] = @user.id
    get :show
    assert_response :success
  end

end

require 'test_helper'

class ChooseTradeHubsControllerTest < ActionController::TestCase

  def setup
    user = create( :user )
    session[:user_id] = user.id
    create( :trade_hub )
  end

  test "should get edit" do
    get :edit
    assert_response :success
  end

  test "should get update" do
    get :update
    assert_redirected_to edit_choose_trade_hubs_path
  end

end

require 'test_helper'

class AdminToolsControllerTest < ActionController::TestCase

  test "should get show" do
    @user = create( :user, last_changes_in_choices: Time.now - 120, region: @heimatar, admin: true )
    session[:user_id] = @user.id
    get :show
    assert_response :success
  end

end

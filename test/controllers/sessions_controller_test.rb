require 'test_helper'

class SessionsControllerTest < ActionController::TestCase

  def setup
    # OmniAuth.config.test_mode = true
    request.env['omniauth.auth'] = OmniAuth.config.mock_auth[:github]
  end

  test "should get new" do
    get :new
    assert_response :success
  end

  test "should get create" do
    post :create, {}, {}
    assert_response :success
  end

  test "should get destroy" do
    get :destroy
    assert_redirected_to root_url
  end

end
require 'test_helper'

class IdentitiesControllerTest < ActionController::TestCase

  def setup
    # OmniAuth.config.test_mode = true
    request.env['omniauth.auth'] = OmniAuth.config.mock_auth[:github]
  end

  test "should get new" do
    get :new
    assert_response :success
  end

end

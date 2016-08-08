require 'test_helper'

class SessionsControllerTest < ActionController::TestCase

  def setup
    OmniAuth.config.test_mode = true
    OmniAuth.config.mock_auth[:twitter] = OmniAuth::AuthHash.new(
      { :provider => 'twitter', :uid => '123545', 'info' => {'email' => 'testuser@testmail.com', 'name' => 'test', 'image' => ''},
      'credentials' => {'token' => '123456', 'expires_at' => 123456789 } } )
    request.env['omniauth.auth'] = OmniAuth.config.mock_auth[:twitter]
  end

  test 'should get new' do
    get :new
    assert_response :success
  end

  test 'should get create' do
    post :create, provider: :twitter
    assert_redirected_to price_advices_advice_prices_url
  end

  test 'should get destroy' do
    get :destroy
    assert_redirected_to root_url
  end

end
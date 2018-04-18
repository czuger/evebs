require 'test_helper'

class SessionsControllerTest < ActionDispatch::IntegrationTest

  def setup
    OmniAuth.config.test_mode = true
    OmniAuth.config.mock_auth[:twitter] = OmniAuth::AuthHash.new(
      { :provider => 'twitter', :uid => '123545', 'info' => {'email' => 'testuser@testmail.com', 'name' => 'test', 'image' => ''},
      'credentials' => {'token' => '123456', 'expires_at' => 123456789 } } )
    Rails.application.env_config['omniauth.auth'] = OmniAuth.config.mock_auth[:twitter]
  end

  test 'should get new' do
    get new_sessions_url
    assert_response :success
  end

  test 'should get create' do
    post '/auth/twitter/callback'
    assert_redirected_to price_advices_advice_prices_url
  end

  test 'should get destroy' do
    get signout_url
    assert_redirected_to root_url
  end

end
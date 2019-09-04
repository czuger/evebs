require 'test_helper'

class SessionsControllerTest < ActionDispatch::IntegrationTest

  def setup
    OmniAuth.config.test_mode = true
    OmniAuth.config.mock_auth[:eve_online_sso] = OmniAuth::AuthHash.new(
      { :provider => 'eve_online_sso', :uid => '123545',
        'info' => {'email' => 'testuser@testmail.com', 'name' => 'test', 'image' => '', character_id: 123456,
                   expires_on: ( Time.now + 100.year ).to_s },
        'credentials' => {'token' => '123456', 'expires_at' => 123456789 } } )
    Rails.application.env_config['omniauth.auth'] = OmniAuth.config.mock_auth[:eve_online_sso]
  end

  def teardown
    OmniAuth.config.test_mode = false
  end

  test 'should get create' do
    post '/auth/eve_online_sso/callback'
    assert_redirected_to buy_orders_url
  end

  test 'should get destroy' do
    get signout_url
    assert_redirected_to root_url
  end

  # test 'developpment mode should be forbidden in production mode' do
  #   get signout_url
  #   OmniAuth.config.test_mode = false
  #   @user = create( :user )
	#
  #   # We fake the production mode
  #   current_mode = Rails.env
  #   Rails.env = ActiveSupport::StringInquirer.new('production')
  #   # Then assert that developer mode raises in production
  #   assert_raises do
  #     post '/auth/developer/callback', params: { name: @user.name }
  #   end
  #   Rails.env = current_mode
  # end


end
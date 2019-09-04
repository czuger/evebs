require 'test_helper'

class JitaMarginsControllerTest < ActionDispatch::IntegrationTest

  def setup
    # @component = create( :component_morphite )
    #
    # @user = create( :user )
    # post '/auth/developer/callback', params: { name: @user.name }
  end

  test 'should show front page when no user is connected' do
    get '/'
    assert_response :success
  end

  test 'should show front page when an user is connected' do
    esi_fake_login

    get '/'
    assert_redirected_to buy_orders_url
  end

end
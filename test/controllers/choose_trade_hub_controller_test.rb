require 'test_helper'

class ChooseTradeHubsControllerTest < ActionDispatch::IntegrationTest

  def setup
     @user = create( :user )
    post '/auth/developer/callback', params: { name: @user.name }
    @trade_hub = create( :trade_hub )
  end

  test 'should get edit' do
    get edit_choose_trade_hubs_url
    assert_response :success
  end

  test 'should get update' do
    patch choose_trade_hubs_url, params: { id: @trade_hub.id }
    assert_response :success
  end

end

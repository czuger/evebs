require 'test_helper'

class ComponentsControllerTest < ActionDispatch::IntegrationTest
  test "should get show" do
    @user = create( :user )
    post '/auth/developer/callback', params: { name: @user.name }

    get components_to_buy_url( @user )
    assert_response :success
  end

end

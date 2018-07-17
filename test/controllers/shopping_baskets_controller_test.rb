require 'test_helper'

class ShoppingBasketsControllerTest < ActionDispatch::IntegrationTest

  test 'should get show' do

    @user = create( :user, last_changes_in_choices: Time.now - 120, region: @heimatar )
    post '/auth/developer/callback', params: { name: @user.name }

    get edit_production_list_url( @user )
    assert_response :success
  end

end

require 'test_helper'

class ComponentsToBuyControllerTest < ActionDispatch::IntegrationTest

  def setup
    @user = create( :user, last_changes_in_choices: Time.now - 120 )
    post '/auth/developer/callback', params: { name: @user.name }
    @user.reload
  end

  test 'should get show' do
    get components_to_buy_url @user
    assert_response :success
  end

end

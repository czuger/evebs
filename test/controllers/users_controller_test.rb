require 'test_helper'

class UsersControllerTest < ActionDispatch::IntegrationTest

  setup do
    @user = create( :user )
    post '/auth/developer/callback', params: { name: @user.name }
  end

  test 'should get edit' do
    get edit_users_url, params: { id: :dummy }
    assert_response :success
  end

  test 'should update user' do
    patch users_url, params: { id: :dummy, user: { name: @user.name, remove_occuped_places: @user.remove_occuped_places } }
    assert_redirected_to edit_users_url
  end

end

require 'test_helper'

class UsersControllerTest < ActionController::TestCase
  setup do
    @user = create( :user )
    session[:user_id] = @user.id
  end

  test "should get edit" do
    get :edit, id: @user
    assert_response :success
  end

  test "should update user" do
    patch :update, id: @user, user: { api_key: @user.api_key, key_user_id: @user.key_user_id, name: @user.name, remove_occuped_places: @user.remove_occuped_places }
    assert_response :success
  end

end

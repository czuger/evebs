require 'test_helper'

class UsersControllerTest < ActionController::TestCase
  setup do
    @user = create( :user )
    session[:user_id] = @user.id
  end

  test "should get edit" do
    get :edit, id: :dummy
    assert_response :success
  end

  test "should update user" do
    patch :update, id: :dummy, user: { api_key: @user.api_key, key_user_id: @user.key_user_id, name: @user.name, remove_occuped_places: @user.remove_occuped_places }
    assert_response :success
  end

  test "should get edit password screen" do
    get :edit_password, user_id: :dummy
    assert_response :success
  end

  test "should change password" do
    get :change_password, user_id: :dummy, new_password: '123456', new_password_confirmation: '123456'
    assert_redirected_to user_edit_password_path
  end

  test "should not change password on error" do
    get :change_password, user_id: :dummy, new_password: '123456', new_password_confirmation: '654321'
    assert_redirected_to user_edit_password_path
  end

end

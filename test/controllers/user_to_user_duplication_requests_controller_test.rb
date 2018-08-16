require 'test_helper'

class UserToUserDuplicationRequestsControllerTest < ActionDispatch::IntegrationTest
  setup do
    @user_to_user_duplication_request = user_to_user_duplication_requests(:one)
  end

  test "should get index" do
    get user_to_user_duplication_requests_url
    assert_response :success
  end

  test "should get new" do
    get new_user_to_user_duplication_request_url
    assert_response :success
  end

  test "should create user_to_user_duplication_request" do
    assert_difference('UserToUserDuplicationRequest.count') do
      post user_to_user_duplication_requests_url, params: { user_to_user_duplication_request: { duplication_type: @user_to_user_duplication_request.duplication_type, reciever_id: @user_to_user_duplication_request.reciever_id } }
    end

    assert_redirected_to user_to_user_duplication_request_url(UserToUserDuplicationRequest.last)
  end

  test "should show user_to_user_duplication_request" do
    get user_to_user_duplication_request_url(@user_to_user_duplication_request)
    assert_response :success
  end

  test "should get edit" do
    get edit_user_to_user_duplication_request_url(@user_to_user_duplication_request)
    assert_response :success
  end

  test "should update user_to_user_duplication_request" do
    patch user_to_user_duplication_request_url(@user_to_user_duplication_request), params: { user_to_user_duplication_request: { duplication_type: @user_to_user_duplication_request.duplication_type, reciever_id: @user_to_user_duplication_request.reciever_id } }
    assert_redirected_to user_to_user_duplication_request_url(@user_to_user_duplication_request)
  end

  test "should destroy user_to_user_duplication_request" do
    assert_difference('UserToUserDuplicationRequest.count', -1) do
      delete user_to_user_duplication_request_url(@user_to_user_duplication_request)
    end

    assert_redirected_to user_to_user_duplication_requests_url
  end
end

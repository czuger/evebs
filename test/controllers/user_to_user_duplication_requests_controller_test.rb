require 'test_helper'

class UserToUserDuplicationRequestsControllerTest < ActionDispatch::IntegrationTest
  setup do
    @user = create( :user )
    post '/auth/developer/callback', params: { name: @user.name }

    user2 = create( :user )
    @user_to_user_duplication_request = create( :user_to_user_duplication_request, sender: @user, receiver: user2 )
  end

  test 'should get index' do
    get user_to_user_duplication_requests_url
    assert_response :success
  end

  test 'should get new' do
    get new_user_to_user_duplication_request_url
    assert_response :success
  end

  test 'should create user_to_user_duplication_request' do
    backup_data = { duplication_type: @user_to_user_duplication_request.duplication_type, receiver_id: @user_to_user_duplication_request.receiver_id }
    @user_to_user_duplication_request.destroy
    assert_difference('UserToUserDuplicationRequest.count') do
      post user_to_user_duplication_requests_url, params: { user_to_user_duplication_request: backup_data }
    end

    assert_redirected_to user_to_user_duplication_requests_url
  end

  test 'should not create user_to_user_duplication_request' do
    assert_no_difference('UserToUserDuplicationRequest.count') do
      post user_to_user_duplication_requests_url, params: { user_to_user_duplication_request: { duplication_type: @user_to_user_duplication_request.duplication_type, receiver_id: @user_to_user_duplication_request.receiver_id } }
    end

    assert_redirected_to user_to_user_duplication_requests_url
  end


  test 'should destroy user_to_user_duplication_request' do
    assert_difference('UserToUserDuplicationRequest.count', -1) do
      delete user_to_user_duplication_request_url(@user_to_user_duplication_request)
    end

    assert_redirected_to user_to_user_duplication_requests_url
  end
end

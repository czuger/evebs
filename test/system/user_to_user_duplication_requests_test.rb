require "application_system_test_case"

class UserToUserDuplicationRequestsTest < ApplicationSystemTestCase
  setup do
    @user_to_user_duplication_request = user_to_user_duplication_requests(:one)
  end

  test "visiting the index" do
    visit user_to_user_duplication_requests_url
    assert_selector "h1", text: "User To User Duplication Requests"
  end

  test "creating a User to user duplication request" do
    visit user_to_user_duplication_requests_url
    click_on "New User To User Duplication Request"

    fill_in "Duplication Type", with: @user_to_user_duplication_request.duplication_type
    fill_in "Reciever", with: @user_to_user_duplication_request.reciever_id
    click_on "Create User to user duplication request"

    assert_text "User to user duplication request was successfully created"
    click_on "Back"
  end

  test "updating a User to user duplication request" do
    visit user_to_user_duplication_requests_url
    click_on "Edit", match: :first

    fill_in "Duplication Type", with: @user_to_user_duplication_request.duplication_type
    fill_in "Reciever", with: @user_to_user_duplication_request.reciever_id
    click_on "Update User to user duplication request"

    assert_text "User to user duplication request was successfully updated"
    click_on "Back"
  end

  test "destroying a User to user duplication request" do
    visit user_to_user_duplication_requests_url
    page.accept_confirm do
      click_on "Destroy", match: :first
    end

    assert_text "User to user duplication request was successfully destroyed"
  end
end

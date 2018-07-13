require 'test_helper'

class CharactersControllerTest < ActionDispatch::IntegrationTest
  test "should get edit" do
    get characters_edit_url
    assert_response :success
  end

  test "should get update" do
    get characters_update_url
    assert_response :success
  end

end

require 'test_helper'

class ListItemsControllerTest < ActionDispatch::IntegrationTest
  test "should get edit" do
    get list_items_edit_url
    assert_response :success
  end

  test "should get update" do
    get list_items_update_url
    assert_response :success
  end

end

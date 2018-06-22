require 'test_helper'

class ComponentsControllerTest < ActionDispatch::IntegrationTest
  test "should get show" do
    get components_show_url
    assert_response :success
  end

end

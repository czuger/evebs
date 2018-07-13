require 'test_helper'

class ComponentsToBuyControllerTest < ActionDispatch::IntegrationTest
  test "should get show" do
    get components_to_buy_show_url
    assert_response :success
  end

end

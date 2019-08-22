require 'test_helper'

class MarketGroupsControllerTest < ActionDispatch::IntegrationTest
  test "should get index" do
    get market_groups_index_url
    assert_response :success
  end

end

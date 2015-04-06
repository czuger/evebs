require 'test_helper'

class OrdersAdvicesControllerTest < ActionController::TestCase

  test "should get index" do
    get :index
    assert_response :success
    assert_not_empty assigns[:order_advices]
  end

end

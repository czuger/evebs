require 'test_helper'

class JitaMarginControllerTest < ActionController::TestCase
  test "should get show" do
    get :index
    assert_response :success
  end

  test "should get update" do
    get :update
    assert_response :success
  end

end

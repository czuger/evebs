require 'test_helper'

class JitaMarginsControllerTest < ActionController::TestCase

  def setup
    @j = create( :jita_margin )
  end

  test "should get show" do
    get :index
    assert_response :success
  end

  test "should get update" do
    put :update, id: @j.eve_item.id
    assert_redirected_to :jita_margins
  end

end

require 'test_helper'

class ChooseItemsControllerTest < ActionController::TestCase

  setup do
    @heimatar = create( :heimatar )
    @user = create( :user, last_changes_in_choices: Time.now - 120, region: @heimatar )
    session[:user_id] = @user.id
    @item = EveItem.find_by_cpp_eve_item_id( 2621 )
  end

  test "should select an item" do
    assert_difference '@user.eve_items.count' do
      post :select_items, { item: 'true', id: @item.id, check_state: 'true' }
    end
  end

  test "should get edit" do
    get :edit
    assert_response :success
  end

  test "should redirect to new session path if not logged in" do
    session[:user_id] = nil
    assigns[:current_user] = nil
    get :edit
    assert_redirected_to new_sessions_path
  end

end

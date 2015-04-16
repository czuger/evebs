require 'test_helper'

class ChooseItemsControllerTest < ActionController::TestCase

  setup do
    @user = create( :user )
    @item = create( :eve_item )
    @user.eve_items << @item
  end

  test "should get edit" do
    get :edit
    assert_response :success
  end

  test "should add to the choosed items if the item does not already exist " do
    @new_item = create( :eve_item )
    session[ :selected_items ] = [ @new_item.id ]
    assert_difference '@user.eve_items.count' do
      get :create
    end
    assert_redirected_to edit_choose_item_path(@user.id)
  end

  test "should not add to the choosed items if the item already exist " do
    session[ :selected_items ] = [ @item.id ]
    assert_no_difference '@user.reload.eve_items.count' do
      get :create
    end
    assert_redirected_to edit_choose_item_path(@user.id)
  end

end

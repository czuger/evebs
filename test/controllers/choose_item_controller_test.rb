require 'test_helper'

class ChooseItemsControllerTest < ActionController::TestCase

  setup do
    @user = create( :user )
    session[:user_id] = @user.id
    @item = create( :eve_item )
    @user.eve_items << @item
  end

  test "should get edit" do
    get :edit
    assert_response :success
  end

  test "should redirect to new session path if not logged in" do
    session[:user_id] = nil
    get :edit
    assert_redirected_to new_sessions_path
  end

  test "should add to the choosed items if the item does not already exist " do
    @new_item = create( :eve_item )
    assert_difference '@user.eve_items.count' do
      get :create, choosen_item: @new_item.id
    end
    assert_redirected_to new_choose_items_path( message: "Item(s) added successfully" )
  end

  test "should add only one item if one is selected" do
    @new_item = create( :eve_item )
    session[ :selected_items ] = [ @new_item.id ]
    assert_difference '@user.eve_items.count' do
      get :create
    end
    assert_redirected_to new_choose_items_path( message: "Item(s) added successfully" )
  end

  test "should remove one item as we keep only the new" do
    @new_item = create( :eve_item )
    @user.eve_items << @new_item
    assert_difference '@user.eve_items.count', -1 do
      get :update, items_to_keep: [@new_item.id]
    end
    assert_redirected_to edit_choose_items_path
  end

  test "should not add to the choosed items if the item already exist " do
    session[ :selected_items ] = [ @item.id ]
    assert_no_difference '@user.reload.eve_items.count' do
      get :create
    end
    assert_redirected_to new_choose_items_path( message: "Item(s) added successfully" )
  end

  test "should return an autocomplete set of items" do
    r = get :autocomplete_eve_item_name_lowcase, term: 'item'
    assert_response :success
    assert_includes session[:selected_items], @item.id
  end

end

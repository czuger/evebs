require 'test_helper'

class ChooseItemsControllerTest < ActionController::TestCase

  setup do
    @heimatar = create( :heimatar )
    @user = create( :user, last_changes_in_choices: Time.now - 120, region: @heimatar )
    session[:user_id] = @user.id
    @item = EveItem.find_by_cpp_eve_item_id( 2621 )
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

  test "should get new" do
    get :new
    assert_response :success
  end

  test "should add to the choosed items if the item does not already exist " do
    @new_item = create( :inferno_precision_cruise_missile )
    assert_difference '@user.eve_items.count' do
      get :create, choosen_item: @new_item.id
    end
    assert_redirected_to new_choose_items_path( message: "Item(s) added successfully" )
  end

  test "should add only one item if one is selected" do
    @item = create( :dummy_eve_item )
    session[ :selected_items ] = [ @item.id ]
    assert_difference '@user.eve_items.count' do
      get :create
    end
    assert_redirected_to new_choose_items_path( message: "Item(s) added successfully" )
  end

  test "should remove one item as we keep only the new" do
    get :update, items_to_keep: [@item.id]
    assert_equal 1, @user.eve_items.count
    assert_redirected_to edit_choose_items_path
  end

  test "should remove all item" do
    get :update, remove_all_items: nil
    assert_equal 0, @user.eve_items.count
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
    r = get :autocomplete_eve_item_name_lowcase, term: 'inferno'
    assert_response :success
    assert_includes session[:selected_items], @item.id
  end

end

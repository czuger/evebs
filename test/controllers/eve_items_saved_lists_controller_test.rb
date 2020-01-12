require 'test_helper'

class EveItemsSavedListsControllerTest < ActionDispatch::IntegrationTest

  def setup
    esi_fake_login

    ifcm = create( :inferno_fury_cruise_missile )
    mfcm = create( :mjolnir_fury_cruise_missile )

    @user.eve_items << ifcm
    @user.eve_items << mfcm

    @saved_list = create( :eve_items_saved_list, user: @user, saved_ids: [ifcm.id, mfcm.id] )
  end

  test 'should get index' do
    get eve_items_saved_lists_url
    assert_response :success
  end

  test 'should get new' do
    get new_eve_items_saved_list_url
    assert_response :success
  end

  test 'should clear current list' do
    assert_difference '@user.eve_items.count', -2 do
      get eve_items_saved_lists_clear_url
    end
    assert_redirected_to eve_items_saved_lists_url
  end

  test 'should create' do
    assert_difference '@user.eve_items_saved_lists.count', 1 do
      post eve_items_saved_lists_url, params: { description: 'test' }
    end
    assert_redirected_to eve_items_saved_lists_url
    follow_redirect!
  end

  test 'should remove saved list' do
    assert_difference '@user.eve_items_saved_lists.count', -1 do
      delete eve_items_saved_list_url( @saved_list.id )
    end
    assert_redirected_to eve_items_saved_lists_url
    follow_redirect!
  end

  test 'should load a saved list' do
    @user.eve_items.delete_all

    assert_difference '@user.eve_items.count', 2 do
      get eve_items_saved_list_load_url( @saved_list.id )
    end
    assert_redirected_to eve_items_saved_lists_url
    follow_redirect!
  end

end

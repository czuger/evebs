require 'test_helper'

class ComponentToBuyTest < ActiveSupport::TestCase

  def setup
    @user = create( :user )
    @inf = create( :inferno_fury_cruise_missile_production_list, user: @user )
    @mjl = create( :mjolnir_fury_cruise_missile_production_list, user: @user )

    jita = TradeHub.find_by_eve_system_id( 30000142 )
    jita_station = create( :station, trade_hub: jita )
    @jita_station_detail = create( :station_detail, station: jita_station )
    @assets_station = create( :bpc_assets_station, user: @user, station_detail: @jita_station_detail )

    @morphite = EveItem.find_by_name( 'Morphite' )
  end

  def test_base_components_request
    ctb = @user.component_to_buys.find_by_name( 'Morphite' )
    assert_equal 1200*2, ctb.total_cost
    assert_equal 0.15*2, ctb.required_volume
    assert_equal 15*2, ctb.qtt_to_buy
  end

  def test_with_higher_volumes
    inf_runs = 137
    mjl_runs = 239

    @inf.update( runs_count: inf_runs, quantity_to_produce: inf_runs*100 )
    @mjl.update( runs_count: mjl_runs, quantity_to_produce: mjl_runs*100 )

    ctb = @user.component_to_buys.reload.find_by_name( 'Morphite' )

    assert_equal 1200 * inf_runs + 1200 * mjl_runs, ctb.total_cost
    assert_equal ( 0.15 * inf_runs + 0.15 * mjl_runs ).round( 1 ), ctb.required_volume
    assert_equal 15 * inf_runs + 15 * mjl_runs, ctb.qtt_to_buy
  end

  def test_with_higher_volumes_and_blueprint_modification
    inf_runs = 137
    mjl_runs = 239

    @inf.update( runs_count: inf_runs, quantity_to_produce: inf_runs*100 )
    @mjl.update( runs_count: mjl_runs, quantity_to_produce: mjl_runs*100 )

    create( :blueprint_modification, user: @user, blueprint: @inf.eve_item.blueprint, percent_modification_value: 0.97 )

    ctb = @user.component_to_buys.find_by_name( 'Morphite' )

    assert_equal 1200 * inf_runs * 0.97 + 1200 * mjl_runs, ctb.total_cost
    assert_equal ( 0.15 * inf_runs * 0.97 + 0.15 * mjl_runs ).round( 1 ), ctb.required_volume.round( 1 )
    assert_equal 15 * inf_runs * 0.97 + 15 * mjl_runs, ctb.qtt_to_buy
  end

  def test_with_higher_volumes_and_double_blueprint_modification
    inf_runs = 137
    mjl_runs = 239

    @inf.update( runs_count: inf_runs, quantity_to_produce: inf_runs*100 )
    @mjl.update( runs_count: mjl_runs, quantity_to_produce: mjl_runs*100 )

    create( :blueprint_modification, user: @user, blueprint: @inf.eve_item.blueprint, percent_modification_value: 0.97 )
    create( :blueprint_modification, user: @user, blueprint: @mjl.eve_item.blueprint, percent_modification_value: 0.93 )
    
    # pp BlueprintModification.all

    ctb = @user.component_to_buys.reload.find_by_name( 'Morphite' )

    assert_equal 1200 * inf_runs * 0.97 + 1200 * mjl_runs * 0.93, ctb.total_cost
    assert_equal ( 0.15 * inf_runs * 0.97 + 0.15 * mjl_runs * 0.93 ).round( 1 ), ctb.required_volume.round( 1 )
    assert_equal 15 * inf_runs * 0.97 + 15 * mjl_runs * 0.93, ctb.qtt_to_buy
  end

  def test_with_higher_volumes_and_double_blueprint_modification_and_present_assets
    inf_runs = 137
    mjl_runs = 239

    @inf.update( runs_count: inf_runs, quantity_to_produce: inf_runs*100 )
    @mjl.update( runs_count: mjl_runs, quantity_to_produce: mjl_runs*100 )

    create( :blueprint_modification, user: @user, blueprint: @inf.eve_item.blueprint, percent_modification_value: 0.97 )
    create( :blueprint_modification, user: @user, blueprint: @mjl.eve_item.blueprint, percent_modification_value: 0.93 )

    create( :bpc_asset, station_detail: @jita_station_detail, eve_item: @morphite, quantity: 547, user: @user )
    @user.update( selected_assets_station_id: @jita_station_detail.id )

    ctb = @user.component_to_buys.reload.find_by_name( 'Morphite' )

    # assert_equal 1200 * inf_runs * 0.97 + 1200 * mjl_runs * 0.93, ctb.total_cost
    # assert_equal ( 0.15 * inf_runs * 0.97 + 0.15 * mjl_runs * 0.93 ).round( 1 ), ctb.required_volume.round( 1 )
    assert_equal 15 * inf_runs * 0.97 + 15 * mjl_runs * 0.93 - 547, ctb.qtt_to_buy
  end

end
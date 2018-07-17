require 'test_helper'

class TradeOrderTestDummy
  def initialize( station_id = 0, type_id = 0 )
    @station_id = station_id
    @type_id = type_id
  end
  def scope=( _ )
  end
  def Characters
    TradeOrderTestDummy.new( @station_id, @type_id )
  end
  def characters
    [ TradeOrderTestDummy.new( @station_id, @type_id ) ]
  end
  def characterID
    0
  end
  def MarketOrders( _ )
    TradeOrderTestDummy.new( @station_id, @type_id )
  end
  def orders
    [ TradeOrderTestDummy.new( @station_id, @type_id ) ]
  end
  def orderState
    '0'
  end
  def typeID
    @type_id
  end
  def stationID
    @station_id
  end
  def price
    0
  end
end

class TradeOrderTest < ActiveSupport::TestCase

  def setup
    @tu = create( :station )
    @blueprint = create( :blueprint )
    @item = create( :eve_item, blueprint_id: @blueprint.id )
    @user = create( :user )
  end

  def teardown
  end

  # test 'Should get trade orders and create no order' do
  #   create( :trade_order, trade_hub_id: @tu.id, eve_item_id: @item.id, user_id: @user.id )
  #   assert_no_difference 'TradeOrder.count' do
  #     TradeOrder.get_trade_orders( @user )
  #   end
  # end

  # test 'Should get trade orders and create an order' do
  #   assert_difference 'TradeOrder.count' do
  #     TradeOrder.get_trade_orders( @user )
  #   end
  # end
  #
  # test 'Should get trade orders and create no order (print errors)' do
  #   EAAL::API.unstub( :new )
  #   EAAL::API.stubs( :new ).returns( TradeOrderTestDummy.new )
  #   assert_no_difference 'TradeOrder.count' do
  #     TradeOrder.get_trade_orders( @user )
  #   end
  # end
end
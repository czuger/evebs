require 'test_helper'

class TradeHubTestDummy
  def initialize( station_id = 0, type_id = 0 )
    @station_id = station_id
    @type_id = type_id
  end
  def scope=( _ )
  end
  def CharacterID( _ )
    TradeHubTestDummy.new(@station_id, @type_id )
  end
  def characters
    [TradeHubTestDummy.new(@station_id, @type_id ) ]
  end
  def characterID
    5
  end
end

class TradeHubTest < ActiveSupport::TestCase

  # test 'Should setup trade hubs' do
  #
  #   TradeHub.delete_all
  #
  #   @tu = create( :station )
  #   @item = create( :eve_item )
  #   EAAL::API.stubs( :new ).returns(TradeHubTestDummy.new(@tu.cpp_station_id, @item.cpp_eve_item_id ) )
  #
  #   Setup::TradeHubs.new
  #
  #   EAAL::API.unstub( :new )
  # end


end

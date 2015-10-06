require 'open-uri'
require 'open-uri/cached'
require 'pp'

class Crest::GetPriceHistory

  include Crest::CrestBase
  
  MAIN_TRADE_REGIONS = { 10000002 => 'The Forge	', 10000032 => 'Sinq Laison	', 10000043 => 'Domain	', 10000030 => 'Heimatar	', 10000042 => 'Metropolis	' }

  LESSER_TRADE_REGIONS = { 10000069 => 'Black Rise	', 10000012 => 'Curse	', 10000036 => 'Devoid	',
    10000064 => 'Essence	', 10000058 => 'Fountain	', 10000067 => 'Genesis	', 10000049 => 'Khanid	', 10000065 => 'Kor-Azor	',
    10000016 => 'Lonetrek	', 10000028 => 'Molden Heath	', 10000048 => 'Placid	', 10000047 => 'Providence	' }

  MARGINAL_TRADE_REGIONS = { 10000055 => 'Branch	', 10000007 => 'Cache	', 10000014 => 'Catch	', 10000051 => 'Cloud Ring	',
    10000053 => 'Cobalt Edge	', 10000054 => 'Aridia	', 10000035 => 'Deklein	', 10000060 => 'Delve	', 10000001 => 'Derelik	',
    10000005 => 'Detorid	', 10000039 => 'Esoteria	', 10000027 => 'Etherium Reach	', 10000037 => 'Everyshore	',
    10000046 => 'Fade	', 10000056 => 'Feythabolis	', 10000029 => 'Geminate	', 10000011 => 'Great Wildlands	',
    10000025 => 'Immensea	', 10000031 => 'Impass	', 10000009 => 'Insmother	', 10000052 => 'Kador	', 10000013 => 'Malpais	',
    10000040 => 'Oasa	', 10000062 => 'Omist	', 10000021 => 'Outer Passage	', 10000057 => 'Outer Ring	', 10000059 => 'Paragon Soul	',
    10000063 => 'Period Basis	', 10000066 => 'Perrigen Falls	', 10000023 => 'Pure Blind	', 10000050 => 'Querious	' }

  UNKNOWN_TRADE_REGIONS = { 10000019=>nil, 11000001=>nil, 11000002=>nil, 11000003=>nil, 11000004=>nil, 11000005=>nil,
    11000006=>nil, 11000007=>nil, 11000008=>nil, 11000009=>nil, 11000010=>nil, 11000011=>nil, 11000012=>nil, 11000013=>nil,
    11000014=>nil, 11000015=>nil, 11000016=>nil, 11000017=>nil, 11000018=>nil, 11000019=>nil, 11000020=>nil, 11000021=>nil,
    11000022=>nil, 11000023=>nil, 11000024=>nil, 11000025=>nil, 11000026=>nil, 11000027=>nil, 11000028=>nil, 11000029=>nil,
    11000030=>nil, 11000031=>nil, 11000032=>nil, 10000017=>nil, 11000033=>nil }

  # TODO : there are trade hub that have no regions : take care of that - protect region access

  def initialize( low_level_transactions = false )
    @low_level_transactions = low_level_transactions
  end

  def get_watched_items_and_region_only()
    used_items, used_trade_hubs = User.get_used_items_and_trade_hubs
    regions = used_trade_hubs.map{ |e| e.region }
    used_items = used_items.map{ |e| [e.id,e.cpp_eve_item_id] }
    regions.each do |region|
      puts "About to retrieve price history for #{region.name}"
      if @low_level_transactions
        get_region_history( region, used_items )
      else
        ActiveRecord::Base.transaction{get_region_history( region, used_items )}
      end
    end
    # Update monthly averages
    Crest::ComputePriceHistoryAvg.new
  end

  def get_jita_components_prices()
    regions = [ Region.find_by_cpp_region_id( Component::JITA_REGION_CPP_ID ) ]
    used_items = EveItem.where( involved_in_blueprint: true ).all
    used_items = used_items.map{ |e| [e.id,e.cpp_eve_item_id] }
    regions.each do |region|
      puts "About to retrieve price history for #{region.name}"
      if @low_level_transactions
        get_region_history( region, used_items )
      else
        ActiveRecord::Base.transaction{get_region_history( region, used_items )}
      end
    end
    # Update monthly averages
    Crest::ComputePriceHistoryAvg.new
  end

  def regionset_update( region_set )
    eve_item_ids_involved_in_blueprints = EveItem.where( involved_in_blueprint: true ).pluck( :id, :cpp_eve_item_id )
    Region.where( cpp_region_id: region_set.keys ).each do |region|
      puts "About to retrieve price history for #{region.name}"
      if @low_level_transactions
        get_region_history( region, eve_item_ids_involved_in_blueprints )
      else
        ActiveRecord::Base.transaction{get_region_history( region, eve_item_ids_involved_in_blueprints )}
      end
    end
    # Update monthly averages
    Crest::ComputePriceHistoryAvg.new
  end

  private

  def get_region_history( region, eve_item_ids_involved_in_blueprints )
    eve_item_ids_involved_in_blueprints.each do |eve_item_array|
      begin
        get( region, eve_item_array )
      rescue OpenURI::HTTPError
        # Nevermind if we can't read
      rescue StandardError => e
        p e.inspect
        p e.message
        p e.backtrace
        exit
      end
    end
  end

  def get( region, eve_item_array )

    html_req = get_crest_url( "market/#{region.cpp_region_id}/types/#{eve_item_array[1]}/history" )
    # puts html_req
    json_result = open( html_req ).read

    parsed_data = JSON.parse( json_result )

    items = parsed_data['items']
    present_timestamps = CrestPriceHistory.where( region_id: region.id, eve_item_id: eve_item_array[0] ).pluck( :day_timestamp )
    inserts = 0

    ActiveRecord::Base.transaction do

      items.each do |item_data|

        date_info = DateTime.parse( item_data['date'] )
        date_info_ts = date_info.strftime( '%Y%m%d' )
        # If we already have an information for that day, we process next record.
        next if present_timestamps.include?( date_info_ts )

        # puts "About to insert #{item_data.inspect}"
        CrestPriceHistory.create!( region_id: region.id, eve_item_id: eve_item_array[0], day_timestamp: date_info_ts, history_date: date_info,
        order_count: item_data['orderCount'], volume: item_data['volume'],
        low_price: item_data['lowPrice'], avg_price: item_data['avgPrice'], high_price: item_data['highPrice'] )

        inserts += 1
      end

    end

    puts "#{inserts} inserts for type #{eve_item_array[1]}"
  end
end
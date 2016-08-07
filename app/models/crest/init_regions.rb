require 'open-uri'
# require 'open-uri/cached'
require 'pp'

class Crest::InitRegions
  include Crest::CrestBase

  def initialize
  end

  def fill_regions
    ActiveRecord::Base.transaction do
      fill_regions_table
      link_region_to_trade_hub
    end
  end

  private

  def fill_regions_table
    parsed_data = get_parsed_data( :regions )
    parsed_data["items"].each do |item|
      name = item['name']
      cpp_id = item['href'].match( /\/(\d+)\// )[1]
      Region.find_or_create_by!( cpp_region_id: cpp_id ) do |region|
        region.name = name
      end
    end
  end

  def link_region_to_trade_hub
    parsed_data = get_parsed_data( :regions )
    parsed_data['items'].each do |region_item|
      # Reading region content
      region_cpp_id = region_item['href'].match( /(\d+)/ )[1]
      region = Region.find_by_cpp_region_id( region_cpp_id )
      item_req = region_item['href'][0 .. -2] + '/'
      json_result = open( item_req ).read
      region_content = JSON.parse( json_result )
      region_content['constellations'].each do |constellation|
        # Reading region's constellations content
        const_req = constellation['href'][0 .. -2] + '/'
        json_result = open( const_req ).read
        const_content = JSON.parse( json_result )
        const_content['systems'].each do |system|
          system_cpp_id = system['href'].match( /(\d+)/ )[1]
          trade_hub = TradeHub.find_by_eve_system_id( system_cpp_id )
          if trade_hub
            puts "#{self.class}::#{__method__} About to link #{trade_hub.name} to #{region.name}"
            region.trade_hubs << trade_hub
          end
        end
      end
    end
  end

end
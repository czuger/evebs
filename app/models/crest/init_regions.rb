require 'open-uri'
require 'open-uri/cached'
require 'pp'

class Crest::InitRegions
  include Crest::CrestBase

  def initialize
    manage_cache

    html_req = get_crest_url( :regions )
    # puts html_req
    json_result = open( html_req ).read

    parsed_data = JSON.parse( json_result )

    ActiveRecord::Base.transaction do
      parsed_data["items"].each do |item|
        name = item['name']
        cpp_id = item['href'].match( /\/(\d+)\// )[1]
        Region.find_or_create_by!( cpp_region_id: cpp_id ) do |region|
          region.name = name
        end
      end
    end
  end

end
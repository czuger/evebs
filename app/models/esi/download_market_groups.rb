class Esi::DownloadTypeInRegion < Esi::Download

  def initialize( debug_request: false )
    super( nil, {}, debug_request: debug_request )
  end

  def update
    puts 'Updating type_in_regions'
    ActiveRecord::Base.connection.execute("TRUNCATE type_in_regions RESTART IDENTITY")

    Region.pluck( :cpp_region_id ).each do |cpp_region_id|
      @rest_url = "markets/#{cpp_region_id}/types/"

      records = get_all_pages.map{ |cpp_type_id| TypeInRegion.new( cpp_region_id: cpp_region_id, cpp_type_id: cpp_type_id ) }
      TypeInRegion.import( records )

      puts "#{records.count} inserted for region #{cpp_region_id}" if @debug_request
    end

  end
end
namespace :data_setup do
  # desc "Feed regions trades hubs and stations"
  # task :regions => :environment do
  #   puts 'About to download trades hubs, regions and stations'
  #
  #   Setup::TradeHubs.new
  #
  #   c = Crest::InitRegions.new
  #   c.fill_regions
  #
  #   open( 'http://biotronics.basicaware.de/eve/download/StationID2Name.txt' ) do |file|
  #     file.readlines.each do |line|
  #       sl = line.split( "\t" )
  #       station_id=sl[0]
  #       unless Station.find_by_cpp_station_id( station_id )
  #         station_name=sl[1][0..-2].strip
  #         system_name=station_name.split(' ').first
  #         trade_hub=TradeHub.where('name=?',system_name).first
  #         if trade_hub
  #           puts "About to insert : #{station_id}, #{station_name}, #{trade_hub}"
  #           Station.find_or_create_by( trade_hub_id: trade_hub.id, name: station_name, cpp_station_id: station_id )
  #         end
  #       end
  #     end
  #   end
  # end

  desc 'Finding the prefect industrial station'
  task :find_station => :environment do
    # Esi::IndustryStationFinder.new.fill_station_table
    # Esi::IndustryStationFinder.new.update_security_status
    # Esi::IndustryStationFinder.new.update_jita_distance
    Esi::IndustryStationFinder.new.update_industry_systems
  end

  desc 'Update the structures'
  task :structures => :environment do
    Esi::DownloadStructuresData.new( debug_request: false ).update
  end

  desc 'Update universe - regions'
  task :regions => :environment do
    # Esi::DownloadUniverseRegions.new(debug_request: true ).download
    Process::UpdateUniverseRegions.new.update
    Process::UpdateTradeHubs.new.update
  end

  desc 'Get the base prices for reactions'
  task :reactions => :environment do
    Esi::DownloadReactionsComponentsPrices.new.download
  end

end
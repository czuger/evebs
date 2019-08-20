require_relative 'download'

# Seems not to require full download of all prices history
# Just jita, see ...
class Esi::DownloadHistory < Esi::Download

  # TODO : Une fois le boulot fait, il faudra supprimer EveMarketHistory et la vue associé (ne pas oublier les modèles)

  def download
    Misc::Banner.p 'About to download regional sales volumes'

    1.upto(Esi::DownloadHistoryReadItemsLists::PROCESSES_COUNT).each do |process_id|
      start_process_and_download( UniverseRegion.where( download_process_id: process_id ), process_id )
    end

    # Wait for all subprocess to finish, then terminate.
    Process.wait

    Misc::Banner.p 'Download regional sales volumes finished'
  end

  def start_process_and_download( regions, process_number )
    result = fork do
      # I'm the child
      @file = File.open( "data/regional_sales_volumes_#{process_number}.json_stream", 'w' )
      $stdout.reopen("log/regional_sales_volumes_#{process_number}.log", 'a')
      $stderr.reopen("log/regional_sales_volumes_#{process_number}.err", 'a')

      Misc::Banner.p "Download started in process #{Process.pid}"

      regions.each do |region|
        update_for_given_region region
      end

      @file.close

      Misc::Banner.p "Download stopped in process #{Process.pid}"
    end

    # I'm your father luke
    puts "Download process created : #{result}"

    result
  end

  def update_for_given_region( region )

    puts "About to process : #{region.name}" if @verbose_output

    @rest_url = "markets/#{region.cpp_region_id}/types/"
    types_ids = get_all_pages

    puts "#{types_ids.count} types_ids to process" if @verbose_output

    types_ids.each do |type_id|

      @rest_url = "markets/#{region.cpp_region_id}/history/"
      @params[:type_id]=type_id

      total_volume = 0
      total_isk = 0.0

      begin
        get_all_pages.each do |record|

          next if Date.parse(record['date']) <= Time.now - 1.month

          total_volume += record['volume'].to_i
          total_isk += record['volume'].to_f*record['average'].to_f
        end

        # We skip small sales
        next if total_isk < 100000

        record = { cpp_region_id: region.cpp_region_id, cpp_type_id: type_id, volume: total_volume }
        @file.puts( record.to_json )
      rescue Esi::Errors::NotFound
        warn "For region #{region.cpp_region_id} : #{type_id} not found."
      end

    end
  end

end
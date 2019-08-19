require_relative 'download'

# Seems not to require full download of all prices history
# Just jita, see ...
class Esi::DownloadHistory < Esi::Download

  # TODO : Une fois le boulot fait, il faudra supprimer EveMarketHistory et la vue associé (ne pas oublier les modèles)

  def update
    Misc::Banner.p 'About to download regional sales volumes'

    pages_count_sum_fourth_counter = pages_count_sum_fourth = UniverseRegion.sum( :orders_pages_count )/4
    regions = []
    file_index = 1

    UniverseRegion.all.order( 'orders_pages_count DESC' ).each do |region|

      regions << region
      pages_count_sum_fourth_counter -= region.orders_pages_count

      if pages_count_sum_fourth_counter <= 0
        start_process_and_download regions, file_index
        file_index += 1

        pages_count_sum_fourth_counter = pages_count_sum_fourth
        regions = []
      end
    end

    start_process_and_download regions, file_index

    # Wait for all subprocess to finish, then terminate.
    Process.wait( -1 )
  end

  def start_process_and_download( regions, file_number )
    result = fork
    unless result
      # I'm the child
      @file = File.open( "data/regional_sales_volumes_#{file_number}.json_stream", 'w' )
      $stdout.reopen("log/regional_sales_volumes_#{file_number}.log", 'w')
      $stderr.reopen("log/regional_sales_volumes_#{file_number}.err", 'w')

      Misc::Banner.p "Download start at #{Time.now} in process #{Process.pid}"

      regions.each do |region|
        update_for_given_region region
      end

      @file.close

      Misc::Banner.p "Download stop at #{Time.now} in process #{Process.pid}"
    else
      # I'm your father luke
    end

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
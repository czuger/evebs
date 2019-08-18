require_relative 'download'

# Seems not to require full download of all prices history
# Just jita, see ...
class Esi::DownloadHistory < Esi::Download

  # TODO : Une fois le boulot fait, il faudra supprimer EveMarketHistory et la vue associé (ne pas oublier les modèles)

  def update
    Misc::Banner.p 'About to download regional sales volumes'

    @file = File.open( 'data/regional_sales_volumes.json_stream', 'w' )

    UniverseRegion.all.each do |region|
      puts "Processing region #{region.name}"
      update_for_given_region region
    end

    @file.close
  end

  def update_for_given_region( region )

    @rest_url = "markets/#{region.cpp_region_id}/types/"
    types_ids = get_all_pages

    puts "#{types_ids.count} to process" if @verbose_output

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
        puts "For region #{region.cpp_region_id} : #{type_id} not found."
      end

    end
  end

end
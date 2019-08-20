require_relative 'download'

class Esi::DownloadHistoryReadItemsLists < Esi::Download

  PROCESSES_COUNT = 4

  def update
    Misc::Banner.p 'About to download regional items lists and update processes ids'

    # This is to avoid starting processes on processes repartition error
    UniverseRegion.update_all( download_process_id: nil )

    download_by_region_types_list
    update_process_ids

    Misc::Banner.p 'Download regional regional items lists and update of processes ids finished'
  end

  def download_by_region_types_list
    UniverseRegion.all.each do |region|

      @rest_url = "markets/#{region.cpp_region_id}/types/"
      types_ids = get_all_pages

      puts "#{types_ids.count} types read for region #{region.name}" if @verbose_output

      region.market_items = types_ids
      region.market_items_count = types_ids.count

      region.save!
    end
  end

  def update_process_ids
    tmp_divided_total_types = divided_total_types = UniverseRegion.sum( :market_items_count ) / PROCESSES_COUNT
    process_index = 1

    UniverseRegion.order( 'market_items_count DESC' ).each do |region|
      tmp_divided_total_types -= region.market_items_count

      region.download_process_id = process_index
      region.save!

      if tmp_divided_total_types <= 0
        process_index += 1
        tmp_divided_total_types = divided_total_types
      end
    end
  end

end